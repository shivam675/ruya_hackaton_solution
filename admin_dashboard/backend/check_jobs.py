"""
Check job postings in database
"""
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client.hr_recruitment_db

print("🔍 Checking job postings...\n")

jobs = list(db.job_postings.find())
print(f"📋 Total job postings: {len(jobs)}")

if jobs:
    for job in jobs:
        print(f"\n   Title: {job.get('title')}")
        print(f"   ID: {job.get('_id')}")
        print(f"   Active: {job.get('is_active')}")
        print(f"   Location: {job.get('location')}")
        print(f"   Required Skills: {job.get('required_skills')}")
else:
    print("   ❌ No job postings found")

client.close()
