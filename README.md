# Baikal-Service

**Logistics and cargo transportation web application across Russia, Kazakhstan, Belarus, Kyrgyzstan, and China.**

---

## Company

**Baikal-Service** — a logistics company offering cargo transportation, courier delivery, and warehouse services.

---

## Project Functionality

### Public Website (App: `core`)
- **Home page** — pinned news, approved reviews, promotions, cities, services, branches
- **News** — paginated listing and detail pages
- **Reviews** — filterable by rating
- **Vacancies** — filterable by department and city
- **FAQs** — published questions and answers
- **Tenders** — active tender listings
- **Promotions** — active promotional campaigns
- **Contact form** — send messages to the company
- **Interactive tools:**
  - **Calculator** — shipping cost estimation with HTMX partial updates
  - **Tracking** — order tracking by tracking number with HTMX
  - **Delivery times** — estimated delivery time between cities
- **Static pages** — About, Directions, Tariffs, Mobile App, Brand Assets, Press, Warehouse

### User Accounts (App: `users`)
- Registration and login (email-based authentication)
- Profile management with settings and password change
- **Balance management** — view transaction history, top-up balance
- **Order management** — view personal orders and order details
- **Support tickets** — create, view, and respond to support tickets with messaging
- **Templates** — save reusable contact, delivery, and cargo templates
- **Accounting documents** — request invoices, acts, receipts

### Services Catalog (App: `services`)
- **Service categories** — hierarchical (parent/child) categories
- **Services** — individual logistics services with descriptions and base pricing
- **Additional services** — optional add-ons (door delivery, insurance, etc.)
- **Tariffs** — weight-based pricing with delivery time ranges

### Order Management (App: `orders`)
- **Order creation** — full order form with pricing calculation, estimated delivery date
- **Order lifecycle** — multi-status workflow (draft → confirmed → ... → delivered/cancelled)
- **Status history** — track all status changes with timestamps
- **Routing engine** — calculates direct vs via-warehouse routes, pricing, and ETA
- **Tracking** — public tracking page with virtual location interpolation for maps
- **Door delivery requests** — request door-to-door service
- **Change requests** — request modifications to an existing order
- **JSON API** — status updates, pickup confirmation, delivery confirmation, template CRUD

### Geography & Branches (App: `geo`)
- **Cities** — managed city list with coordinates, regions, timezones
- **Branches** — warehouses, pickup points, and offices with addresses, hours, photos
- **Branch map** — view all branches on a map

### Partner Program (App: `partners`)
- **Partner applications** — companies can apply for partnership
- **Banners** — managed advertising banners with placement and scheduling
- **Iframe modules** — embeddable widgets for partner sites

### Documents (App: `documents`)
- **Document repository** — categorized documents (contracts, shipping docs, receipts, etc.)
- **Accounting requests** — users can request accounting documents for specific periods

