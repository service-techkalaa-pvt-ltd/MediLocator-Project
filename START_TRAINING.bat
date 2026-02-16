@echo off
echo ============================================================
echo PRESCRIPTION DETECTION MODEL - TRAINING
echo ============================================================
echo.

cd /d "%~dp0ml_models"

echo Checking requirements...
python -c "import ultralytics, torch" 2>nul
if errorlevel 1 (
    echo.
    echo Installing required packages...
    pip install ultralytics torch torchvision
    echo.
)

echo.
echo Starting training...
echo.
python train_complete.py

echo.
echo ============================================================
echo.
pause
