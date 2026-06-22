#!/bin/bash
set -e

# SSL Deployment Script for Docker + Nginx + Let's Encrypt
# Usage: ./deploy-ssl.sh <domain-name> [email]

DOMAIN="${1:-}"
EMAIL="${2:-}"

if [ -z "$DOMAIN" ]; then
    echo "Usage: $0 <domain-name> [email]"
    echo "Example: $0 example.com admin@example.com"
    exit 1
fi

if [ -z "$EMAIL" ]; then
    echo "Enter your email for Let's Encrypt notifications: "
    read EMAIL
fi

echo "=========================================="
echo "SSL Deployment Script"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo "=========================================="

# Determine docker compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Step 1: Ensure .env has correct settings
echo ""
echo "Step 1: Updating configuration..."
if [ -f ".env" ]; then
    # Update allowed hosts
    if grep -q "DJANGO_ALLOWED_HOSTS" .env; then
        sed -i "s/DJANGO_ALLOWED_HOSTS=.*/DJANGO_ALLOWED_HOSTS=$DOMAIN,localhost,127.0.0.1/" .env
    else
        echo "DJANGO_ALLOWED_HOSTS=$DOMAIN,localhost,127.0.0.1" >> .env
    fi
fi

# Step 2: Start services with HTTP only (for certbot challenge)
echo ""
echo "Step 2: Starting services..."

# Create temporary nginx config for HTTP only
cat > deploy/nginx/default.conf << 'EOF'
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name _;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

$COMPOSE_CMD up -d --build

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Step 3: Obtain SSL certificate
echo ""
echo "Step 3: Obtaining SSL certificate from Let's Encrypt..."

docker run --rm \
    -v certbot_certs:/etc/letsencrypt \
    -v certbot_data:/var/www/certbot \
    -v certbot_certs:/var/log/letsencrypt \
    certbot/certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --domain "$DOMAIN"

# Check if certificate was obtained successfully
if docker run --rm -v certbot_certs:/etc/letsencrypt certbot/certbot certificates 2>&1 | grep -q "$DOMAIN"; then
    echo "Certificate obtained successfully!"
else
    echo "Failed to obtain certificate. Check the logs above."
    exit 1
fi

# Step 4: Update nginx config with SSL
echo ""
echo "Step 4: Configuring Nginx with SSL..."

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
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

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

# Step 5: Restart nginx to apply SSL config
echo ""
echo "Step 5: Restarting Nginx with SSL..."
$COMPOSE_CMD restart nginx

# Step 6: Set up auto-renewal
echo ""
echo "Step 6: Setting up SSL auto-renewal..."

cat > renew-ssl.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "Renewing SSL certificates..."
docker run --rm \
    -v certbot_certs:/etc/letsencrypt \
    -v certbot_data:/var/www/certbot \
    certbot/certbot renew --quiet

echo "Reloading Nginx..."
docker compose exec -T nginx nginx -s reload 2>/dev/null || docker-compose exec -T nginx nginx -s reload

echo "SSL renewal check completed at $(date)"
EOF

chmod +x renew-ssl.sh

# Add cron job for auto-renewal (runs twice daily at midnight and noon)
(crontab -l 2>/dev/null | grep -v renew-ssl.sh; echo "0 0,12 * * * $(pwd)/renew-ssl.sh >> $(pwd)/logs/renew-ssl.log 2>&1") | crontab -

# Create logs directory
mkdir -p logs

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Your site is now available at:"
echo "  https://$DOMAIN"
echo ""
echo "SSL certificates will auto-renew via cron job."
echo ""
echo "Useful commands:"
echo "  - Check certificates: docker run --rm -v certbot_certs:/etc/letsencrypt certbot/certbot certificates"
echo "  - Manual renewal: ./renew-ssl.sh"
echo "  - View logs: docker compose logs -f nginx"
echo ""
