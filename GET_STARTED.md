# 🚀 Get Started (Replit Stack)

This project now assumes a single runtime: **Replit**. The frontend, backend, and PostgreSQL database all run in one Repl, so there is no reliance on Supabase, Netlify, Vercel, or any other external hosting providers.

---

## 1. What you get

- ✅ FastAPI backend with all routers enabled
- ✅ PostgreSQL hosted by Replit (via `REPLIT_DB_URL`)
- ✅ Static frontend served through `server.py`
- ✅ Built-in sample data loader (`backend/init_db.py`)
- ✅ Pre-wired `.replit` that orchestrates everything

---

## 2. Create or open the Repl

1. Go to [replit.com](https://replit.com)
2. Click **Create Repl → Import from GitHub**
3. Paste the repository URL and wait for Replit to finish installing dependencies

> **Tip:** The provided `.replit` + `replit.nix` files already install Python 3.11, uvicorn, PostgreSQL client libs, and everything the backend needs.

---

## 3. Enable the managed PostgreSQL database

1. In the sidebar open **Tools → Database → PostgreSQL**
2. Click **Enable**
3. Replit provisions a database and injects `REPLIT_DB_URL`. The backend automatically picks it up through `app/db/database.py`, so no `.env` edits are required.

---

## 4. Keep secrets in one place

Use **Tools → Secrets** for anything sensitive. Recommended keys:

| Variable | Required? | Notes |
| --- | --- | --- |
| `SECRET_KEY` | ✅ | Pre-filled for convenience; replace in production |
| `RESEND_API_KEY` | Optional | Needed only if you enable transactional email |
| `STRIPE_SECRET_KEY` | Optional | Enable if you turn on billing features |
| `POSTGRES_URL` | Optional | Overrides `REPLIT_DB_URL` when you migrate to another Postgres provider |

All other configuration (ports, URLs, etc.) is driven by `.replit`.

---

## 5. Run locally inside Replit

Click the green **Run** button. The workflow:

1. Installs backend dependencies (`pip install -r requirements.txt`)
2. Runs `backend/init_db.py` to ensure the schema and demo data exist
3. Starts the FastAPI backend with uvicorn on port 8000
4. Launches `server.py`, which exposes the frontend on port 5000 (or `PORT` in a deployment)

When you see `Serving on http://0.0.0.0:5000`, open the webview. Replit maps port 5000 to your public URL automatically.

---

## 6. Verify the stack

| Check | Command / URL | Expected |
| --- | --- | --- |
| API health | `https://<repl-url>/health` | `{ "status": "healthy", ... }` |
| API docs | `https://<repl-url>/docs` | Swagger UI loads |
| Frontend | `https://<repl-url>/` | Opportunities list renders |
| Database | Replit shell → `psql $REPLIT_DB_URL -c "SELECT count(*) FROM users;"` | Shows seeded rows |

Demo login credentials (from `init_db.py`): `demo@example.com / demo123`.

---

## 7. Deploy on Replit

1. Click **Deploy** in the sidebar
2. Choose **Autoscale** or **Reserved VM**
3. Replit injects a `PORT` variable during deployment; `server.py` already reads it, so no extra work is needed
4. Enable **Always On** if you want background jobs like email sending to keep running

---

## 8. Custom domains & CORS

- For preview/deploy URLs, everything runs on a single origin, so default `BACKEND_CORS_ORIGINS=["*"]` works.
- If you map a custom domain, update `BACKEND_CORS_ORIGINS` in Secrets to include that domain (e.g., `["https://app.yourdomain.com"]`).
- Static assets stay in this repo; no external CDN configuration is necessary.

---

## 9. Troubleshooting on Replit

| Symptom | Fix |
| --- | --- |
| `command finished with error [python server.py]: signal: terminated` | Make sure no other process is using `PORT`; restart the Repl (server now auto-detects `PORT`) |
| `Database not configured` | Confirm PostgreSQL is enabled and `REPLIT_DB_URL` exists in Secrets |
| Module import errors | Run `pip install -r requirements.txt` inside the Replit shell and click Run again |
| Frontend loads but API fails | Open the shell and run `curl https://<repl-url>/health` to inspect the error message |

---

## 10. Next steps

- Customize UI copy or styling in `*.html`, `css/`, and `js/`
- Extend FastAPI routes in `backend/app/routers`
- Add new SQLAlchemy models or migrations (use the existing engine/session helpers)
- Automate background tasks via Replit’s scheduled jobs if needed

Replit now provides everything this project needs—no Supabase, Netlify, or Vercel integration remains. Happy building! 🎉
