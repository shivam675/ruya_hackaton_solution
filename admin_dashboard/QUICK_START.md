# Quick Start Guide

## Prerequisites Check

1. **Python 3.11+**
   ```powershell
   python --version
   ```

2. **Node.js 20+**
   ```powershell
   node --version
   ```

3. **MongoDB**
   - Download from https://www.mongodb.com/try/download/community
   - Or use Docker: `docker run -d -p 27017:27017 mongo:7`

4. **Ollama with Ministral 3b**
   ```powershell
   ollama pull ministral-3:3b
   ollama pull llama3.2:1b
   ```

## Installation (5 Minutes)

### Step 1: Backend Setup
```powershell
cd E:\ruya_hackaton_solution\admin_dashboard\backend
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
- Set your MongoDB URL
- Add a secret key (any random 32+ character string)
- Configure SMTP (use Gmail App Password)

Start backend:
```powershell
python main.py
```

### Step 2: CV Agent Setup
```powershell
cd E:\ruya_hackaton_solution\admin_dashboard\agents\cv_shortlisting_agent
pip install -r requirements.txt
python main.py
```

### Step 3: Email Agent Setup
```powershell
cd E:\ruya_hackaton_solution\admin_dashboard\agents\email_scheduling_agent
pip install -r requirements.txt
python main.py
```

### Step 4: Interview Agent Setup
```powershell
cd E:\ruya_hackaton_solution\admin_dashboard\agents\interview_agent
pip install -r requirements.txt
python main.py
```

### Step 5: Frontend Setup
```powershell
cd E:\ruya_hackaton_solution\admin_dashboard\frontend
npm install
npm run dev
```

## Test the Application

1. **Open browser**: http://localhost:5173
2. **Login**: admin@admin.com / password123
3. **Create Job Posting**:
   - Title: "Senior Python Developer"
   - Add job description
   - Add required skills
4. **Click "Fetch Candidates"** button
5. **Select candidates** and click "Approve & Send Email"
6. **Open Interview Portal**: http://localhost:5173/interview
7. **Enter candidate name** and start interview

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running: `mongod --version`
- Check connection string in `.env`

### Frontend Can't Connect
- Check backend is running on port 8001
- Verify CORS settings

### Interview Agent Not Working
- Ensure Ollama is running: `ollama list`
- Check Ministral 3b is downloaded

### Port Already in Use
```powershell
# Find and kill process
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

## Architecture Diagram

```
┌─────────────────┐
│  React Frontend │  Port 5173
│  (shadcn/ui)    │
└────────┬────────┘
         │
    ┌────┴─────────────────────────────┐
    │                                  │
┌───▼─────────────┐              ┌────▼────────────┐
│  Main Backend   │◄─────────────┤   MongoDB       │
│  (FastAPI)      │              │                 │
│  Port 8001      │              │  Port 27017     │
└───┬─────────────┘              └─────────────────┘
    │
    ├────► CV Agent (Port 8002)
    ├────► Email Agent (Port 8003)
    ├────► Interview Agent (Port 8004)
    │      └─► STT + Ollama + TTS
    └────► HR Chat Agent (Port 8005)
```

## Next Steps

1. **Customize CV Agent**: Replace mock logic with actual CV parsing
2. **Configure SMTP**: Set up email sending for production
3. **Integrate Audio**: Connect your voice_client.py to Interview Agent
4. **Add Flutter App**: Connect to HR Chat Agent WebSocket
5. **Deploy**: Use docker-compose for production

## Support

Check the main README.md for detailed documentation.
