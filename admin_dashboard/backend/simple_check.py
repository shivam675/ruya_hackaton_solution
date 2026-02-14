"""
Simple MongoDB check using pymongo
"""
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client.hr_recruitment_db

print("🔍 Checking MongoDB database...\n")

# Check candidates
candidates = list(db.candidates.find({}))
print(f"📋 Total candidates: {len(candidates)}")
for c in candidates:
    print(f"   - {c.get('name')} (status: {c.get('status')}, id: {c.get('_id')})")

print()

# Check for John Smith specifically
john = db.candidates.find_one({'name': 'John Smith'})
if john:
    print(f"✅ Found John Smith:")
    print(f"   Status: {john.get('status')}")
    print(f"   ID: {john.get('_id')}")
    
    # Check interview
    interview = db.interviews.find_one({'candidate_id': str(john['_id'])})
    if interview:
        print(f"\n✅ Found interview:")
        print(f"   Status: {interview.get('status')}")
        print(f"   Candidate ID: {interview.get('candidate_id')}")
    else:
        print(f"\n❌ No interview found for candidate_id: {str(john['_id'])}")
        
        # Show all interviews
        interviews = list(db.interviews.find({}))
        print(f"\n📋 Total interviews: {len(interviews)}")
        for i in interviews:
            print(f"   - Candidate ID: {i.get('candidate_id')} (status: {i.get('status')})")
else:
    print("❌ No candidate named 'John Smith' found")

client.close()
