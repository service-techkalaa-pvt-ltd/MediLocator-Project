#!/bin/bash

# Quick Setup Script for Replit
# This script initializes the database and creates necessary directories

echo "🔧 Medilocator Quick Setup for Replit"
echo "======================================"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p media/prescriptions
mkdir -p staticfiles
mkdir -p logs

# Install dependencies
echo "📦 Installing Python packages..."
pip install -r requirements.txt --quiet

# Run migrations
echo "🗄️  Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Optional: Load sample data
# echo "📊 Loading sample data..."
# python load_pharmacy_data.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Create a superuser: python manage.py createsuperuser"
echo "2. Load pharmacy data: python load_pharmacy_data.py (if applicable)"
echo "3. Click the Run button to start the server"
echo ""
echo "🌐 Your app will be available at the Replit-provided URL"
echo ""
