# Replit Connection Guide

This guide explains how the backend connects to PostgreSQL on Replit. The short version: **everything is automatic with the postgresql-16 module in .replit**.

---

## 1. Database Configuration

`backend/app/db/database.py` uses PG* environment variables set in `.replit`:

- `PGHOST=db` - Replit's internal PostgreSQL host
- `PGDATABASE=replit` - Database name
- `PGUSER=replit` - Database user
- `PGPORT=5432` - PostgreSQL port

These are automatically configured when you have `modules = ["postgresql-16"]` in your `.replit` file.

---

## 2. Verifying the database

Run this in the Replit shell:

```bash
psql -h db -U replit -d replit -c "SELECT now();"
```

If you see a timestamp, the database is reachable.

---

## 3. Application URLs

- `server.py` serves static files and proxies any `/api/*` request to the FastAPI backend running on port 8000.
- `.replit` already maps port 5000 → public HTTPS URL. You do not need Netlify, Vercel, or any external static host.
- When you deploy, Replit sets `PORT` and `REPLIT_DEPLOYMENT=1`; `server.py` automatically binds to the provided port.

---

## 4. Customizing settings

All customization happens through Secrets:

| Secret | Description |
| --- | --- |
| `SECRET_KEY` | JWT signing key (replace before going live) |
| `BACKEND_CORS_ORIGINS` | JSON list of allowed origins, default `"*"` |
| `RESEND_API_KEY` | Optional email provider key |
| `STRIPE_SECRET_KEY` | Optional billing secret |

No `.env` files need to exist in the repo for Replit deployments.

---

## 5. First-run checklist

1. Make sure `modules = ["postgresql-16"]` is in your `.replit` file
2. Click **Run** and wait for `server.py` to print `Serving on http://0.0.0.0:5000`
3. Visit `https://<repl-slug>.<username>.repl.co/health` – you should see `"database": "connected"`
4. Load `/docs` to confirm the API is ready
5. Sign in with the demo credentials from `backend/init_db.py`

If any step fails, check the Replit console for error messages.
