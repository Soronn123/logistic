# Baikal-Service

**Logistics and cargo transportation web application** serving Russia, Kazakhstan, Belarus, Kyrgyzstan, and China. Built with Django 6.0.6, Python ≥3.13, PostgreSQL, Docker, Tailwind CSS, Alpine.js, and HTMX. Bilingual (RU/EN).

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Project Structure](#project-structure)
3. [Pages](#pages)
4. [URL Endpoints](#url-endpoints)
5. [Models](#models)
6. [Cargo Transportation Simulation](#cargo-transportation-simulation)
7. [Docker & Deployment](#docker--deployment)
8. [Makefile Commands](#makefile-commands)
9. [Settings & Configuration](#settings--configuration)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6.0.6, Python ≥3.13 |
| **Database** | PostgreSQL 16 (prod), SQLite (dev) |
| **Frontend** | Server-side Django templates, Tailwind CSS, Alpine.js, HTMX, Font Awesome |
| **i18n** | Russian (default), English |
| **Deployment** | Docker Compose, Nginx, Gunicorn |
| **Testing** | Django TestCase (7 test files) |

---

## Project Structure

```
front5/
├── apps/
│   ├── core/          # Public pages, content, news, vacancies, reviews, FAQ, contact, tenders, promotions
│   ├── users/         # Authentication, profile, balance, tickets, templates, company applications
│   ├── services/      # Service catalog, categories, additional services, weight-based tariffs
│   ├── orders/        # Order CRUD, tracking, routing engine, simulation, JSON API
│   ├── geo/           # Cities, branches (warehouses/pickup points/offices)
│   ├── partners/      # Partner applications, banners, iframe embed modules
│   ├── documents/     # Document repository, accounting document requests
│   └── dashboard/     # Staff admin panel with full CRUD for all entities
├── baikal/            # Django project settings, root URL conf, WSGI
├── templates/         # 109 HTML template files (base, partials, pages)
│   ├── pages/core/          # 27 public pages
│   ├── pages/users/         # 16 account pages
│   ├── pages/services/      # 5 service pages
│   ├── pages/orders/        # 5 order pages
│   ├── pages/geo/           # 2 branch pages
│   ├── pages/partners/      # 4 partner pages
│   ├── pages/documents/     # 2 document pages
│   └── pages/dashboard/     # 42 admin dashboard pages
├── deploy/            # Docker entrypoint, Nginx config
├── fixtures/          # Initial seed data (JSON)
├── static/            # Static assets (CSS, JS, images)
├── staticfiles/       # Collected static files (prod)
├── media/             # User-uploaded files
├── tests/             # Django test suite (7 files)
├── locale/            # Translation files (RU/EN)
├── Dockerfile         # Production container image
├── docker-compose.yml         # Production stack (Postgres + Web + Nginx)
├── docker-compose.debug.yml   # Debug stack (bind-mounted, runserver, no Nginx)
├── Makefile           # 18 command targets
├── pyproject.toml     # Python project metadata
├── requirements.txt   # Python dependencies
├── uv.lock            # Lock file (uv package manager)
└── .env.example       # Environment variable template
```

---

## Pages

### Public Website (27 pages)

| Page | Route | Description |
|------|-------|-------------|
| Home | `/` | Pinned news, approved reviews, active promotions, cities, services, branches |
| About | `/about/` | Company information |
| News | `/news/` | Paginated news listing with detail pages |
| Reviews | `/reviews/` | Customer reviews, filterable by rating |
| Vacancies | `/careers/` | Job listings filterable by department and city |
| Contact | `/contact/` | Contact form (creates ContactMessage) |
| FAQ | `/faq/` | Published questions and answers |
| Tenders | `/tenders/` | Active tender listings |
| Promotions | `/promotions/` | Active promotional campaigns |
| Directions | `/directions/` | Service region information |
| Calculator | `/tools/calculator/` | HTMX-powered shipping cost estimation |
| Delivery Times | `/tools/delivery-times/` | Estimated delivery time between cities |
| Tracking | `/tracking/` | Order tracking by tracking number (HTMX) |
| Tariffs | `/tariffs/` | Weight-based pricing table |
| Mobile App | `/mobile-app/` | Mobile application info |
| Brand Assets | `/brand-assets/` | Branding resources |
| Press | `/press/` | Press kit and media information |
| Warehouse | `/warehouse/` | Warehouse services information |
| Info Pages | `/info/<page_type>/` | Dynamic content pages (about, press, etc.) |
| Privacy Policy | `/privacy-policy/` | Privacy policy |
| Terms of Use | `/terms-of-use/` | Terms of use |
| Transport Terms | `/transport-terms/` | Transportation terms |

### User Account (16 pages)

| Page | Route | Description |
|------|-------|-------------|
| Login | `/login/` | Email-based authentication |
| Register | `/register/` | New user registration |
| Profile | `/profile/` | User dashboard overview |
| Settings | `/profile/settings/` | Profile editing, password change |
| Balance | `/profile/balance/` | Transaction history |
| Balance Top-Up | `/profile/balance/topup/` | Deposit funds |
| Balance Success | `/profile/balance/success/` | Top-up confirmation |
| Orders | `/profile/orders/` | Personal orders list |
| Order Detail | `/profile/orders/<slug:tracking_number>/` | Single order details |
| Tickets | `/profile/tickets/` | Support tickets list |
| Ticket Create | `/profile/tickets/create/` | New support ticket |
| Ticket Detail | `/profile/tickets/<int:pk>/` | Ticket conversation |
| Templates | `/profile/templates/` | Saved contact/delivery/cargo templates |
| Template Edit | `/profile/templates/<int:pk>/edit/` | Edit delivery template |
| Accounting Docs | `/profile/documents/` | Request invoices, acts, receipts |
| Company Apply Success | `/profile/company/apply/success/` | Company application confirmation |

### Services (5 pages)

| Page | Route | Description |
|------|-------|-------------|
| Service Categories | `/services/` | All service categories |
| Category Detail | `/services/<slug:slug>/` | Services within a category |
| Service Detail | `/services/<slug:category_slug>/<slug:slug>/` | Individual service description |
| Additional Services | `/services/additional/` | Optional add-ons list |
| Tariffs | `/services/tariffs/` | Weight-based tariff table |

### Orders (5 pages)

| Page | Route | Description |
|------|-------|-------------|
| Create Order | `/orders/create/` | Full order form with pricing and ETA |
| Track Order | `/orders/track/<slug:tracking_number>/` | Order tracking detail |
| Public Tracking | `/tracking/<slug:tracking_number>/` | Public tracking page (no auth) |
| Door Delivery Request | `/orders/track/<slug:tracking_number>/door-delivery/` | Request door-to-door service |
| Request Changes | `/orders/track/<slug:tracking_number>/request-changes/` | Request order modification |

### Geo / Branches (2 pages)

| Page | Route | Description |
|------|-------|-------------|
| Branch Map | `/geo/` | All branches on a map |
| City Branches | `/geo/<int:pk>/` | Branches in a specific city |

### Partners (4 pages)

| Page | Route | Description |
|------|-------|-------------|
| Partners Overview | `/partners/` | Partner program info |
| Partner Apply | `/partners/apply/` | Partnership application form |
| Iframe Modules | `/partners/iframe/` | Embeddable widgets for partner sites |
| Banners | `/partners/banners/` | Available advertising banners |

### Documents (2 pages)

| Page | Route | Description |
|------|-------|-------------|
| Documents | `/documents/` | Document repository by category |
| Documents by Category | `/documents/<str:category>/` | Filtered document list |

### Admin Dashboard (42 pages)

Full CRUD interface for all entities:

| Section | Routes | Description |
|---------|--------|-------------|
| Dashboard Home | `/dashboard/` | Stats (today's orders, active shipments, open tickets, total users) |
| Users | `/dashboard/users/` | List, create, edit, delete |
| Orders | `/dashboard/orders/` | List, detail, edit, delete, **simulate** |
| Tickets | `/dashboard/tickets/` | View and manage support tickets |
| Services | `/dashboard/services/` | CRUD for services, categories, tariffs |
| Content | `/dashboard/content/` | CRUD for pages, news, vacancies, FAQs, reviews, tenders |
| Branches | `/dashboard/branches/` | CRUD for branches |
| Documents | `/dashboard/documents/` | View documents and accounting requests |
| Partners | `/dashboard/partners/` | Manage applications, banners |
| Contacts | `/dashboard/contacts/` | View contact form submissions |
| Settings | `/dashboard/settings/` | Site settings |
| Permissions | `/dashboard/directory-permissions/` | Manager directory access control |

---

## URL Endpoints

### Root URL Configuration (`baikal/urls.py`)

```
Non-i18n routes:
  /i18n/                                    Language switcher
  /tracking/                                Public tracking lookup form

i18n-prefixed routes (RU/EN):
  /tracking/<slug:tracking_number>/         Public tracking detail
  /admin/                                   Django admin
  /                                         Core public pages
  /                                         User account pages
  /services/                                Services catalog
  /orders/                                  Orders + JSON API
  /geo/                                     Geography & branches
  /partners/                                Partner program
  /documents/                               Document repository
  /dashboard/                               Admin dashboard
```

### Complete Endpoint List (~122 routes)

#### Core (`apps/core/urls.py`)
```
GET  /                                           HomeView
GET  /about/                                     AboutView
GET  /news/                                      NewsListView
GET  /news/<slug:slug>/                          NewsDetailView
GET  /reviews/                                   ReviewsView
GET  /careers/                                   VacancyListView
GET  /careers/<slug:slug>/                       VacancyDetailView
POST /contact/                                   ContactView
GET  /faq/                                       FAQView
GET  /tenders/                                   TenderListView
GET  /tenders/<slug:slug>/                       TenderDetailView
GET  /promotions/                                PromotionListView
GET  /promotions/<slug:slug>/                    PromotionDetailView
GET  /directions/                                DirectionsView
GET  /tools/calculator/                          CalculatorView
GET  /tools/delivery-times/                      DeliveryTimesView
GET  /tools/create-order/                        CreateOrderRedirectView
GET  /tracking/                                  TrackView
GET  /tariffs/                                   TariffsView
GET  /mobile-app/                                MobileAppView
GET  /brand-assets/                              BrandAssetsView
GET  /press/                                     PressView
GET  /warehouse/                                 WarehouseView
GET  /info/<slug:page_type>/                     InfoPageView
GET  /privacy-policy/                            PrivacyPolicyView
GET  /terms-of-use/                              TermsOfUseView
GET  /transport-terms/                           TransportTermsView
```

#### Users (`apps/users/urls.py`)
```
GET+POST /login/                                 LoginView
GET+POST /logout/                                LogoutView
GET+POST /register/                              RegisterView
GET      /profile/                               ProfileView
GET+POST /profile/settings/                      ProfileSettingsView
GET      /profile/balance/                       BalanceView
GET+POST /profile/balance/topup/                 BalanceTopUpView
GET      /profile/balance/success/               BalanceSuccessView
GET      /profile/company/apply/success/         CompanyApplySuccessView
GET      /profile/tickets/                       TicketListView
GET+POST /profile/tickets/create/                TicketCreateView
GET      /profile/tickets/<int:pk>/              TicketDetailView
GET      /profile/orders/                        OrderListView
GET      /profile/orders/<slug:tracking_number>/ OrderDetailView
GET      /profile/documents/                     AccountingDocumentsView
GET      /profile/templates/                     TemplatesView
GET+POST /profile/templates/<int:pk>/edit/       DeliveryTemplateEditView
```

#### Services (`apps/services/urls.py`)
```
GET  /services/additional/                       AdditionalServiceListView
GET  /services/tariffs/                          TariffListView
GET  /services/                                  ServiceCategoryListView
GET  /services/<slug:slug>/                      ServiceCategoryDetailView
GET  /services/<slug:category_slug>/<slug:slug>/ ServiceDetailView
```

#### Orders (`apps/orders/urls.py`)
```
GET+POST /orders/create/                                              OrderCreateView
GET      /orders/track/<slug:tracking_number>/                        OrderTrackView
GET+POST /orders/track/<slug:tracking_number>/door-delivery/          DoorDeliveryRequestView
GET+POST /orders/track/<slug:tracking_number>/request-changes/        RequestChangesView
POST     /orders/api/<slug:tracking_number>/status/                   OrderStatusUpdateView
POST     /orders/api/<slug:tracking_number>/pickup/                   OrderPickupConfirmView
POST     /orders/api/<slug:tracking_number>/deliver/                  OrderDeliveryConfirmView
GET      /orders/api/<slug:tracking_number>/track/                    OrderTrackingAPIView
GET+POST /orders/api/templates/                                       ContactTemplateListView
DELETE   /orders/api/templates/<int:pk>/                              ContactTemplateDeleteView
GET+POST /orders/api/delivery-templates/                              DeliveryTemplateListView
PUT+DELETE /orders/api/delivery-templates/<int:pk>/                   DeliveryTemplateDetailView
GET+POST /orders/api/cargo-templates/                                 CargoTemplateListView
DELETE   /orders/api/cargo-templates/<int:pk>/                        CargoTemplateDeleteView
GET      /orders/api/address-suggest/                                 AddressSuggestView
```

#### Geo (`apps/geo/urls.py`)
```
GET  /geo/                                     BranchMapView
GET  /geo/<int:pk>/                            CityBranchListView
```

#### Partners (`apps/partners/urls.py`)
```
GET  /partners/                                PartnerOverviewView
POST /partners/apply/                          PartnerApplyView
GET  /partners/iframe/                         IframeModulesView
GET  /partners/banners/                        PartnerBannersView
```

#### Documents (`apps/documents/urls.py`)
```
GET  /documents/                               DocumentListView
GET  /documents/<str:category>/                CategoryDocumentView
```

#### Dashboard (`apps/dashboard/urls.py`) — 63 routes
```
GET      /dashboard/login/                          DashboardLoginView
GET      /dashboard/                                DashboardHomeView
GET      /dashboard/users/                          DashboardUsersView
GET+POST /dashboard/users/create/                   DashboardUserCreateView
GET+POST /dashboard/users/<int:pk>/edit/            DashboardUserUpdateView
POST     /dashboard/users/<int:pk>/delete/          DashboardUserDeleteView
GET      /dashboard/orders/                         DashboardOrdersView
GET      /dashboard/orders/<int:pk>/                DashboardOrderDetailView
GET+POST /dashboard/orders/<int:pk>/edit/           DashboardOrderUpdateView
POST     /dashboard/orders/<int:pk>/delete/         DashboardOrderDeleteView
POST     /dashboard/orders/<int:pk>/simulate/       DashboardOrderSimulateView
GET      /dashboard/tickets/                        DashboardTicketsView
... (full CRUD for services, categories, tariffs, content pages, news, vacancies, FAQs, reviews, tenders, branches, partners, banners, contacts, settings, permissions)
```

---

## Models

### App: `core` — Content & Public Pages (8 models)

| Model | Fields | Relationships |
|-------|--------|---------------|
| **ContentPage** | slug, title, title_en, content, content_en, meta_description, is_published, created_at, updated_at, page_type (about/news/vacancy/review/press/tender/faq) | — |
| **FAQ** | question, question_en, answer, answer_en, category, order, is_published | — |
| **Review** | author_name, author_company, text, rating (1–5), is_approved, created_at, source | — |
| **NewsItem** | title, title_en, slug, short_text, short_text_en, full_text, full_text_en, image, published_at, is_published, is_pinned | — |
| **Vacancy** | title, title_en, slug, department, short_description, full_description, requirements, salary_from, salary_to, is_active, published_at | FK → geo.City |
| **ContactMessage** | name, email, phone, subject, message, is_read, created_at | — |
| **Tender** | title, slug, description, deadline, is_active, published_at | — |
| **Promotion** | title, title_en, slug, short_description, full_description, image, start_date, end_date, is_active, created_at | — |

### App: `users` — Users, Accounts, Templates (9 models)

| Model | Fields | Relationships |
|-------|--------|---------------|
| **CustomUser** | email (unique, login field), username, phone, balance, role (client/manager/admin), language (ru/en), theme (light/dark), company_name, inn, is_company, avatar | Extends AbstractUser, USERNAME_FIELD=email |
| **ContactTemplate** | name, template_type (sender/recipient), recipient_name, recipient_phone, recipient_email, address_detail, created_at | FK → CustomUser, FK → geo.City |
| **DeliveryTemplate** | name, weight, length, width, height, cargo_description, declared_value, sender_address_detail, recipient_address_detail, total_price | FK → CustomUser, FK → geo.City (from/to), FK → Service, M2M → AdditionalService |
| **CargoTemplate** | name, cargo_description, weight, length, width, height, declared_value | FK → CustomUser |
| **Ticket** | subject, status (open/in_progress/closed), priority (low/medium/high) | FK → CustomUser (created_by), FK → CustomUser (assigned_to) |
| **TicketMessage** | message, is_internal_note | FK → Ticket, FK → CustomUser (sender) |
| **Transaction** | amount, transaction_type (deposit/withdrawal/refund), description, balance_after | FK → CustomUser |
| **CompanyApplication** | company_name, inn, status (pending/reviewing/approved/rejected), admin_comment | FK → CustomUser |
| **ManagerDirectoryPermission** | directory (17 choices), can_access | FK → CustomUser (manager), unique_together=(manager, directory) |

### App: `services` — Services & Tariffs (4 models)

| Model | Fields | Relationships |
|-------|--------|---------------|
| **ServiceCategory** | name, name_en, slug, icon, description, description_en, order | FK → self (parent, nullable) |
| **Service** | name, name_en, slug, description, description_en, short_description, icon, base_price, price_unit, is_active, sort_order | FK → ServiceCategory, unique_together=(category, slug) |
| **AdditionalService** | name, name_en, slug, description, description_en, price, price_type (fixed/per_unit/percentage), is_door_service, is_active | — |
| **Tariff** | name, name_en, description, description_en, min_weight, max_weight, price_per_kg, delivery_days_min, delivery_days_max, is_active | — |

### App: `orders` — Orders & Tracking (3 models)

| Model | Fields | Relationships |
|-------|--------|---------------|
| **Order** | tracking_number (unique, BK-XXXXX), sender_name, sender_phone, sender_email, sender_address_detail, recipient_name, recipient_phone, recipient_email, recipient_address_detail, cargo_description, weight, volume, length, width, height, declared_value, status (draft/confirmed/awaiting_delivery_to_branch/available_in_warehouse/awaiting_courier/picked_up/in_transit/customs_clearance/at_warehouse/out_for_delivery/delivered/cancelled), total_price, estimated_delivery_date, actual_delivery_date, is_fragile, is_dangerous, is_temperature_sensitive | FK → CustomUser (nullable), FK → geo.City (sender_address), FK → geo.City (recipient_address), FK → Service, M2M → AdditionalService |
| **OrderStatusHistory** | status, timestamp, comment | FK → Order, FK → CustomUser (changed_by) |
| **OrderDocument** | document_type, file | FK → Order |

### App: `geo` — Geography & Branches (3 models)

| Model | Fields | Relationships |
|-------|--------|---------------|
| **City** | name (unique), name_en, region, region_en, latitude, longitude, is_active, timezone, country (default RU) | — |
| **Branch** | branch_type (warehouse/pickup_point/office), address, address_en, phone, email, working_hours (JSON), latitude, longitude, is_active, has_pickup, has_delivery, has_loading_equipment | FK → City |
| **BranchImage** | image, caption, order | FK → Branch |

### App: `partners` — Partners & Banners (3 models)

| Model | Fields | Relationships |
|-------|--------|---------------|
| **PartnerApplication** | company_name, contact_person, email, phone, website, status (new/reviewing/approved/rejected) | — |
| **Banner** | title, image, link, placement (header/sidebar/footer), start_date, end_date, is_active, clicks_count | — |
| **IframeModule** | name, description, embed_code, documentation | — |

### App: `documents` — Documents & Accounting (2 models)

| Model | Fields | Relationships |
|-------|--------|---------------|
| **Document** | title, title_en, category (contracts/shipping_docs/receipt_docs/power_of_attorney/charter/claims/refunds/tue_replacement), file, description, is_active | — |
| **AccountingRequest** | document_type (invoice/act/receipt/other), period_start, period_end, status (pending/processing/fulfilled/rejected) | FK → CustomUser |

**Total: 33 models across 7 Django apps**

---

## Cargo Transportation Simulation

The routing and simulation engine lives in `apps/orders/routing.py` (391 lines). It powers automatic service assignment, pricing, route calculation, status transitions, and map tracking.

### Auto-Assignment of Services (`auto_assign_services`, line 26)

Based on cargo properties and route, the engine applies **10 rules** to automatically select a main service and optional add-ons:

| Rule | Condition | Action |
|------|-----------|--------|
| 1 | International route | Add `customs-duty` + `customs-clearance` |
| 2 | No direct route | Add `warehouse-transit` |
| 3 | No warehouse in destination city | Add `last-mile-delivery` |
| 4 | International route | Add all 3 email notifications |
| 5 | Domestic route | Add 2 email notifications (created + delivered) |
| 6 | Oversize/overweight (weight >80kg or any dim >120cm) | Use truck or rail transport |
| 7 | Declared value >50,000 ₽ | Add `extended-insurance` |
| 8 | Fragile cargo | Add `hand-carry` |
| 9 | Dangerous goods | Add `adr-transport` |
| 10 | Temperature-sensitive | Add `refrigerated-transport` |

### Pricing Engine (`calculate_price`, line 207)

1. Looks up the best **Tariff** by weight tier (Economy: 0–9.99kg, Standard: 10–49.99kg, Business: 50–199.99kg, Wholesale: 200–999.99kg, Corporate: 1000+kg, Express: 0–29.99kg)
2. Calculates `price_per_kg × weight`
3. Falls back to `service.base_price × weight` if no tariff matches
4. Falls back to `weight × 50 ₽` as absolute minimum
5. Applies **1.3× surcharge** if sender city has no branch
6. Adds **500 ₽ handling fee** if route passes through a warehouse
7. Sums all additional service costs (fixed, per-unit, or percentage of declared value)
8. Randomizes delivery days within the tariff's min–max range

### Route Calculation (`calculate_route`, line 168)

Uses **Haversine distance** between city coordinates:

- **Direct route** — if cities are within 500 km and branch-to-destination distance is less than the inter-city distance
- **Via-warehouse route** — if no direct route is feasible, routes through the nearest warehouse (adds 1 day)
- Returns `{type: "direct"|"via_warehouse", warehouse_stop, delivery_days}`

### Order Status Lifecycle

**11 statuses:** `draft → confirmed → awaiting_delivery_to_branch → available_in_warehouse → awaiting_courier → picked_up → in_transit → customs_clearance → at_warehouse → out_for_delivery → delivered + cancelled`

Initial status depends on whether the sender's city has a branch.

### Simulation Flow (`get_simulation_flow`, `simulate_next_status`)

The **dashboard simulation** steps an order through a simplified flow:

```
draft → confirmed → picked_up → in_transit
  → [customs_clearance if international] → at_warehouse → out_for_delivery → delivered
```

Triggered via `POST /dashboard/orders/<pk>/simulate/` — advances one status per call and returns `{status, status_label, complete}`.

### Virtual Location Tracking (`compute_virtual_location`, line 334)

For live map display during tracking:

- Maps each status to a progress percentage range (e.g., `in_transit`: 20–85%)
- Interpolates lat/lng between sender and recipient cities
- Adds sinusoidal route deviation for visual realism
- Injects small random noise (deterministic, seeded by timestamp) so position varies slightly between views
- Caps at 0–100% progress

### ETA Computation (`compute_eta`, line 323)

```
ETA = today + delivery_days (+1 if via warehouse)
```

### API-Driven Status Transitions

The orders API (`apps/orders/api.py`) provides JSON endpoints for:

| Endpoint | Action | Auth |
|----------|--------|------|
| `POST .../status/` | Staff-only status update (validates transition) | Staff |
| `POST .../pickup/` | User confirms cargo picked up | Owner |
| `POST .../deliver/` | Recipient confirms delivery | Owner/Recipient |
| `GET .../track/` | Public tracking data + virtual location | None |
| `GET+POST .../templates/` | CRUD for contact templates | Owner |
| `GET+POST .../delivery-templates/` | CRUD for delivery templates | Owner |
| `GET+POST .../cargo-templates/` | CRUD for cargo templates | Owner |
| `GET .../address-suggest/` | Address autocomplete (stub) | None |

---

## Docker & Deployment

### Dockerfile

Based on `python:3.13-slim`, installs PostgreSQL client libraries, copies project, exposes port 8000, runs `deploy/entrypoint.sh`.

### docker-compose.yml (Production)

3 services:
- **db** — PostgreSQL 16 Alpine with persistent volume
- **web** — Django app built from Dockerfile, depends on db
- **nginx** — Custom Nginx Alpine reverse proxy, serves static/media, proxies to web on port 8000

### docker-compose.debug.yml (Development)

Overrides web service with `python manage.py runserver`, bind-mounts the project for hot-reload, disables Nginx.

### Entrypoint (`deploy/entrypoint.sh`)

1. Waits for PostgreSQL to be ready
2. Runs migrations
3. Seeds data (via `seed_data` management command) if City table is empty
4. Collects static files
5. Starts Gunicorn (4 workers)

### Nginx Configuration

- Listens on port 80
- Proxies `/` to Django at `web:8000`
- Serves `/static/` and `/media/` directly
- Max body size: 10 MB

---

## Makefile Commands

### Docker Targets

| Command | Description |
|---------|-------------|
| `make prod` | Build & run production (Nginx + Gunicorn + Postgres) on port 8000 |
| `make dev` | Build & run debug (Django runserver + Postgres, bind-mounted, port 8000) |
| `make stop` | Stop all containers |
| `make restart` | Restart all containers |
| `make logs` | Tail logs from all containers |
| `make build` | Rebuild images without starting |

### Management Targets (run inside web container)

| Command | Description |
|---------|-------------|
| `make test` | Run tests (`tests/` with verbosity 2) |
| `make migrate` | Apply database migrations |
| `make makemigrations` | Generate new migrations |
| `make shell` | Open Django shell |
| `make collectstatic` | Collect static files |
| `make loadfixtures` | Load seed data into database |
| `make clean` | Remove Python cache files |

### Local (Non-Docker) Targets

| Command | Description |
|---------|-------------|
| `make venv` | Create Python virtual environment and install dependencies |
| `make local` | Start local dev server on port 8000 with SQLite (auto-migrates) |
| `make test-local` | Run tests locally with in-memory SQLite |
| `make loadfixtures-local` | Load seed data into local SQLite |

---

## Settings & Configuration

Key settings from `baikal/settings.py`:

| Setting | Value | Notes |
|---------|-------|-------|
| `AUTH_USER_MODEL` | `users.CustomUser` | Email-based authentication |
| `LANGUAGE_CODE` | `ru` | Russian default, English also supported |
| `TIME_ZONE` | `Europe/Moscow` | |
| `USE_I18N` / `USE_TZ` | True / True | |
| `STATIC_ROOT` | `BASE_DIR / 'staticfiles'` | Collected static files |
| `MEDIA_ROOT` | `BASE_DIR / 'media'` | User uploads |
| `LOGIN_URL` | `users:login` | |
| `LOGIN_REDIRECT_URL` | `users:profile` | |
| `LOGOUT_REDIRECT_URL` | `core:home` | |
| `FI XTURE_DIRS` | `BASE_DIR / 'fixtures'` | Seed data |

**Database:** PostgreSQL by default (host: `db`, port: `5432`, name: `baikal`, user: `baikal`, password: `baikal_secret`). Falls back to SQLite via `DJANGO_DB_ENGINE` env var.

**Installed Apps:**
- Django built-in (admin, auth, contenttypes, sessions, messages, staticfiles)
- `django_htmx` — HTMX integration
- `apps.core`, `apps.users`, `apps.services`, `apps.orders`, `apps.geo`, `apps.partners`, `apps.documents`, `apps.dashboard`

**Middleware:** Standard Django stack + `HtmxMiddleware` + `ThemeMiddleware` (light/dark theme).

**Context Processors:** Default Django processors + `apps.core.context_processors.site_settings`.

**Environment Variables** (see `.env.example`):
`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_DB_ENGINE`, `DJANGO_DB_NAME`, `DJANGO_DB_USER`, `DJANGO_DB_PASSWORD`, `DJANGO_DB_HOST`, `DJANGO_DB_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.
