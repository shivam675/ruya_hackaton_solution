# Testing Guide

## Prerequisites

Before testing, ensure:
- MongoDB is running
- Ollama is running with required models
- All dependencies installed
- `.env` file configured

## Unit Testing (Future Enhancement)

```powershell
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

## Manual Testing Workflow

### 1. Start All Services

**Option A: Using Docker**
```powershell
docker-compose up --build
```

**Option B: Using Start Script**
```powershell
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

**Option C: Manual Start**
```powershell
# Terminal 1: MongoDB
mongod

# Terminal 2: Backend
cd backend
python main.py

# Terminal 3: CV Agent
cd agents/cv_shortlisting_agent
python main.py

# Terminal 4: Email Agent
cd agents/email_scheduling_agent
python main.py

# Terminal 5: Interview Agent
cd agents/interview_agent
python main.py

# Terminal 6: HR Chat Agent
cd agents/hr_chat_agent
python main.py

# Terminal 7: Frontend
cd frontend
npm run dev
```

### 2. Test Authentication

1. Open browser: `http://localhost:5173`
2. Login with credentials:
   - Email: `admin@admin.com`
   - Password: `password123`
3. Verify you're redirected to `/dashboard`
4. Check that header shows "Super Admin"
5. Test logout and re-login

**Expected Result:**
- ✅ JWT token stored in localStorage
- ✅ Axios interceptor adds Authorization header
- ✅ Protected routes accessible
- ✅ Logout clears token and redirects to login

### 3. Test Job Posting Creation

1. Navigate to Dashboard
2. Note: Job creation UI is **not yet implemented**
3. Create job via API instead:

```powershell
# Using curl
curl -X POST http://localhost:8001/job-postings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "job_description": "We are looking for an experienced Python developer...",
    "required_skills": ["Python", "FastAPI", "MongoDB", "Docker"],
    "min_experience": 5,
    "max_experience": 10,
    "location": "Remote",
    "department": "Engineering"
  }'

# Using PowerShell
$token = "YOUR_TOKEN"
$headers = @{ "Authorization" = "Bearer $token" }
$body = @{
  title = "Senior Python Developer"
  job_description = "We are looking for..."
  required_skills = @("Python", "FastAPI")
  min_experience = 5
  max_experience = 10
  location = "Remote"
  department = "Engineering"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/job-postings" -Method Post -Headers $headers -Body $body -ContentType "application/json"
```

4. Refresh job postings page
5. Verify new job appears

**Expected Result:**
- ✅ Job created in database
- ✅ Shows in job postings list
- ✅ Shows correct candidates_count (0)

### 4. Test CV Agent Integration

1. Click on a job posting
2. Click "Fetch from CV Agent" button
3. Wait for loading spinner
4. Verify candidates appear

**What happens:**
- Frontend → `POST /candidates/fetch-from-cv-agent/{job_id}`
- Backend → `GET http://localhost:8002/shortlist?job_id={id}`
- CV Agent returns 5 mock candidates
- Backend saves to MongoDB with status "shortlisted"
- Frontend refreshes candidate list

**Expected Result:**
- ✅ 5 candidates displayed
- ✅ Shows name, email, skills, experience
- ✅ Confidence score shown
- ✅ Status badge shows "Shortlisted"
- ✅ Checkboxes appear for selection

### 5. Test Candidate Approval & Email

1. Select 2-3 candidates using checkboxes
2. Click "Approve & Send Email" button
3. Verify success toast appears

**What happens:**
- Frontend → `POST /candidates/approve`
- Backend updates status to "approved"
- Email Agent sends invitation emails via SMTP
- Status updated to "email_sent"

**Expected Result:**
- ✅ Selected candidates show "Email Sent" status
- ✅ Email sent (check SMTP logs)
- ✅ Success message displayed

**Note:** Email sending may fail if SMTP not configured. Check logs.

### 6. Test Interview Portal (Candidate Side)

1. Open new incognito window: `http://localhost:5173/interview`
2. Enter candidate name (e.g., "Shivam")
3. Click "Start Interview"
4. Verify interview starts

