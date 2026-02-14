"""
Development utility routes for manual data seeding
"""
from fastapi import APIRouter, Depends
from utils.database import get_db
from utils.seed_sample_data import seed_sample_interview, seed_multiple_candidates
from typing import Optional

router = APIRouter(prefix="/dev", tags=["Development"])


@router.post("/seed-sample-interview")
async def create_sample_interview(db=Depends(get_db)):
    """
    Manually create sample interview data for testing
    
    Creates:
    - A sample job posting (if doesn't exist)
    - A sample candidate (John Smith)
    - A sample interview scheduled for 2 hours from now
    
    Use candidate name "John Smith" to login to the interview portal.
    """
    result = await seed_sample_interview(db)
    return result


@router.post("/seed-candidates/{job_id}")
async def create_sample_candidates(
    job_id: str,
    count: int = 5,
    db=Depends(get_db)
):
    """
    Create multiple sample candidates for a specific job posting
    
    Args:
        job_id: Job posting ID
        count: Number of candidates to create (max 5)
    """
    if count > 5:
        count = 5
    
    candidate_ids = await seed_multiple_candidates(db, job_id, count)
    
    return {
        "success": True,
        "job_id": job_id,
        "candidates_created": len(candidate_ids),
        "candidate_ids": candidate_ids
    }
