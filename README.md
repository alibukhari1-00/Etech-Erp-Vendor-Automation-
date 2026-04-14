# ETSolar ERP — FAST API Based Backend

Enterprise Resource Planning API for ETSolar, built with **FastAPI** and **PostgreSQL**.

## Tech Stack

| Layer       | Technology                    |
| ----------- | ----------------------------- |
| Framework   | FastAPI 0.135                 |
| Database    | PostgreSQL (via SQLAlchemy 2) |
| Auth        | JWT (python-jose + bcrypt)    |
| Validation  | Pydantic v2                   |
| Migrations  | Alembic                       |

## Project Structure

```
backend/
├── main.py                  # App entrypoint & router registration
├── requirements.txt         # Pinned dependencies
├── .env.example             # Environment variable template
├── scripts/                 # CLI utilities (seed, clear, test connection)
│   ├── seed.py
│   ├── clear_db.py
│   └── test_db.py
└── app/
    ├── core/                # Config, security, auth dependencies
    │   ├── config.py
    │   ├── security.py
    │   └── dependencies.py
    ├── db/                  # Database engine & session
    │   ├── base.py
    │   └── database.py
    ├── models/              # SQLAlchemy ORM models
    ├── schemas/             # Pydantic request / response schemas
    ├── crud/                # Database query logic
    └── routes/              # API route handlers
```

## Getting Started

### 1. Clone & Install

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### 3. Run the Server

```bash
uvicorn main:app --reload
```

API docs available at **http://localhost:8000/docs**

### 4. Seed the Database (optional)

```bash
python -m scripts.seed
```

### 5. Clear the Database (optional)

```bash
python -m scripts.clear_db               # Truncate (keep schema)
python -m scripts.clear_db --drop-tables  # Drop everything
```

### 6. Test Database Connection

```bash
python -m scripts.test_db
```
