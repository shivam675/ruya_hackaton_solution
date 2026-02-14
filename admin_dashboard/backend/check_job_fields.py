"""
Check job posting fields
"""
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client.hr_recruitment_db

print("🔍 Checking job postings fields...\n")

jobs = list(db.job_postings.find())
print(f"📋 Total job postings: {len(jobs)}\n")

for job in jobs:
    print(f"Title: {job.get('title')}")
    print(f"  - has job_description: {('job_description' in job)}")
    print(f"  - has created_by: {('created_by' in job)}")
    print(f"  - has created_at: {('created_at' in job)}")
    print(f"  - has is_active: {('is_active' in job)}")
    print(f"  - has candidates_count: {('candidates_count' in job)}")
    print()

client.close()
