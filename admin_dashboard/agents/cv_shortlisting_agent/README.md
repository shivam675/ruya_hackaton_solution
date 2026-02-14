# CV Shortlisting Agent

This microservice handles CV analysis and candidate shortlisting.

## Setup

```bash
cd agents/cv_shortlisting_agent
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

The service will run on **port 8002**.

## API Endpoints

### GET /shortlist
Get shortlisted candidates for a job posting.

**Query Parameters:**
- `job_id` (required): Job posting ID

**Response:**
```json
{
  "shortlisted": [
    {
      "name": "Candidate Name",
      "confidence": 0.95,
      "email": "email@example.com",
      "cv_path": "/path/to/cv",
      "skills": ["Skill1", "Skill2"],
      "experience": 5,
      "cover_letter": "Cover letter text..."
    }
  ]
}
```

## Integration

This is a **mock implementation**. Replace `agent_logic.py` with your actual CV shortlisting logic.

The main backend calls this service when the user clicks "Fetch Candidates" in the UI.
