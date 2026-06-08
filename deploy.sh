#!/bin/bash
set -e

# Ввод данных
read -p "Введите домен (например, example.com): " DOMAIN
read -p "Введите email для SSL (например, admin@example.com): " EMAIL
PROJECT_NAME=$(python3 -c "import os; print(os.path.basename(os.getcwd()))" || echo "myproject")

echo "🚀 Настройка окружения..."

# 1. Создание структуры папок
mkdir -p nginx certbot/conf certbot/www data static

# 2. Генерация docker-compose.yml
cat > docker-compose.yml <<EOF
services:
  web:
    build: .
    environment:
      - DJANGO_ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},localhost,127.0.0.1,web
    volumes:
      - sqlite_data:/app/data
      - static_data:/app/static
    command: sh -c "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn ${PROJECT_NAME}.wsgi:application --bind 0.0.0.0:8000"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
      - static_data:/app/static
    depends_on:
      - web

  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait \$${!}; done;'"

volumes:
  sqlite_data:
  static_data:
EOF

# 3. Генерация nginx/default.conf
cat > nginx/default.conf <<EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /app/static/;
    }
}
EOF

# 4. Создание Dockerfile (если его нет)
if [ ! -f Dockerfile ]; then
cat > Dockerfile <<EOF
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY . .
RUN uv pip install --system -r requirements.txt
EOF
fi

echo "🔐 Получение SSL сертификата..."
docker compose up -d nginx
docker compose run --rm certbot certonly --webroot --webroot-path /var/www/certbot --email $EMAIL --agree-tos --no-eff-email -d $DOMAIN -d www.$DOMAIN
docker compose restart nginx

echo "⚙️ Сборка и запуск проекта..."
docker compose up -d --build

echo "✅ Готово! Твой проект доступен по адресу: https://${DOMAIN}"
