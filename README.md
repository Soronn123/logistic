# Baikal-Service

**Logistics and Cargo Transportation Management System**

A comprehensive web application for Baikal-Service, a logistics company founded in 2005 that provides cargo transportation services across Russia, Kazakhstan, Belarus, Kyrgyzstan, and China.

---

## Company Overview

**Baikal-Service** is a leading logistics and cargo transportation company:
- Founded: 2005 in Moscow, Russia
- Coverage: 200+ cities across 5 countries
- Network: 80+ branches
- Experience: 1.5M+ shipments delivered
- Clients: Thousands of corporate clients

The company provides domestic and international cargo transportation, warehouse services, and comprehensive logistics solutions.

---

## Tech Stack

### Backend
- **Framework:** Django 6.0.6
- **Language:** Python ≥3.13 (3.13.7 / 3.14.5)
- **Database:** PostgreSQL 16 (Production), SQLite (Development)
- **API:** Django REST Framework patterns with JSON endpoints

### Frontend
- **Templates:** Django Server-side Templates (109 HTML files)
- **Styling:** Tailwind CSS
- **Interactivity:** Alpine.js, HTMX
- **Icons:** Font Awesome

### Infrastructure & Deployment
- **Containerization:** Docker & Docker Compose
- **Web Server:** Nginx (Alpine)
- **WSGI Server:** Gunicorn
- **Package Manager:** uv (0.8.17)

### Additional Technologies
- **Internationalization:** Django i18n (Russian, English)
- **Testing:** Django TestCase (7 test files)
- **Task Simulation:** Custom routing engine with cargo transportation simulation

---

## Features

### Public Website
- Home page with news, reviews, and promotions
- Company information and history
- Service catalog with categories and pricing
- Shipping calculator and delivery time estimator
- Order tracking system
- News, vacancies, reviews, and FAQ sections
- Contact forms and partner program

### User Account
- Email-based authentication
- Profile management and settings
- Balance management and transaction history
- Order management and tracking
- Support ticket system
- Saved templates for contacts, delivery, and cargo
- Accounting document requests

### Admin Dashboard
- Full CRUD interface for all entities
- Order management with simulation
- User and permission management
- Content management (news, vacancies, reviews, etc.)
- Branch and service management
- Partner and banner management

### Advanced Features
- **Cargo Transportation Simulation:** Auto-assignment of services, pricing engine, route calculation
- **Bilingual Support:** Russian and English with i18n_patterns
- **HTMX Integration:** Dynamic page updates without full reloads
- **Theme Support:** Light/dark mode
- **Real-time Tracking:** Virtual location tracking for live maps

---

## Quick Start

### Prerequisites
- Python ≥3.13
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL 16 (for production without Docker)
- uv package manager (recommended) or pip

### Running with Docker (Recommended)

#### Production Mode
```bash
make prod
```
- Builds and runs Nginx + Gunicorn + PostgreSQL
- Access at: http://localhost:8000

#### Development Mode
```bash
make dev
```
- Uses Django runserver with bind-mounted code for hot-reload
- No Nginx (direct access to Django)
- Access at: http://localhost:8000

#### Other Docker Commands
```bash
make stop          # Stop all containers
make restart       # Restart all containers
make logs          # View logs from all containers
make build         # Rebuild images without starting
```

### Running Locally (Without Docker)

1. **Create virtual environment and install dependencies:**
```bash
make venv
```

2. **Start local development server with SQLite:**
```bash
make local
```
- Uses SQLite database
- Auto-migrates on startup
- Access at: http://localhost:8000

### Running Tests

**With Docker:**
```bash
make test
```

**Locally:**
```bash
make test-local
```

---

## Environment Setup

1. **Clone the repository**

2. **Copy environment file:**
```bash
cp .env.example .env
```

3. **Edit `.env` file** with your settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | `change-me-to-a-real-secret-key-in-production` |
| `DJANGO_DEBUG` | Debug mode | `False` |
| `DJANGO_ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DJANGO_DB_ENGINE` | Database engine | `django.db.backends.postgresql` |
| `DJANGO_DB_NAME` | Database name | `baikal` |
| `DJANGO_DB_USER` | Database user | `baikal` |
| `DJANGO_DB_PASSWORD` | Database password | `baikal_secret` |
| `DJANGO_DB_HOST` | Database host | `db` |
| `DJANGO_DB_PORT` | Database port | `5432` |