**What happens:**
- Frontend → `POST /interviews/candidate-auth` with name
- Backend finds candidate by name
- Creates/retrieves interview record
- Returns interview details + job description
- WebSocket connection established to `ws://localhost:8004/ws/interview/{id}`
- Interview Agent initialized with LLM

**Expected Result:**
- ✅ Name validation successful
- ✅ WebSocket connected
- ✅ Initial greeting from AI interviewer displayed
- ✅ Text input box enabled

### 7. Test Interview Conversation

1. Type a response: "I have 5 years of Python experience"
2. Click Send
3. Wait for AI response
4. Verify response appears
5. Continue conversation with 2-3 exchanges

**What happens:**
- User input → WebSocket → Interview Agent
- Interview Agent → LLM (Ministral 3b)
- LLM generates response
- Response → TTS (Kokoro) → Audio (if enabled)
- Transcript updated in real-time

**Expected Result:**
- ✅ User messages appear immediately
- ✅ AI responses relevant to job description
- ✅ Transcript updates in real-time
- ✅ Conversation flows naturally

**Debug:**
- Check Interview Agent logs for LLM calls
- Check Ollama logs: `ollama list`
- Verify Ministral 3b model loaded

### 8. Test Interview End & Transcript

1. Click "End Interview" button
2. Verify confirmation dialog
3. Confirm end
4. Check transcript saved

**What happens:**
- WebSocket sends "end" message
- Interview Agent → `POST /end-interview/{id}`
- Saves transcript to `/storage/transcripts/{id}_transcript.json`
- WebSocket closed

**Expected Result:**
- ✅ Interview ended gracefully
- ✅ Transcript file created
- ✅ JSON contains full conversation
- ✅ Timestamps for each message

**Verify transcript:**
```powershell
cat storage/transcripts/{interview_id}_transcript.json
```

### 9. Test Email Availability Parsing

```powershell
# Test LLM-based parsing
curl -X POST http://localhost:8003/parse-availability \
  -H "Content-Type: application/json" \
  -d '{
    "email_text": "I am available Monday 2-4pm and Wednesday 10am-12pm",
    "candidate_id": "..."
  }'
```

**Expected Result:**
```json
{
  "candidate_id": "...",
  "time_slots": [
    {
      "day": "Monday",
      "date": "2026-02-17",
      "start_time": "14:00",
      "end_time": "16:00"
    },
    {
      "day": "Wednesday",
      "date": "2026-02-19",
      "start_time": "10:00",
      "end_time": "12:00"
    }
  ],
  "timezone": "UTC",
  "notes": "Parsed successfully"
}
```

### 10. Test API Documentation

1. Open: `http://localhost:8001/docs`
2. Explore all endpoints
3. Test endpoints with "Try it out"

**Expected Result:**
- ✅ Swagger UI loads
- ✅ All routes documented
- ✅ Schemas visible
- ✅ Can execute requests

## Performance Testing

### Load Test with Apache Bench

```powershell
# Install Apache Bench
choco install apache-httpd

# Test backend endpoint
ab -n 100 -c 10 http://localhost:8001/job-postings
```

### WebSocket Stress Test

```python
import asyncio
import websockets

async def stress_test():
    tasks = []
    for i in range(10):
        tasks.append(test_interview_ws(i))
    await asyncio.gather(*tasks)

async def test_interview_ws(id):
    uri = f"ws://localhost:8004/ws/interview/test_{id}"
    async with websockets.connect(uri) as ws:
        for i in range(5):
            await ws.send(f"Message {i}")
            response = await ws.recv()
            print(f"[{id}] {response}")

asyncio.run(stress_test())
```

## Database Testing

### MongoDB Queries

```javascript
// Connect to MongoDB
mongosh

use hr_recruitment_db

// Check default users
db.users.find().pretty()

// Check job postings
db.job_postings.find().pretty()

// Check candidates
db.candidates.find().pretty()

// Check interviews
db.interviews.find().pretty()

// Count documents
db.candidates.countDocuments({ status: "shortlisted" })

// Aggregation - candidates per job
db.candidates.aggregate([
  { $group: { _id: "$job_posting_id", count: { $sum: 1 } } }
])
```

