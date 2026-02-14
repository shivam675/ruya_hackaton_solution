"""
Job Posting Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId
from models.job_posting import JobPosting, JobPostingCreate, JobPostingUpdate
from utils.database import get_db
import logging

router = APIRouter(prefix="/job-postings", tags=["Job Postings"])
logger = logging.getLogger(__name__)


@router.post("", response_model=JobPosting, status_code=status.HTTP_201_CREATED)
async def create_job_posting(
    job_posting: JobPostingCreate
):
    """Create a new job posting"""
    db = get_db()
    
    job_doc = {
        **job_posting.model_dump(),
        "is_active": True,
        "created_at": datetime.utcnow(),
        "created_by": "system",
        "candidates_count": 0
    }
    
    result = await db.job_postings.insert_one(job_doc)
    job_doc["_id"] = str(result.inserted_id)
    
    logger.info(f"✅ Job posting created: {job_doc['title']}")
    
    return JobPosting(**job_doc)


@router.get("", response_model=List[JobPosting])
async def get_job_postings(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None
):
    """Get all job postings"""
    db = get_db()
    
    query = {}
    if is_active is not None:
        query["is_active"] = is_active
    
    cursor = db.job_postings.find(query).skip(skip).limit(limit).sort("created_at", -1)
    job_postings = []
    
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        job_postings.append(JobPosting(**doc))
    
    return job_postings


@router.get("/{job_id}", response_model=JobPosting)
async def get_job_posting(
    job_id: str
):
    """Get a specific job posting"""
    db = get_db()
    
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job posting ID")
    
    job_doc = await db.job_postings.find_one({"_id": ObjectId(job_id)})
    
    if not job_doc:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    job_doc["_id"] = str(job_doc["_id"])
    return JobPosting(**job_doc)


@router.put("/{job_id}", response_model=JobPosting)
async def update_job_posting(
    job_id: str,
    job_update: JobPostingUpdate
):
    """Update a job posting"""
    db = get_db()
    
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job posting ID")
    
    update_data = {k: v for k, v in job_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.job_postings.find_one_and_update(
        {"_id": ObjectId(job_id)},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    result["_id"] = str(result["_id"])
    logger.info(f"✅ Job posting updated: {job_id}")
    
    return JobPosting(**result)


@router.delete("/{job_id}")
async def delete_job_posting(
    job_id: str
):
    """Delete a job posting (soft delete by setting is_active to False)"""
    db = get_db()
    
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job posting ID")
    
    result = await db.job_postings.find_one_and_update(
        {"_id": ObjectId(job_id)},
        {"$set": {"is_active": False}},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    logger.info(f"✅ Job posting deleted: {job_id}")
    
    return {"message": "Job posting deleted successfully"}
