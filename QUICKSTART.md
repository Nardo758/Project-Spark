# Quick Start Guide - Frontend + Backend + Database Connection

## ⚡ Fastest Way to Get Started

### Step 1: Configure Database (Choose One)

#### Option A: Supabase (Recommended)
1. Go to https://app.supabase.com and create a project
2. Copy your connection string from Settings > Database
3. Edit `backend/.env` and update:
   ```
   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
   ```

#### Option B: Local Docker Database
```powershell
docker compose --profile local up -d
```
Then edit `backend/.env`:
```
DATABASE_URL=postgresql://friction_user:friction_password@localhost:5432/friction_db
```

### Step 2: Generate Secret Key
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output and update `SECRET_KEY` in `backend/.env`

### Step 3: Start Everything
```powershell
.\start-app.ps1
```

This opens two windows:
- Backend API: http://localhost:8000
- Frontend: http://localhost:5500

### Step 4: Test the Connection
1. Open http://localhost:5500
2. Open browser console (F12)
3. Run: `fetch('http://localhost:8000/health').then(r => r.json()).then(console.log)`
4. Should see: `{status: "healthy"}`

## 🔧 Manual Startup

### Start Backend Only:
```powershell
.\start-backend.ps1
```

### Start Frontend Only:
```powershell
.\start-frontend.ps1
```

## 📚 More Details

See `CONNECTION_GUIDE.md` for complete documentation including:
- API endpoints
- Authentication flow
- Troubleshooting
- Production deployment

## 🎯 What's Been Configured

✅ Backend API with FastAPI  
✅ PostgreSQL database (Supabase or local)  
✅ CORS configured for frontend  
✅ JWT authentication  
✅ Frontend API client (`js/api.js`)  
✅ Startup scripts  

## 🔑 Default Credentials (Local DB)

Database User: `friction_user`  
Database Password: `friction_password`  
Database Name: `friction_db`

## ⚠️ Important

- MUST update `SECRET_KEY` in `backend/.env` before production use
- MUST configure `DATABASE_URL` in `backend/.env`
- Frontend must be served via HTTP server (not file://)
