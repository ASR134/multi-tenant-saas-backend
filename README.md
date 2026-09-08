# Multi-Tenant SaaS Backend

A multi-tenant SaaS backend built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Redis**, and **Celery**.

The project implements authentication, organizations, memberships, tenant-based access, projects, tasks, comments, invitations, and background task processing.

## 🚀 Features

- JWT Authentication
- User Management
- Multi-Tenant Organizations
- Organization Memberships
- Tenant-based Authorization
- Projects & Tasks
- Comments
- Invitations
- Redis Integration
- Celery Background Tasks
- Async PostgreSQL with SQLAlchemy
- Alembic Database Migrations
- Docker & Docker Compose
- Unit & Integration Tests

## 🛠️ Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT
- **Database Driver:** asyncpg
- **Migrations:** Alembic
- **Background Tasks:** Celery
- **Message Broker:** Redis
- **Testing:** Pytest
- **Containerization:** Docker
- **Deployment:** Render + Neon

## 📁 Project Structure

```text
multi_tenant_saas_system/
│
├── alembic/
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── comments.py
│   │       ├── invitations.py
│   │       ├── organizations.py
│   │       ├── projects.py
│   │       ├── tasks.py
│   │       └── users.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── redis.py
│   │   ├── session.py
│   │   └── __init__.py
│   │
│   ├── dependencies/
│   │   ├── auth.py
│   │   └── tenant.py
│   │
│   ├── models/
│   │   ├── comment.py
│   │   ├── invitation.py
│   │   ├── membership.py
│   │   ├── organization.py
│   │   ├── project.py
│   │   ├── task.py
│   │   ├── user.py
│   │   └── __init__.py
│   │
│   ├── repositories/
│   │   ├── comment.py
│   │   ├── invitation.py
│   │   ├── membership.py
│   │   ├── organization.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── comment.py
│   │   ├── invitation.py
│   │   ├── organization.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── user.py
│   │
│   ├── services/
│   │   ├── comment.py
│   │   ├── invitation.py
│   │   ├── membership.py
│   │   ├── organization.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── user.py
│   │
│   ├── utils/
│   │   └── security.py
│   │
│   ├── worker/
│   │   ├── celery_app.py
│   │   ├── tasks.py
│   │   └── __init__.py
│   │
│   ├── main.py
│   └── __init__.py
│
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_auth.py
│   ├── test_comments.py
│   ├── test_invitations.py
│   ├── test_organizations.py
│   ├── test_projects.py
│   ├── test_tasks.py
│   └── unit/
│       └── test_project_service.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── README.md
└── requirements.txt
```

## ⚙️ Local Setup

### 1. Clone the repository

    git clone https://github.com/ASR134/multi-tenant-saas-backend.git
    cd multi-tenant-saas-backend

### 2. Create a virtual environment

    python -m venv venv

Activate it on Windows:

    venv\Scripts\activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Configure environment variables

Create a `.env` file using `.env.example` as a reference.

Example:

    SECRET_KEY=your-secret-key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30

    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=your-password
    POSTGRES_DB=saas_db

    DATABASE_URL=postgresql+asyncpg://postgres:your-password@localhost:5432/saas_db

    REDIS_URL=redis://localhost:6379

### 5. Start PostgreSQL and Redis

    docker compose up -d postgres redis

### 6. Run database migrations

    alembic upgrade head

### 7. Start FastAPI

    uvicorn app.main:app --reload

API:

    http://localhost:8000

Swagger Documentation:

    http://localhost:8000/docs

## 🧪 Testing

Run the test suite:

    pytest

## 🐳 Docker

The project includes Docker support for running the application and its services.

Start all services:

    docker compose up

Stop all services:

    docker compose down

Docker Compose includes:

- PostgreSQL
- Redis
- FastAPI
- Celery Worker

## ☁️ Deployment

The current production setup uses:

    FastAPI      → Render
    PostgreSQL   → Neon
    Redis        → Render
    Celery       → Not deployed yet

The FastAPI application is deployed on Render without using Docker.

## 📌 Project Status

The core backend functionality is implemented, including:

- Authentication
- Multi-tenancy
- Organizations and memberships
- Projects and tasks
- Comments and invitations
- Database migrations
- Redis and Celery integration
- Testing
- Cloud deployment

The Celery worker is implemented but its production deployment is currently pending.

## 👨‍💻 Author

**ASR134**

GitHub: https://github.com/ASR134/multi-tenant-saas-backend