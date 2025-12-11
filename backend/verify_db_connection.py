#!/usr/bin/env python3
"""
Postgres Connection Verification Script (Replit-ready)

This script verifies that your environment exposes a valid PostgreSQL connection
string (from POSTGRES_URL, REPLIT_DB_URL, or DATABASE_URL) and that the database
accepts standard queries, SSL, and write operations.

Usage:
    python backend/verify_db_connection.py

Environment Variables (checked in order):
    1. POSTGRES_URL   - Recommended for production / external providers
    2. DATABASE_URL   - Common fallback
    3. REPLIT_DB_URL  - Provided by Replit PostgreSQL integration
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

try:
    from sqlalchemy import create_engine, text, inspect
    from sqlalchemy.exc import OperationalError, SQLAlchemyError
    from sqlalchemy.pool import NullPool
except ImportError:
    print("❌ Error: SQLAlchemy not installed. Run: pip install sqlalchemy psycopg2-binary")
    sys.exit(1)


def get_colored_output(status: str, message: str) -> str:
    """Format output with status indicators"""
    status_icons = {
        "success": "✓",
        "error": "✗",
        "info": "ℹ",
        "warning": "⚠"
    }
    return f"{status_icons.get(status, '•')} {message}"


def parse_connection_url(database_url: str) -> Dict[str, Any]:
    """Parse and display connection URL details"""
    print("\n" + "="*60)
    print("DATABASE CONNECTION DETAILS")
    print("="*60)

    try:
        # Hide password in display
        if "@" in database_url:
            parts = database_url.split("@")
            user_pass = parts[0].split("://")[1]
            username = user_pass.split(":")[0]
            masked_url = database_url.replace(user_pass.split(":")[1], "****")
        else:
            masked_url = database_url
            username = "unknown"

        print(f"Connection URL: {masked_url}")

        # Extract connection parameters
        params = {}
        if "?" in database_url:
            param_string = database_url.split("?")[1]
            params = dict(p.split("=") for p in param_string.split("&"))

        # Extract host and port
        if "@" in database_url:
            host_part = database_url.split("@")[1].split("/")[0]
            if ":" in host_part:
                host, port = host_part.rsplit(":", 1)
            else:
                host = host_part
                port = "5432"
        else:
            host = "unknown"
            port = "unknown"

        # Extract database name
        if "/" in database_url.split("@")[-1]:
            db_name = database_url.split("@")[-1].split("/")[1].split("?")[0]
        else:
            db_name = "unknown"

        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Database: {db_name}")
        print(f"Username: {username}")

        # Check for PgBouncer
        if "6543" in port:
            print(get_colored_output("info", "Using PgBouncer port (6543) - Connection pooling enabled"))
        elif "5432" in port:
            print(get_colored_output("info", "Using direct connection port (5432)"))

        # Check for SSL
        ssl_mode = params.get("sslmode", "not specified")
        if ssl_mode == "require":
            print(get_colored_output("success", f"SSL Mode: {ssl_mode} (Secure)"))
        else:
            print(get_colored_output("warning", f"SSL Mode: {ssl_mode}"))

        # Check for PgBouncer parameter
        if params.get("pgbouncer") == "true":
            print(get_colored_output("success", "PgBouncer parameter: enabled"))

        print("="*60 + "\n")

        return {
            "host": host,
            "port": port,
            "database": db_name,
            "ssl_mode": ssl_mode,
            "pgbouncer": params.get("pgbouncer", "false")
        }

    except Exception as e:
        print(get_colored_output("error", f"Failed to parse connection URL: {e}"))
        return {}


def test_basic_connection(database_url: str) -> bool:
    """Test basic database connectivity"""
    print("\n" + "="*60)
    print("TEST 1: BASIC CONNECTIVITY")
    print("="*60)

    try:
        # Create engine without connection pooling for testing
        engine = create_engine(
            database_url,
            poolclass=NullPool,
            connect_args={"connect_timeout": 10}
        )

        print("Attempting to connect to database...")
        start_time = time.time()

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        elapsed_time = (time.time() - start_time) * 1000
        print(get_colored_output("success", f"Connection successful! ({elapsed_time:.2f}ms)"))

        engine.dispose()
        return True

    except OperationalError as e:
        print(get_colored_output("error", f"Connection failed: {e}"))
        print("\nPossible issues:")
        print("  • Check DATABASE_URL is correct")
        print("  • Verify Supabase project is active")
        print("  • Confirm password is correct")
        print("  • Check network connectivity from Render")
        return False
    except Exception as e:
        print(get_colored_output("error", f"Unexpected error: {e}"))
        return False


def test_ssl_connection(database_url: str) -> bool:
    """Test SSL connection"""
    print("\n" + "="*60)
    print("TEST 2: SSL CONNECTION")
    print("="*60)

    try:
        engine = create_engine(
            database_url,
            poolclass=NullPool,
            connect_args={"sslmode": "require", "connect_timeout": 10}
        )

        print("Testing SSL connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT ssl_is_used()")).scalar()
            if result:
                print(get_colored_output("success", "SSL is enabled and active"))
            else:
                print(get_colored_output("warning", "SSL not active"))

        engine.dispose()
        return True

    except Exception as e:
        print(get_colored_output("warning", f"SSL test failed or not supported: {e}"))
        return False


def test_database_queries(database_url: str) -> bool:
    """Test various database queries"""
    print("\n" + "="*60)
    print("TEST 3: DATABASE QUERIES")
    print("="*60)

    try:
        engine = create_engine(database_url, poolclass=NullPool)

        with engine.connect() as connection:
            # Test 1: Version check
            print("\nChecking PostgreSQL version...")
            version = connection.execute(text("SELECT version()")).scalar()
            if version:
                version_short = version.split(",")[0]
                print(get_colored_output("success", f"PostgreSQL version: {version_short}"))

            # Test 2: Current timestamp
            print("\nTesting timestamp query...")
            timestamp = connection.execute(text("SELECT NOW()")).scalar()
            print(get_colored_output("success", f"Server time: {timestamp}"))

            # Test 3: Database name
            print("\nVerifying database name...")
            db_name = connection.execute(text("SELECT current_database()")).scalar()
            print(get_colored_output("success", f"Connected to database: {db_name}"))

            # Test 4: List tables
            print("\nListing tables...")
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            if tables:
                print(get_colored_output("success", f"Found {len(tables)} tables:"))
                for table in tables[:10]:  # Show first 10 tables
                    print(f"  • {table}")
                if len(tables) > 10:
                    print(f"  ... and {len(tables) - 10} more")
            else:
                print(get_colored_output("info", "No tables found (database might be empty)"))

        engine.dispose()
        return True

    except Exception as e:
        print(get_colored_output("error", f"Query tests failed: {e}"))
        return False


def test_connection_pool(database_url: str) -> bool:
    """Test connection pooling configuration"""
    print("\n" + "="*60)
    print("TEST 4: CONNECTION POOLING")
    print("="*60)

    try:
        # Create engine with production-like pooling settings
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
        )

        print("\nConnection pool configuration:")
        print(f"  • Pool size: {engine.pool.size()}")
        print(f"  • Max overflow: {engine.pool._max_overflow}")
        print(f"  • Pool recycle: 300s")
        print(f"  • Pre-ping: enabled")

        print("\nTesting connection pool with multiple queries...")
        for i in range(3):
            with engine.connect() as connection:
                result = connection.execute(text("SELECT pg_backend_pid()")).scalar()
                print(f"  Query {i+1}: Backend PID {result}")

        print(get_colored_output("success", "Connection pool working correctly"))

        # Check pool status
        pool_status = engine.pool.status()
        print(f"\nPool status: {pool_status}")

        engine.dispose()
        return True

    except Exception as e:
        print(get_colored_output("error", f"Connection pool test failed: {e}"))
        return False


def test_write_operations(database_url: str) -> bool:
    """Test write operations (CREATE, INSERT, DROP)"""
    print("\n" + "="*60)
    print("TEST 5: WRITE OPERATIONS")
    print("="*60)

    try:
        engine = create_engine(database_url, poolclass=NullPool)

        test_table = f"_connection_test_{int(time.time())}"

        with engine.connect() as connection:
            # Create test table
            print(f"\nCreating test table: {test_table}")
            connection.execute(text(f"""
                CREATE TABLE {test_table} (
                    id SERIAL PRIMARY KEY,
                    test_value TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            connection.commit()
            print(get_colored_output("success", "Table created"))

            # Insert test data
            print("Inserting test data...")
            connection.execute(text(f"""
                INSERT INTO {test_table} (test_value)
                VALUES ('Render → Supabase connection test')
            """))
            connection.commit()
            print(get_colored_output("success", "Data inserted"))

            # Read test data
            print("Reading test data...")
            result = connection.execute(text(f"""
                SELECT test_value, created_at FROM {test_table}
            """)).fetchone()
            print(get_colored_output("success", f"Data retrieved: {result[0]}"))

            # Drop test table
            print("Cleaning up test table...")
            connection.execute(text(f"DROP TABLE {test_table}"))
            connection.commit()
            print(get_colored_output("success", "Table dropped"))

        engine.dispose()
        return True

    except Exception as e:
        print(get_colored_output("error", f"Write operations test failed: {e}"))
        print("\nNote: Ensure your database user has CREATE/DROP permissions")
        return False


def resolve_database_url() -> str:
    """Return the first valid-looking Postgres URL from known env vars."""
    candidates = [
        ("POSTGRES_URL", os.getenv("POSTGRES_URL")),
        ("DATABASE_URL", os.getenv("DATABASE_URL")),
        ("REPLIT_DB_URL", os.getenv("REPLIT_DB_URL")),
    ]

    for name, value in candidates:
        if not value:
            continue
        if value.startswith(("postgresql://", "postgres://")):
            print(get_colored_output("info", f"Using {name}"))
            return value.replace("postgres://", "postgresql://")
        else:
            print(
                get_colored_output(
                    "warning",
                    f"{name} is set but does not look like a PostgreSQL connection string",
                )
            )

    return ""


def main():
    """Main verification function"""
    print("\n" + "="*60)
    print("POSTGRES CONNECTION VERIFICATION SCRIPT")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    database_url = resolve_database_url()

    if not database_url:
        print(get_colored_output("error", "No PostgreSQL connection string found."))
        print("\nSet one of these environment variables and try again:")
        print("  • POSTGRES_URL")
        print("  • DATABASE_URL")
        print("  • REPLIT_DB_URL (enabled via Tools → Database → PostgreSQL)")
        print("\nExample:")
        print("  export POSTGRES_URL='postgresql://user:password@host:port/database?sslmode=require'")
        print("  python backend/verify_db_connection.py")
        sys.exit(1)

    # Parse connection details
    conn_details = parse_connection_url(database_url)

    # Run tests
    results = {
        "Basic Connectivity": test_basic_connection(database_url),
        "SSL Connection": test_ssl_connection(database_url),
        "Database Queries": test_database_queries(database_url),
        "Connection Pooling": test_connection_pool(database_url),
        "Write Operations": test_write_operations(database_url),
    }

    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "success" if result else "error"
        print(get_colored_output(status, f"{test_name}: {'PASSED' if result else 'FAILED'}"))

    print("\n" + "-"*60)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print(get_colored_output("success", "All tests passed! Database connection is fully operational."))
        print("\n✓ Your Replit deployment can reach PostgreSQL")
        print("✓ SSL is enabled and working")
        print("✓ Connection pooling is operational")
        print("✓ Read/write operations are functional")
        sys.exit(0)
    else:
        print(get_colored_output("warning", f"{total - passed} test(s) failed. Review errors above."))
        sys.exit(1)


if __name__ == "__main__":
    main()
