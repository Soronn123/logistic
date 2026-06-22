#!/bin/bash
set -eo pipefail

# Baikal-Service — Production deploy script with SSL (Let's Encrypt)
# Usage:  sudo ./deploy.sh <domain> <email>
# Example: sudo ./deploy.sh app.example.com admin@example.com

DOMAIN=${1:-}
EMAIL=${2:-}
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE="docker compose"

# ─── Helpers ─────────────────────────────────────────────────
die() { echo "[ERROR] $*" >&2; exit 1; }
info() { echo "[INFO] $*"; }
ask() {
  local prompt="$1"
  local default="${2:-}"
  read -rp "$prompt${default:+ [$default]}: " val
  echo "${val:-$default}"
}

# ─── Pre-flight checks ─────────────────────────────────────────
[[ $EUID -eq 0 ]] || die "Please run as root (or with sudo) so certbot can bind :80/:443 and write cron jobs."
command -v docker >/dev/null || die "Docker is not installed."
command -v docker-compose &>/dev/null || command -v docker &>/dev/null || die "Docker Compose plugin not found."
[[ -f "$PROJECT_DIR/docker-compose.yml" ]] || die "docker-compose.yml not found in $PROJECT_DIR"
[[ -f "$PROJECT_DIR/.env" ]] || die ".env file not found"

if [[ -z "$DOMAIN" ]]; then
  DOMAIN=$(ask "Enter your public domain for this deployment" "")
  [[ -n "$DOMAIN" ]] || die "Domain is required."
fi
if [[ -z "$EMAIL" ]]; then
  EMAIL=$(ask "Enter e-mail address for Let's Encrypt notifications" "")
  [[ -n "$EMAIL" ]] || die "E-mail is required."
fi

info "Deploying Baikal-Service to production"
info "  Domain : $DOMAIN"
info "  E-mail : $EMAIL"
info "  Dir    : $PROJECT_DIR"

# ─── Prepare .env ────────────────────────────────────────────
info "Updating .env with production values..."

# Ensure a real secret key exists
if grep -q '^DJANGO_SECRET_KEY=change-me' "$PROJECT_DIR/.env"; then
  NEW_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || openssl rand -base64 50 | tr -dc 'a-zA-Z0-9!@#%^&*(-_=+)' | head -c 50)
  sed -i "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=${NEW_KEY}|" "$PROJECT_DIR/.env"
  info "Generated a new DJANGO_SECRET_KEY."
fi

# Update ALLOWED_HOSTS
sed -i "s|^DJANGO_ALLOWED_HOSTS=.*|DJANGO_ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},localhost,127.0.0.1|" "$PROJECT_DIR/.env"

info ".env prepared."

# ─── Build & start containers ────────────────────────────────
cd "$PROJECT_DIR"
info "Building images..."
$COMPOSE build --no-cache

info "Starting services in the background..."
$COMPOSE up -d

# ─── Wait for DB ─────────────────────────────────────────────
info "Waiting for PostgreSQL to accept connections..."
for i in {1..30}; do
  if $COMPOSE exec -T db pg_isready -U baikal -q 2>/dev/null; then
    break
  fi
  sleep 1
done
info "PostgreSQL is ready."

# ─── Run migrations (safety net) ───────────────────────────
info "Applying database migrations inside the 'web' container..."
$COMPOSE exec -T web python manage.py migrate --noinput

# ─── Load fixtures if DB looks empty ───────────────────────
CITY_COUNT=$($COMPOSE exec -T web python manage.py shell -c "from apps.geo.models import City; print(City.objects.count())" 2>/dev/null | tail -1 || echo "0")
if [[ "$CITY_COUNT" == "0" ]]; then
  info "Database appears empty — loading fixtures / seed data..."
  $COMPOSE exec -T web python manage.py seed_data --force
else
  info "Database already seeded ($CITY_COUNT cities), skipping fixtures."
fi

# ─── Collect static files ────────────────────────────────────
info "Collecting static files..."
$COMPOSE exec -T web python manage.py collectstatic --noinput

# ─── SSL / Let's Encrypt ───────────────────────────────────
info "Requesting SSL certificate from Let's Encrypt..."

# Make sure the webroot volume exists and nginx is serving ACME challenges
$COMPOSE exec -T nginx mkdir -p /var/www/certbot

# Obtain certificate using webroot ($COMPOSE with exec to use existing nginx)
$COMPOSE exec -T nginx certbot certonly \
  --webroot \
  -w /var/www/certbot \
  -d "$DOMAIN" \
  --email "$EMAIL" \
  --agree-tos \
  --non-interactive \
  --rsa-key-size 4096 \
  --staging=false || die "Certbot failed. Check DNS points to this server and ports 80/443 are open."

info "Certificate obtained successfully for $DOMAIN."

# ─── Deploy HTTPS nginx configuration ────────────────────────
info "Installing HTTPS nginx configuration..."

cat > "$PROJECT_DIR/deploy/nginx/default.conf" <<'NGINX'
upstream django {
    server web:8000;
}

# Redirect HTTP -> HTTPS
server {
    listen 80;
    server_name _;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name _;

    ssl_certificate /etc/letsencrypt/live/<DOMAIN>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<DOMAIN>/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        access_log off;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 1y;
        access_log off;
        add_header Cache-Control "public, immutable";
    }
}
NGINX

# Inject the real domain into the SSL paths
sed -i "s|<DOMAIN>|${DOMAIN}|g" "$PROJECT_DIR/deploy/nginx/default.conf"

$COMPOSE exec -T nginx cp /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.bak 2>/dev/null || true
$COMPOSE cp "$PROJECT_DIR/deploy/nginx/default.conf" nginx:/etc/nginx/conf.d/default.conf
$COMPOSE exec -T nginx nginx -t || die "Nginx configuration test failed."
$COMPOSE exec -T nginx nginx -s reload

# ─── Auto-renewal cron job ───────────────────────────────────
CRON_CMD="0 3 * * * cd ${PROJECT_DIR} && ${COMPOSE} exec -T nginx certbot renew --quiet && ${COMPOSE} exec -T nginx nginx -s reload >> /var/log/baikal-certbot-renew.log 2>&1"
if ! crontab -l 2>/dev/null | grep -qF "baikal-certbot-renew"; then
  info "Installing auto-renewal cron job..."
  (crontab -l 2>/dev/null || true; echo "# baikal-certbot-renew"; echo "$CRON_CMD") | crontab -
else
  info "Auto-renewal cron job already present."
fi

# ─── Summary ─────────────────────────────────────────────────
info ""
info "=========================================="
info "  DEPLOYMENT COMPLETE"
info "=========================================="
info "  Site      : https://${DOMAIN}"
info "  Local HTTP: http://localhost  (redirects to HTTPS)"
info ""
info "  Useful commands (run from ${PROJECT_DIR}):"
info "    docker compose logs -f          # view all logs"
info "    docker compose exec web bash    # shell in Django"
info "    make migrate                    # apply migrations"
info "    make loadfixtures               # re-load seed data"
info "    make test                       # run tests"
info ""
info "  SSL certificate will auto-renew via cron."
info "=========================================="
