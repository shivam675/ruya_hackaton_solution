"""
Email Scheduling Agent Microservice
Port: 8003
"""
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from contextlib import asynccontextmanager
import logging

from availability_parser import availability_parser
from scheduler import email_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ParseAvailabilityRequest(BaseModel):
    """Request to parse availability from email"""
    email_text: str
    candidate_id: str


class ParseAvailabilityResponse(BaseModel):
    """Response with parsed availability"""
    candidate_id: str
    time_slots: List[dict]
    timezone: str
    notes: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting Email Scheduling Agent")
    email_scheduler.start()
    yield
    logger.info("👋 Shutting down Email Scheduling Agent")
    email_scheduler.stop()


app = FastAPI(
    title="Email Scheduling Agent",
    description="Microservice for email management and interview scheduling",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Email Scheduling Agent",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "scheduler_running": email_scheduler.is_running}


@app.post("/parse-availability", response_model=ParseAvailabilityResponse)
async def parse_availability(request: ParseAvailabilityRequest):
    """
    Parse candidate availability from email text using LLM
    
    Args:
        request: Email text and candidate ID
        
    Returns:
        Parsed availability data
    """
    logger.info(f"📧 Parsing availability for candidate: {request.candidate_id}")
    
    try:
        parsed = availability_parser.parse_availability(request.email_text)
        
        return ParseAvailabilityResponse(
            candidate_id=request.candidate_id,
            time_slots=parsed.get("time_slots", []),
            timezone=parsed.get("timezone", "UTC"),
            notes=parsed.get("notes", "")
        )
    except Exception as e:
        logger.error(f"❌ Error parsing availability: {e}")
        return ParseAvailabilityResponse(
            candidate_id=request.candidate_id,
            time_slots=[],
            timezone="UTC",
            notes=f"Error: {str(e)}"
        )


@app.post("/schedule-reminder")
async def schedule_reminder(interview_id: str, reminder_datetime: str):
    """
    Schedule an interview reminder
    
    Args:
        interview_id: Interview ID
        reminder_datetime: ISO format datetime string
    """
    from datetime import datetime
    
    try:
        reminder_time = datetime.fromisoformat(reminder_datetime)
        email_scheduler.schedule_interview_reminder(interview_id, reminder_time)
        
        return {
            "message": "Reminder scheduled successfully",
            "interview_id": interview_id,
            "reminder_time": reminder_datetime
        }
    except Exception as e:
        logger.error(f"❌ Error scheduling reminder: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Email Scheduling Agent on port 8003")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
