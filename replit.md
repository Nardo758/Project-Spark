# Friction - Problem Discovery Engine

## Overview
Friction is a full-stack web application that serves as a problem discovery engine for founders, researchers, and innovators. It allows users to find validated opportunities, track emerging needs, and solve real problems.

## Architecture
- **Frontend**: Static HTML/CSS/JavaScript served on port 5000
- **Backend**: Python FastAPI running on port 8000 (internal)
- **Database**: PostgreSQL (Replit-managed)

## Project Structure
```
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── core/      # Configuration, security
│   │   ├── db/        # Database setup
│   │   ├── models/    # SQLAlchemy models
│   │   ├── routers/   # API routes
│   │   └── schemas/   # Pydantic schemas
│   └── requirements.txt
├── js/                # Frontend JavaScript
├── css/               # Frontend CSS
├── *.html             # Frontend HTML pages
└── server.py          # Combined server (frontend + proxy to backend)
```

## Running the Application
The application is started via `python server.py` which:
1. Starts the FastAPI backend on localhost:8000
2. Serves static frontend files on 0.0.0.0:5000
3. Proxies `/api/*` requests to the backend

## API Endpoints
- `GET /health` - Health check
- `GET /docs` - Swagger documentation
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/opportunities` - List opportunities
- And more...

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string (auto-configured)
- `SECRET_KEY` - JWT secret key
- `BACKEND_CORS_ORIGINS` - CORS allowed origins
