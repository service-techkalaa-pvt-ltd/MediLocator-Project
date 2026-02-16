#!/bin/bash

# Medilocator Startup Script for Replit
echo "🚀 Starting Medilocator Application..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Load initial data (optional)
# Uncomment if you want to load pharmacy data on startup
# echo "📊 Loading pharmacy data..."
# python load_pharmacy_data.py

# Create superuser if needed (optional)
# echo "👤 Creating superuser..."
# python manage.py createsuperuser --noinput

# Start the Django development server
echo "✅ Starting Django server on 0.0.0.0:3000..."
python manage.py runserver 0.0.0.0:3000
