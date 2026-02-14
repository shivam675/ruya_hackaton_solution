# Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         HR Recruitment System                    │
│                   Production-Grade Microservices                 │
└─────────────────────────────────────────────────────────────────┘

                        ┌──────────────────┐
                        │  React Frontend  │
                        │   (shadcn/ui)    │
                        │   Port 5173      │
                        └────────┬─────────┘
                                 │
                          HTTP/WebSocket
                                 │
              ┌──────────────────┴──────────────────┐
              │                                     │
   ┌──────────▼──────────┐              ┌──────────▼────────┐
   │  Main Backend API   │◄─────────────┤     MongoDB       │
   │    (FastAPI)        │              │   Port 27017      │
   │    Port 8001        │              │   Database        │
   └──────────┬──────────┘              └───────────────────┘
              │
              │  REST API Communication
              │
    ┌─────────┼─────────┬─────────┬─────────┐
    │         │         │         │         │
┌───▼───┐ ┌──▼───┐ ┌───▼───┐ ┌───▼───┐ ┌──▼───┐
│  CV   │ │Email │ │Interview│ │HR Chat│ │      │
│ Agent │ │Agent │ │ Agent  │ │ Agent │ │Storage│
│ 8002  │ │ 8003 │ │ 8004   │ │ 8005  │ │ FS   │
└───────┘ └──┬───┘ └───┬────┘ └───────┘ └──────┘
             │         │
         ┌───▼───┐ ┌──▼──────┐
         │ SMTP  │ │ Ollama  │
         │Server │ │Ministral│
         └───────┘ │   3b    │
                   │Llama3.2 │
                   └─────────┘
