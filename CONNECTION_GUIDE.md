# Frontend-Backend-Database Connection Guide

This guide will help you connect your frontend, backend, and database for the Friction application.

## 🎯 Quick Start

### Option 1: Using Supabase (Recommended for Production)

1. **Set up Supabase Database**
   - Go to [https://app.supabase.com](https://app.supabase.com)
   - Create a new project
   - Get your database credentials from Project Settings > Database
   - Note your connection string (looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres`)

2. **Configure Backend Environment**
   - Open `backend/.env`
   - Replace the `DATABASE_URL` with your Supabase connection string:
     ```
     DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
     ```
   - Generate a secure SECRET_KEY:
     ```powershell
     python -c "import secrets; print(secrets.token_urlsafe(32))"
     ```
   - Update the SECRET_KEY in `.env` with the generated value

3. **Install Backend Dependencies**
   ```powershell
   cd backend
   pip install -r requirements.txt
   ```

4. **Start the Backend Server**
   ```powershell
   cd backend
   uvicorn app.main:app --reload
   ```
   The backend will be available at: `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

5. **Serve the Frontend**
   - Open your HTML files with a local web server (not just double-clicking)
   - Using Python:
     ```powershell
     python -m http.server 5500
     ```
   - Or use VS Code's Live Server extension
   - Access at: `http://localhost:5500`

### Option 2: Using Local PostgreSQL with Docker

1. **Start PostgreSQL Database**
   ```powershell
   docker compose --profile local up -d
   ```

2. **Configure Backend Environment**
   - Open `backend/.env`
   - Update DATABASE_URL to use local database:
     ```
     DATABASE_URL=postgresql://friction_user:friction_password@localhost:5432/friction_db
     ```
   - Generate and set SECRET_KEY (see Option 1, step 2)

3. **Continue with steps 3-5 from Option 1**

## 📝 Configuration Files Created

### Backend Configuration (`backend/.env`)
- `DATABASE_URL`: Your database connection string
- `SECRET_KEY`: For JWT token encryption (MUST be changed!)
- `BACKEND_CORS_ORIGINS`: Frontend URLs allowed to access the API

### Frontend Configuration (`js/config.js`)
- `API_BASE_URL`: Backend API endpoint (default: `http://localhost:8000/api/v1`)

## 🔗 How the Connection Works

```
Frontend (HTML/JS) 
    ↓
js/api.js (API Client)
    ↓
Backend API (FastAPI on :8000)
    ↓
Database (PostgreSQL)
```

### API Endpoints Available

All endpoints are prefixed with `/api/v1`:

- **Authentication**: `/api/v1/auth/`
  - POST `/register` - Create new account
  - POST `/login` - Sign in
  - POST `/logout` - Sign out

- **Opportunities**: `/api/v1/opportunities/`
  - GET `/` - List opportunities
  - POST `/` - Create opportunity
  - GET `/{id}` - Get specific opportunity
  - PUT `/{id}` - Update opportunity
  - DELETE `/{id}` - Delete opportunity

- **Validations**: `/api/v1/validations/`
  - POST `/` - Validate an opportunity
  - GET `/opportunity/{id}` - Get validations for opportunity

- **Comments**: `/api/v1/comments/`
  - POST `/` - Add comment
  - GET `/opportunity/{id}` - Get comments for opportunity

- **Users**: `/api/v1/users/`
  - GET `/me` - Get current user profile
  - PUT `/me` - Update profile

## 🧪 Testing the Connection

### 1. Test Backend Health
```powershell
curl http://localhost:8000/health
```
Should return: `{"status":"healthy"}`

### 2. Test API Documentation
Open browser to: `http://localhost:8000/docs`
You should see interactive API documentation.

### 3. Test Frontend Connection
1. Open `http://localhost:5500` (or your frontend URL)
2. Open browser console (F12)
3. Run:
   ```javascript
   fetch('http://localhost:8000/health')
     .then(r => r.json())
     .then(console.log)
   ```
4. Should log: `{status: "healthy"}`

## 🔐 Using the API from Frontend

The frontend uses `js/api.js` to communicate with the backend:

```javascript
// Example: Register a new user
const api = new FrictionAPI();
const user = await api.register('user@example.com', 'password123', 'John Doe');

// Example: Login
const token = await api.login('user@example.com', 'password123');

// Example: Get opportunities
const opportunities = await api.getOpportunities();

// Example: Create an opportunity (requires authentication)
const newOpp = await api.createOpportunity({
    title: 'Finding affordable housing',
    description: 'It\'s hard to find apartments in my budget',
    category: 'housing',
    problem_statement: 'Rental prices are too high...',
    current_solutions: 'Manual searching on multiple sites',
    desired_solution: 'A unified search platform'
});
```

## 🐛 Troubleshooting

### Backend won't start
- **Error: `DATABASE_URL` not set**
  - Solution: Make sure `backend/.env` exists and has DATABASE_URL configured

- **Error: Can't connect to database**
  - Solution: Verify your database is running and credentials are correct
  - For Docker: Run `docker compose --profile local ps` to check status
  - For Supabase: Verify your connection string is correct

### Frontend can't connect to backend
- **Error: CORS policy blocking request**
  - Solution: Add your frontend URL to `BACKEND_CORS_ORIGINS` in `backend/.env`
  - Restart the backend after changing .env

- **Error: Failed to fetch**
  - Solution: Make sure backend is running on port 8000
  - Check `js/config.js` has correct `API_BASE_URL`

### Authentication issues
- **Token expired**
  - Solution: Login again. Tokens expire after 30 minutes by default
  - Change `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env` to adjust

## 🚀 Production Deployment

### Backend Deployment
1. Use environment variables instead of .env file
2. Set DATABASE_URL to production database
3. Generate strong SECRET_KEY
4. Update BACKEND_CORS_ORIGINS with production frontend URL
5. Deploy to platforms like:
   - Render
   - Railway
   - Heroku
   - AWS/GCP/Azure

### Frontend Deployment
1. Update `js/config.js` with production API URL
2. Deploy static files to:
   - Vercel
   - Netlify
   - GitHub Pages
   - AWS S3 + CloudFront

## 📚 Next Steps

1. Customize the frontend pages to connect to the API
2. Implement authentication flow in login/signup pages
3. Update opportunity submission form to use API
4. Add real-time features with WebSockets
5. Set up proper error handling and loading states

## 🆘 Need Help?

- Check API documentation: `http://localhost:8000/docs`
- Review backend logs for errors
- Check browser console for frontend errors
- Verify database connection with: `docker compose logs db` (if using Docker)
