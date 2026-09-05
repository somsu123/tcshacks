# FraudShield AI - Database Setup Guide

## Local Development with PostgreSQL

### Option 1: Using Docker (Recommended)

```bash
# Pull and run PostgreSQL
docker run --name fraudshield-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=fraudshield \
  -p 5432:5432 \
  -d postgres:16-alpine

# Verify it's running
docker ps | grep fraudshield-db
```

### Option 2: Install PostgreSQL Locally

**macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
createdb fraudshield
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb fraudshield
```

### Option 3: Use Supabase (Free Tier)

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Copy connection string from Settings → Database
4. Add to `.env`:
```bash
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[HOST]:5432/postgres
```

---

## Running Migrations

### 1. Set Database URL

```bash
# For local development
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fraudshield

# Or add to .env file
echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fraudshield" >> .env
```

### 2. Generate Migration (First Time)

```bash
source venv/bin/activate
alembic revision --autogenerate -m "Initial migration: create transactions, users, audit_logs tables"
```

### 3. Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Verify tables created
psycopg2 -h localhost -U postgres -d fraudshield -c "\dt"
```

### 4. Rollback if Needed

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Reset everything
alembic downgrade base
```

---

## Production Deployment (Render)

### 1. Add PostgreSQL Service in Render

1. Go to Render Dashboard
2. Click "New" → "PostgreSQL"
3. Name: `fraudshield-db`
4. Plan: Free (500MB, good for testing)
5. Create database

### 2. Link to Web Service

In your `fraudshield-api` web service:

1. Go to "Environment" tab
2. Add environment variable:
   - Key: `DATABASE_URL`
   - Value: **(Auto-filled from PostgreSQL service connection)**

Or manually copy from PostgreSQL service "Internal Database URL"

### 3. Run Migrations on Deploy

Add to `render.yaml`:
```yaml
services:
  - type: web
    name: fraudshield-api
    runtime: python
    buildCommand: |
      pip install -r requirements.txt
      alembic upgrade head
    startCommand: gunicorn --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 -w 2 --timeout 120 app.main:app
```

Or create `build.sh` script:
```bash
#!/bin/bash
pip install -r requirements.txt
alembic upgrade head
```

And reference in `render.yaml`:
```yaml
buildCommand: ./build.sh
```

---

## Verifying Database Connection

### Test Script

Create `scripts/test_db.py`:
```python
from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("✅ Database connected!")
        print(f"PostgreSQL version: {result.fetchone()[0]}")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

Run:
```bash
python scripts/test_db.py
```

---

## Troubleshooting

### Connection Refused

**Problem:** `psycopg2.OperationalError: connection refused`

**Solution:**
- Check PostgreSQL is running: `docker ps` or `brew services list`
- Verify port 5432 is not in use: `lsof -i :5432`
- Check DATABASE_URL format: `postgresql://user:password@host:port/database`

### Render Postgres:// vs PostgreSQL://

**Problem:** Render provides `postgres://` but SQLAlchemy needs `postgresql://`

**Solution:** Already handled in `app/database.py`:
```python
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
```

### Migrations Out of Sync

**Problem:** "Target database is not up to date"

**Solution:**
```bash
# Check current version
alembic current

# Show migration history
alembic history

# Stamp database to specific version
alembic stamp head
```

---

## Development Workflow

### Creating New Migrations

1. Modify models in `app/db_models.py`
2. Generate migration:
```bash
alembic revision --autogenerate -m "Add column to transactions table"
```
3. Review generated file in `alembic/versions/`
4. Apply:
```bash
alembic upgrade head
```

### Seeding Data

After migrations, seed demo data:
```bash
# Backend automatically loads seed data on startup
# See app/main.py:lifespan()
uvicorn app.main:app --reload
```

---

## For Now: Continue Without Database

The in-memory storage still works for development. To switch to PostgreSQL later:

1. Set up PostgreSQL (any option above)
2. Run migrations: `alembic upgrade head`
3. Update `app/main.py` to use database session instead of `transaction_store`

The models are ready, migrations are configured - just need database running!
