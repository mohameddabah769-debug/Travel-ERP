@echo off
chcp 65001 >nul 2>&1
title Al-Haramain Travel ERP - شركة الحرمين للسياحة والسفر
color 0B

echo ======================================================================
echo    Al-Haramain Travel ERP - Al-Haramain Travel and Tourism
echo    Powered by Sanad Digital Solutions
echo ======================================================================
echo.
echo [1/3] Checking environment and database...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+
    pause
    exit /b
)

echo [2/3] Initializing local database (travel_erp.db)...
python -c "from app.database import init_db; from app.seed import seed_database; init_db(); seed_database()" >nul 2>&1

echo [3/3] Opening Al-Haramain ERP in your default browser...
start http://localhost:5000

echo.
echo ======================================================================
echo  Server is LIVE at: http://localhost:5000
echo  Local Network URL: http://127.0.0.1:5000
echo  Proposal URL:      http://localhost:5000/proposal.html
echo ======================================================================
echo.

python run_server.py
pause
