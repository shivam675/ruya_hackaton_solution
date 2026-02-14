"""
Manually create sample interview data
"""
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta

client = MongoClient('mongodb://localhost:27017')
db = client.hr_recruitment_db

print("🔧 Creating sample interview data...\n")

# Check if John Smith already exists
existing = db.candidates.find_one({"name": "John Smith"})
if existing:
    print("⚠️  John Smith already exists")
    print(f"   ID: {existing['_id']}")
    print(f"   Status: {existing.get('status')}")
else:
    # Create or find job posting
    job_posting = db.job_postings.find_one({"title": "Senior Python Developer"})
    if not job_posting:
        job_id = ObjectId()
        job_posting = {
            "_id": job_id,
            "title": "Senior Python Developer",
            "description": "Looking for an experienced Python developer to join our team.",
            "job_description": "We are seeking a talented Senior Python Developer with expertise in FastAPI, MongoDB, and React. You will be responsible for building scalable backend systems and working closely with the frontend team.",
            "required_skills": ["Python", "FastAPI", "MongoDB", "React"],
            "min_experience": 5,
            "department": "Engineering",
            "location": "Remote",
            "salary_range": "$100,000 - $130,000",
            "is_active": True,
            "candidates_count": 0,
            "created_at": datetime.utcnow()
        }
        db.job_postings.insert_one(job_posting)
        print(f"✅ Created job posting: {job_id}")
    else:
        job_id = job_posting["_id"]
        print(f"✅ Using existing job: {job_id}")
    
    # Create candidate
    candidate_id = ObjectId()
    candidate = {
        "_id": candidate_id,
        "name": "John Smith",
        "email": "john.smith@example.com",
        "skills": ["Python", "FastAPI", "Docker", "MongoDB", "React", "TypeScript"],
        "experience": 6,
        "job_posting_id": str(job_id),
        "confidence": 0.92,
        "status": "approved",
        "created_at": datetime.utcnow(),
        "cv_path": None,
        "cover_letter": "I am a passionate Python developer with 6 years of experience in building scalable web applications.",
        "notes": "Sample candidate for demo"
    }
    
    db.candidates.insert_one(candidate)
    print(f"✅ Created candidate: John Smith ({candidate_id})")
    
    # Create interview
    interview_id = ObjectId()
    scheduled_time = datetime.utcnow() + timedelta(hours=2)
    
    interview = {
        "_id": interview_id,
        "candidate_id": str(candidate_id),
        "job_posting_id": str(job_id),
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
    
    db.interviews.insert_one(interview)
    print(f"✅ Created interview: {interview_id}")
    print(f"   Scheduled: {scheduled_time}")

print("\n🎯 Sample data ready!")
print("   Candidate: John Smith")
print("   Portal: http://localhost:5173/interview")

# Verify
print("\n🔍 Verification:")
john = db.candidates.find_one({"name": "John Smith"})
if john:
    print(f"✅ Candidate exists (status: {john['status']})")
    interview = db.interviews.find_one({"candidate_id": str(john['_id'])})
    if interview:
        print(f"✅ Interview exists (status: {interview['status']})")
    else:
        print("❌ Interview not found")
else:
    print("❌ Candidate not found")

client.close()