```

## Component Details

### Frontend (React + TypeScript)
**Port:** 5173  
**Tech Stack:**
- React 18.2
- TypeScript
- Vite
- shadcn/ui
- Tailwind CSS
- Zustand (State Management)
- React Query
- React Router

**Pages:**
- Login (`/login`)
- Dashboard (`/dashboard`)
- Job Postings (`/dashboard/job-postings`)
- Candidates (`/dashboard/candidates`)
- Interview Portal (`/interview`)

### Main Backend API
**Port:** 8001  
**Tech Stack:**
- FastAPI 0.109.0
- Motor (MongoDB Async)
- JWT Authentication
- Pydantic Models
- CORS Middleware

**Routes:**
- `/auth/*` - Authentication endpoints
- `/job-postings/*` - CRUD for job postings
- `/candidates/*` - Candidate management
- `/interviews/*` - Interview scheduling

**Security:**
- HTTPBearer with JWT tokens
- Role-based access control
- Password hashing (bcrypt)

### CV Shortlisting Agent
**Port:** 8002  
**Purpose:** Analyze CVs and shortlist candidates

**Endpoints:**
- `GET /shortlist?job_id={id}` - Get shortlisted candidates

**Output Schema:**
```json
{
  "shortlisted": [
    {
      "name": "string",
      "email": "string",
      "confidence": 0.95,
      "skills": ["..."],
      "experience": 5,
      "cv_path": "string",
      "cover_letter": "string"
    }
  ]
}
```

**Note:** Mock implementation provided. Replace with actual CV parsing logic.

### Email Scheduling Agent
**Port:** 8003  
**Tech Stack:**
- aiosmtplib (SMTP)
- Ollama (llama3.2:1b)
- APScheduler

**Features:**
- SMTP email sending
- LLM-based availability parsing
- Background job scheduler
- Email template rendering

**Endpoints:**
- `POST /parse-availability` - Parse candidate availability
- `POST /schedule-reminder` - Schedule email reminder

### Interview Agent
**Port:** 8004  
**Tech Stack:**
- RealtimeSTT
- Ollama (Ministral 3b)
- Kokoro TTS (af_bella voice)
- WebSocket

**Pipeline:**
```
User Audio → STT → Text → LLM → Response → TTS → Audio
```

**Endpoints:**
- `POST /start-interview` - Initialize interview
- `POST /process-response` - Process text response
- `POST /end-interview/{id}` - Save transcript
- `WS /ws/interview/{id}` - WebSocket connection

**Storage:**
- Transcripts: JSON files
- Recordings: Audio files (future)

### HR Chat Agent
**Port:** 8005  
**Purpose:** Future Flutter app integration

**Endpoints:**
- `WS /ws/chat` - WebSocket for real-time chat

**Status:** Scaffold implementation ready

### Database (MongoDB)
**Port:** 27017  
**Database:** hr_recruitment_db

**Collections:**
- `users` - HR staff accounts
- `job_postings` - Job descriptions
- `candidates` - Candidate profiles
- `interviews` - Interview records

**Indexes:**
- `candidates`: `job_posting_id`, `status`
- `interviews`: `candidate_id`, `status`
- `job_postings`: `is_active`, `created_at`

## Data Flow

### 1. Candidate Shortlisting Flow
```
HR creates job posting
    ↓
Click "Fetch Candidates" button
    ↓
Backend → CV Agent (GET /shortlist?job_id=X)
    ↓
CV Agent returns shortlisted candidates
    ↓
Backend saves to MongoDB (status: "shortlisted")
    ↓
Frontend displays candidates with checkboxes
```

### 2. Approval & Email Flow
```
HR selects candidates
    ↓
Click "Approve & Send Email"
    ↓
Backend updates status to "approved"
    ↓
Email Agent sends invitation emails (SMTP)
    ↓
Candidate receives email with interview link
    ↓
Status updated to "email_sent"
```

### 3. Interview Flow
```
Candidate clicks link → /interview page
    ↓
Enters name (name-based auth)
    ↓
Frontend → Backend (POST /interviews/candidate-auth)
    ↓
Backend returns interview details
    ↓
Frontend establishes WebSocket to Interview Agent
    ↓
Interview Agent initializes STT/LLM/TTS pipeline
    ↓
┌─────────────────────────────────────┐
│  Interview Loop:                    │
│  1. User speaks/types               │
│  2. STT converts to text (optional) │
│  3. LLM generates response          │
│  4. TTS synthesizes audio           │
│  5. Frontend plays audio            │
│  6. Save to transcript              │
└─────────────────────────────────────┘
    ↓
End interview → Save transcript as JSON
    ↓
HR reviews transcript and makes decision
```

## Security Architecture

### Authentication Flow
```
User → POST /auth/login (Basic Auth: email:password)
    ↓
Backend validates credentials
    ↓
Generate JWT token (30 min expiry)
    ↓
Return access_token
    ↓
Frontend stores in localStorage
    ↓
All subsequent requests include:
    Authorization: Bearer <token>
```

### Role-Based Access Control
- **Super Admin**: Full access to all resources
- **HR Manager**: Manage jobs, candidates, interviews
- **Interviewer**: View candidates, conduct interviews (read-only)

### Candidate Authentication
- **No password required** for interview portal
- **Name-based verification** against database
- **One-time access** with interview ID

## Storage Architecture

```
storage/
├── cvs/              # Uploaded CV files
├── recordings/       # Interview audio recordings
└── transcripts/      # Interview transcripts (JSON)
    └── {interview_id}_transcript.json
```

**Transcript Format:**
```json
{
  "interview_id": "...",
  "candidate_id": "...",
  "started_at": "2026-02-14T10:00:00",
  "ended_at": "2026-02-14T10:25:00",
  "job_description": "...",
  "transcript": [
    {
      "timestamp": "2026-02-14T10:00:30",
      "speaker": "interviewer",
      "text": "Tell me about yourself."
    },
    {
      "timestamp": "2026-02-14T10:01:00",
      "speaker": "candidate",
      "text": "I have 5 years of Python experience..."
    }
  ]
}
```

## Deployment Architecture

### Docker Compose (Development/Production)
```
docker-compose.yml
├── mongodb (service)
├── backend (service)
├── cv_agent (service)
├── email_agent (service)
├── interview_agent (service)
├── hr_chat_agent (service)
└── frontend (service)

All connected via: hr_network (bridge)
```

### Network Configuration
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8001`
- CV Agent: `http://localhost:8002`
- Email Agent: `http://localhost:8003`
- Interview Agent: `http://localhost:8004`
- HR Chat Agent: `http://localhost:8005`
- MongoDB: `mongodb://localhost:27017`

## External Dependencies

### Ollama Models
- **Ministral 3b** - Interview conversation generation
- **Llama 3.2 1b** - Email availability parsing

### SMTP Server
- Gmail (recommended with App Password)
- SendGrid
- Custom SMTP server

### Audio Libraries
- RealtimeSTT - Speech-to-text
- Kokoro - Text-to-speech
- sounddevice - Audio playback

## Future Enhancements

1. **Flutter Mobile App** → Connect to HR Chat Agent (Port 8005)
2. **Real-time Audio** → Integrate voice_client.py
3. **Video Recording** → Save interview videos
4. **Analytics Dashboard** → Hiring metrics
5. **Calendar Integration** → Google Calendar API
6. **Notification System** → Push notifications
7. **Multi-language Support** → i18n
8. **AI Resume Builder** → For candidates
9. **Automated Scoring** → AI-based candidate evaluation
10. **Kubernetes Deployment** → Scale microservices

## Performance Considerations

- **Database Indexing**: All query fields indexed
- **Async Operations**: Motor (MongoDB), aiosmtplib (email)
- **WebSocket**: Real-time bidirectional communication
- **Lazy Loading**: Frontend uses React Query for caching
- **File Streaming**: Large file uploads via chunks
- **Connection Pooling**: MongoDB connection reuse

## Monitoring & Logging

- **Docker Logs**: `docker-compose logs -f`
- **FastAPI Logs**: Uvicorn logging
- **Frontend**: Browser console + Sentry (future)
- **Health Checks**: `/docs` endpoint validation
- **Database Monitoring**: MongoDB Compass
