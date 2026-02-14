# API Documentation

## Base URLs

- Main Backend: `http://localhost:8001`
- CV Agent: `http://localhost:8002`
- Email Agent: `http://localhost:8003`
- Interview Agent: `http://localhost:8004`
- HR Chat Agent: `http://localhost:8005`

## Authentication

All API requests (except login and candidate interview) require JWT authentication.

**Header:**
```
Authorization: Bearer <access_token>
```

### POST /auth/login
Login with email and password.

**Request:**
```http
POST /auth/login
Authorization: Basic base64(email:password)
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### GET /auth/me
Get current user information.

**Response:**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "email": "admin@admin.com",
  "full_name": "Super Admin",
  "role": "super_admin",
  "is_active": true,
  "created_at": "2026-02-14T10:00:00"
}
```

## Job Postings

### POST /job-postings
Create a new job posting.

**Request:**
```json
{
  "title": "Senior Python Developer",
  "job_description": "Looking for experienced Python developer...",
  "required_skills": ["Python", "FastAPI", "MongoDB"],
  "min_experience": 5,
  "max_experience": 10,
  "location": "Remote",
  "department": "Engineering"
}
```

### GET /job-postings
List all job postings.

**Query Parameters:**
- `is_active` (boolean, optional): Filter by active status
- `skip` (int, optional): Pagination offset
- `limit` (int, optional): Pagination limit

**Response:**
```json
[
  {
    "_id": "...",
    "title": "Senior Python Developer",
    "job_description": "...",
    "required_skills": ["Python", "FastAPI"],
    "min_experience": 5,
    "candidates_count": 3,
    "is_active": true,
    "created_at": "2026-02-14T10:00:00",
    "created_by": "..."
  }
]
```

### GET /job-postings/{id}
Get a specific job posting.

### PUT /job-postings/{id}
Update a job posting.

### DELETE /job-postings/{id}
Delete (soft delete) a job posting.

## Candidates

### POST /candidates/fetch-from-cv-agent/{job_id}
Trigger CV agent to fetch shortlisted candidates.

**Response:**
```json
{
  "message": "Successfully fetched candidates from CV agent",
  "added": 5,
  "skipped": 2,
  "total": 7
}
```

### GET /candidates/job/{job_id}
Get all candidates for a job posting.

**Query Parameters:**
- `status_filter` (string, optional): Filter by status

**Response:**
```json
[
  {
    "_id": "...",
    "name": "John Doe",
    "email": "john@example.com",
    "skills": ["Python", "ML"],
    "experience": 5,
    "confidence": 0.95,
    "status": "shortlisted",
    "job_posting_id": "...",
    "created_at": "2026-02-14T10:00:00"
  }
]
```

### POST /candidates/approve
Approve candidates and send email invitations.

**Request:**
```json
{
  "candidate_ids": ["id1", "id2", "id3"],
  "send_email": true
}
```

**Response:**
```json
{
  "message": "Candidate approval completed",
  "approved": 3,
  "emails_sent": 3,
  "errors": []
}
```

### PUT /candidates/{id}
Update candidate status or notes.

**Request:**
```json
{
  "status": "approved",
  "notes": "Strong candidate"
}
```

## Interviews

### POST /interviews
Create a new interview.

**Request:**
```json
{
  "candidate_id": "...",
  "job_posting_id": "...",
  "scheduled_at": "2026-02-15T14:00:00"
}
```

### GET /interviews
List all interviews.

**Query Parameters:**
- `job_posting_id` (string, optional)
- `status_filter` (string, optional): "scheduled", "in_progress", "completed"

### POST /interviews/candidate-auth
Authenticate candidate for interview.

**Request:**
```json
{
  "name": "John Doe"
}
```

**Response:**
```json
{
  "candidate": {...},
  "interview": {...},
  "job_description": "..."
}
```

### WebSocket /interviews/ws/{interview_id}
Real-time interview WebSocket connection.

**Client → Server Messages:**
```json
{
  "type": "text",
  "data": "I have 5 years of experience in Python..."
}
```

**Server → Client Messages:**
```json
{
  "type": "text",
  "data": "That's great! Can you tell me about a project..."
}

{
  "type": "audio",
  "data": "base64_encoded_audio",
  "sentence": "That's great!"
}

{
  "type": "transcript",
  "data": {
    "timestamp": "2026-02-14T10:30:00",
    "speaker": "interviewer",
    "text": "That's great!"
  }
}
```

## CV Shortlisting Agent

### GET /shortlist
Get shortlisted candidates for a job.

**Query Parameters:**
- `job_id` (string, required): Job posting ID

**Response:**
```json
{
  "shortlisted": [
    {
      "name": "Shivam",
      "confidence": 0.95,
      "email": "shivam31199@gmail.com",
      "cv_path": "/path/to/cv",
      "skills": ["Python", "ML"],
      "experience": 5,
      "cover_letter": "..."
    }
  ]
}
```

## Email Scheduling Agent

### POST /parse-availability
Parse candidate availability from email text.

**Request:**
```json
{
  "email_text": "I'm available Monday 2-4pm and Wednesday 10am-12pm",
  "candidate_id": "..."
}
```

**Response:**
```json
{
  "candidate_id": "...",
  "time_slots": [
    {
      "day": "Monday",
      "date": "2026-02-17",
      "start_time": "14:00",
      "end_time": "16:00"
    }
  ],
  "timezone": "UTC",
  "notes": "Parsed successfully"
}
```

## Interview Agent

### POST /start-interview
Start a new interview session.

**Request:**
```json
{
  "interview_id": "...",
  "job_description": "Looking for Python developer..."
}
```

**Response:**
```json
{
  "interview_id": "...",
  "status": "started",
  "greeting": "Hello! I'm excited to interview you today...",
  "greeting_audio": "base64_encoded_audio"
}
```

### POST /process-response
Process candidate's text response.

**Request:**
```json
{
  "interview_id": "...",
  "candidate_text": "I have 5 years of Python experience"
}
```

### POST /end-interview/{interview_id}
End interview and save transcript.

**Response:**
```json
{
  "interview_id": "...",
  "status": "completed",
  "transcript_path": "/path/to/transcript.json",
  "duration": "25 minutes",
  "transcript": [...]
}
```

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message here"
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

Currently no rate limiting implemented. Add in production.

## WebSocket Protocol

### Interview WebSocket

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8004/ws/interview/{interview_id}');
```

**Message Types:**
- `text` - Text message from candidate/interviewer
- `audio` - Audio data (base64 encoded)
- `transcript` - Transcript update
- `control` - Control commands (e.g., "end")
- `status` - Status updates
- `error` - Error messages

### HR Chat WebSocket

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8005/ws/chat');
```

For Flutter app integration.
