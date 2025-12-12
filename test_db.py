#!/usr/bin/env python3
"""
Simple PostgreSQL connection test for Replit
Uses PG* environment variables only
"""
import os
import sys

print("=" * 60)
print("REPLIT POSTGRESQL CONNECTION TEST")
print("=" * 60)

# Check PG* variables
print("\nChecking PG* environment variables:")
print("-" * 60)

pg_vars = {
    "PGHOST": os.getenv("PGHOST", "NOT SET"),
    "PGDATABASE": os.getenv("PGDATABASE", "NOT SET"),
    "PGUSER": os.getenv("PGUSER", "NOT SET"),
    "PGPASSWORD": "***SET***" if os.getenv("PGPASSWORD") else "NOT SET",
    "PGPORT": os.getenv("PGPORT", "5432"),
}

all_set = True
for key, value in pg_vars.items():
    if value == "NOT SET" and key != "PGPASSWORD":  # PGPASSWORD is optional
        status = "✗"
        all_set = False
    else:
        status = "✓"
    print(f"{status} {key:15} = {value}")

if not all_set:
    print("\n✗ Missing required PG* variables!")
    print("\nFIX: Check your .replit file has these lines in [env] section:")
    print('  PGHOST = "db"')
    print('  PGDATABASE = "replit"')
    print('  PGUSER = "replit"')
    print('  PGPORT = "5432"')
    sys.exit(1)

# Try to connect
print("\nTesting database connection...")
print("-" * 60)

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    from app.db.database import get_database_url, initialize_database
    from sqlalchemy import text
    
    url = get_database_url()
    print(f"✓ Connection URL: postgresql://{pg_vars['PGUSER']}@{pg_vars['PGHOST']}:{pg_vars['PGPORT']}/{pg_vars['PGDATABASE']}")
    
    engine = initialize_database()
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✓ Connected successfully!")
        print(f"✓ PostgreSQL version: {version.split(',')[0]}")
        
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - Database is ready!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Initialize database: cd backend && python init_db.py")
    print("2. Start server: python server.py")
    
except Exception as e:
    print(f"\n✗ CONNECTION FAILED!")
    print(f"Error: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Make sure 'postgresql-16' is in modules list in .replit")
    print("2. Restart your Repl to ensure PostgreSQL service starts")
    print("3. Check Replit console for PostgreSQL service errors")
    sys.exit(1)
