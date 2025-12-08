# Friction Backend API

FastAPI backend for the Friction problem discovery platform. Provides REST API endpoints for scrapers to submit opportunities and for the frontend to query data.

## Features

- 🔐 JWT-based authentication
- 📊 REST API with automatic OpenAPI docs
- 🗄️ PostgreSQL database with SQLAlchemy ORM
- 🤖 Dedicated scraper endpoints with API key auth
- ✅ Data validation with Pydantic schemas
- 🚀 Fast and async-ready with FastAPI

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and configure your database and secret key:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/friction_db
SECRET_KEY=your-secret-key-here
```

### 3. Initialize Database

```bash
python init_db.py
```

This creates:
- Database tables
- Sample categories
- Test user (email: test@example.com, password: password123)

### 4. Run the Server

```bash
uvicorn main:app --reload
```

Server will start at `http://localhost:8000`

## API Documentation

Once running, view the interactive API docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Scraper Endpoints (API Key Required)

**POST /api/scraper/opportunities**
Submit a single opportunity
```json
{
  "title": "Need better email analytics",
  "description": "I wish my email provider had better analytics...",
  "source": "reddit",
  "source_url": "https://reddit.com/r/saas/comments/...",
  "source_id": "abc123",
  "author": "username",
  "category_slug": "saas-business"
}
```

**POST /api/scraper/opportunities/bulk**
Submit multiple opportunities at once

**Headers Required:**
```
X-API-Key: your-scraper-api-key-change-in-production
```

### Authentication

**POST /api/auth/signup**
Register a new user

**POST /api/auth/login**
Login and get access token

### Opportunities

**GET /api/opportunities**
Get paginated opportunities with filters
- Query params: `skip`, `limit`, `category_id`, `source`, `status`, `sort_by`

**GET /api/opportunities/{id}**
Get specific opportunity

**GET /api/opportunities/trending**
Get trending opportunities

**PATCH /api/opportunities/{id}**
Update opportunity (admin)

**DELETE /api/opportunities/{id}**
Delete opportunity (admin)

### Validations

**POST /api/validations**
Create a validation (agree/disagree with opportunity)

**GET /api/validations/opportunity/{id}**
Get all validations for an opportunity

### Categories

**GET /api/categories**
Get all categories

**GET /api/categories/{id}**
Get category by ID

**GET /api/categories/slug/{slug}**
Get category by slug

**POST /api/categories**
Create new category (admin)

## Database Models

### Opportunity
- Core entity representing a discovered problem/pain point
- Fields: title, description, source, author, metrics, status
- Sources: reddit, twitter, linkedin, github, hackernews, producthunt

### User
- User accounts for authentication
- Can validate opportunities (agree/disagree)

### Validation
- User validation of an opportunity
- Tracks agree/disagree votes and comments

### Category
- Categorization of opportunities
- Includes slug, icon, and color for frontend display

## Scraper Integration

Your scrapers should:

1. Make POST requests to `/api/scraper/opportunities` or `/api/scraper/opportunities/bulk`
2. Include API key in `X-API-Key` header
3. Provide required fields: title, description, source, source_url
4. Optionally include: source_id, author, author_url, category_slug

Example Python scraper code:

```python
import requests

BACKEND_URL = "http://localhost:8000"
API_KEY = "your-scraper-api-key-change-in-production"

headers = {"X-API-Key": API_KEY}

opportunity = {
    "title": "Need better analytics",
    "description": "I wish there was better analytics for...",
    "source": "reddit",
    "source_url": "https://reddit.com/...",
    "source_id": "abc123",
    "category_slug": "saas-business"
}

response = requests.post(
    f"{BACKEND_URL}/api/scraper/opportunities",
    json=opportunity,
    headers=headers
)

print(response.json())
```

## Development

### Project Structure

```
backend/
├── app/
│   ├── core/           # Config, database, security
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── routes/         # API endpoints
│   └── services/       # Business logic
├── main.py            # FastAPI app
├── init_db.py         # Database initialization
└── requirements.txt   # Dependencies
```

### Adding New Endpoints

1. Create route in `app/routes/`
2. Define schemas in `app/schemas/`
3. Add models if needed in `app/models/`
4. Include router in `main.py`

## Security Notes

⚠️ **Before production:**
- Change SECRET_KEY in `.env`
- Change SCRAPER_API_KEY in `app/routes/scraper.py`
- Configure CORS allowed origins
- Use HTTPS
- Set up proper database backups
- Implement rate limiting
- Add logging and monitoring

## License

MIT
