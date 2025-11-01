# PowerShell Setup Script for Deep Learning Project
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  DEEP LEARNING PROJECT SETUP" -ForegroundColor Cyan
Write-Host "  Retail Inventory Management - Invoice Forecasting" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install dependencies
Write-Host "[1/4] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 2: Train models
Write-Host "[2/4] Training models (this may take a few minutes)..." -ForegroundColor Yellow
python train_models.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to train models" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "✓ Models trained" -ForegroundColor Green
Write-Host ""

# Step 3: Verify installation
Write-Host "[3/4] Verifying installation..." -ForegroundColor Yellow
python verify_installation.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Some checks failed" -ForegroundColor Yellow
    Write-Host "Please review the output above" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Complete
Write-Host "[4/4] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ALL DONE! You can now run the application:" -ForegroundColor Green
Write-Host "  python app.py" -ForegroundColor White
Write-Host ""
Write-Host "  Then open: http://localhost:5000" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

pause
