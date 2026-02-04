# Saved Searches - Quick Reference

**5-Minute Setup Guide**

---

## 🚀 Quick Start

### 1. Deploy (3 commands)

```bash
# 1. Run database migration
alembic upgrade head

# 2. Test the API
curl -X GET http://localhost:8000/api/v1/saved-searches/ \
  -H "Authorization: Bearer <your-token>"

# 3. Start background job (choose one):

# Option A: Test run
python -m app.services.saved_search_alerts

# Option B: Cron (production)
echo "0 * * * * /path/to/scripts/run_saved_search_alerts.sh" | crontab -
```

---

## 📡 API Endpoints

**Base:** `/api/v1/saved-searches`  
**Auth:** Bearer token required

```bash
# Create saved search
POST /saved-searches
{
  "name": "Tech Opportunities",
  "filters": {"category": "Tech", "min_feasibility": 75},
  "notification_prefs": {"email": true, "frequency": "daily"}
}

# List all
GET /saved-searches

# Delete
DELETE /saved-searches/{id}

# Get recommendations
GET /opportunities/recommended?limit=10
```

---

## 🎯 Tier Limits

| Tier | Saved Searches |
|------|----------------|
| Free | 1 |
| Pro  | 10 |
| Business+ | Unlimited |

---

## 🔔 Notification Channels

- ✅ **Email** - Fully implemented
- 🚧 **Push** - Placeholder (TODO: FCM)
- 🚧 **Slack** - Placeholder (TODO: OAuth)

---

## 📊 Match Score Algorithm

```
Base:               50
+ Category Match:   +20
+ High Feasibility: +15
+ Growth Trend:     +10
+ Similar Users:    +5
───────────────────────
Max:               100
```

---

## 🧪 Test

```bash
pytest tests/test_saved_searches.py -v
# Expected: 15 passed
```

---

## 📚 Full Docs

- `docs/SAVED_SEARCHES_IMPLEMENTATION.md` - Complete guide
- `SAVED_SEARCHES_SUMMARY.md` - Implementation summary
- `/docs` - API docs (Swagger UI)

---

## 🐛 Troubleshoot

**Alerts not sending?**
```bash
# Check job is running
ps aux | grep saved_search_alerts

# Check logs
tail -f logs/saved_search_alerts.log

# Test manually
python -c "from app.services.saved_search_alerts import run_saved_search_alerts; run_saved_search_alerts()"
```

**Tier limits not working?**
```sql
-- Check user subscription
SELECT * FROM user_subscriptions WHERE user_id = ?;
```

---

## ✅ Files Modified

- ✅ `app/models/saved_search.py` - Updated model
- ✅ `app/routers/saved_searches.py` - New CRUD endpoints
- ✅ `app/routers/opportunities.py` - Added /recommended
- ✅ `app/services/saved_search_alerts.py` - Background job
- ✅ `app/main.py` - Registered router
- ✅ `alembic/versions/20260203_...py` - Migration

---

**Ready to ship!** 🎉
