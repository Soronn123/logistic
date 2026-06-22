#!/bin/bash
set -e

# Simple SSL Deployment Script (Webroot Method)
# Usage: ./deploy-ssl-simple.sh <domain-name> [email]

DOMAIN="${1:-}"
EMAIL="${2:-admin@example.com}"

if [ -z "$DOMAIN" ]; then
    echo "Usage: $0 <domain-name> [email]"
    echo "Example: $0 example.com admin@example.com"
    exit 1
fi

echo "=========================================="
echo "SSL Deployment Script (Webroot Method)"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo "=========================================="

# Determine docker compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Step 1: Start nginx temporarily with HTTP only for certbot challenge
echo ""
echo "Step 1: Starting services..."
$COMPOSE_CMD up -d --build

# Wait for nginx to start
sleep 5

# Step 2: Obtain SSL certificate using webroot method
echo ""
echo "Step 2: Obtaining SSL certificate..."

$COMPOSE_CMD run --rm \
    -v certbot_certs:/etc/letsencrypt \
    -v certbot_data:/var/www/certbot \
    nginx \
    certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN" || true

# Alternative: use certbot docker image
docker run --rm \
    -v certbot_certs:/etc/letsencrypt \
    -v certbot_data:/var/www/certbot \
    certbot/certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN"

# Step 3: Update nginx config with domain and restart
echo ""
echo "Step 3: Configuring Nginx with SSL..."

# Create nginx config with actual domain
cat > deploy/nginx/default.conf << EOF
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name $DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 10M;

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Restart nginx to apply new config
$COMPOSE_CMD restart nginx

# Step 4: Set up auto-renewal
echo ""
echo "Step 4: Setting up SSL auto-renewal cron job..."

cat > renew-ssl.sh << EOF
#!/bin/bash
cd ${PWD}
docker run --rm \\
    -v certbot_certs:/etc/letsencrypt \\
    -v certbot_data:/var/www/certbot \\
    certbot/certbot renew --webroot --webroot-path /var/www/certbot --quiet
$COMPOSE_CMD exec -T nginx nginx -s reload
EOF

chmod +x renew-ssl.sh

# Add cron job (renew twice daily)
(crontab -l 2>/dev/null | grep -v renew-ssl.sh; echo "0 0,12 * * * ${PWD}/renew-ssl.sh >> ${PWD}/renew-ssl.log 2>&1") | crontab -

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Site available at: https://$DOMAIN"
echo ""
echo "To check certificate: docker run --rm -v certbot_certs:/etc/letsencrypt certbot/certbot certificates"
echo ""
