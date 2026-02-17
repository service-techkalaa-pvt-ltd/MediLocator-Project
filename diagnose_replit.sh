#!/bin/bash

# Replit Diagnostics Script
# Run this to check for common issues

echo "🔍 Replit Diagnostics - Medilocator Project"
echo "=========================================="

# Check Python version
echo "🐍 Python Version:"
python --version

# Check pip
echo -e "\n📦 Pip Version:"
pip --version

# Check Django
echo -e "\n🎯 Django Version:"
python -c "import django; print('Django', django.VERSION)" 2>/dev/null || echo "❌ Django not installed"

# Check key packages
echo -e "\n📚 Key Packages:"
python -c "import pytesseract; print('✅ pytesseract OK')" 2>/dev/null || echo "❌ pytesseract missing"
python -c "import cv2; print('✅ opencv OK')" 2>/dev/null || echo "❌ opencv missing"
python -c "import numpy; print('✅ numpy OK')" 2>/dev/null || echo "❌ numpy missing"
python -c "from decouple import config; print('✅ python-decouple OK')" 2>/dev/null || echo "❌ python-decouple missing"

# Check Tesseract
echo -e "\n🔤 Tesseract OCR:"
which tesseract >/dev/null 2>&1 && echo "✅ Tesseract found at: $(which tesseract)" || echo "❌ Tesseract not found"
tesseract --version 2>/dev/null | head -1 || echo "❌ Tesseract not working"

# Check database
echo -e "\n🗄️  Database:"
[ -f "db.sqlite3" ] && echo "✅ Database file exists" || echo "❌ Database file missing"

# Check static files
echo -e "\n📁 Static Files:"
[ -d "staticfiles" ] && echo "✅ Static files directory exists" || echo "❌ Static files directory missing"

# Check media directory
echo -e "\n🖼️  Media Directory:"
[ -d "media" ] && echo "✅ Media directory exists" || echo "❌ Media directory missing"

# Check environment variables
echo -e "\n🔐 Environment Variables:"
[ -n "$SECRET_KEY" ] && echo "✅ SECRET_KEY set" || echo "❌ SECRET_KEY not set"
[ -n "$DEBUG" ] && echo "✅ DEBUG set to: $DEBUG" || echo "❌ DEBUG not set"
[ -n "$ALLOWED_HOSTS" ] && echo "✅ ALLOWED_HOSTS set to: $ALLOWED_HOSTS" || echo "❌ ALLOWED_HOSTS not set"

# Check .env file
echo -e "\n📄 .env File:"
[ -f ".env" ] && echo "✅ .env file exists" || echo "❌ .env file missing"

# Check requirements.txt
echo -e "\n📋 Requirements:"
[ -f "requirements.txt" ] && echo "✅ requirements.txt exists" || echo "❌ requirements.txt missing"

# Check disk space
echo -e "\n💾 Disk Space:"
df -h . | tail -1

# Check memory
echo -e "\n🧠 Memory:"
free -h | grep "^Mem:" || echo "Memory info not available"

# Test Django check
echo -e "\n✅ Django System Check:"
python manage.py check 2>/dev/null && echo "✅ Django check passed" || echo "❌ Django check failed"

echo -e "\n📝 Diagnostics complete!"
echo "If you see ❌ errors above, check REPLIT_MANUAL_FIXES.md for solutions."
