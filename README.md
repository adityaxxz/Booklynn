# Booklynn – FastAPI Backend for Books and Reviews

### Overview
Booklynn is a modern FastAPI backend that powers a book discovery and review service. It provides:
- User authentication with JWT access/refresh tokens and role-based authorization
- CRUD for books linked to users
- Reviews for books by users
- Centralized error handling, middleware, and async SQLAlchemy + SQLModel ORM
- Celery-based background email sending with optional Flower monitoring

### Tech Stack
- Python 3.12
- FastAPI, Pydantic, SQLModel (SQLAlchemy ORM)
- Postgres(production), SQLite (dev) via SQLAlchemy; Alembic for migrations
- Redis for token blocklist (logout/revocation)
- Celery for background tasks (email); with flower webui

### Repository Structure
```
bookApp/
  alembic.ini
  migrations/
  books.db                   # SQLite dev database
  src/
    __init__.py              # FastAPI app factory and router wiring
    routesv2.py              # Book endpoints (v2)
    auth/                    # Auth routes, deps, schemas, service, utils
    reviews/                 # Review routes, schemas, service
    db/                      # DB engine/session, models, redis utils
    errors.py                # Centralized exception types & handlers
    middleware.py            # Request logging middleware
    celery_task.py           # Celery app and tasks
    config.py                # Pydantic Settings
  requirements.txt
  cmds.txt                   # Helpful run commands
```

### Prerequisites
- Python 3.12 installed and available on PATH.
- Redis running locally (default: `redis://localhost:6379/`) *if you want logout token revocation and Celery to work*.
- uv package manager (used for installing Python dependencies).
- Optional: SMTP account (Gmail or other) for email-sending features.

### Quick Start

1) Create and activate a virtual environment (Python 3.12)
```powershell
python -m venv .\.venv
or
uv venv --python=3.12 --clear
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies with **uv** *(coz its rust-based and 100x faster than pip)*
```powershell
uv pip install -r requirements.txt
```

3) Configure environment
Create a `.env` file at the `src/` : 
```
#Database: set when using Postgres in production, else SQLite (books.db)
DATABASE_URL=

JWT_SECRET_KEY=

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379

MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your@gmail.com
```

5) Database setup (SQLite dev)
The app ships with a local SQLite `books.db` also, run migrations:
```powershell
alembic revision --autogenerate -m "message"
alembic upgrade head
```

6) Run the API server
```powershell
uvicorn src:app --reload
```
**Docs at http://localhost:8000/v2/docs**

7) Optional: Celery worker and Flower
```powershell
# Start worker
celery -A src.celery_task:c_app worker -l info

# Start Flower UI (monitoring)
celery -A src.celery_task.c_app flower
# Open http://localhost:5555/tasks
```

### Configuration
Settings are defined in `src/config.py` via Pydantic `BaseSettings` and environment variables. Key settings:
- `DATABASE_URL`: When provided (e.g., Postgres), the app uses it; otherwise SQLite `books.db` is used
- `JWT_SECRET_KEY`, `JWT_ALGORITHM`: Token signing
- `REDIS_URL`: Blocklist for revoked tokens
- Mail credentials for SMTP
- `DOMAIN`: Used for links in account verification/password reset emails

### Authentication & Authorization
- JWT Access token (short-lived) and Refresh token (longer-lived)
- Bearer token dependencies validate type and expiry
- Token revocation supported via Redis blocklist
- Role-based Access control using `RoleChecker` with roles as `admin` and `user`


### API Overview
Base: `http://localhost:8000/v2` (Docs at `/v2/docs`)

Auth
- POST `/auth/signup`
- POST `/auth/login`
- GET `/auth/me` (requires access token)
- POST `/auth/refresh` (requires refresh token)
- GET `/auth/logout` (revokes access token)
- POST `/auth/password-reset` (email)
- POST `/auth/password-reset-confirm/{token}`

Books (requires user role mainly)
- POST `/books/` – Create
- GET `/books/` – List
- GET `/books/{book_uid}` – Retrieve
- PATCH `/books/{book_uid}` – Update
- DELETE `/books/{book_uid}` – Delete (admin role)

Reviews
- GET `/reviews/` – List all reviews (admin role)
- GET `/reviews/book/{book_uid}` – Get a review for a book
- POST `/reviews/book/{book_uid}` – Add review (user)
- DELETE `/reviews/{review_uid}` – Delete review (admin role)

### Example Requests
```powershell
# Signup
curl -X POST "http://localhost:8000/v2/auth/signup" `
  -H "Content-Type: application/json" `
  -d '{
    "first_name": "Jane",
    "username": "jane",
    "email": "jane@example.com",
    "password": "secret",
    "role": "user"
  }'

# Login
$login = curl -X POST "http://localhost:8000/v2/auth/login" `
  -H "Content-Type: application/json" `
  -d '{"email": "jane@example.com", "password": "secret"}'


# Create a book
curl -X POST "http://localhost:8000/v2/books/" `
  -H "Authorization: Bearer <ACCESS_TOKEN>" `
  -H "Content-Type: application/json" `
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "year": "1925",
    "language": "English"
  }'
```

#### Ideas to implement
- frontend for the endpoints using streamlit, or any other framework
- add email routing and setup a smtp for emails from cloudflare added site, instead of gmail
- add some ml model for the book score that tells, how many people like this book, or something like that