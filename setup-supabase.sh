#!/bin/bash

# Friction - Supabase Setup Script
# This script helps you set up the backend with Supabase

echo "🚀 Friction Backend - Supabase Setup"
echo "===================================="
echo ""

# Check if .env exists
if [ -f "backend/.env" ]; then
    echo "⚠️  backend/.env already exists!"
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborting. Please update backend/.env manually."
        exit 1
    fi
fi

# Copy template
cp backend/.env.supabase backend/.env

echo "📝 Please enter your Supabase credentials:"
echo ""

# Get Supabase URL
read -p "Supabase Project URL (e.g., https://xxxxx.supabase.co): " SUPABASE_URL

# Get Project Ref (extract from URL)
PROJECT_REF=$(echo $SUPABASE_URL | sed 's/https:\/\/\(.*\)\.supabase\.co/\1/')

# Get Database Password
read -sp "Database Password: " DB_PASSWORD
echo ""

# Get Anon Key
read -p "Anon/Public Key: " ANON_KEY

# Get Service Role Key
read -sp "Service Role Key (secret): " SERVICE_KEY
echo ""

# Generate new SECRET_KEY
echo ""
echo "🔐 Generating new SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)

# Build DATABASE_URL
DATABASE_URL="postgresql://postgres:${DB_PASSWORD}@db.${PROJECT_REF}.supabase.co:5432/postgres"

# Update .env file
cat > backend/.env << EOF
# Supabase Configuration
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_ANON_KEY=${ANON_KEY}
SUPABASE_SERVICE_ROLE_KEY=${SERVICE_KEY}

# Database - Supabase Connection String
DATABASE_URL=${DATABASE_URL}

# Security
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=Friction API

# CORS - Update with your frontend URLs
BACKEND_CORS_ORIGINS=["http://localhost:8000","http://localhost:3000","http://127.0.0.1:8000","http://localhost:5500"]
EOF

echo ""
echo "✅ Configuration saved to backend/.env"
echo ""
echo "📦 Next steps:"
echo ""
echo "1. Install Python dependencies:"
echo "   cd backend && pip install -r requirements.txt"
echo ""
echo "2. Initialize the database:"
echo "   python init_db.py"
echo ""
echo "3. Start the backend:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Visit: http://localhost:8000/docs"
echo ""
echo "🎉 Setup complete!"
