# Quick Start – Replit Only

This project is designed to run end-to-end on Replit: static frontend, FastAPI backend, and the managed PostgreSQL database. Follow these steps to get a working environment in a couple of minutes.

## 1. Import and open the Repl
1. Go to [replit.com](https://replit.com)
2. Click **Create Repl → Import from GitHub**
3. Paste your repository URL and wait for Replit to finish cloning

## 2. Enable the managed PostgreSQL database
1. In the Replit sidebar choose **Tools → Database → PostgreSQL**
2. Click **Enable**
3. Replit will provision a database and expose the connection string via `REPLIT_DB_URL` (no manual edits required)

## 3. Check the required secrets
| Key | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | JWT signing | Pre-filled in `.replit`; replace for production |
| `RESEND_API_KEY` | Email (optional) | Only set if you need email notifications |
| `STRIPE_SECRET_KEY` | Billing (optional) | Leave unset unless billing is enabled |

Use **Tools → Secrets** to add or update the variables above. Everything else is preconfigured through `.replit`.

## 4. Run the project
Click the green **Run** button. The workflow does the following:
1. Installs backend requirements
2. Initializes the PostgreSQL schema
3. Starts the FastAPI backend on port 8000
4. Proxies traffic through `server.py`, exposing the frontend on Replit’s public URL

When the logs show `Serving on http://0.0.0.0:5000`, open the preview window. Replit automatically maps that to `https://<repl-slug>.<username>.repl.co`.

## 5. Verify everything is healthy
1. Visit `https://<repl-url>/docs` to confirm the API is live
2. Visit `https://<repl-url>/api/v1/health` (proxied) to make sure the DB connection succeeded
3. Use the UI to log in with the demo credentials created by `init_db.py`

## 6. Deploy
When you are ready for an always-on deployment:
1. Click **Deploy** in the Replit sidebar
2. Choose **Autoscale** (recommended) or **Reserved VM**
3. Replit automatically sets the `PORT` variable; `server.py` already picks it up

That’s it—you now have a single-Replit stack with no external hosting dependencies.
