# Fix Replit Secrets Overriding Database Configuration

## The Problem
Replit Secrets are taking priority over the `.replit` file configuration. The imported secrets likely contain old database URLs that are overriding the correct PostgreSQL settings.

## Solution: Clean Up Replit Secrets

### Step 1: Open Replit Secrets
1. In your Replit project, click the **lock icon** (🔒) in the left sidebar, or
2. Click **Tools** → **Secrets**

### Step 2: Delete or Update These Secrets

**DELETE these if they exist:**
- `DATABASE_URL` - (if it points to KV store or old database)
- `POSTGRES_URL` - (if it points to Neon or any external database)
- `REPLIT_DB_URL` - (this is for KV store, not PostgreSQL)

**KEEP these if they exist (but verify they're correct):**
- `SECRET_KEY` - Your app's secret key
- `RESEND_API_KEY` - For email service
- `STRIPE_*` - For payments
- `GOOGLE_CLIENT_ID`, `GITHUB_CLIENT_ID` - For OAuth

### Step 3: Verify .replit File Takes Over

After deleting the problematic secrets, the app will use values from `.replit`:
```toml
PGHOST = "db"
PGPORT = "5432"
PGDATABASE = "replit"
PGUSER = "replit"
```

### Step 4: Alternative - Override with Correct Secret

If you want to keep using Secrets (recommended for production), **DELETE the bad DATABASE_URL** and add a new one:

**Option A: Let code use PG* variables from .replit**
- Don't set DATABASE_URL in Secrets at all
- The code will automatically use PGHOST, PGDATABASE, etc.

**Option B: Set DATABASE_URL to correct PostgreSQL**
```
DATABASE_URL=postgresql://replit@db:5432/replit
```

### Step 5: Restart and Test

1. **Stop** your Repl (click Stop button)
2. **Run** the diagnostic: `python check_db.py`
3. **Start** the server: `python server.py`

## How to Check What's in Secrets

Run this in Replit Shell:
```bash
python -c "import os; print('DATABASE_URL:', os.getenv('DATABASE_URL', 'NOT SET')[:60]); print('POSTGRES_URL:', os.getenv('POSTGRES_URL', 'NOT SET')[:60]); print('PGHOST:', os.getenv('PGHOST', 'NOT SET'))"
```

## Expected Output After Fix

```
✓ PGHOST = db
✓ PGDATABASE = replit  
✓ PGUSER = replit
✓ Will use: PG* variables
✓ DATABASE CONNECTION SUCCESSFUL!
```
