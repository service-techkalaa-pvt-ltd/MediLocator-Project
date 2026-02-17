# Replit Diagnostics Script (PowerShell)
# Run this to check for common issues on Windows

Write-Host "🔍 Replit Diagnostics - Medilocator Project" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check Python version
Write-Host "`n🐍 Python Version:" -ForegroundColor Yellow
python --version

# Check pip
Write-Host "`n📦 Pip Version:" -ForegroundColor Yellow
pip --version

# Check Django
Write-Host "`n🎯 Django Version:" -ForegroundColor Yellow
try {
    python -c "import django; print('Django', django.VERSION)"
    Write-Host "✅ Django OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Django not installed" -ForegroundColor Red
}

# Check key packages
Write-Host "`n📚 Key Packages:" -ForegroundColor Yellow
try {
    python -c "import pytesseract"
    Write-Host "✅ pytesseract OK" -ForegroundColor Green
} catch {
    Write-Host "❌ pytesseract missing" -ForegroundColor Red
}

try {
    python -c "import cv2"
    Write-Host "✅ opencv OK" -ForegroundColor Green
} catch {
    Write-Host "❌ opencv missing" -ForegroundColor Red
}

try {
    python -c "import numpy"
    Write-Host "✅ numpy OK" -ForegroundColor Green
} catch {
    Write-Host "❌ numpy missing" -ForegroundColor Red
}

try {
    python -c "from decouple import config"
    Write-Host "✅ python-decouple OK" -ForegroundColor Green
} catch {
    Write-Host "❌ python-decouple missing" -ForegroundColor Red
}

# Check Tesseract
Write-Host "`n🔤 Tesseract OCR:" -ForegroundColor Yellow
$tesseractPath = Get-Command tesseract -ErrorAction SilentlyContinue
if ($tesseractPath) {
    Write-Host "✅ Tesseract found at: $($tesseractPath.Source)" -ForegroundColor Green
    try {
        tesseract --version | Select-Object -First 1
    } catch {
        Write-Host "❌ Tesseract not working" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Tesseract not found" -ForegroundColor Red
}

# Check database
Write-Host "`n🗄️  Database:" -ForegroundColor Yellow
if (Test-Path "db.sqlite3") {
    Write-Host "✅ Database file exists" -ForegroundColor Green
} else {
    Write-Host "❌ Database file missing" -ForegroundColor Red
}

# Check static files
Write-Host "`n📁 Static Files:" -ForegroundColor Yellow
if (Test-Path "staticfiles") {
    Write-Host "✅ Static files directory exists" -ForegroundColor Green
} else {
    Write-Host "❌ Static files directory missing" -ForegroundColor Red
}

# Check media directory
Write-Host "`n🖼️  Media Directory:" -ForegroundColor Yellow
if (Test-Path "media") {
    Write-Host "✅ Media directory exists" -ForegroundColor Green
} else {
    Write-Host "❌ Media directory missing" -ForegroundColor Red
}

# Check environment variables
Write-Host "`n🔐 Environment Variables:" -ForegroundColor Yellow
if ($env:SECRET_KEY) {
    Write-Host "✅ SECRET_KEY set" -ForegroundColor Green
} else {
    Write-Host "❌ SECRET_KEY not set" -ForegroundColor Red
}

if ($env:DEBUG) {
    Write-Host "✅ DEBUG set to: $($env:DEBUG)" -ForegroundColor Green
} else {
    Write-Host "❌ DEBUG not set" -ForegroundColor Red
}

if ($env:ALLOWED_HOSTS) {
    Write-Host "✅ ALLOWED_HOSTS set to: $($env:ALLOWED_HOSTS)" -ForegroundColor Green
} else {
    Write-Host "❌ ALLOWED_HOSTS not set" -ForegroundColor Red
}

# Check .env file
Write-Host "`n📄 .env File:" -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "❌ .env file missing" -ForegroundColor Red
}

# Check requirements.txt
Write-Host "`n📋 Requirements:" -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    Write-Host "✅ requirements.txt exists" -ForegroundColor Green
} else {
    Write-Host "❌ requirements.txt missing" -ForegroundColor Red
}

# Check disk space (approximate)
Write-Host "`n💾 Disk Space:" -ForegroundColor Yellow
$drive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq $pwd.Path.Substring(0,3) }
if ($drive) {
    $freeGB = [math]::Round($drive.FreeSpace / 1GB, 2)
    $totalGB = [math]::Round($drive.Size / 1GB, 2)
    Write-Host "Free: ${freeGB}GB / Total: ${totalGB}GB"
} else {
    Write-Host "Disk info not available"
}

# Test Django check
Write-Host "`n✅ Django System Check:" -ForegroundColor Yellow
try {
    python manage.py check
    Write-Host "✅ Django check passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Django check failed" -ForegroundColor Red
}

Write-Host "`n📝 Diagnostics complete!" -ForegroundColor Cyan
Write-Host "If you see ❌ errors above, check REPLIT_MANUAL_FIXES.md for solutions." -ForegroundColor Yellow
