"""
Quick script to check if sample data exists
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_data():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.hr_recruitment_db
    
    print("🔍 Checking for sample data...\n")
    
    # Check candidate
    candidate = await db.candidates.find_one({'name': 'John Smith'})
    if candidate:
        print(f"✅ Found candidate:")
        print(f"   Name: {candidate.get('name')}")
        print(f"   Email: {candidate.get('email')}")
        print(f"   Status: {candidate.get('status')}")
        print(f"   ID: {candidate.get('_id')}")
    else:
        print("❌ No candidate named 'John Smith' found")
        
        # Check all candidates
        all_candidates = await db.candidates.find({}).to_list(length=10)
        print(f"\n📋 Total candidates in DB: {len(all_candidates)}")
        for c in all_candidates:
            print(f"   - {c.get('name')} (status: {c.get('status')})")
    
    print()
    
    # Check interviews
    if candidate:
        interview = await db.interviews.find_one({'candidate_id': str(candidate['_id'])})
        if interview:
            print(f"✅ Found interview:")
            print(f"   Candidate ID: {interview.get('candidate_id')}")
            print(f"   Status: {interview.get('status')}")
            print(f"   Scheduled: {interview.get('scheduled_at')}")
            print(f"   ID: {interview.get('_id')}")
        else:
            print(f"❌ No interview found for candidate ID: {candidate['_id']}")
            
            # Check all interviews
            all_interviews = await db.interviews.find({}).to_list(length=10)
            print(f"\n📋 Total interviews in DB: {len(all_interviews)}")
            for i in all_interviews:
                print(f"   - Candidate ID: {i.get('candidate_id')} (status: {i.get('status')})")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(check_data())
