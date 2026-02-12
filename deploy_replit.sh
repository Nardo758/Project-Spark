#!/bin/bash
# 🚀 OppGrid Replit Deployment Script
# This script prepares the project for Replit deployment

echo "🚀 Preparing OppGrid for Replit deployment..."

# Set up Python environment
echo "📦 Setting up Python environment..."
python3 -m pip install --user -r backend/requirements.txt

# Set up frontend
echo "📦 Setting up frontend..."
cd frontend
npm install
npm run build
cd ..

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p temp

# Set permissions
echo "🔐 Setting permissions..."
chmod +x server.py
chmod +x backend/app/main.py

# Create deployment log
echo "📝 Creating deployment log..."
echo "Deployment completed at: $(date)" > deployment.log
echo "Python version: $(python3 --version)" >> deployment.log
echo "Node version: $(node --version)" >> deployment.log
echo "NPM version: $(npm --version)" >> deployment.log

echo "✅ Replit deployment preparation complete!"
echo "🎯 Ready to run: python server.py"