For complete list of environment variables, see `.env.example`.

---

## Project Structure

```
front5/
├── apps/                          # 8 Django applications
│   ├── core/          # Public pages, content, news, vacancies
│   ├── users/         # Authentication, profile, balance, tickets
│   ├── services/      # Service catalog, categories, tariffs
│   ├── orders/        # Order CRUD, tracking, routing engine
│   ├── geo/           # Cities, branches (warehouses/pickup points)
│   ├── partners/      # Partner applications, banners, iframe modules
│   ├── documents/     # Document repository, accounting requests
│   └── dashboard/     # Staff admin panel with full CRUD
├── baikal/                       # Django project settings
├── templates/                    # 109 HTML template files
├── deploy/                       # Docker entrypoint, Nginx config
├── fixtures/                     # Initial seed data (JSON)
├── static/                       # Static assets (CSS, JS, images)
├── media/                        # User-uploaded files
├── tests/                        # Django test suite (7 files)
├── locale/                       # Translation files (RU/EN)
├── Dockerfile                    # Production container image
├── docker-compose.yml            # Production stack
├── docker-compose.debug.yml      # Debug stack
├── Makefile                      # 18 command targets
├── requirements.txt              # Python dependencies
└── .env.example                  # Environment variable template
```

---

## Makefile Commands

### Docker Targets
| Command | Description |
|---------|-------------|
| `make prod` | Build & run production stack |
| `make dev` | Build & run debug stack with hot-reload |
| `make stop` | Stop all containers |
| `make restart` | Restart all containers |
| `make logs` | Tail logs from all containers |
| `make build` | Rebuild images without starting |

### Management Targets (Inside Docker Container)
| Command | Description |
|---------|-------------|
| `make test` | Run tests |
| `make migrate` | Apply database migrations |
| `make makemigrations` | Generate new migrations |
| `make shell` | Open Django shell |
| `make collectstatic` | Collect static files |
| `make loadfixtures` | Load seed data into database |

### Local (Non-Docker) Targets
| Command | Description |
|---------|-------------|
| `make venv` | Create virtual environment |
| `make local` | Local dev server with SQLite |
| `make test-local` | Run tests with in-memory SQLite |
| `make loadfixtures-local` | Load seed data to local SQLite |

---

## Database Information

**Production (PostgreSQL):**
- Database: `baikal`
- User: `baikal`
- Password: `baikal_secret`
- Host: `db` (Docker service name)
- Port: `5432`

**Development (SQLite):**
- Database file: `db.sqlite3`

---

## Key Configuration

### Custom User Model
- Email as `USERNAME_FIELD`
- Fields: phone, balance, role (client/manager/admin), language, theme
- Company support with `company_name`, `inn`, `is_company`

### Settings Highlights
- `LANGUAGE_CODE = 'ru'` (Russian default)
- `TIME_ZONE = 'Europe/Moscow'`
- `LANGUAGES = [('ru', 'Russian'), ('en', 'English')]`
- Bilingual support with `i18n_patterns`

---

## Deployment Architecture

### Production Stack (3 services)
1. **db** - PostgreSQL 16 Alpine with persistent volume
2. **web** - Django application with Gunicorn
3. **nginx** - Reverse proxy serving static files and proxying Django requests

### Entrypoint Process
1. Waits for PostgreSQL to be ready
2. Runs migrations
3. Seeds data if City table is empty
4. Collects static files
5. Starts Gunicorn (4 workers)

---

## Development Notes

### Code Style
- Ruff linter (pyproject.toml): line-length 120, single quotes, target py313
- No type checker, no pre-commit, no lint CI

### Testing
- Django TestCase with in-memory SQLite (`make test-local`)
- All tests in `tests/` directory (7 files)
- Tests create their own fixtures

---

**Built with Django and ❤️ for Baikal-Service**
