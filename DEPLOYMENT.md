# 🚀 Production Deployment Guide

## Your Deployment URLs

**Backend (Render):** https://YOUR-APP-NAME.onrender.com
**Frontend (Netlify):** https://YOUR-SITE-NAME.netlify.app

---

## 🔧 Step-by-Step Configuration

### 1️⃣ Update Frontend URLs (You Need to Do This)

Replace `YOUR-RENDER-APP` in these files with your actual Render app name:

**File: `js/api.js` (line 9)**
```javascript
: 'https://YOUR-RENDER-APP.onrender.com/api/v1';
```

**File: `js/app.js` (line 9)**
```javascript
: 'https://YOUR-RENDER-APP.onrender.com/api/v1';
```

**For example, if your Render URL is:**
```
https://friction-api.onrender.com
```

**Change to:**
```javascript
: 'https://friction-api.onrender.com/api/v1';
```

### 2️⃣ Update Backend CORS Settings

In your **Render Dashboard**:

1. Go to your backend service
2. Click **Environment** tab
3. Add/Update these environment variables:

```env
BACKEND_CORS_ORIGINS=["https://YOUR-SITE-NAME.netlify.app","https://localhost:5500","http://localhost:5500"]
```

**Replace `YOUR-SITE-NAME` with your actual Netlify site name.**

For example:
```env
BACKEND_CORS_ORIGINS=["https://friction-app.netlify.app","https://localhost:5500","http://localhost:5500"]
```

4. Click **Save Changes**
5. Backend will automatically redeploy

### 3️⃣ Verify Render Environment Variables

Make sure these are set in Render:

```env
# Database - Your Supabase connection (USE POOLED CONNECTION FOR RENDER)
# Pooled (Port 6543 - RECOMMENDED for serverless/Render):
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:6543/postgres?pgbouncer=true&sslmode=require
# Direct (Port 5432 - NOT recommended for Render):
# DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres

# Security - IMPORTANT: Use a strong secret key
SECRET_KEY=your-production-secret-key-here

# Algorithm
ALGORITHM=HS256

# Token expiration
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API settings
API_V1_PREFIX=/api/v1
PROJECT_NAME=Friction API

# CORS - Add your Netlify URL
BACKEND_CORS_ORIGINS=["https://your-site.netlify.app"]
```

### 4️⃣ Push Updated Frontend to Netlify

After updating the URLs in `js/api.js` and `js/app.js`:

```bash
git add js/api.js js/app.js
git commit -m "feat: Configure production API URLs"
git push
```

Netlify will automatically redeploy.

---

## ✅ Quick Configuration Checklist

**In `js/api.js`:**
- [ ] Line 9: Replace `YOUR-RENDER-APP` with your Render app name

**In `js/app.js`:**
- [ ] Line 9: Replace `YOUR-RENDER-APP` with your Render app name

**In Render Dashboard:**
- [ ] Set `BACKEND_CORS_ORIGINS` with your Netlify URL
- [ ] Verify `DATABASE_URL` is set to Supabase
- [ ] Verify `SECRET_KEY` is set
- [ ] Save and wait for redeploy

**After Changes:**
- [ ] Push code to Git
- [ ] Wait for Netlify to redeploy
- [ ] Test login on your Netlify site

---

## 🔍 Verifying Database Connection

### Using the Verification Script

A comprehensive verification script is provided to test your Supabase connection:

```bash
# Navigate to backend directory
cd backend

# Set your DATABASE_URL
export DATABASE_URL="postgresql://postgres:your_password@db.xxxxx.supabase.co:6543/postgres?pgbouncer=true&sslmode=require"

# Run verification script
python verify_db_connection.py
```

### What Gets Tested

The script runs 5 comprehensive tests:

1. **Basic Connectivity** - Establishes connection to Supabase
2. **SSL Connection** - Verifies encryption is active
3. **Database Queries** - Tests SELECT, version check, table listing
4. **Connection Pooling** - Validates pool configuration
5. **Write Operations** - Tests CREATE, INSERT, DROP operations

### Expected Output

```
==============================================================
VERIFICATION SUMMARY
==============================================================
✓ Basic Connectivity: PASSED
✓ SSL Connection: PASSED
✓ Database Queries: PASSED
✓ Connection Pooling: PASSED
✓ Write Operations: PASSED

Results: 5/5 tests passed
✓ All tests passed! Database connection is fully operational.
```

### Supabase Connection Format

**For Render (Serverless) - Use Pooled Connection:**

```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:6543/postgres?pgbouncer=true&sslmode=require
```

**Key Points:**
- **Port 6543**: PgBouncer pooled connection (recommended for Render)
- **pgbouncer=true**: Enables connection pooling
- **sslmode=require**: Forces SSL encryption
- Get your connection string from: Supabase Dashboard → Settings → Database → Connection pooling

