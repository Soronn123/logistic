.PHONY: help test run dev migrate shell collectstatic clean

help:
	@echo "Available commands:"
	@echo "  make test       - Run all tests"
	@echo "  make run        - Run tests, then start production server (gunicorn)"
	@echo "  make dev        - Run tests, then start development server (runserver)"
	@echo "  make migrate    - Apply database migrations"
	@echo "  make shell      - Open Django shell"
	@echo "  make collectstatic - Collect static files"
	@echo "  make clean      - Remove Python cache files"

test:
	@echo "=========================================="
	@echo "  Running tests..."
	@echo "=========================================="
	.venv/bin/python manage.py test tests/ --verbosity=2
	@echo "=========================================="
	@echo "  All tests passed!"
	@echo "=========================================="

run: test
	@echo "=========================================="
	@echo "  Starting production server..."
	@echo "=========================================="
	.venv/bin/python manage.py migrate --noinput
	.venv/bin/python manage.py collectstatic --noinput
	.venv/bin/gunicorn baikal.wsgi:application --bind 0.0.0.0:8000 --workers 4

dev: test
	@echo "=========================================="
	@echo "  Starting development server..."
	@echo "=========================================="
	.venv/bin/python manage.py migrate --noinput
	.venv/bin/python manage.py runserver 0.0.0.0:8000

devnotest:
	@echo "=========================================="
	@echo "  Starting development server..."
	@echo "=========================================="
	.venv/bin/python manage.py runserver 0.0.0.0:8000

migrate:
	.venv/bin/python manage.py makemigrations
	.venv/bin/python manage.py migrate

shell:
	.venv/bin/python manage.py shell

collectstatic:
	.venv/bin/python manage.py collectstatic --noinput

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
