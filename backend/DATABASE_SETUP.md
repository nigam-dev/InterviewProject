# Database Setup Guide

## Overview

The Cricket Team Optimizer supports two data sources:
1. **PostgreSQL Database** (primary, optional)
2. **CSV File** (fallback, always available)

The system automatically falls back to CSV if the database is unavailable.

## Quick Start (CSV Only)

No setup needed! The system works out of the box with CSV:

```bash
cd backend
python -m uvicorn main:app --reload
```

## PostgreSQL Setup (Optional)

### 1. Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download from https://www.postgresql.org/download/windows/

### 2. Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE cricket_optimizer;
CREATE USER cricket_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cricket_optimizer TO cricket_user;

# Exit
\q
```

### 3. Install Python PostgreSQL Driver

```bash
# Install psycopg2-binary
pip install psycopg2-binary==2.9.9

# Or add to virtual environment
source ../.venv/bin/activate  # from backend folder
pip install psycopg2-binary==2.9.9
```

### 4. Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Option 1: Full database URL
DATABASE_URL=postgresql://cricket_user:your_password@localhost:5432/cricket_optimizer

# Option 2: Individual components
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cricket_optimizer
DB_USER=cricket_user
DB_PASSWORD=your_password
```

### 5. Start Application

```bash
cd backend
python -m uvicorn main:app --reload
```

The application will:
1. Try to connect to PostgreSQL
2. Create `players` table if it doesn't exist
3. Auto-sync CSV data to database (first run)
4. Use database as primary data source

## Data Synchronization

### Automatic Sync (on startup)
If database is empty, CSV data is automatically synced on first run.

### Manual Sync

```python
from player_repository import sync_csv_to_database

# Sync CSV to database
sync_csv_to_database("players.csv")
```

## Fallback Behavior

The system gracefully handles database unavailability:

| Scenario | Behavior |
|----------|----------|
| Database connected, has data | ✅ Use database |
| Database connected, but empty | ✅ Auto-sync CSV → database |
| Database unavailable | ✅ Use CSV fallback |
| psycopg2 not installed | ✅ Use CSV fallback |

## Health Check

Check current data source:

```bash
curl http://localhost:8000/
```

Response includes:
```json
{
  "message": "Cricket Team Optimizer API",
  "version": "1.0.0",
  "data_source": "database",  // or "csv"
  "endpoints": ["/players", "/optimize"]
}
```

## Database Schema

### Players Table

```sql
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    runs INTEGER NOT NULL,
    wickets INTEGER NOT NULL,
    strike_rate FLOAT NOT NULL,
    price FLOAT NOT NULL,
    role VARCHAR(10) NOT NULL
);
```

### Constraints
- `name`: Unique, max 100 characters
- `runs`: Integer, 0-1000
- `wickets`: Integer, 0-50
- `strike_rate`: Float, 0-250
- `price`: Float, >0
- `role`: String, one of: WK, BAT, BOWL, ALL

## Troubleshooting

### "No module named 'psycopg2'"
**Solution:** Install psycopg2-binary (only needed for PostgreSQL)
```bash
pip install psycopg2-binary==2.9.9
```

### "Database initialization failed"
**Solution:** This is normal if PostgreSQL is not installed. CSV fallback will be used automatically.

### "Connection refused"
**Solution:** Ensure PostgreSQL is running
```bash
# macOS
brew services start postgresql@15

# Linux
sudo systemctl start postgresql
```

### "FATAL: database does not exist"
**Solution:** Create the database
```bash
psql postgres -c "CREATE DATABASE cricket_optimizer;"
```

## Production Deployment

### Docker Compose with PostgreSQL

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: cricket_optimizer
      POSTGRES_USER: cricket_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://cricket_user:secure_password@db:5432/cricket_optimizer
    depends_on:
      - db
    ports:
      - "8000:8000"

volumes:
  postgres_data:
```

### Environment Variables (Production)

```bash
# Use full DATABASE_URL for production
DATABASE_URL=postgresql://user:password@host:port/dbname

# Or use managed database services (AWS RDS, Google Cloud SQL, etc.)
DATABASE_URL=postgresql://user:password@rds-endpoint.region.rds.amazonaws.com:5432/dbname
```

## Benefits of PostgreSQL

- **Performance**: Faster queries for large datasets
- **Persistence**: Data survives server restarts
- **Scalability**: Add indexes, query optimization
- **Multi-user**: Concurrent access support
- **ACID compliance**: Data integrity guarantees

## CSV Fallback Benefits

- **Zero setup**: Works immediately
- **Simple deployment**: No database required
- **Development**: Easy testing and iteration
- **Portability**: Works anywhere Python runs
