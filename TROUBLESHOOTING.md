# Login and Stripe Issues - Diagnosis and Fix

## Issue 1: Login Not Working

### Likely Causes:
1. **Backend server not running** - Most common issue
2. **Database connection failing** - PostgreSQL not initialized
3. **No demo users in database** - Database needs initialization

### Fix for Login Issue:

**Step 1: On Replit, test database connection**
```bash
python test_db.py
```

Expected output: `✓ ALL TESTS PASSED - Database is ready!`

If it fails:
- Check that `.replit` has `modules = ["postgresql-16"]` 
- Stop and restart your Repl

**Step 2: Initialize the database (creates demo users)**
```bash
cd backend
python init_db.py
cd ..
```

This will create:
- Demo user: `demo@example.com` / `demo123`
- Admin user: `admin@example.com` / `admin123`

**Step 3: Start the server**
```bash
python server.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
[Frontend] Serving on http://0.0.0.0:5000
```

**Step 4: Test login**
- Open your Replit app URL
- Use credentials: `demo@example.com` / `demo123`

### Common Login Errors:

**Error: "Social login not yet implemented"**
- This is just a placeholder message
- Real issue: Backend API not responding
- Fix: Make sure `python server.py` is running

**Error: "An error occurred"**
- Frontend can't reach backend
- Fix: Check server is running on port 5000 and 8000

**Error: "Invalid credentials"**
- Database not initialized or wrong password
- Fix: Run `backend/init_db.py` again

---

## Issue 2: Stripe Not Working

### Current Configuration:
The code uses **Replit's Stripe Connector** which automatically provides keys.

### How to Configure Stripe:

**Option A: Use Replit Stripe Connector (Recommended)**

1. **In your Replit project, go to Tools → Integrations**
2. **Find "Stripe" and click "Connect"**
3. **Enter your Stripe credentials:**
   - Secret Key (starts with `sk_test_` or `sk_live_`)
   - Publishable Key (starts with `pk_test_` or `pk_live_`)
4. **Select environment: "development" for testing**

The connector will automatically inject the keys at runtime.

**Option B: Manual Configuration via Secrets**

If the connector doesn't work, add to Replit Secrets:

```bash
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
```

### How to Get Stripe Keys:

1. **Sign up at https://stripe.com** (if you don't have an account)
2. **Go to Developers → API Keys**
3. **Use TEST keys** (they start with `sk_test_` and `pk_test_`)
4. **Copy both keys:**
   - Secret key (for backend)
   - Publishable key (for frontend)

### Test Stripe Configuration:

**On Replit shell, run:**
```bash
python -c "from app.services.stripe_service import get_stripe_credentials; sk, pk = get_stripe_credentials(); print(f'Secret Key: {\"SET\" if sk else \"NOT SET\"}'); print(f'Publishable Key: {\"SET\" if pk else \"NOT SET\"}')"
```

Expected output:
```
Secret Key: SET
Publishable Key: SET
```

### Common Stripe Errors:

**Error: "Stripe not configured"**
- No API keys found
- Fix: Set up Stripe connector or add keys to Secrets

**Error: "Invalid API key"**
- Wrong key format or expired
- Fix: Verify keys in Stripe dashboard

**Error: "Test mode vs Live mode mismatch"**
- Using test key with live publishable key (or vice versa)
- Fix: Ensure both keys are either test or live (use test for development)

### Stripe Webhook Setup (For Production):

If you need webhooks (for subscription updates):

1. **In Stripe dashboard, go to Developers → Webhooks**
2. **Add endpoint:** `https://your-repl-url.replit.dev/api/v1/subscriptions/webhook`
3. **Select events:** 
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. **Copy webhook signing secret** (starts with `whsec_`)
5. **Add to Replit Secrets:**
   ```
   STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE
   ```

---

## Quick Troubleshooting Commands:

**Check if backend is running:**
```bash
curl http://localhost:8000/health
```

**Check if database is connected:**
```bash
python -c "from backend.app.db.database import initialize_database, get_database_url; print(get_database_url()); initialize_database()"
```

**Check Stripe keys:**
```bash
python -c "import os; print('Stripe Secret:', 'SET' if os.getenv('STRIPE_SECRET_KEY') or os.getenv('REPLIT_CONNECTORS_HOSTNAME') else 'NOT SET')"
```

**View server logs:**
- Check the Replit console output when `python server.py` runs
- Look for error messages with `ERROR` or `WARNING`

---

## Complete Setup Checklist:

- [ ] `.replit` file has `modules = ["postgresql-16"]`
- [ ] Database test passes: `python test_db.py`
- [ ] Database initialized: `cd backend && python init_db.py`
- [ ] Server running: `python server.py` (shows both ports 5000 and 8000)
- [ ] Demo login works: `demo@example.com` / `demo123`
- [ ] Stripe keys configured (via connector or secrets)
- [ ] Stripe test passes: Keys show as "SET"

---

## If Still Not Working:

**Provide this information:**

1. **Login issue - paste error message from:**
   - Browser console (F12 → Console tab)
   - Replit console output

2. **Stripe issue - run and paste output:**
   ```bash
   python -c "from app.services.stripe_service import get_stripe_credentials; print(get_stripe_credentials())"
   ```

3. **Server status - run and paste output:**
   ```bash
   curl http://localhost:8000/health
   ```