### Admin Dashboard (App: `dashboard`)
- Staff-only interface separate from Django admin
- **Dashboard home** — stats (today's orders, active shipments, open tickets, total users)
- **Full CRUD** for: users, services, categories, tariffs, content pages, news, vacancies, FAQs, reviews, tenders, branches, banners, partner applications
- **Order overview** — view all orders
- **Ticket management** — view and manage support tickets
- **Documents overview** — view documents and accounting requests
- **Contact messages** — view submitted contact form messages
- **Settings page**

### Technical Stack
- **Backend:** Django 6.0.6, Python ≥3.13, SQLite (dev) / PostgreSQL (prod)
- **Frontend:** Server-side Django templates, Tailwind CSS, Alpine.js, HTMX, Font Awesome
- **i18n:** Russian (default) and English
- **Admin:** Django Admin registered for all models with custom admin classes
- **Deployment:** Docker, Gunicorn

---

## Database Structure

### `core` — Content & Public Pages

| Model | Fields | Relationships |
|-------|--------|---------------|
| **ContentPage** | slug, title, title_en, content, content_en, meta_description, is_published, created_at, updated_at, page_type (about/news/vacancy/review/press/tender/faq) | — |
| **FAQ** | question, question_en, answer, answer_en, category, order, is_published | — |
| **Review** | author_name, author_company, text, rating (1–5), is_approved, created_at, source | — |
| **NewsItem** | title, title_en, slug, short_text, short_text_en, full_text, full_text_en, image, published_at, is_published, is_pinned | — |
| **Vacancy** | title, title_en, slug, department, short_description, full_description, requirements, salary_from, salary_to, is_active, published_at | FK → geo.City (nullable) |
| **ContactMessage** | name, email, phone, subject, message, is_read, created_at | — |
| **Tender** | title, slug, description, deadline, is_active, published_at | — |
| **Promotion** | title, title_en, slug, short_description, full_description, image, start_date, end_date, is_active, created_at | — |

### `users` — Users, Accounts, Templates

| Model | Fields | Relationships |
|-------|--------|---------------|
| **CustomUser** | username, email (unique, login field), phone, balance, role (client/manager/admin), language (ru/en), theme (light/dark), company_name, inn, is_company, avatar | Extends `AbstractUser` |
| **ContactTemplate** | name, template_type (sender/recipient), recipient_name, recipient_phone, recipient_email, address_detail, created_at | FK → CustomUser, FK → geo.City (nullable) |
| **DeliveryTemplate** | name, weight, cargo_description, declared_value, sender_address_detail, recipient_address_detail, total_price, created_at | FK → CustomUser, FK → geo.City (from/to), FK → services.Service (nullable), M2M → services.AdditionalService |
| **CargoTemplate** | name, cargo_description, weight, length, width, height, declared_value, created_at | FK → CustomUser |
| **Ticket** | subject, status (open/in_progress/closed), priority (low/medium/high), created_at, updated_at | FK → CustomUser (created_by), FK → CustomUser (assigned_to, nullable) |
| **TicketMessage** | message, created_at, is_internal_note | FK → Ticket, FK → CustomUser (sender) |
| **Transaction** | amount, transaction_type (deposit/withdrawal/refund), description, balance_after | FK → CustomUser |

### `services` — Services & Tariffs

| Model | Fields | Relationships |
|-------|--------|---------------|
| **ServiceCategory** | name, name_en, slug, icon, description, description_en, order | FK → self (parent, nullable) |
| **Service** | name, name_en, slug, description, description_en, short_description, short_description_en, icon, base_price, price_unit, is_active, sort_order | FK → ServiceCategory |
| **AdditionalService** | name, name_en, slug, description, description_en, price, price_type (fixed/per_unit/percentage), is_door_service | — |
| **Tariff** | name, name_en, description, description_en, min_weight, max_weight, price_per_kg, delivery_days_min, delivery_days_max | — |

### `orders` — Orders & Tracking

| Model | Fields | Relationships |
|-------|--------|---------------|
| **Order** | tracking_number (unique, BK-XXXX), sender_name, sender_phone, sender_email, sender_address_detail, recipient_name, recipient_phone, recipient_email, recipient_address_detail, cargo_description, weight, volume, length, width, height, declared_value, status (draft/confirmed/awaiting_delivery_to_branch/available_in_warehouse/awaiting_courier/picked_up/in_transit/at_warehouse/out_for_delivery/delivered/cancelled), total_price, created_at, updated_at, estimated_delivery_date, actual_delivery_date | FK → CustomUser (nullable), FK → geo.City (sender_address, nullable), FK → geo.City (recipient_address, nullable), FK → services.Service (nullable), M2M → services.AdditionalService |
| **OrderStatusHistory** | status, timestamp, comment | FK → Order, FK → CustomUser (changed_by, nullable) |
| **OrderDocument** | document_type, file, uploaded_at | FK → Order |

### `geo` — Geography & Branches

| Model | Fields | Relationships |
|-------|--------|---------------|
| **City** | name, name_en, region, region_en, latitude, longitude, is_active, timezone | — |
| **Branch** | branch_type (warehouse/pickup_point/office), address, address_en, phone, email, working_hours (JSON), latitude, longitude, is_active, has_pickup, has_delivery, has_loading_equipment | FK → City |
| **BranchImage** | image, caption, order | FK → Branch |

### `partners` — Partners & Banners

| Model | Fields | Relationships |
|-------|--------|---------------|
| **PartnerApplication** | company_name, contact_person, email, phone, website, status (new/reviewing/approved/rejected) | — |
| **Banner** | title, image, link, placement (header/sidebar/footer), start_date, end_date, is_active, clicks_count | — |
| **IframeModule** | name, description, embed_code, documentation | — |

### `documents` — Documents & Accounting

| Model | Fields | Relationships |
|-------|--------|---------------|
| **Document** | title, title_en, category (contracts/shipping_docs/receipt_docs/power_of_attorney/charter/claims/refunds/tue_replacement), file, description, is_active | — |
| **AccountingRequest** | document_type (invoice/act/receipt/other), period_start, period_end, status (pending/processing/fulfilled/rejected), created_at, fulfilled_at | FK → CustomUser |

---
