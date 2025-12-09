#!/usr/bin/env python3
"""
Friction - Supabase Setup Script
Interactive setup for connecting to Supabase database
"""

import os
import secrets
import re
from pathlib import Path
from getpass import getpass


def main():
    print("🚀 Friction Backend - Supabase Setup")
    print("=" * 50)
    print()

    backend_dir = Path(__file__).parent / "backend"
    env_file = backend_dir / ".env"

    # Check if .env exists
    if env_file.exists():
        print("⚠️  backend/.env already exists!")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower()
        if overwrite != 'y':
            print("Aborting. Please update backend/.env manually.")
            return

    print("📝 Please enter your Supabase credentials:")
    print()
    print("You can find these in your Supabase Dashboard:")
    print("  • Project Settings → Database → Connection string")
    print("  • Project Settings → API")
    print()

    # Get Supabase URL
    supabase_url = input("Supabase Project URL (e.g., https://xxxxx.supabase.co): ").strip()

    # Extract project reference from URL
    match = re.search(r'https://(.+?)\.supabase\.co', supabase_url)
    if match:
        project_ref = match.group(1)
    else:
        print("⚠️  Invalid Supabase URL format")
        project_ref = input("Project Reference ID (the 'xxxxx' part): ").strip()

    # Get Database Password
    db_password = getpass("Database Password: ")

    # Get API Keys
    anon_key = input("Anon/Public Key: ").strip()
    service_key = getpass("Service Role Key (keep secret!): ")

    # Generate SECRET_KEY
    print()
    print("🔐 Generating new SECRET_KEY...")
    secret_key = secrets.token_hex(32)

    # Build DATABASE_URL
    database_url = f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"

    # Create .env content
    env_content = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_ANON_KEY={anon_key}
SUPABASE_SERVICE_ROLE_KEY={service_key}

# Database - Supabase Connection String
DATABASE_URL={database_url}

# Security
SECRET_KEY={secret_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=Friction API

# CORS - Update with your frontend URLs
BACKEND_CORS_ORIGINS=["http://localhost:8000","http://localhost:3000","http://127.0.0.1:8000","http://localhost:5500"]
"""

    # Write to file
    env_file.write_text(env_content)

    print()
    print("✅ Configuration saved to backend/.env")
    print()
    print("📦 Next steps:")
    print()
    print("1. Install Python dependencies:")
    print("   cd backend")
    print("   pip install -r requirements.txt")
    print()
    print("2. Initialize the database:")
    print("   python init_db.py")
    print()
    print("3. Start the backend:")
    print("   uvicorn app.main:app --reload")
    print()
    print("   Or with Docker:")
    print("   docker compose up backend")
    print()
    print("4. Visit: http://localhost:8000/docs")
    print()
    print("🎉 Setup complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
