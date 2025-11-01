@echo off
echo ============================================================
echo   DEEP LEARNING PROJECT SETUP
echo   Retail Inventory Management - Invoice Forecasting
echo ============================================================
echo.

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [2/4] Training models...
python train_models.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to train models
    pause
    exit /b 1
)
echo.

echo [3/4] Verifying installation...
python verify_installation.py
if %errorlevel% neq 0 (
    echo WARNING: Some checks failed
    echo Please review the output above
)
echo.

echo [4/4] Setup complete!
echo.
echo ============================================================
echo   ALL DONE! You can now run the application:
echo   python app.py
echo.
echo   Then open: http://localhost:5000
echo ============================================================
echo.
pause
