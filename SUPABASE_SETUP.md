# 🚀 Supabase Setup Guide for Friction

## Quick Start

### 1. Get Your Supabase Credentials

After creating your project at [supabase.com](https://supabase.com):

**Database Connection:**
1. Go to **Project Settings** → **Database**
2. Scroll to **Connection string** → **URI**
3. Copy the string (replace `[YOUR-PASSWORD]` with your actual password)

**API Keys:**
1. Go to **Project Settings** → **API**
2. Copy:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key
   - **service_role** key (keep this secret!)

### 2. Update Your Environment File

Copy the example file:
```bash
cp backend/.env.supabase backend/.env
```

Edit `backend/.env` and replace:
- `[YOUR-PASSWORD]` with your database password
- `xxxxxxxxxxxxx` with your project reference ID
- `your_anon_key_here` with your anon key
- `your_service_role_key_here` with your service role key

### 3. Initialize the Database

**Option A: Using Docker (Recommended)**
```bash
# Start only the backend (not the local database)
docker compose up backend -d

# Initialize database
docker compose exec backend python init_db.py
```

**Option B: Run Locally**
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run initialization
python init_db.py
```

### 4. Verify Setup

Visit the Supabase Dashboard:
1. Go to **Table Editor** in your Supabase project
2. You should see 4 tables: `users`, `opportunities`, `validations`, `comments`
3. Click on tables to see sample data

### 5. Start Your Backend

```bash
# With Docker
docker compose up backend

# Or locally
cd backend
uvicorn app.main:app --reload
```

Visit: **http://localhost:8000/docs**

---

## 🎯 Connection Details Locations

### In Supabase Dashboard:

**Database Connection String:**
```
Project Settings → Database → Connection string → URI
```

**API Credentials:**
```
Project Settings → API → Project URL
Project Settings → API → Project API keys
```

**Connection Pooler (for production):**
```
Project Settings → Database → Connection Pooling → Connection string
```

---

## 📊 Database Tables Schema

After initialization, you'll have:

### `users` table
- id, email, name, bio, avatar_url
- impact_points, badges, hashed_password
- is_active, is_verified
- created_at, updated_at

### `opportunities` table
- id, title, description
- category, subcategory, severity
- validation_count, growth_rate, market_size
- author_id (FK), is_anonymous, status
- created_at, updated_at

### `validations` table
- id, user_id (FK), opportunity_id (FK)
- created_at

### `comments` table
- id, content, user_id (FK), opportunity_id (FK)
- likes, created_at, updated_at

---

## 🔐 Supabase Authentication (Optional)

Supabase has built-in auth! You can optionally use it instead of our custom JWT:

### Enable Email/Password Auth
1. Go to **Authentication** → **Providers**
2. Enable **Email**
3. Configure email templates

### Get Auth API
Instead of our custom auth, you could use Supabase Auth:
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Sign up
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password123'
})

// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password123'
})
```

---

## 🌐 Production Deployment

For production, use the **Connection Pooler**:

1. Go to **Project Settings** → **Database**
2. Enable **Connection Pooling**
3. Use the pooler connection string for better performance

Update your production `.env`:
```env
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

---

## 🔍 Monitoring & Management

### View Data
**Supabase Dashboard** → **Table Editor**
- Browse all tables
- Edit data directly
- Run SQL queries

### Run SQL Queries
**SQL Editor**
```sql
-- See all opportunities
SELECT * FROM opportunities ORDER BY created_at DESC;

-- Count users
SELECT COUNT(*) FROM users;

-- Top validated opportunities
SELECT title, validation_count
FROM opportunities
ORDER BY validation_count DESC
LIMIT 10;
```

### Database Logs
**Logs** section shows:
- Query performance
- Error logs
- Connection logs

---

## 💰 Supabase Pricing

### Free Tier (What you get)
- ✅ 500MB database storage
- ✅ 1GB file storage
- ✅ 2GB bandwidth
- ✅ 50,000 monthly active users
- ✅ Unlimited API requests
- ✅ Up to 500MB data transfer/day

**Perfect for development and small production apps!**

### Pro Tier ($25/month) - Upgrade when needed
- 8GB database storage
- 100GB file storage
- 250GB bandwidth
- 100,000 monthly active users
- Daily backups
- Priority support

---

## 🐛 Troubleshooting

### Connection Refused
- ✅ Check your password is correct
- ✅ Verify the connection string format
- ✅ Make sure project is not paused (free tier pauses after 1 week inactivity)

### SSL Required Error
Add `?sslmode=require` to your DATABASE_URL:
```env
DATABASE_URL=postgresql://postgres:pass@db.xxx.supabase.co:5432/postgres?sslmode=require
```

### Too Many Connections
Use the Connection Pooler (see Production Deployment above)

### Tables Not Created
Run the initialization script again:
```bash
docker compose exec backend python init_db.py
```

---

## 🔄 Migration from Local Docker

If you were using local Docker PostgreSQL:

1. Export local data:
```bash
docker compose exec db pg_dump -U friction_user friction_db > backup.sql
```

2. Import to Supabase:
```bash
psql "postgresql://postgres:[password]@db.xxx.supabase.co:5432/postgres" < backup.sql
```

Or just run `init_db.py` fresh with sample data.

---

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Database Backups](https://supabase.com/docs/guides/platform/backups)
- [Connection Pooling](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
- [Security Best Practices](https://supabase.com/docs/guides/platform/going-into-prod)

---

## ✅ Checklist

- [ ] Created Supabase account
- [ ] Created new project
- [ ] Copied connection string
- [ ] Updated backend/.env with credentials
- [ ] Ran init_db.py
- [ ] Verified tables in Supabase dashboard
- [ ] Tested API at /docs
- [ ] Frontend connects successfully

---

## 🎉 You're All Set!

Your Friction app is now powered by Supabase!

**Next steps:**
1. Test the API: http://localhost:8000/docs
2. View your data: Supabase Dashboard → Table Editor
3. Configure your frontend to use the API
