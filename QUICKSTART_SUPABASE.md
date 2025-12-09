# ⚡ Supabase Quick Start - 5 Minutes!

## Step 1: Create Supabase Project (2 min)

1. Go to **https://supabase.com** → Sign up
2. Click **"New Project"**
3. Fill in:
   - **Name**: `friction-db`
   - **Password**: (generate strong password - save it!)
   - **Region**: Choose closest to you
4. Click **"Create new project"**
5. Wait ~2 minutes ☕

## Step 2: Get Credentials (1 min)

### Database Connection String
1. Click **Project Settings** (⚙️ icon)
2. Go to **Database** tab
3. Scroll to **Connection string**
4. Select **URI**
5. Copy the string
6. **Replace `[YOUR-PASSWORD]`** with your actual password!

Example:
```
postgresql://postgres:your_password@db.abcdefghijk.supabase.co:5432/postgres
```

### API Keys (Optional but recommended)
1. Go to **Project Settings** → **API**
2. Copy:
   - **URL**: `https://abcdefghijk.supabase.co`
   - **anon public** key
   - **service_role** key (keep secret!)

## Step 3: Configure Backend (1 min)

**Option A: Interactive Setup (Easiest)**
```bash
python setup_supabase.py
```

**Option B: Manual Setup**
```bash
# Copy template
cp backend/.env.supabase backend/.env

# Edit with your values
nano backend/.env
```

Replace these in `backend/.env`:
- `[YOUR-PASSWORD]` → your database password
- `xxxxxxxxxxxxx` → your project reference (the ID from URL)
- `your_anon_key_here` → your anon key
- `your_service_role_key_here` → your service role key

## Step 4: Initialize Database (1 min)

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Create tables & add sample data
python init_db.py
```

You should see:
```
✅ Database initialized successfully!
Created 3 users
Created 5 opportunities
```

## Step 5: Start Backend & Test

```bash
# Start the backend
uvicorn app.main:app --reload
```

Visit: **http://localhost:8000/docs**

### Test Login:
- Email: `demo@example.com`
- Password: `demo123`

## 🎉 Done! Your Backend is Live

### What You Can Do Now:

**1. View Your Data**
- Go to Supabase Dashboard → **Table Editor**
- You'll see: `users`, `opportunities`, `validations`, `comments`

**2. Try the API**
- Visit: http://localhost:8000/docs
- Click **"Authorize"**
- Login with demo credentials
- Try creating an opportunity!

**3. Connect Frontend**
Add to your HTML files:
```html
<script src="js/api.js"></script>
<script>
  // Login
  api.login('demo@example.com', 'demo123')
    .then(data => console.log('Logged in!'));

  // Get opportunities
  api.getOpportunities({ limit: 10 })
    .then(data => console.log(data));
</script>
```

---

## 🔍 Verify Everything Works

### Check 1: Database Tables
```bash
# In Supabase Dashboard → Table Editor
# You should see 4 tables with data
```

### Check 2: API Health
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Check 3: Get Opportunities
```bash
curl http://localhost:8000/api/v1/opportunities/
# Should return JSON with 5 sample opportunities
```

---

## 💡 Common Issues

### "Connection refused"
- ✅ Check password in DATABASE_URL is correct
- ✅ Make sure Supabase project is active (not paused)
- ✅ Check you replaced `[YOUR-PASSWORD]` with actual password

### "No tables found"
```bash
# Run init script again
cd backend
python init_db.py
```

### "Module not found"
```bash
# Install dependencies
pip install -r requirements.txt
```

---

## 📊 What's Free on Supabase?

✅ **500MB** database storage
✅ **1GB** file storage
✅ **Unlimited** API requests
✅ **50,000** monthly active users
✅ **2GB** bandwidth per day
✅ **Up to 7 days** of data retention

**Perfect for development and small production apps!**

---

## 🚀 Next Steps

- [ ] Frontend integration (`js/api.js` already created!)
- [ ] Add your domain to CORS settings
- [ ] Configure scrapers to POST to API
- [ ] Set up Supabase Auth (optional)
- [ ] Enable Row Level Security for production

---

## 📚 Resources

- **Supabase Dashboard**: https://app.supabase.com
- **API Docs**: http://localhost:8000/docs
- **Full Setup Guide**: See `SUPABASE_SETUP.md`
- **Supabase Docs**: https://supabase.com/docs

---

## 🎯 Quick Commands Reference

```bash
# Setup
python setup_supabase.py          # Interactive setup
python backend/init_db.py         # Initialize database

# Start backend
cd backend
uvicorn app.main:app --reload    # Development mode

# Or with Docker
docker compose up backend         # Without local DB

# View logs
docker compose logs -f backend

# Reset database (delete all data)
# Go to Supabase Dashboard → Database → Reset database
```

---

**Questions?** Check `SUPABASE_SETUP.md` for detailed troubleshooting!