**Why Pooled Connection?**
- ✅ Better for serverless environments (Render, Vercel, AWS Lambda)
- ✅ Handles many concurrent connections efficiently
- ✅ Prevents "too many connections" errors
- ✅ Automatically manages connection lifecycle

---

## 🧪 Testing Your Production Deployment

### 1. Test Backend API

Visit: `https://YOUR-RENDER-APP.onrender.com/docs`

You should see the FastAPI interactive documentation.

**Try:**
- Click **GET /api/v1/opportunities/**
- Click "Try it out" → "Execute"
- Should return JSON with opportunities

### 2. Test Frontend

Visit: `https://YOUR-SITE-NAME.netlify.app`

**Try:**
1. Browse opportunities (should load from Render backend)
2. Click on an opportunity (should show details)
3. Go to login page
4. Login with: `demo@example.com` / `demo123`
5. Should successfully authenticate!

### 3. Check Browser Console

Press **F12** → Console tab

Look for:
- ✅ No CORS errors
- ✅ Successful API calls to your Render URL
- ✅ "Login successful!" message after login

---

## 🐛 Troubleshooting

### CORS Error

**Error in console:**
```
Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS policy
```

**Fix:**
1. Go to Render → Environment variables
2. Update `BACKEND_CORS_ORIGINS` to include your Netlify URL
3. Save and wait for redeploy

### Wrong API URL

**Error:** Frontend still calling `localhost:8000`

**Fix:**
1. Make sure you replaced `YOUR-RENDER-APP` in both files
2. Push changes to Git
3. Wait for Netlify to redeploy
4. Hard refresh browser (Ctrl+Shift+R)

### Database Connection Error

**Error in Render logs:**
```
OperationalError: could not connect to server
```

**Fix:**
1. Check `DATABASE_URL` in Render environment variables
2. Verify Supabase database is active
3. Check Supabase allows connections from 0.0.0.0/0

### Login Not Working

**Check:**
1. Backend is running: Visit `YOUR-RENDER-APP.onrender.com/docs`
2. Database has users: Run `init_db.py` on Render
3. CORS is configured correctly
4. Frontend is calling correct API URL

---

## 📝 Example: Complete Configuration

**Your URLs:**
- Render: `https://friction-api.onrender.com`
- Netlify: `https://friction-app.netlify.app`
- Supabase: `db.abcdefg.supabase.co`

**js/api.js (line 9):**
```javascript
: 'https://friction-api.onrender.com/api/v1';
```

**js/app.js (line 9):**
```javascript
: 'https://friction-api.onrender.com/api/v1';
```

**Render Environment Variables:**
```env
DATABASE_URL=postgresql://postgres:mypass123@db.abcdefg.supabase.co:6543/postgres?pgbouncer=true&sslmode=require
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_PREFIX=/api/v1
PROJECT_NAME=Friction API
BACKEND_CORS_ORIGINS=["https://friction-app.netlify.app","http://localhost:5500"]
```

---

## 🚀 After Configuration

Once everything is set up:

1. **Visit your Netlify site** - Should load opportunities
2. **Login works** - Can authenticate users
3. **Features work** - Filters, search, validation all functional
4. **Analytics work** - Feasibility scores, geographic distribution
5. **No console errors** - Check F12 developer tools

---

## 💡 Pro Tips

### Render Specific

- **Free tier sleeps after 15min inactivity** - First request takes ~30 seconds to wake up
- **Logs available** in Render dashboard - Check for errors
- **Auto-deploys** when you push to main branch

### Netlify Specific

- **Instant deploys** - Changes go live in ~1 minute
- **Preview deploys** for pull requests
- **Custom domain** - Can add your own domain in settings

### Development vs Production

The code automatically detects the environment:
- **localhost** → Uses `http://localhost:8000`
- **Netlify** → Uses your Render URL

This means you can still develop locally without changing anything!

---

## 📋 Quick Commands

**Verify database connection:**
```bash
cd backend
export DATABASE_URL="your-supabase-connection-string"
python verify_db_connection.py
```

**Update and deploy:**
```bash
# 1. Update the URLs in js/api.js and js/app.js
# 2. Commit and push
git add js/api.js js/app.js
git commit -m "feat: Configure production API URLs"
git push

# Netlify auto-deploys!
```

**Check Render logs:**
```
Render Dashboard → Your Service → Logs tab
```

**Redeploy Render manually:**
```
Render Dashboard → Your Service → Manual Deploy → Deploy latest commit
```

---

## ✅ All Set!

Once configured:
- ✅ Frontend on Netlify talks to Backend on Render
- ✅ Backend on Render talks to Database on Supabase
- ✅ All features work in production
- ✅ Users can login and use the app

**Your full-stack app is live! 🎉**
