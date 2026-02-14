"""
Seed Sample Data for Testing
Creates sample candidates and interviews for demo purposes
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


async def seed_sample_interview(db: AsyncIOMotorDatabase):
    """
    Create a sample candidate and interview for testing the interview portal
    """
    try:
        # Check if sample data already exists
        existing = await db.candidates.find_one({"name": "John Smith"})
        if existing:
            logger.info("✅ Sample data already exists")
            return {
                "candidate_id": str(existing["_id"]),
                "message": "Sample data already exists"
            }
        
        # Create a sample job posting first
        job_posting = {
            "_id": ObjectId(),
            "title": "Senior Python Developer",
            "description": "Looking for an experienced Python developer to join our team.",
            "required_skills": ["Python", "FastAPI", "MongoDB", "React"],
            "department": "Engineering",
            "location": "Remote",
            "salary_range": "$100,000 - $130,000",
            "status": "open",
            "created_at": datetime.utcnow()
        }
        
        # Check if job already exists
        existing_job = await db.job_postings.find_one({"title": "Senior Python Developer"})
        if existing_job:
            job_id = str(existing_job["_id"])
        else:
            await db.job_postings.insert_one(job_posting)
            job_id = str(job_posting["_id"])
            logger.info(f"✅ Created sample job posting: {job_id}")
        
        # Create sample candidate
        candidate_id = ObjectId()
        candidate = {
            "_id": candidate_id,
            "name": "John Smith",
            "email": "john.smith@example.com",
            "skills": ["Python", "FastAPI", "Docker", "MongoDB", "React", "TypeScript"],
            "experience": 6,
            "job_posting_id": job_id,
            "confidence": 0.92,
            "status": "approved",
            "created_at": datetime.utcnow(),
            "cv_path": None,
            "cover_letter": "I am a passionate Python developer with 6 years of experience...",
            "notes": "Sample candidate for demo"
        }
        
        await db.candidates.insert_one(candidate)
        logger.info(f"✅ Created sample candidate: {candidate_id}")
        
        # Create sample interview
        interview_id = ObjectId()
        scheduled_time = datetime.utcnow() + timedelta(hours=2)
        
        interview = {
            "_id": interview_id,
            "candidate_id": str(candidate_id),
            "job_posting_id": job_id,
            "status": "scheduled",
            "scheduled_at": scheduled_time,
            "created_at": datetime.utcnow(),
            "transcript": [],
            "recording_path": None,
            "transcript_path": None,
            "score": None,
            "evaluation": None,
            "notes": "Sample interview for demo - use candidate name 'John Smith' to access",
            "interview_type": "AI Interview"
        }
        
        await db.interviews.insert_one(interview)
        logger.info(f"✅ Created sample interview: {interview_id}")
        
        return {
            "success": True,
            "candidate_id": str(candidate_id),
            "candidate_name": "John Smith",
            "interview_id": str(interview_id),
            "scheduled_at": scheduled_time.isoformat(),
            "message": "Sample interview created! Use candidate name 'John Smith' to login to the interview portal."
        }
        
    except Exception as e:
        logger.error(f"❌ Error seeding sample data: {str(e)}")
        raise


async def seed_multiple_candidates(db: AsyncIOMotorDatabase, job_id: str, count: int = 5):
    """
    Create multiple sample candidates for a job posting
    
    Args:
        db: Database instance
        job_id: Job posting ID
        count: Number of candidates to create
    """
    sample_candidates = [
        {
            "name": "Sarah Johnson",
            "email": "sarah.j@example.com",
            "skills": ["Python", "Django", "PostgreSQL", "AWS"],
            "experience": 5,
            "confidence": 0.88
        },
        {
            "name": "Michael Chen",
            "email": "michael.chen@example.com",
            "skills": ["Python", "FastAPI", "MongoDB", "Docker"],
            "experience": 4,
            "confidence": 0.85
        },
        {
            "name": "Emily Davis",
            "email": "emily.davis@example.com",
            "skills": ["Python", "Flask", "React", "MongoDB"],
            "experience": 3,
            "confidence": 0.82
        },
        {
            "name": "David Kim",
            "email": "david.kim@example.com",
            "skills": ["Python", "FastAPI", "PostgreSQL", "React", "TypeScript"],
            "experience": 7,
            "confidence": 0.95
        },
        {
            "name": "Lisa Anderson",
            "email": "lisa.anderson@example.com",
            "skills": ["Python", "Django", "Vue.js", "Redis"],
            "experience": 4,
            "confidence": 0.78
        }
    ]
    
    inserted_ids = []
    
    for candidate_data in sample_candidates[:count]:
        candidate_id = ObjectId()
        candidate = {
            "_id": candidate_id,
            **candidate_data,
            "job_posting_id": job_id,
            "status": "shortlisted",
            "created_at": datetime.utcnow(),
            "cv_path": None,
            "cover_letter": f"Sample cover letter for {candidate_data['name']}",
            "notes": "Auto-generated sample candidate"
        }
        
        await db.candidates.insert_one(candidate)
        inserted_ids.append(str(candidate_id))
    
    logger.info(f"✅ Created {len(inserted_ids)} sample candidates")
    return inserted_ids
