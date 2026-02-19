# PostgreSQL Setup Guide (pgAdmin Web First)

This project works with:

- pgAdmin web: `http://34.155.143.75/pgadmin4/browser/`

Use this guide if you are new and will work from pgAdmin UI (recommended).

## 1) Open pgAdmin web

Go to:

- `http://34.155.143.75/pgadmin4/browser/`

Log in with the credentials provided by your team/admin.

## 2) Register/connect the PostgreSQL server (if not already visible)

In pgAdmin:

1. Right-click **Servers** -> **Register** -> **Server...**
2. In **General**, choose a name (example: `Transport Project`).
3. In **Connection**, set:
   - Host: `34.155.143.75`
   - Port: `5432` (unless your admin gave another port)
   - Username/password: from your team/admin
4. Save.

## 3) Create/select database

Use Query Tool in pgAdmin and run:

```sql
CREATE DATABASE transport_analytics;
```

If database already exists, skip this step.

## 4) Apply project SQL scripts

In pgAdmin Query Tool, open and execute:

1. `sql/01_schema.sql`
2. `sql/02_views.sql`
3. (optional for learning) `sql/03_analytics_examples.sql`

## 5) Configure Python code (only if you run loaders from scripts/notebooks)

Set environment variables before running Python loaders:

```bash
export PGHOST=34.155.143.75
export PGPORT=5432
export PGDATABASE=transport_analytics
export PGUSER=<your_user>
export PGPASSWORD=<your_password>
export PGSCHEMA=transport
```

Then `src/transport_analytics/postgres.py` can load `data/processed/*.csv` into PostgreSQL.