## Error Testing

### Test Invalid Login
- Wrong password → 401 Unauthorized
- Non-existent user → 401 Unauthorized
- Missing credentials → 422 Validation Error

### Test Unauthorized Access
- No token → 403 Forbidden
- Expired token → 401 Unauthorized
- Invalid token → 403 Forbidden

### Test Missing Data
- Create job without required fields → 422 Validation Error
- Fetch candidates for non-existent job → 404 Not Found
- Approve non-existent candidate → 404 Not Found

### Test Duplicate Data
- Create job with same title → Should allow (no unique constraint)
- Fetch candidates twice → Should skip duplicates

## Common Issues & Solutions

### MongoDB Connection Failed
```
ERROR: Could not connect to MongoDB
```
**Solution:**
- Start MongoDB: `mongod`
- Check connection string in `.env`
- Verify port 27017 is not blocked

### Ollama Model Not Found
```
ERROR: Model ministral-3:3b not found
```
**Solution:**
```powershell
ollama pull ministral-3:3b
ollama pull llama3.2:1b
```

### Frontend Can't Reach Backend
```
Network Error: ERR_CONNECTION_REFUSED
```
**Solution:**
- Check backend is running on port 8001
- Verify proxy in `vite.config.ts`
- Check CORS settings in backend

### WebSocket Connection Failed
```
WebSocket connection to 'ws://localhost:8004/' failed
```
**Solution:**
- Ensure Interview Agent is running
- Check WebSocket endpoint in code
- Verify no firewall blocking port 8004

### Email Not Sending
```
ERROR: Could not send email
```
**Solution:**
- Check SMTP credentials in `.env`
- Use Gmail App Password (not regular password)
- Enable "Less secure app access" (Gmail)
- Check SMTP logs in Email Agent

## Automated Testing Scripts

### Full Workflow Test (PowerShell)

```powershell
# Full workflow automation
$token = "YOUR_TOKEN"
$headers = @{ "Authorization" = "Bearer $token" }

# 1. Create job
$job = Invoke-RestMethod -Uri "http://localhost:8001/job-postings" -Method Post -Headers $headers -Body (@{
  title = "Test Job"
  job_description = "Test description"
  required_skills = @("Python")
  min_experience = 2
  max_experience = 5
} | ConvertTo-Json) -ContentType "application/json"

$jobId = $job._id

# 2. Fetch candidates
Invoke-RestMethod -Uri "http://localhost:8001/candidates/fetch-from-cv-agent/$jobId" -Method Post -Headers $headers

# 3. Get candidates
$candidates = Invoke-RestMethod -Uri "http://localhost:8001/candidates/job/$jobId" -Headers $headers

# 4. Approve first candidate
$candidateId = $candidates[0]._id
Invoke-RestMethod -Uri "http://localhost:8001/candidates/approve" -Method Post -Headers $headers -Body (@{
  candidate_ids = @($candidateId)
  send_email = $false
} | ConvertTo-Json) -ContentType "application/json"

Write-Host "Test completed successfully!"
```

## Testing Checklist

- [ ] All services start without errors
- [ ] MongoDB connection successful
- [ ] Login/logout works
- [ ] Job postings display correctly
- [ ] CV agent fetch returns candidates
- [ ] Candidate approval updates status
- [ ] Interview portal loads
- [ ] Candidate authentication works
- [ ] WebSocket connection established
- [ ] AI responses generated
- [ ] Interview transcript saved
- [ ] Email parsing works (if SMTP configured)
- [ ] API documentation accessible
- [ ] No console errors in frontend
- [ ] No Python errors in backend logs

## Next Steps After Testing

1. **Fix any issues found**
2. **Implement missing features:**
   - Job posting creation form
   - Interview list/management page
   - Analytics dashboard
3. **Add error handling:**
   - Network errors
   - Validation errors
   - Server errors
4. **Improve UX:**
   - Loading states
   - Error messages
   - Success notifications
5. **Deploy to production:**
   - Use Docker Compose
   - Configure HTTPS
   - Set up monitoring
