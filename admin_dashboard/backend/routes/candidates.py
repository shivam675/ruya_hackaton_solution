"""
Candidate Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId
from models.candidate import Candidate, CandidateCreate, CandidateUpdate, CandidateApproval, CandidateStatus
from services.email_service import email_service
from utils.database import get_db
import logging
import sys
from pathlib import Path
import importlib.util

# Add cv_shortlisting_agent to path first for imports
cv_agent_dir = Path(__file__).parent.parent.parent / "agents" / "cv_shortlisting_agent"
sys.path.insert(0, str(cv_agent_dir))

# Import CV agent using importlib to avoid conflicts
cv_agent_path = cv_agent_dir / "agent_logic.py"
spec = importlib.util.spec_from_file_location("cv_agent_logic", cv_agent_path)
cv_module = importlib.util.module_from_spec(spec)
sys.modules['cv_agent_logic'] = cv_module  # Register in sys.modules
spec.loader.exec_module(cv_module)
cv_agent = cv_module.cv_agent

router = APIRouter(prefix="/candidates", tags=["Candidates"])
logger = logging.getLogger(__name__)


@router.post("/fetch-from-cv-agent/{job_id}")
async def fetch_candidates_from_cv_agent(
    job_id: str
):
    """
    Trigger CV agent to process candidates and shortlist for a job posting
    Uses two-phase shortlisting:
    1. Phase 1: Keyword-based filtering
    2. Phase 2: LLM-based comprehensive review
    """
    db = get_db()
    
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job posting ID")
    
    # Verify job posting exists
    job_posting = await db.job_postings.find_one({"_id": ObjectId(job_id)})
    if not job_posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    try:
        logger.info(f"🚀 Starting CV shortlisting process for job: {job_id}")
        
        # Call CV agent - this triggers the full 2-phase shortlisting process
        result = await cv_agent.shortlist_candidates_async(job_id)
        
        logger.info(f"✅ CV Agent completed: {result.get('shortlisted_count', 0)} candidates shortlisted")
        
        added_count = 0
        skipped_count = 0
        
        # Process each shortlisted candidate
        for candidate_data in result.get('shortlisted', []):
            # Check if candidate already exists for this job
            existing = await db.candidates.find_one({
                "job_posting_id": job_id,
                "email": candidate_data.get('email')
            })
            
            if existing:
                skipped_count += 1
                logger.info(f"   ⏭️  Skipping existing candidate: {candidate_data.get('email')}")
                continue
            
            # Create candidate document
            candidate_doc = {
                "name": candidate_data.get('name'),
                "email": candidate_data.get('email'),
                "skills": candidate_data.get('skills', []),
                "experience": candidate_data.get('experience'),
                "confidence": candidate_data.get('confidence', 0.5),
                "cover_letter": candidate_data.get('cover_letter',''),
                "cv_path": candidate_data.get('cv_path', ''),
                "job_posting_id": job_id,
                "status": CandidateStatus.SHORTLISTED,
                "created_at": datetime.utcnow(),
                "interview_scheduled_at": None,
                "availability_response": None,
                "notes": candidate_data.get('llm_reasoning', '')
            }
            
            await db.candidates.insert_one(candidate_doc)
            added_count += 1
            logger.info(f"   ✅ Added candidate: {candidate_data.get('name')} (confidence: {candidate_data.get('confidence', 0):.2f})")
        
        # Update candidates count in job posting
        total_candidates = await db.candidates.count_documents({"job_posting_id": job_id})
        await db.job_postings.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"candidates_count": total_candidates}}
        )
        
        logger.info(f"🎉 Shortlisting complete: {added_count} added, {skipped_count} skipped, {total_candidates} total")
        
        return {
            "message": f"Successfully shortlisted candidates using AI",
            "phase1_count": result.get('phase1_count', 0),
            "shortlisted_count": result.get('shortlisted_count', 0),
            "added": added_count,
            "skipped": skipped_count,
            "total": total_candidates
        }
        
    except Exception as e:
        logger.error(f"❌ Error in CV shortlisting: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/job/{job_id}", response_model=List[Candidate])
async def get_candidates_by_job(
    job_id: str,
    status_filter: CandidateStatus = None
):
    """Get all candidates for a specific job posting"""
    db = get_db()
    
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job posting ID")
    
    query = {"job_posting_id": job_id}
    if status_filter:
        query["status"] = status_filter
    
    cursor = db.candidates.find(query).sort("confidence", -1)
    candidates = []
    
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        candidates.append(Candidate(**doc))
    
    return candidates


@router.get("/{candidate_id}", response_model=Candidate)
async def get_candidate(
    candidate_id: str
):
    """Get a specific candidate"""
    db = get_db()
    
    if not ObjectId.is_valid(candidate_id):
        raise HTTPException(status_code=400, detail="Invalid candidate ID")
    
    candidate_doc = await db.candidates.find_one({"_id": ObjectId(candidate_id)})
    
    if not candidate_doc:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    candidate_doc["_id"] = str(candidate_doc["_id"])
    return Candidate(**candidate_doc)


@router.put("/{candidate_id}", response_model=Candidate)
async def update_candidate(
    candidate_id: str,
    candidate_update: CandidateUpdate
):
    """Update a candidate"""
    db = get_db()
    
    if not ObjectId.is_valid(candidate_id):
        raise HTTPException(status_code=400, detail="Invalid candidate ID")
    
    update_data = {k: v for k, v in candidate_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.candidates.find_one_and_update(
        {"_id": ObjectId(candidate_id)},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    result["_id"] = str(result["_id"])
    logger.info(f"✅ Candidate updated: {candidate_id}")
    
    return Candidate(**result)


@router.post("/approve", status_code=status.HTTP_200_OK)
async def approve_candidates(
    approval: CandidateApproval
):
    """
    Approve candidates for interview and optionally send invitation emails
    """
    db = get_db()
    
    approved_count = 0
    email_sent_count = 0
    errors = []
    
    for candidate_id in approval.candidate_ids:
        try:
            if not ObjectId.is_valid(candidate_id):
                errors.append(f"Invalid candidate ID: {candidate_id}")
                continue
            
            # Get candidate
            candidate = await db.candidates.find_one({"_id": ObjectId(candidate_id)})
            if not candidate:
                errors.append(f"Candidate not found: {candidate_id}")
                continue
            
            # Update status to approved
            await db.candidates.update_one(
                {"_id": ObjectId(candidate_id)},
                {"$set": {"status": CandidateStatus.APPROVED}}
            )
            approved_count += 1
            
            # Send email if requested
            if approval.send_email:
                # Get job posting
                job_posting = await db.job_postings.find_one(
                    {"_id": ObjectId(candidate["job_posting_id"])}
                )
                
                if job_posting:
                    plain_text, html = email_service.generate_interview_invitation_email(
                        candidate_name=candidate["name"],
                        job_title=job_posting["title"]
                    )
                    
                    success = await email_service.send_email(
                        to=[candidate["email"]],
                        subject=f"Interview Invitation - {job_posting['title']}",
                        body=plain_text,
                        html=html
                    )
                    
                    if success:
                        email_sent_count += 1
                        # Update status to email_sent
                        await db.candidates.update_one(
                            {"_id": ObjectId(candidate_id)},
                            {"$set": {"status": CandidateStatus.EMAIL_SENT}}
                        )
                    else:
                        errors.append(f"Failed to send email to: {candidate['email']}")
            
        except Exception as e:
            errors.append(f"Error processing candidate {candidate_id}: {str(e)}")
    
    logger.info(f"✅ Approved {approved_count} candidates, sent {email_sent_count} emails")
    
    return {
        "message": "Candidate approval completed",
        "approved": approved_count,
        "emails_sent": email_sent_count,
        "errors": errors
    }


@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: str
):
    """Delete a candidate"""
    db = get_db()
    
    if not ObjectId.is_valid(candidate_id):
        raise HTTPException(status_code=400, detail="Invalid candidate ID")
    
    result = await db.candidates.delete_one({"_id": ObjectId(candidate_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    logger.info(f"✅ Candidate deleted: {candidate_id}")
    
    return {"message": "Candidate deleted successfully"}
