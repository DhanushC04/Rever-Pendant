@REM Email & Reminder System Testing - Windows PowerShell/CMD Commands
@REM Save as test_reminders.bat and run from backend directory

@echo off
echo.
echo ====================================================================
echo  EMAIL & REMINDER SYSTEM - QUICK TEST
echo ====================================================================
echo.

set BASE_URL=http://localhost:5000/api

echo [1/5] Checking if backend is running...
curl -s %BASE_URL%/health | find "healthy" >nul
if errorlevel 1 (
    echo ERROR: Backend not running! Start it with: python app.py
    exit /b 1
)
echo OK: Backend is running
echo.

echo [2/5] Checking reminder debug status...
curl -s %BASE_URL%/debug/reminders
echo.
echo.

echo [3/5] Getting conversations (to find keynote_id)...
curl -s %BASE_URL%/conversations
echo.
echo.

@REM Calculate reminder time as current time + 2 minutes
@REM This is approximate - adjust in actual request
echo [4/5] Creating test reminder (will fire in 2 minutes)...
echo.
echo Example JSON for reminder (adjust reminder_time):
echo {
echo   "user_id": 1,
echo   "keynote_id": 1,
echo   "reminder_time": "2024-12-02T15:35:00"
echo }
echo.
echo To test, copy this and modify the reminder_time to 2 minutes from now:
echo.
echo PowerShell:
echo ------
echo $body = @{ user_id=1; keynote_id=1; reminder_time="2024-12-02T15:35:00" } ^| ConvertTo-Json
echo Invoke-WebRequest -Uri "http://localhost:5000/api/reminders" -Method Post -Body $body -ContentType "application/json"
echo.
echo.
echo CMD curl:
echo ------
echo curl -X POST http://localhost:5000/api/reminders -H "Content-Type: application/json" -d "{\"user_id\":1,\"keynote_id\":1,\"reminder_time\":\"2024-12-02T15:35:00\"}"
echo.
echo.

echo [5/5] After creating reminder, check status:
echo curl -s %BASE_URL%/debug/reminders | find "scheduled_jobs"
echo.
echo ====================================================================
echo  NEXT STEPS
echo ====================================================================
echo.
echo 1. Modify reminder_time to 2 minutes from now (YYYY-MM-DDTHH:MM:SS)
echo 2. Run the POST request above
echo 3. Wait for reminder time
echo 4. Watch console for logs starting with ⏰
echo 5. Check email inbox
echo.
echo LOG MESSAGES TO LOOK FOR:
echo - ✅ [CREATE REMINDER] Job scheduled successfully
echo - ⏰ [REMINDER EMAIL] Starting for reminder_id
echo - ✅ [REMINDER EMAIL] SUCCESS - Reminder sent
echo.
pause
