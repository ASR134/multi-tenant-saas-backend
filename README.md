# Multi-Tenant SaaS Backend

A multi-tenant SaaS backend built with FastAPI, PostgreSQL, SQLAlchemy, Redis, and Celery.

The project focuses on authentication, organizations, tenant-based access, projects, tasks, comments, invitations, and background tasks.

## 🚀 Features

- JWT Authentication
- User Management
- Multi-Tenant Organizations
- Organization Memberships
- Projects & Tasks
- Comments
- Invitations
- Background Tasks with Celery
- Redis Integration
- Async PostgreSQL with SQLAlchemy
- Alembic Database Migrations
- Docker & Docker Compose
- Unit & Integration Tests

## 🛠️ Tech Stack

- Backend: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Authentication: JWT
- Database Driver: asyncpg
- Migrations: Alembic
- Background Tasks: Celery
- Message Broker: Redis
- Testing: Pytest
- Containerization: Docker
- Deployment: Render + Neon

## 📁 Project Structure

app/
├── api/
│   └── v1/
│       ├── auth.py
│       ├── comments.py
│       ├── invitations.py
│       ├── organizations.py
│       ├── projects.py
│       ├── tasks.py
│       └── users.py
├── core/
├── db/
├── dependencies/
├── models/
│   ├── comment.py
│   ├── invitation.py
│   ├── membership.py
│   ├── organization.py
│   ├── project.py
│   ├── task.py
│   └── user.py
├── repositories/
├── schemas/
├── services/
├── utils/
├── worker/
├── __init__.py
└── main.py

alembic/
├── versions/
└── env.py

tests/
├── unit/

.dockerignore
.env.example
.gitignore
Dockerfile
README.md
alembic.ini
docker-compose.yml
pytest.ini
requirements.txt

## ⚙️ Local Setup

### 1. Clone the repository

    git clone https://github.com/ASR134/multi-tenant-saas-backend.git
    cd multi-tenant-saas-backend

### 2. Create virtual environment

    python -m venv venv
    venv\Scripts\activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Configure environment variables

Create a `.env` file using `.env.example` as a reference.

### 5. Start PostgreSQL and Redis

    docker compose up -d postgres redis

### 6. Run migrations

    alembic upgrade head

### 7. Start FastAPI

    uvicorn app.main:app --reload

API:

    http://localhost:8000

Swagger Docs:

    http://localhost:8000/docs

## ☁️ Deployment

The backend is deployed using:

    FastAPI     → Render
    PostgreSQL  → Neon
    Redis       → Render

Docker is included for local development and containerized deployment, but the current Render deployment does not use Docker.

## 📌 Project Status

Core backend functionality, authentication, multi-tenancy, database migrations, Redis/Celery integration, testing setup, and cloud deployment are implemented.

Celery worker deployment is currently pending.

## 👨‍💻 Author

ASR134

GitHub: https://github.com/ASR134
