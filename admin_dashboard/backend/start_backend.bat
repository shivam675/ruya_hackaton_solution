@echo off
echo ====================================
echo Starting HR Recruitment Backend
echo ====================================
echo.

cd /d E:\ruya_hackaton_solution\admin_dashboard\backend

echo Starting backend server on port 8001...
echo.
echo Backend will be available at: http://localhost:8001
echo API docs: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

pause
