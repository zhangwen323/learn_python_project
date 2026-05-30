# Blog API

A RESTful blog backend built with FastAPI + SQLAlchemy + JWT — no frontend, just JSON.

## Quick Start

```bash
cd blog_api
pip install -e .
uvicorn blog_api.main:app --reload
# Open http://localhost:8000/docs for Swagger UI
```

## API Endpoints

```
POST   /api/auth/register          # Register
POST   /api/auth/login             # Login → JWT token

GET    /api/posts                  # List posts (pagination + filters)
GET    /api/posts/{slug}           # Get post by slug
POST   /api/posts                  # Create post (auth required)
PUT    /api/posts/{slug}           # Update post (author only)
DELETE /api/posts/{slug}           # Delete post (author only)

GET    /api/posts/{slug}/comments  # List comments
POST   /api/posts/{slug}/comments  # Add comment (auth required)

GET    /api/categories             # List categories
GET    /api/tags                   # List tags
```

## Table Relationships

```
┌──────────────┐          ┌──────────────────┐          ┌──────────────┐
│    users     │          │  post_tags       │          │    tags      │
├──────────────┤          ├──────────────────┤          ├──────────────┤
│ id           │          │ post_id ────────────────────│ id           │
│ username     │          │ tag_id  ────────────────────│ name         │
│ email        │          └──────────────────┘          └──────────────┘
│ password_hash│
│ created_at   │
└──┬───────────┘
   │ 1
   │ N
   ▼
┌──────────────────────────────────────┐
│              posts                   │
├──────────────────────────────────────┤
│ id                                   │      ┌──────────────┐
│ title / slug / content / published   │      │  categories  │
│ created_at / updated_at              │      ├──────────────┤
│ author_id  ──── FK → users.id        │ N  1 │ id           │
│ category_id ─── FK → categories.id   │◄─────│ name / slug  │
└──┬───────────────────────────────────┘      └──────────────┘
   │ 1
   │ N
   ▼
┌──────────────────────────────────────┐
│             comments                 │
├──────────────────────────────────────┤
│ id / content / created_at            │
│ post_id   ──── FK → posts.id         │
│ author_id ──── FK → users.id         │
└──────────────────────────────────────┘
```

| Relationship | Implementation |
|--------------|----------------|
| One-to-many | `users` → `posts` → `comments`: ForeignKey + `relationship()` |
| Many-to-one | `posts` → `categories`: ForeignKey `category_id` |
| Many-to-many | `posts` ↔ `tags`: junction table `post_tags` via `secondary` |

## Tech Stack

| Layer | Library |
|-------|---------|
| Framework | FastAPI (async, auto-docs, dependency injection) |
| ORM | SQLAlchemy 2.0 (async session) |
| Validation | Pydantic v2 |
| Auth | bcrypt + python-jose (JWT) |
| Migrations | Alembic |
| Tests | pytest + pytest-asyncio + httpx |

## Code Navigation

Recommended reading order:

```
config.py          →  App configuration (DB URL, JWT secret)
models/            →  SQLAlchemy models (user, post, comment, category, tag)
schemas/           →  Pydantic request/response schemas
services/auth.py   →  bcrypt hashing + JWT create/decode
database.py        →  Async engine + session factory
dependencies.py    →  FastAPI Depends (get_db, get_current_user)
routers/auth.py    →  POST /api/auth/register + /login
routers/posts.py   →  CRUD with pagination, filtering, ownership checks
routers/comments.py →  Nested under /api/posts/{slug}/comments
main.py            →  App creation, CORS, router registration
```

## Running Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## Database Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Project Initialization

```bash
cd blog_api
pip install -e .            # editable install
pip install -e ".[dev]"     # with test dependencies
```
