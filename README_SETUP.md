# Friction Backend Setup Guide

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git

### 1. Start the Backend Services

```bash
# Start PostgreSQL and FastAPI backend
docker-compose up -d

# Wait for services to be healthy (about 30 seconds)
docker-compose ps
```

### 2. Initialize the Database

```bash
# Run the database initialization script
docker-compose exec backend python init_db.py
```

This will create:
- Database tables
- Sample users and opportunities
- Demo account (email: demo@example.com, password: demo123)

### 3. Access the API

**Interactive API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**API Base URL:** http://localhost:8000/api/v1

### 4. Serve the Frontend

You can use any static file server. Here are a few options:

**Option 1: Python HTTP Server**
```bash
# From the project root
python3 -m http.server 5500
```

**Option 2: VS Code Live Server**
- Install "Live Server" extension
- Right-click on index.html
- Select "Open with Live Server"

**Option 3: Node.js http-server**
```bash
npx http-server -p 5500
```

Then open: http://localhost:5500

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/{user_id}` - Get user by ID

### Opportunities
- `POST /api/v1/opportunities/` - Create opportunity
- `GET /api/v1/opportunities/` - List opportunities (with filters)
- `GET /api/v1/opportunities/{id}` - Get opportunity details
- `PUT /api/v1/opportunities/{id}` - Update opportunity
- `DELETE /api/v1/opportunities/{id}` - Delete opportunity
- `GET /api/v1/opportunities/search/` - Search opportunities

### Validations
- `POST /api/v1/validations/` - Validate opportunity ("I Need This Too")
- `DELETE /api/v1/validations/{id}` - Remove validation
- `GET /api/v1/validations/opportunity/{id}` - Get opportunity validations

### Comments
- `POST /api/v1/comments/` - Create comment
- `GET /api/v1/comments/opportunity/{id}` - Get opportunity comments
- `PUT /api/v1/comments/{id}` - Update comment
- `DELETE /api/v1/comments/{id}` - Delete comment
- `POST /api/v1/comments/{id}/like` - Like comment

## 🔧 Configuration

### Environment Variables

Edit `backend/.env` to configure:

```env
# Database
DATABASE_URL=postgresql://friction_user:friction_password@db:5432/friction_db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS - Add your frontend URLs
BACKEND_CORS_ORIGINS=["http://localhost:8000","http://localhost:5500"]
```

### Production Deployment

**⚠️ Before deploying to production:**

1. **Change SECRET_KEY**: Generate a secure secret key
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Update DATABASE_URL**: Use a production PostgreSQL instance

3. **Configure CORS**: Add your production domain to BACKEND_CORS_ORIGINS

4. **Enable HTTPS**: Use a reverse proxy (nginx, Caddy) with SSL

5. **Set environment to production**: Add proper logging and monitoring

## 🧪 Testing the API

### Using the Interactive Docs (Recommended)

1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Login with demo credentials or register a new user
4. Try out the endpoints

### Using curl

```bash
# Register a user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@example.com&password=demo123"

# Get opportunities (no auth required)
curl "http://localhost:8000/api/v1/opportunities/?limit=5"

# Create opportunity (requires auth token)
curl -X POST "http://localhost:8000/api/v1/opportunities/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Problem","description":"Testing...","category":"Technology","severity":3}'
```

## 🔍 Database Management

### Access PostgreSQL

```bash
# Connect to the database
docker-compose exec db psql -U friction_user -d friction_db

# Common commands:
# \dt - List tables
# \d opportunities - Describe table
# SELECT * FROM opportunities; - Query data
# \q - Quit
```

### Reset Database

```bash
# Stop services
docker-compose down

# Remove volumes (⚠️ this deletes all data!)
docker-compose down -v

# Start fresh
docker-compose up -d
docker-compose exec backend python init_db.py
```

## 📊 Database Schema

```
users
├── id (PK)
├── email (unique)
├── hashed_password
├── name
├── bio
├── avatar_url
├── impact_points
├── badges
├── is_active
├── is_verified
├── created_at
└── updated_at

opportunities
├── id (PK)
├── title
├── description
├── category
├── subcategory
├── severity
├── validation_count
├── growth_rate
├── market_size
├── author_id (FK → users)
├── is_anonymous
├── status
├── created_at
└── updated_at

validations
├── id (PK)
├── user_id (FK → users)
├── opportunity_id (FK → opportunities)
└── created_at

comments
├── id (PK)
├── content
├── user_id (FK → users)
├── opportunity_id (FK → opportunities)
├── likes
├── created_at
└── updated_at
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose up --build
```

### Database connection error
```bash
# Ensure database is healthy
docker-compose ps

# Check database logs
docker-compose logs db
```

### CORS errors
- Add your frontend URL to `BACKEND_CORS_ORIGINS` in `backend/.env`
- Restart the backend: `docker-compose restart backend`

## 📦 Development Commands

```bash
# View logs
docker-compose logs -f backend

# Restart backend only
docker-compose restart backend

# Stop all services
docker-compose down

# Start in foreground (see live logs)
docker-compose up

# Run Python shell in backend
docker-compose exec backend python

# Install new Python package
docker-compose exec backend pip install package-name
# Then add to requirements.txt
```

## 🔐 Sample Credentials

**Demo Account:**
- Email: demo@example.com
- Password: demo123

**Test Accounts:**
- Email: john@example.com, Password: password123
- Email: jane@example.com, Password: password123

## 📝 Next Steps

1. ✅ Backend API is running
2. ✅ Database is set up
3. ✅ Frontend API client created
4. 🔄 Update HTML files to use the API (add `<script src="js/api.js">`)
5. 🔄 Replace mock data with real API calls
6. 🧪 Test the complete integration

## 🔗 Useful Links

- FastAPI Documentation: https://fastapi.tiangolo.com
- PostgreSQL Documentation: https://www.postgresql.org/docs
- Docker Compose: https://docs.docker.com/compose
