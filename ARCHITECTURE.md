# Connection Architecture Summary

## 📁 Files Created/Modified

### Configuration Files
- ✅ `backend/.env` - Backend environment variables (DATABASE, SECRET_KEY, CORS)
- ✅ `.env.example` - Template for environment variables
- ✅ `js/config.js` - Frontend configuration (API URL)

### Startup Scripts
- ✅ `start-backend.ps1` - Start backend API server
- ✅ `start-frontend.ps1` - Start frontend HTTP server
- ✅ `start-app.ps1` - Start both servers at once

### Documentation
- ✅ `CONNECTION_GUIDE.md` - Comprehensive setup guide
- ✅ `QUICKSTART.md` - Quick start instructions

### Modified Files
- ✅ `js/api.js` - Updated to use config file

## 🔗 Connection Flow

```
User Browser (localhost:5500)
    │
    ├── Loads HTML pages (index.html, signin.html, etc.)
    ├── Loads js/config.js (API configuration)
    └── Loads js/api.js (API client)
         │
         └── Makes HTTP requests to ↓
                                      
Backend API (localhost:8000)
    │
    ├── Validates JWT tokens
    ├── Processes requests
    └── Queries database ↓
                         
PostgreSQL Database
    │
    ├── Supabase (cloud) OR
    └── Local Docker container

```

## 🔐 Authentication Flow

1. User registers/logs in via frontend
2. Backend validates credentials
3. Backend generates JWT token
4. Frontend stores token in localStorage
5. Frontend includes token in all subsequent API requests
6. Backend validates token for protected endpoints

## 🚀 How to Use

### First Time Setup:
1. Configure `backend/.env` with your database URL
2. Generate and set SECRET_KEY
3. Run `.\start-app.ps1`

### Daily Development:
```powershell
# Start everything
.\start-app.ps1

# Or start individually:
.\start-backend.ps1  # In terminal 1
.\start-frontend.ps1 # In terminal 2
```

### Testing Connection:
```javascript
// In browser console at localhost:5500
const api = new OppGridAPI();

// Test health
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log);

// Test registration
api.register('test@example.com', 'password123', 'Test User')
  .then(console.log);

// Test login
api.login('test@example.com', 'password123')
  .then(console.log);

// Test getting opportunities
api.getOpportunities()
  .then(console.log);
```

## 📊 API Endpoints

All endpoints are at `http://localhost:8000/api/v1/`

### Public Endpoints:
- `POST /auth/register` - Create account
- `POST /auth/login` - Sign in
- `GET /opportunities/` - List opportunities
- `GET /opportunities/{id}` - Get opportunity details

### Protected Endpoints (requires authentication):
- `POST /opportunities/` - Create opportunity
- `PUT /opportunities/{id}` - Update opportunity
- `DELETE /opportunities/{id}` - Delete opportunity
- `POST /validations/` - Validate opportunity
- `POST /comments/` - Add comment
- `GET /users/me` - Get current user
- `PUT /users/me` - Update profile

## 🛠️ Environment Variables

### backend/.env
```env
# Database - MUST CONFIGURE
DATABASE_URL=postgresql://user:password@host:5432/database

# Security - MUST CHANGE
SECRET_KEY=your-secret-key-here

# CORS - Frontend URLs
BACKEND_CORS_ORIGINS=["http://localhost:5500"]
```

## ✅ Checklist Before Starting

- [ ] Python 3.8+ installed
- [ ] Database configured (Supabase or Docker)
- [ ] backend/.env file created
- [ ] DATABASE_URL set in .env
- [ ] SECRET_KEY set in .env
- [ ] Dependencies installed (`pip install -r backend/requirements.txt`)

## 🐛 Common Issues

### Backend won't start
- Check `backend/.env` exists
- Verify DATABASE_URL is correct
- Ensure Python dependencies are installed

### Frontend can't connect
- Backend must be running on port 8000
- Frontend must be served via HTTP (not file://)
- Check CORS origins in backend/.env

### Database connection fails
- For Supabase: Verify credentials and project is active
- For Docker: Run `docker compose --profile local ps`

## 📚 Next Steps

1. Update HTML pages to integrate with API
2. Implement authentication in login/signup pages
3. Connect opportunity forms to backend
4. Add error handling and loading states
5. Test all features end-to-end
