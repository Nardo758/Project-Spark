#!/usr/bin/env python3
"""
Database Connection Diagnostic Script
Run this on Replit to check database configuration
"""
import os
import sys

print("=" * 60)
print("DATABASE CONNECTION DIAGNOSTIC")
print("=" * 60)

# Check environment variables
print("\n1. Checking Environment Variables:")
print("-" * 60)

env_vars = {
    "DATABASE_URL": os.getenv("DATABASE_URL", "NOT SET"),
    "POSTGRES_URL": os.getenv("POSTGRES_URL", "NOT SET"),
    "REPLIT_DB_URL": os.getenv("REPLIT_DB_URL", "NOT SET"),
    "PGHOST": os.getenv("PGHOST", "NOT SET"),
    "PGDATABASE": os.getenv("PGDATABASE", "NOT SET"),
    "PGUSER": os.getenv("PGUSER", "NOT SET"),
    "PGPASSWORD": os.getenv("PGPASSWORD", "***" if os.getenv("PGPASSWORD") else "NOT SET"),
    "PGPORT": os.getenv("PGPORT", "NOT SET"),
}

for key, value in env_vars.items():
    status = "✓" if value != "NOT SET" else "✗"
    # Mask passwords in output
    display_value = value if key != "PGPASSWORD" else ("***SET***" if value != "NOT SET" else "NOT SET")
    print(f"{status} {key:20} = {display_value}")

# Check which URL will be used
print("\n2. Database URL Priority Check:")
print("-" * 60)

postgres_url = os.getenv("POSTGRES_URL", "")
database_url = os.getenv("DATABASE_URL", "")
pg_host = os.getenv("PGHOST")
pg_db = os.getenv("PGDATABASE")
pg_user = os.getenv("PGUSER")
pg_password = os.getenv("PGPASSWORD")

if postgres_url.startswith(("postgresql://", "postgres://")):
    print("✓ Will use: POSTGRES_URL")
    print(f"  URL: {postgres_url.split('@')[-1]}")  # Hide credentials
elif database_url.startswith(("postgresql://", "postgres://")):
    print("✓ Will use: DATABASE_URL")
    print(f"  URL: {database_url.split('@')[-1]}")  # Hide credentials
elif pg_host and pg_db and pg_user and pg_password:
    print("✓ Will use: PG* variables")
    print(f"  Host: {pg_host}")
    print(f"  Database: {pg_db}")
    print(f"  User: {pg_user}")
else:
    print("✗ NO VALID DATABASE CONFIGURATION FOUND!")
    print("\nRECOMMENDED ACTIONS:")
    print("1. Go to Replit Tools → Database")
    print("2. Enable PostgreSQL (not just KV store)")
    print("3. Replit will automatically set PG* variables")
    print("4. Restart your Repl")
    sys.exit(1)

# Try to connect
print("\n3. Testing Database Connection:")
print("-" * 60)

try:
    # Import after env check
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    from app.db.database import get_database_url, initialize_database
    
    url = get_database_url()
    print(f"✓ Database URL constructed: {url.split('@')[-1]}")
    
    print("\nAttempting to connect...")
    engine = initialize_database()
    
    # Test query
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        if row and row[0] == 1:
            print("✓ DATABASE CONNECTION SUCCESSFUL!")
            print("\n" + "=" * 60)
            print("✓ All checks passed! Your database is ready.")
            print("=" * 60)
        else:
            print("✗ Query returned unexpected result")
            
except Exception as e:
    print(f"✗ CONNECTION FAILED: {str(e)}")
    print("\nERROR DETAILS:")
    print(str(e))
    print("\nRECOMMENDED ACTIONS:")
    print("1. Verify PostgreSQL is enabled in Replit Tools → Database")
    print("2. Check that PGHOST is NOT 'localhost' (should be db.internal or similar)")
    print("3. Restart your Repl after enabling PostgreSQL")
    print("4. Check Replit logs for more details")
    sys.exit(1)
