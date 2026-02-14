"""
Interview Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from models.interview import (
    Interview, InterviewCreate, InterviewUpdate, 
    InterviewStatus, CandidateInterviewAuth
)
from models.candidate import CandidateStatus
from services.email_service import email_service
from utils.database import get_db
from config.settings import settings
import logging
import json
import httpx

router = APIRouter(prefix="/interviews", tags=["Interviews"])
logger = logging.getLogger(__name__)


@router.post("", response_model=Interview, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_data: InterviewCreate
):
    """Create a new interview"""
    db = get_db()
    
    # Verify candidate exists
    if not ObjectId.is_valid(interview_data.candidate_id):
        raise HTTPException(status_code=400, detail="Invalid candidate ID")
    
    candidate = await db.candidates.find_one({"_id": ObjectId(interview_data.candidate_id)})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Check if interview already exists
    existing = await db.interviews.find_one({"candidate_id": interview_data.candidate_id})
    if existing:
        raise HTTPException(status_code=400, detail="Interview already exists for this candidate")
    
    interview_doc = {
        **interview_data.model_dump(),
        "status": InterviewStatus.SCHEDULED,
        "started_at": None,
        "completed_at": None,
        "transcript": [],
        "recording_path": None,
        "transcript_path": None,
        "score": None,
        "evaluation": None,
        "notes": None,
        "created_at": datetime.utcnow()
    }
    
    result = await db.interviews.insert_one(interview_doc)
    interview_doc["_id"] = str(result.inserted_id)
    
    # Update candidate status
    await db.candidates.update_one(
        {"_id": ObjectId(interview_data.candidate_id)},
        {"$set": {"status": CandidateStatus.SCHEDULED}}
    )
    
    logger.info(f"✅ Interview created for candidate: {interview_data.candidate_id}")
    
    return Interview(**interview_doc)


@router.get("", response_model=List[Interview])
async def get_interviews(
    job_posting_id: Optional[str] = None,
    status_filter: Optional[InterviewStatus] = None
):
    """Get interviews"""
    db = get_db()
    
    query = {}
    if job_posting_id:
        if not ObjectId.is_valid(job_posting_id):
            raise HTTPException(status_code=400, detail="Invalid job posting ID")
        query["job_posting_id"] = job_posting_id
    
    if status_filter:
        query["status"] = status_filter
    
    cursor = db.interviews.find(query).sort("created_at", -1)
    interviews = []
    
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        interviews.append(Interview(**doc))
    
    return interviews


@router.get("/{interview_id}", response_model=Interview)
async def get_interview(
    interview_id: str
):
    """Get a specific interview"""
    db = get_db()
    
    if not ObjectId.is_valid(interview_id):
        raise HTTPException(status_code=400, detail="Invalid interview ID")
    
    interview_doc = await db.interviews.find_one({"_id": ObjectId(interview_id)})
    
    if not interview_doc:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview_doc["_id"] = str(interview_doc["_id"])
    return Interview(**interview_doc)


@router.get("/candidate/{candidate_id}", response_model=Interview)
async def get_interview_by_candidate(
    candidate_id: str
):
    """Get interview by candidate ID"""
    db = get_db()
    
    if not ObjectId.is_valid(candidate_id):
        raise HTTPException(status_code=400, detail="Invalid candidate ID")
    
    interview_doc = await db.interviews.find_one({"candidate_id": candidate_id})
    
    if not interview_doc:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview_doc["_id"] = str(interview_doc["_id"])
    return Interview(**interview_doc)


@router.put("/{interview_id}", response_model=Interview)
async def update_interview(
    interview_id: str,
    interview_update: InterviewUpdate
):
    """Update an interview"""
    db = get_db()
    
    if not ObjectId.is_valid(interview_id):
        raise HTTPException(status_code=400, detail="Invalid interview ID")
    
    update_data = {k: v for k, v in interview_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.interviews.find_one_and_update(
        {"_id": ObjectId(interview_id)},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Update candidate status if interview is completed
    if interview_update.status == InterviewStatus.COMPLETED:
        await db.candidates.update_one(
            {"_id": ObjectId(result["candidate_id"])},
            {"$set": {"status": CandidateStatus.INTERVIEWED}}
        )
    
    result["_id"] = str(result["_id"])
    logger.info(f"✅ Interview updated: {interview_id}")
    
    return Interview(**result)


@router.post("/candidate-auth")
async def authenticate_candidate_for_interview(auth_data: CandidateInterviewAuth):
    """
    Authenticate candidate for interview using just their name
    Returns candidate and interview information
    """
    db = get_db()
    
    # Find candidate by name (case-insensitive)
    candidate = await db.candidates.find_one({
        "name": {"$regex": f"^{auth_data.name}$", "$options": "i"},
        "status": {"$in": [CandidateStatus.SCHEDULED, CandidateStatus.EMAIL_SENT, CandidateStatus.APPROVED]}
    })
    
    if not candidate:
        raise HTTPException(
            status_code=404, 
            detail="No scheduled interview found for this name"
        )
    
    # Get interview
    interview = await db.interviews.find_one({
        "candidate_id": str(candidate["_id"]),
        "status": {"$in": [InterviewStatus.SCHEDULED, InterviewStatus.IN_PROGRESS]}
    })
    
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="No active interview found for this candidate"
        )
    
    # Get job posting
    job_posting = await db.job_postings.find_one({"_id": ObjectId(candidate["job_posting_id"])})
    
    candidate["_id"] = str(candidate["_id"])
    interview["_id"] = str(interview["_id"])
    
    return {
        "candidate": candidate,
        "interview": interview,
        "job_description": job_posting["job_description"] if job_posting else ""
    }


@router.websocket("/ws/{interview_id}")
async def interview_websocket(websocket: WebSocket, interview_id: str):
    """
    WebSocket endpoint for live interview
    Proxies to Interview Agent microservice
    """
    await websocket.accept()
    
    try:
        db = get_db()
        
        # Verify interview exists
        if not ObjectId.is_valid(interview_id):
            await websocket.send_json({"error": "Invalid interview ID"})
            await websocket.close()
            return
        
        interview = await db.interviews.find_one({"_id": ObjectId(interview_id)})
        if not interview:
            await websocket.send_json({"error": "Interview not found"})
            await websocket.close()
            return
        
        # Update interview status to in_progress
        await db.interviews.update_one(
            {"_id": ObjectId(interview_id)},
            {
                "$set": {
                    "status": InterviewStatus.IN_PROGRESS,
                    "started_at": datetime.utcnow()
                }
            }
        )
        
        # Connect to Interview Agent WebSocket
        interview_agent_ws_url = f"ws://localhost:8004/interview/{interview_id}"
        
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", interview_agent_ws_url) as response:
                # Proxy messages between client and interview agent
                while True:
                    try:
                        # Receive from client
                        client_message = await websocket.receive_text()
                        
                        # Forward to interview agent
                        # Send to interview agent via HTTP (simplified)
                        # In production, maintain persistent WebSocket connection
                        
                        # For now, acknowledge receipt
                        await websocket.send_json({
                            "type": "acknowledgment",
                            "message": "Message received"
                        })
                        
                    except WebSocketDisconnect:
                        logger.info(f"Client disconnected from interview {interview_id}")
                        break
        
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()
