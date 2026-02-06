# 🚀 OppGrid Replit Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ Backend Setup
- [ ] Python dependencies installed via Replit packages
- [ ] Database configured (Replit PostgreSQL)
- [ ] Environment variables set in Replit Secrets
- [ ] Backend server starting on port 8000

### ✅ Frontend Setup  
- [ ] Node.js dependencies installed
- [ ] Build process working
- [ ] Frontend serving on correct port

### ✅ Integration
- [ ] CORS configured for Replit domains
- [ ] API endpoints responding
- [ ] Frontend-backend connectivity verified

---

## 🔧 Replit-Specific Configuration

### Environment Variables (Set in Replit Secrets)
```bash
# Database (Replit PostgreSQL)
DATABASE_URL=postgresql://replit:password@db:5432/replit

# AI Service Keys (Add your actual keys)
AI_INTEGRATIONS_ANTHROPIC_API_KEY=your-anthropic-key
DEEPSEEK_API_KEY=your-deepseek-key
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key

# Stripe (Add your actual keys)
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-webhook-secret

# Email Service
RESEND_API_KEY=your-resend-key

# Security
SECRET_KEY=your-secret-key-here
```

### Port Configuration
```
Backend API: 8000 (external: 8000)
Frontend Dev: 5000 (external: 80)
Database: 5432 (external: 3000)
```

---

## 🚀 Deployment Steps

### Step 1: Backend Deployment
1. **Install Python Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Test database connection
   python -c "from app.db.database import engine; print('DB Connected')"
   ```

3. **Start Backend Server**
   ```bash
   cd backend
   PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Step 2: Frontend Deployment
1. **Install Node Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Build Frontend**
   ```bash
   npm run build
   ```

3. **Start Dev Server**
   ```bash
   npm run dev -- --port 5000 --host 0.0.0.0
   ```

### Step 3: Integration Testing
Use the integration test suite:
```bash
# Open in browser
python -m http.server 8080
# Navigate to http://localhost:8080/integration_test.html
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -tlnp | grep :8000

# Kill process if needed
pkill -f "uvicorn"
```

#### 2. Database Connection Failed
```bash
# Test database connection
python -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://replit:password@db:5432/replit')
    print('✅ Database connected')
    conn.close()
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

#### 3. CORS Issues
```bash
# Check CORS configuration in .env
BACKEND_CORS_ORIGINS='["*"]'  # For development
```

#### 4. Frontend Build Errors
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 🧪 Testing Checklist

### Backend Tests
```bash
# Test API endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/opportunities
curl http://localhost:8000/api/agents

# Test database
python backend/test_db.py
```

### Frontend Tests
```bash
# Test build
cd frontend && npm run build

# Test dev server
curl http://localhost:5000
```

### Integration Tests
```bash
# Run comprehensive test
python test_comprehensive.py

# Open integration test page
python -m http.server 8080
# Open http://localhost:8080/integration_test.html
```

---

## 📊 Performance Monitoring

### Backend Metrics
- Response time: < 200ms for API calls
- Database queries: < 100ms
- Memory usage: Monitor via Replit dashboard

### Frontend Metrics  
- Build time: < 30 seconds
- Bundle size: < 2MB
- Load time: < 3 seconds

---

## 🚨 Production Considerations

### Security
- [ ] Change default SECRET_KEY
- [ ] Set up proper CORS origins
- [ ] Configure rate limiting
- [ ] Enable HTTPS (Replit handles this)

### Performance
- [ ] Enable database connection pooling
- [ ] Set up Redis for caching (optional)
- [ ] Optimize frontend bundle size
- [ ] Configure proper logging

### Monitoring
- [ ] Set up error tracking
- [ ] Monitor API usage
- [ ] Track performance metrics
- [ ] Set up alerts for downtime

---

## 📞 Support

If you encounter issues:

1. **Check Replit Console** for error messages
2. **Review Environment Variables** in Secrets
3. **Check Port Configurations** match .replit settings
4. **Test Individual Components** using provided scripts
5. **Review Logs** in Replit console

**🚀 Ready for Replit deployment!**