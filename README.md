# Multi-Tenant SaaS Backend

A production-oriented multi-tenant SaaS backend built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Redis**, and **Celery**.

The project implements authentication, email verification, password recovery, organizations, memberships, tenant-based authorization, projects, tasks, comments, invitations, background task processing, rate limiting, and automated testing.

## 🚀 Features

### Authentication & Security

- JWT Authentication
- User Registration & Login
- Email Verification
- Resend Verification Email
- Forgot Password
- Password Reset
- Password Hashing
- Login Rate Limiting
- Secure Token Generation
- Hashed Verification & Password Reset Tokens
- Token Expiration
- Protected Routes

### Multi-Tenancy

- Multi-Tenant Organizations
- Organization Memberships
- Tenant-Based Authorization
- Organization-Level Access Control
- Role-Based Membership Handling

### Application Features

- User Management
- Organizations
- Projects
- Tasks
- Comments
- Invitations

### Infrastructure

- Redis Integration
- Celery Background Tasks
- Async PostgreSQL
- SQLAlchemy ORM
- Alembic Database Migrations
- Docker & Docker Compose
- Unit & Integration Tests

### Email

- Transactional Email using Resend
- Email Verification Emails
- Resend Verification Emails
- Password Reset Emails
- Custom Verified Sending Domain
- `noreply@mail.stackwork.dev` sender

---

## 🛠️ Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT
- **Password Hashing:** Argon2id
- **Database Driver:** asyncpg
- **Migrations:** Alembic
- **Caching / Rate Limiting:** Redis
- **Background Tasks:** Celery
- **Message Broker:** Redis
- **Email:** Resend
- **Validation:** Pydantic
- **Testing:** Pytest
- **Containerization:** Docker
- **Production Backend:** Render
- **Production Database:** Neon PostgreSQL

---


## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/ASR134/multi-tenant-saas-backend.git
cd multi-tenant-saas-backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file using `.env.example` as a reference.


### 5. Start PostgreSQL and Redis

```bash
docker compose up -d postgres redis
```

The local PostgreSQL container uses:

```text
Host: localhost
Port: 5433
```

while PostgreSQL inside Docker uses:

```text
Port: 5432
```

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start FastAPI

```bash
uvicorn app.main:app --reload
```

API:

```text
http://localhost:8000
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

---

## 🧪 Testing

Run the complete test suite:

```bash
python -m pytest
```

The project contains:

* API tests
* Authentication tests
* Organization tests
* Project tests
* Task tests
* Comment tests
* Invitation tests
* Unit tests

The test environment uses PostgreSQL and Redis.

---

## 🐳 Docker

The project includes Docker support for running the application and infrastructure locally.

Start all services:

```bash
docker compose up -d
```

Stop all services:

```bash
docker compose down
```

Docker Compose includes:

* PostgreSQL
* Redis
* FastAPI
* Celery Worker

---

## ☁️ Deployment


### Production Services

| Service             | Provider | Status     |
| ------------------- | -------- | ---------- |
| FastAPI Backend     | Render   | Deployed   |
| PostgreSQL          | Neon     | Deployed   |
| Redis               | Render   | Configured |
| Celery Worker       | Render   | Pending    |
| Transactional Email | Resend   | Configured |

### API Domain

The backend is available through:

```text
https://api.stackwork.dev
```


### Email Domain

Resend uses:

```text
mail.stackwork.dev
```

for transactional email sending.

---

## 🔑 Security

The backend includes several security mechanisms:

* JWT-based authentication
* Password hashing
* Email verification
* Password reset tokens
* Token expiration
* Single-use verification/reset tokens
* Login rate limiting using Redis
* Generic responses for password recovery
* Tenant-based authorization
* Organization membership checks
* Environment-based secret management

Password recovery endpoints intentionally use generic responses to avoid revealing whether an email address is registered.

---

## 📌 Project Status

### Completed

* User authentication
* JWT authentication
* Email verification
* Resend verification email
* Password recovery
* Password reset
* Login rate limiting
* Multi-tenancy
* Organizations
* Memberships
* Tenant-based authorization
* Projects
* Tasks
* Comments
* Invitations
* PostgreSQL integration
* Redis integration
* Celery integration
* Alembic migrations
* Docker setup
* Unit tests
* Integration tests
* Production backend deployment
* Neon PostgreSQL deployment
* Resend transactional email
* Custom API domain

### Pending

* Production Celery worker deployment
* Frontend application
* Frontend deployment
* Frontend/API integration

---

## 👨‍💻 Author

**ASR134**

GitHub: [https://github.com/ASR134/multi-tenant-saas-backend](https://github.com/ASR134/multi-tenant-saas-backend)
