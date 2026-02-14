@echo off
echo ========================================
echo  HR Recruitment System - Starting...
echo ========================================
echo.

REM Check prerequisites
echo [1/5] Checking prerequisites...
call E:\ruya_hackaton_solution\env\Scripts\activate.bat
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python virtual environment not found at E:\ruya_hackaton_solution\env
    echo Please create it with: python -m venv E:\ruya_hackaton_solution\env
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Please install Node.js 20+
    pause
    exit /b 1
)

echo [OK] Python and Node.js found
echo.

REM Check MongoDB
echo [2/5] Checking MongoDB...
mongod --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: MongoDB not detected. Please ensure MongoDB is running.
    echo You can start MongoDB with: mongod
    echo Or use Docker: docker run -d -p 27017:27017 mongo:7
    pause
)
echo.

REM Check Ollama
echo [3/5] Checking Ollama...
ollama list >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama not found. Please install Ollama and download models:
    echo   ollama pull ministral-3:3b
    echo   ollama pull llama3.2:1b
    pause
    exit /b 1
)
echo [OK] Ollama found
echo.

REM Check environment file
echo [4/5] Checking environment configuration...
if not exist "backend\.env" (
    echo WARNING: .env file not found. Creating from template...
    copy backend\.env.example backend\.env
    echo PLEASE EDIT backend\.env with your configuration before proceeding!
    pause
)
echo.

REM Start services
echo [5/5] Starting all services...
echo.

echo Starting MongoDB (if not already running)...
start "MongoDB" cmd /k "mongod --dbpath E:\ruya_hackaton_solution\admin_dashboard\data\db"
timeout /t 3 /nobreak >nul

echo Starting Backend (Port 8001) with integrated CV & HR Chat agents...
start "Backend" cmd /k "cd backend && E:\ruya_hackaton_solution\env\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 5 /nobreak >nul

echo Starting Email Agent (Port 8003)...
start "Email Agent" cmd /k "cd agents\email_scheduling_agent && E:\ruya_hackaton_solution\env\Scripts\activate.bat && python main.py"
timeout /t 2 /nobreak >nul

echo Starting Interview Agent (Port 8004)...
start "Interview Agent" cmd /k "cd agents\interview_agent && E:\audio_jam\env\Scripts\activate.bat && python main.py"
timeout /t 2 /nobreak >nul

echo Starting Frontend (Port 5173)...
start "Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo  All services started!
echo ========================================
echo.
echo MongoDB:       mongodb://localhost:27017
echo Frontend:      http://localhost:5173
echo Backend API:   http://localhost:8001/docs
echo Email Agent:   http://localhost:8003
echo Interview:     http://localhost:8004
echo.
echo NOTE: CV Shortlisting and HR Chat agents are integrated into the main backend.
echo NOTE: Critic Agent evaluations are available via backend API at /critic/*
echo.
echo Press Ctrl+C in each window to stop services.
pause
echo.
echo Login credentials:
echo   Email:    admin@admin.com
echo   Password: password123
echo.
echo Press any key to open frontend in browser...
pause >nul
start http://localhost:5173
