# Multi-Tenant SaaS Backend

A production-oriented multi-tenant SaaS backend built with **FastAPI, PostgreSQL, SQLAlchemy, Redis, and Celery**, featuring secure authentication, tenant-based authorization, caching, background processing, and automated testing.

**Live API:** [api.stackwork.dev](https://api.stackwork.dev) 

## 🚀 Features

- **Authentication:** JWT authentication, registration, login, email verification, password recovery, and Argon2id password hashing.
- **Security:** Hashed and expiring tokens, login rate limiting, single-use reset tokens, and protected routes.
- **Multi-Tenancy:** Organizations, memberships, role-based access control, and tenant-level authorization.
- **Core Resources:** Users, organizations, projects, tasks, comments, and invitations.
- **Caching:** Redis caching, cache invalidation, and rate limiting.
- **Background Processing:** Celery with Redis as the message broker.
- **Email:** Resend integration for verification and password-reset emails.
- **Database:** Asynchronous PostgreSQL access using SQLAlchemy and asyncpg.
- **Testing:** Pytest-based unit and integration tests.
- **Infrastructure:** Alembic migrations, Docker, and Docker Compose.

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Backend | FastAPI, Python |
| Database & ORM | PostgreSQL, Neon, SQLAlchemy |
| Authentication | JWT, Argon2id |
| Validation | Pydantic |
| Caching & Broker | Redis |
| Background Tasks | Celery |
| Email | Resend |
| Migrations | Alembic |
| Testing | Pytest, HTTPX |
| Deployment | Render |
| Containerization | Docker |

## 🏗️ Architecture

The application follows a layered architecture separating API routes, business logic, data access, and infrastructure.

```text
Client
  |
FastAPI Routes
  |
Dependencies & Authorization
  |
Service Layer
  |
  +---- Repository Layer ---- PostgreSQL
  |
  +---- Redis Cache
  |
  +---- Celery Tasks
             |
         Redis Broker
```

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/ASR134/multi-tenant-saas-backend.git
cd multi-tenant-saas-backend
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
```

Activate on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file using `.env.example` as a reference. Configure PostgreSQL, Redis, JWT secrets, and Resend credentials.

### 4. Start PostgreSQL, Redis, Fastapi and Celery

```bash
docker compose up -d 
```

PostgreSQL is exposed on `localhost:5433` and listens on port `5432` inside Docker.

### 5. Run migrations 

```bash
alembic upgrade head
```

- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs

## 🧪 Testing

Run the test suite:

```bash
python -m pytest -v
```

Tests cover authentication, organizations, projects, tasks, comments, invitations, authorization, service logic, caching, and API workflows.

Use the appropriate test database and Redis configuration for tests that require external infrastructure.

## ☁️ Deployment

- **Backend API:** [api.stackwork.dev](https://api.stackwork.dev)
- **Hosting:** Render
- **Production Database:** Neon PostgreSQL
- **Transactional Email:** Resend
- **Email Sending Domain:** `mail.stackwork.dev`

## 👨‍💻 Author

**ASR134**