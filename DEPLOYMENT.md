# 🚀 Deployment Guide (Replit Only)

This repository now targets a single hosting story: **Replit**. The static frontend, FastAPI backend, and PostgreSQL database all live in the same Repl, so you no longer need Render, Netlify, Vercel, or Supabase.

---

## 1. Prerequisites

- A Replit account with access to the project repository
- Secrets configured in **Tools → Secrets** (at minimum `SECRET_KEY`, optionally `RESEND_API_KEY`, `STRIPE_SECRET_KEY`, etc.)
- Replit PostgreSQL enabled via **Tools → Database → PostgreSQL**

Replit automatically injects `REPLIT_DB_URL` and `PORT`; `server.py` and the backend pick them up with no manual edits.

---

## 2. Local run vs deployment

| Mode | How | Notes |
| --- | --- | --- |
| Development | Click **Run** | Uses the same workflow as production; great for testing changes before pushing |
| Deployment | Click **Deploy** → Autoscale or Reserved VM | Replit provisions an always-on environment that runs the exact same command (`python server.py`) |

---

## 3. Configure secrets

Use **Tools → Secrets** to define:

```
SECRET_KEY=<replace-with-strong-random-value>
BACKEND_CORS_ORIGINS=["*"]              # or your custom domains
RESEND_API_KEY=<optional>
STRIPE_SECRET_KEY=<optional>
STRIPE_WEBHOOK_SECRET=<optional>
# PostgreSQL configured via PG* variables in .replit file
```

All secrets are available both during development and deployment. No `.env` files are required inside the repo.

---

## 4. Running the deployment

1. Open your Repl
2. Confirm `python server.py` works via the **Run** button
3. Click **Deploy** in the sidebar
4. Choose **Autoscale** (recommended) or **Reserved VM**
5. Keep the default start command (`python server.py`)
6. Enable **Auto-deploy from Git** if you want every push to trigger a redeploy

During deployment Replit sets the `PORT` variable dynamically; `server.py` already binds to it, so health checks pass immediately.

---

## 5. Custom domains & HTTPS

1. While viewing your deployment, click **Add Custom Domain**
2. Follow Replit’s DNS instructions (CNAME to `replit.com`)
3. Update `BACKEND_CORS_ORIGINS` to include the custom domain, e.g.
   ```
   BACKEND_CORS_ORIGINS=["https://app.yourdomain.com"]
   ```
4. Replit provisions HTTPS certificates automatically

---

## 6. Database management

- Replit PostgreSQL is available from the shell: `psql $REPLIT_DB_URL`
- `backend/init_db.py` can be re-run at any time to recreate tables or seed demo data
- For backups/export, run `pg_dump $REPLIT_DB_URL > backup.sql`

If you later decide to use another Postgres provider, set `POSTGRES_URL` in Secrets; the backend prefers that over `REPLIT_DB_URL`.

---

## 7. Observability & troubleshooting

| Issue | Resolution |
| --- | --- |
| Deployment immediately stops | Check logs for `signal: terminated`. Usually indicates another process already bound to `PORT`; stopping and redeploying clears it. |
| Database connection errors | Confirm PostgreSQL is enabled and `REPLIT_DB_URL` exists. Use `psql` to verify credentials. |
| Static files not updating | Re-run or redeploy so the new assets are served. |
| Background tasks need to keep running | Use a Reserved VM deployment or enable **Always On**. |

Logs for both development and deployment are visible directly in the Replit UI.

---

## 8. Scaling considerations

- **Autoscale** adds more containers automatically when traffic increases.
- **Reserved VM** gives you consistent resources (useful for predictable workloads).
- The FastAPI backend already uses `uvicorn` with a single worker; for heavier workloads you can update `server.py` to launch multiple workers or gunicorn, but most Replit apps do fine as-is.

---

## 9. After deployment

- Visit `https://<repl-slug>.<username>.repl.co` (or your custom domain)
- Use `/docs` to confirm the API is available
- Exercise critical flows (login, create opportunity, validate opportunity)
- Monitor logs for errors during the first few minutes of traffic

Congratulations—you now have a fully hosted application running 100% on Replit. 🎉
