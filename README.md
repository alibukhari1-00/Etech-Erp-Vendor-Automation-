# ETSolar ERP — NestJS Backend

Production-grade NestJS rewrite of the FastAPI backend. **Zero breaking changes** — the frontend works without modification.

## Stack

- **NestJS** (TypeScript)
- **TypeORM** + **PostgreSQL** (existing schema, `synchronize: false`)
- **Passport JWT** (HS256, access + refresh tokens)
- **bcrypt** password hashing
- **nodemailer** SMTP for OTP emails
- **class-validator / class-transformer** DTO validation

## Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/etsolar_erp
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080
OPENAI_API_KEY=sk-...          # optional, for AI chat
SMTP_HOST=smtp.gmail.com
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your-app-password
PORT=8000
```

### 3. Run

```bash
# Development (watch mode)
npm run start:dev

# Production build
npm run build
npm run start:prod
```

The API starts on **http://localhost:8000** — same port as the FastAPI backend.

## API Routes (identical to FastAPI)

| Module | Routes |
|---|---|
| Auth | `POST /auth/login`, `POST /auth/refresh`, `GET/PUT/PATCH /auth/me`, `POST /auth/forgot-password`, `POST /auth/verify-otp`, `POST /auth/reset-password` |
| Users | `GET/POST /users/`, `GET/PUT/DELETE /users/:id` |
| Dashboard | `GET /dashboard/stats` |
| Settings | `GET/PUT /settings/purchaser-access` |
| Brands | `GET/POST /brands/`, `GET/PUT/DELETE /brands/:id` |
| Locations | `GET/POST /locations/`, `GET/PUT/DELETE /locations/:id` |
| Categories | `GET/POST /categories/`, `GET/PUT/DELETE /categories/:id` |
| SubCategories | `GET/POST /subcategories/`, `GET/PUT/DELETE /subcategories/:id` |
| Items | `GET/POST /items/`, `GET /items/search`, `GET /items/:id/vendors`, `GET/PUT/DELETE /items/:id` |
| Vendors | `GET/POST /vendors/`, `GET/PUT/DELETE /vendors/:id` |
| Vendor Groups | `GET/POST /vendor-groups/`, `DELETE /vendor-groups/:id` |
| Vendor Brands | `GET/POST /vendor-brands/`, `DELETE /vendor-brands/:id` |
| Vendor Contacts | `GET/POST /vendor-contacts/`, `DELETE /vendor-contacts/:id` |
| Projects | `GET/POST /projects/`, `GET/PUT /projects/:id`, `DELETE /projects/:id` |
| Purchase Demands | Full workflow: create, list, get, update, submit, approve, reject, cancel, delete, vendor assignment, quotation candidates |
| Purchase Quotations | `POST /purchase-quotations/initiate/:demandId`, `GET /purchase-quotations/demand/:demandId`, `PATCH /purchase-quotations/:id`, `POST /purchase-quotations/:id/select` |
| AI Chat | `POST /ai-chat/ask` (SSE streaming) |

## Architecture

```
src/
  config/           # App config (env vars)
  common/
    guards/         # JwtAuthGuard, AdminGuard
    decorators/     # @CurrentUser()
    filters/        # HttpExceptionFilter (FastAPI-compatible { detail } format)
    pipes/          # Global ValidationPipe
  database/
    entities/       # TypeORM entities (map 1:1 to existing DB tables)
  modules/
    auth/           # JWT login, refresh, OTP password reset
    users/          # Admin user management
    dashboard/      # Stats aggregation
    settings/       # Purchaser access toggle
    brands/         # Brand CRUD
    locations/      # Location CRUD
    categories/     # Category CRUD
    subcategories/  # SubCategory CRUD
    items/          # Item CRUD + search + vendor lookup
    vendors/        # Vendor CRUD
    vendor-groups/  # Vendor ↔ Category links
    vendor-brands/  # Vendor ↔ Brand links
    vendor-contacts/# Vendor contact persons
    projects/       # Project CRUD
    purchase-demands/  # Full PD workflow
    purchase-quotations/ # Quotation management
    ai-chat/        # LangChain SQL agent (SSE streaming)
```

## Key Design Decisions

- `synchronize: false` — TypeORM never touches the existing schema
- Error responses use `{ detail: "..." }` format to match FastAPI exactly
- JWT strategy validates `type: "access"` claim to prevent refresh token misuse
- Purchaser access gate is enforced in both JWT strategy and login flow
- AI chat uses lazy `require()` for LangChain to avoid startup cost when key is absent
