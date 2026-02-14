#!/bin/bash

echo "========================================"
echo " HR Recruitment System - Starting..."
echo "========================================"
echo ""

# Check prerequisites
echo "[1/5] Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found. Please install Python 3.11+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found. Please install Node.js 20+"
    exit 1
fi

echo "[OK] Python and Node.js found"
echo ""

# Check MongoDB
echo "[2/5] Checking MongoDB..."
if ! command -v mongod &> /dev/null; then
    echo "WARNING: MongoDB not detected. Please ensure MongoDB is running."
    echo "You can start MongoDB with: mongod"
    echo "Or use Docker: docker run -d -p 27017:27017 mongo:7"
    read -p "Press enter to continue..."
fi
echo ""

# Check Ollama
echo "[3/5] Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama not found. Please install Ollama and download models:"
    echo "  ollama pull ministral-3:3b"
    echo "  ollama pull llama3.2:1b"
    exit 1
fi
echo "[OK] Ollama found"
echo ""

# Check environment file
echo "[4/5] Checking environment configuration..."
if [ ! -f "backend/.env" ]; then
    echo "WARNING: .env file not found. Creating from template..."
    cp backend/.env.example backend/.env
    echo "PLEASE EDIT backend/.env with your configuration before proceeding!"
    read -p "Press enter to continue..."
fi
echo ""

# Start services
echo "[5/5] Starting all services..."
echo ""

echo "Starting Backend (Port 8001)..."
cd backend && python3 main.py &
sleep 2
cd ..

echo "Starting CV Agent (Port 8002)..."
cd agents/cv_shortlisting_agent && python3 main.py &
sleep 1
cd ../..

echo "Starting Email Agent (Port 8003)..."
cd agents/email_scheduling_agent && python3 main.py &
sleep 1
cd ../..

echo "Starting Interview Agent (Port 8004)..."
cd agents/interview_agent && python3 main.py &
sleep 1
cd ../..

echo "Starting HR Chat Agent (Port 8005)..."
cd agents/hr_chat_agent && python3 main.py &
sleep 1
cd ../..

echo "Starting Frontend (Port 5173)..."
cd frontend && npm run dev &
sleep 2
cd ..

echo ""
echo "========================================"
echo " All services started!"
echo "========================================"
echo ""
echo "Frontend:  http://localhost:5173"
echo "Backend:   http://localhost:8001/docs"
echo ""
echo "Login credentials:"
echo "  Email:    admin@admin.com"
echo "  Password: password123"
echo ""
