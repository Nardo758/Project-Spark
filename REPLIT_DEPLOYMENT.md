# Replit Deployment Guide

## Overview

This project is fully configured to run on Replit with integrated PostgreSQL database support. The application consists of:

- **Frontend**: Static HTML/CSS/JavaScript (served on port 5000)
- **Backend**: FastAPI Python application (runs on port 8000)
- **Database**: Replit PostgreSQL (automatically managed)

## Quick Start on Replit

### 1. Import Repository

1. Go to [Replit](https://replit.com)
2. Click "Create Repl" → "Import from GitHub"
3. Paste your repository URL
4. Replit will automatically detect the configuration

### 2. Enable PostgreSQL Database

1. In your Repl, click on "Tools" in the sidebar
2. Select "Database" → "PostgreSQL"
3. Click "Enable PostgreSQL"
4. Replit will automatically set the `REPLIT_DB_URL` environment variable

### 3. Configure Environment Variables

The application will automatically use Replit's environment variables. You can optionally add:

**Required (if not using defaults):**
- `SECRET_KEY` - JWT secret key (auto-configured in .replit)

**Optional (for features):**
- `RESEND_API_KEY` - For email notifications
- `FROM_EMAIL` - Email sender address
- `GOOGLE_CLIENT_ID` - For Google OAuth
- `GOOGLE_CLIENT_SECRET` - For Google OAuth
- `GITHUB_CLIENT_ID` - For GitHub OAuth
- `GITHUB_CLIENT_SECRET` - For GitHub OAuth

To add these:
1. Click on "Tools" → "Secrets" (or the lock icon in sidebar)
2. Add your environment variables as key-value pairs

### 4. Run the Application

Simply click the "Run" button! The application will:
1. Install Python dependencies
2. Initialize the database
3. Start both frontend (port 5000) and backend (port 8000)
4. Open in the webview

The app will be accessible at: `https://[your-repl-name].[your-username].repl.co`

## Architecture on Replit

### Automatic Configuration

The application automatically detects the Replit environment and configures itself:

1. **Database**: Uses `REPLIT_DB_URL` if available, falls back to `DATABASE_URL`
2. **URLs**: Automatically sets frontend/backend URLs using Replit's domain
3. **CORS**: Configured to allow all origins for development

### Port Configuration

- **Port 5000**: Frontend (exposed as main webview on port 80)
- **Port 8000**: Backend API (internal, proxied through frontend)

API requests from the frontend to `/api/*` are automatically proxied to the backend.

### File Structure

```
.
├── .replit              # Replit configuration
├── replit.nix           # Nix dependencies
├── server.py            # Main server (starts both frontend & backend)
├── backend/             # FastAPI backend
│   ├── app/
│   │   ├── core/        # Configuration
│   │   ├── db/          # Database setup
│   │   ├── models/      # SQLAlchemy models
│   │   ├── routers/     # API routes
│   │   └── schemas/     # Pydantic schemas
│   ├── init_db.py       # Database initialization
│   └── requirements.txt
├── js/                  # Frontend JavaScript
├── css/                 # Frontend CSS
└── *.html               # Frontend pages
```

## Database Management

### Automatic Initialization

The database is automatically initialized on first run with all required tables:
- users
- opportunities
- validations
- comments
- watchlist
- notifications

### Manual Database Access

To access the database console:
1. Open the Replit Shell
2. Run: `psql $REPLIT_DB_URL`

### Reset Database

To reset the database:
```bash
python backend/init_db.py
```

## Deployment

### Development (Current)

The Repl runs in development mode by default with:
- Hot reloading disabled (restart needed for changes)
- Detailed error messages
- CORS allowing all origins

### Production Deployment

To deploy to production:

1. Click "Deploy" in the Replit sidebar
2. Choose deployment type:
   - **Autoscale**: Recommended for production
   - **Reserved VM**: For consistent performance
3. Configure custom domain (optional)
4. Update environment variables for production:
   ```
   SECRET_KEY=[generate-strong-key]
   BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
   ```

## Environment Variables Reference

### Database
- `REPLIT_DB_URL`: PostgreSQL connection (auto-set by Replit)
- `DATABASE_URL`: Fallback database connection

### Security
- `SECRET_KEY`: JWT signing key (default provided, change for production)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 30)

### Application
- `PROJECT_NAME`: API name (default: Friction API)
- `API_V1_PREFIX`: API route prefix (default: /api/v1)
- `BACKEND_CORS_ORIGINS`: Allowed origins (default: ["*"])

### URLs (Auto-configured)
- `REPL_SLUG`: Your Repl name (auto-set by Replit)
- `REPL_OWNER`: Your username (auto-set by Replit)
- `FRONTEND_URL`: Frontend URL (auto-generated)
- `BACKEND_URL`: Backend URL (auto-generated)

### Email (Optional)
- `RESEND_API_KEY`: Resend API key for emails
- `FROM_EMAIL`: Sender email address

### OAuth (Optional)
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth secret
- `GITHUB_CLIENT_ID`: GitHub OAuth client ID
- `GITHUB_CLIENT_SECRET`: GitHub OAuth secret

## Troubleshooting

### Database Connection Issues

If you see database connection errors:
1. Ensure PostgreSQL is enabled in Tools → Database
2. Check that `REPLIT_DB_URL` is set in environment
3. Restart the Repl

### Port Already in Use

If ports are in use:
1. Stop the Repl
2. Clear processes: Open Shell and run `pkill -f python`
3. Start the Repl again

### Module Not Found Errors

If you see import errors:
1. Open Shell
2. Run: `pip install -r requirements.txt`
3. Restart the Repl

### Frontend Not Loading

If the frontend doesn't load:
1. Check that server.py is running
2. Verify port 5000 is configured in .replit
3. Open the webview at the Repl URL

## API Documentation

Once running, access API documentation at:
- Swagger UI: `https://[your-repl-url]/docs`
- ReDoc: `https://[your-repl-url]/redoc`

## Local Development vs Replit

### On Replit
- Database: Replit PostgreSQL (managed)
- URLs: Auto-configured
- Secrets: Use Replit Secrets
- Deployment: One-click deploy

### Local Development
- Database: Local PostgreSQL
- URLs: localhost:3000, localhost:8000
- Secrets: .env file
- Deployment: Manual setup

## Support

For issues or questions:
1. Check the documentation files in the repository
2. Review the API documentation at /docs
3. Open an issue on GitHub

## Security Notes

**Important for Production:**

1. Change `SECRET_KEY` to a strong random value
2. Restrict `BACKEND_CORS_ORIGINS` to your actual domains
3. Use Replit Secrets for all sensitive data
4. Enable HTTPS (automatic on Replit deployments)
5. Set up proper OAuth redirect URLs for production domain
6. Use environment-specific email configuration
7. Enable rate limiting for API endpoints (configure in backend)

## Next Steps

1. ✅ Enable PostgreSQL database
2. ✅ Run the application
3. ⏭️ Configure optional features (OAuth, email)
4. ⏭️ Customize branding and content
5. ⏭️ Deploy to production
6. ⏭️ Set up custom domain
