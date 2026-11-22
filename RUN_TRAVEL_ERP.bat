@echo off
chcp 65001 >nul
title شركة الحرمين للسياحة والسفر - نظام الإدارة والحسابات
color 0B

echo ======================================================================
echo    🕋  شركة الحرمين للسياحة والسفر - Al-Haramain Travel ERP
echo        نظام إدارة رحلات العمرة والحج، الطيران، والحسابات
echo ======================================================================
echo.
echo [1/3] جاري فحص بيئة التشغيل وقاعدة البيانات...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [خطأ] بايثون غير مثبت على هذا الجهاز! يرجى تثبيت Python 3.10+ أولاً.
    pause
    exit /b
)

echo [2/3] جاري تهيئة قاعدة البيانات المحلية (travel_erp.db)...
python -c "from app.database import init_db; from app.seed import seed_database; init_db(); seed_database()"

echo [3/3] جاري تشغيل السيرفر وفتح السيستم في المتصفح...
start http://localhost:5000

echo.
echo ======================================================================
echo  🚀 السيستم يعمل الآن على: http://localhost:5000
echo  📄 العرض الفني والمالي: http://localhost:5000/proposal.html
echo  (لا تغلق هذه النافذة طالما أنك تستخدم السيستم)
echo ======================================================================
echo.

python run_server.py
pause
