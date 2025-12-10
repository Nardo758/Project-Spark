# CORS Configuration Guide for Production

## Problem
Your frontend (hosted on basekite.com, Netlify, or other hosting services) cannot communicate with your Render backend due to CORS (Cross-Origin Resource Sharing) restrictions. The browser blocks requests from your frontend domain because the backend doesn't list it as an allowed origin.

## Quick Fix - Update Render Environment Variables

### Step 1: Identify Your Frontend URL

Your frontend URL could be:
- **basekite.com**: `https://basekite.com` and `https://www.basekite.com`
- **Netlify**: `https://your-app-name.netlify.app`
- **Custom domain**: `https://your-custom-domain.com`

Make sure to include both the www and non-www versions if applicable.

### Step 2: Update CORS in Render

1. **Go to Render Dashboard:**
   - Navigate to https://dashboard.render.com
   - Select your `friction-api` service

2. **Update Environment Variables:**
   - Click "Environment" tab
   - Find or add `BACKEND_CORS_ORIGINS`
   - Set the value to (replace with your actual domains):

   **For basekite.com:**
   ```json
   ["https://basekite.com","https://www.basekite.com","https://project-spark.onrender.com","http://localhost:3000"]
   ```

   **For Netlify:**
   ```json
   ["https://your-app.netlify.app","https://project-spark.onrender.com","http://localhost:3000"]
   ```

   **Important:**
   - Use the exact format with square brackets and quotes
   - Include both www and non-www versions if your site uses both
   - Include your frontend URL (starts with https://)
   - Include your Render backend URL
   - Include localhost for local development (optional)
   - No spaces after commas

3. **Example Values:**

   ```json
   ["https://basekite.com","https://www.basekite.com","https://project-spark.onrender.com","http://localhost:3000"]
   ```

   Or for Netlify:
   ```json
   ["https://friction-app.netlify.app","https://project-spark.onrender.com","http://localhost:3000"]
   ```

4. **Save Changes:**
   - Click "Save Changes"
   - Render will automatically redeploy your service

### Step 3: Wait for Deployment

- Watch the deployment logs in Render
- Wait for "Your service is live 🎉"
- Usually takes 2-3 minutes

### Step 4: Test Your Application

1. Clear your browser cache (or use incognito mode)
2. Go to your frontend application (e.g., https://basekite.com)
3. Try accessing the API endpoints (opportunities, authentication, etc.)
4. Check browser console (F12) - CORS errors should be gone!

## Verification Steps

### 1. Check Backend Health

Visit these URLs to verify backend is running:

```
https://project-spark.onrender.com/
https://project-spark.onrender.com/health
https://project-spark.onrender.com/docs
```

### 2. Test CORS Headers

Open browser console on your frontend application and run:

```javascript
// Test opportunities endpoint
fetch('https://project-spark.onrender.com/api/v1/opportunities/?limit=20&sort_by=recent')
.then(res => res.json())
.then(data => console.log('Success:', data))
.catch(err => console.error('Error:', err));

// Or test authentication endpoint
fetch('https://project-spark.onrender.com/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: 'username=demo@example.com&password=demo123'
})
.then(res => res.json())
.then(data => console.log('Success:', data))
.catch(err => console.error('Error:', err));
```

If CORS is configured correctly, you should see a response without CORS errors.

### 3. Check Browser Network Tab

1. Open Developer Tools (F12)
2. Go to Network tab
3. Try to log in
4. Look for the API request
5. Check Response Headers - should include:
   ```
   Access-Control-Allow-Origin: https://basekite.com
   Access-Control-Allow-Credentials: true
   ```
   (Replace basekite.com with your actual frontend domain)

## Common Issues & Solutions

### Issue 1: Still Getting CORS Errors

**Symptoms:**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solutions:**
1. Double-check the BACKEND_CORS_ORIGINS format (must be valid JSON)
2. Ensure your frontend URL is exactly correct (https, no trailing slash)
3. Include both www and non-www versions if your site uses both
4. Clear browser cache and try incognito mode
5. Check Render logs for any errors during startup
6. Verify the environment variable saved correctly in Render

### Issue 2: Wildcard Origin Not Working

**Problem:** Using `"*"` for BACKEND_CORS_ORIGINS doesn't work with credentials.

**Solution:** List specific domains explicitly:
```json
["https://basekite.com","https://www.basekite.com","https://project-spark.onrender.com"]
```

### Issue 3: Multiple Domains Not Working

**Problem:** Need to allow multiple frontend domains.

**Solution:** Add all domains to the array:
```json
["https://basekite.com","https://www.basekite.com","https://app.netlify.app","https://custom-domain.com"]
```

### Issue 4: Environment Variable Not Updating

**Problem:** Changes to environment variables don't seem to apply.

**Solution:**
1. Make sure you clicked "Save Changes" in Render
2. Wait for the automatic redeploy to complete
3. Check the deployment logs to confirm new settings loaded
4. Look for log message: "Database engine created successfully"

## Testing with cURL

Test CORS preflight from command line:

```bash
# Test OPTIONS request (CORS preflight) - replace with your frontend domain
curl -X OPTIONS \
  -H "Origin: https://basekite.com" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -i https://project-spark.onrender.com/api/v1/opportunities/

# Test actual GET request for opportunities
curl -X GET \
  -H "Origin: https://basekite.com" \
  https://project-spark.onrender.com/api/v1/opportunities/?limit=20&sort_by=recent

# Test actual login request
curl -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@example.com&password=demo123" \
  https://project-spark.onrender.com/api/v1/auth/login
```

## Environment Variables Summary

Here are all the critical environment variables you need in Render:

| Variable | Example Value | Required |
|----------|---------------|----------|
| `DATABASE_URL` | `postgres://postgres:password@db.xxx.supabase.co:6543/postgres?pgbouncer=true&sslmode=require` | ✅ Yes |
| `SECRET_KEY` | `your-super-secret-key-min-32-characters-long` | ✅ Yes |
| `BACKEND_CORS_ORIGINS` | `["https://basekite.com","https://www.basekite.com","https://project-spark.onrender.com"]` | ✅ Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | ❌ No (defaults to 30) |
| `ALGORITHM` | `HS256` | ❌ No (defaults to HS256) |
| `PROJECT_NAME` | `Friction API` | ❌ No (defaults to "Friction API") |

## Security Best Practices

1. **Never use `"*"` for CORS origins in production** - Always list specific domains
2. **Always use HTTPS** in production - Never allow HTTP origins for production
3. **Keep SECRET_KEY secure** - Generate a strong random key:
   ```bash
   openssl rand -hex 32
   ```
4. **Limit token expiry** - Set ACCESS_TOKEN_EXPIRE_MINUTES to 30-60 minutes
5. **Monitor CORS errors** - Set up logging to catch unauthorized access attempts

## Local Development

For local development, your CORS origins should include localhost:

```json
["http://localhost:3000","http://localhost:8000","http://127.0.0.1:3000"]
```

## Need Help?

If you're still experiencing issues:

1. Check Render deployment logs for errors
2. Check browser console for specific error messages
3. Verify all environment variables are set correctly
4. Try the verification steps above
5. Clear browser cache completely

## Additional Resources

- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)
