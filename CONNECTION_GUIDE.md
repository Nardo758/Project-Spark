# Replit Connection Guide

This guide explains how the backend discovers its database and service URLs when running on Replit. The short version: **everything is automatic once PostgreSQL is enabled inside the Repl**.

---

## 1. Environment discovery order

`backend/app/db/database.py` resolves the connection string in this order:

1. `POSTGRES_URL` (optional secret if you want to point to an external Postgres server)
2. `REPLIT_DB_URL` (provisioned by Replit’s PostgreSQL integration)
3. `DATABASE_URL` (fallback for local development)

On Replit you only need step 2. When you enable the database tool, Replit injects `REPLIT_DB_URL` into Secrets automatically.

---

## 2. Verifying the database

Run this in the Replit shell:

```bash
psql "$REPLIT_DB_URL" -c "SELECT now();"
```

If you see a timestamp, the database is reachable.

You can also run the built-in script:

```bash
python backend/verify_db_connection.py
```

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
| `POSTGRES_URL` | Optional override for the database connection |

No `.env` files need to exist in the repo for Replit deployments.

---

## 5. First-run checklist

1. Enable PostgreSQL in **Tools → Database**
2. Click **Run** and wait for `server.py` to print `Serving on http://0.0.0.0:5000`
3. Visit `https://<repl-slug>.<username>.repl.co/health` – you should see `"database": "connected"`
4. Load `/docs` to confirm the API is ready
5. Sign in with the demo credentials from `backend/init_db.py`

If any step fails, consult the troubleshooting notes in `GET_STARTED.md`.

---

## 6. Migrating away from Replit (optional)

Should you ever need another host, set `POSTGRES_URL` and other secrets pointing to the new provider. Until then, enjoy the zero-config Replit setup.
