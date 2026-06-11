.PHONY: help prod dev stop restart logs test migrate makemigrations shell collectstatic clean build

COMPOSE_PROD  = docker compose
COMPOSE_DEBUG = docker compose -f docker-compose.yml -f docker-compose.debug.yml

help:
	@echo "Usage:  make <target>"
	@echo ""
	@echo "Docker targets:"
	@echo "  make prod         Build and run in production (Nginx + Gunicorn + Postgres)"
	@echo "  make dev          Build and run in debug    (Django runserver + Postgres, port 8000)"
	@echo "  make stop         Stop all containers"
	@echo "  make restart      Restart all containers"
	@echo "  make logs         Tail logs from all containers"
	@echo "  make build        Rebuild images without starting"
	@echo ""
	@echo "Management targets (run inside the web container):"
	@echo "  make test         Run tests"
	@echo "  make migrate      Apply database migrations"
	@echo "  make makemigrations  Generate new migrations"
	@echo "  make shell        Open Django shell"
	@echo "  make collectstatic   Collect static files"
	@echo "  make clean        Remove Python cache files (local)"

prod:
	@echo "=========================================="
	@echo "  Starting PRODUCTION stack..."
	@echo "  Access via http://localhost:8000"
	@echo "=========================================="
	$(COMPOSE_PROD) up --build -d
	@echo ""
	@echo "  Production server is up."
	@echo "  Run 'make logs' to follow output."

dev:
	@echo "=========================================="
	@echo "  Starting DEBUG stack..."
	@echo "  Access via http://localhost:8000"
	@echo "=========================================="
	$(COMPOSE_DEBUG) up --build
	@echo ""
	@echo "  Debug server is up."
	@echo "  Run 'make logs' to follow output."

stop:
	@echo "Stopping all containers..."
	$(COMPOSE_PROD) down

restart:
	@echo "Restarting all containers..."
	$(COMPOSE_PROD) restart

logs:
	$(COMPOSE_PROD) logs -f

build:
	$(COMPOSE_PROD) build

test:
	$(COMPOSE_PROD) exec web python manage.py test tests/ --verbosity=2

migrate:
	$(COMPOSE_PROD) exec web python manage.py migrate --noinput

makemigrations:
	$(COMPOSE_PROD) exec web python manage.py makemigrations

shell:
	$(COMPOSE_PROD) exec web python manage.py shell

collectstatic:
	$(COMPOSE_PROD) exec web python manage.py collectstatic --noinput

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
