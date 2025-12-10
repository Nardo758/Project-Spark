# Render Database Connection Fix

## Issue
The deployment is failing with:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server at "aws-0-us-east-1.pooler.supabase.com" (52.45.94.125), port 6543 failed: FATAL:  Tenant or user not found
```

## Root Cause
This error occurs when the DATABASE_URL is incorrectly formatted for Supabase connection. There are two possible connection methods:

### 1. Direct Connection (Port 5432) - **RECOMMENDED**
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### 2. Pooler Connection (Port 6543)
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

**Note:** For pooler connections, the username MUST be `postgres.[PROJECT-REF]` (not just `postgres`)

## Solution

### Step 1: Get Your Correct DATABASE_URL from Supabase

1. Go to your Supabase project dashboard
2. Click on "Settings" → "Database"
3. Find the "Connection String" section
4. Copy the **Connection String** (use the direct connection, port 5432)
5. Make sure to replace `[YOUR-PASSWORD]` with your actual database password

Example:
```
postgresql://postgres:your_actual_password@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
```

### Step 2: Update DATABASE_URL in Render

1. Go to your Render dashboard
2. Navigate to your `friction-api` service
3. Go to "Environment" tab
4. Find the `DATABASE_URL` environment variable
5. Update it with the correct connection string from Step 1
6. Make sure to add `?sslmode=require` at the end:

```
postgresql://postgres:your_actual_password@db.xxxxxxxxxxxxx.supabase.co:5432/postgres?sslmode=require
```

### Step 3: Redeploy

1. Save the environment variable changes
2. Trigger a manual deploy or push a new commit
3. The deployment should now succeed

## Code Changes Made

The following files were updated to make the database connection more resilient:

1. **backend/app/db/database.py**: Added error handling and retry logic
2. **backend/app/main.py**: Moved table creation to startup event with graceful error handling
3. **backend/init_db.py**: Added connection retry logic with exponential backoff

These changes ensure that:
- The application can start even if the database is temporarily unavailable
- Database initialization is retried multiple times before giving up
- Better logging helps diagnose connection issues
- The app gracefully degrades if database is not available during build

## Verification

After deploying, you can verify the connection by checking:
1. The deployment logs should show: "Database connection successful!"
2. Visit your API health endpoint: `https://your-app.onrender.com/health`
3. It should return: `{"status": "healthy", "database": "connected"}`

## Important Notes

- Always use port **5432** (direct connection) for better reliability
- Always add `?sslmode=require` to the connection string
- Keep your database password secure and never commit it to git
- If you must use the pooler (port 6543), ensure username is `postgres.[PROJECT-REF]`
