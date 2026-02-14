"""
Test job postings API endpoint
"""
import requests

print("🔍 Testing job postings API...\n")

try:
    response = requests.get("http://localhost:8001/job-postings")
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data)} job postings")
        for job in data:
            print(f"\n   Title: {job.get('title')}")
            print(f"   ID: {job.get('_id')}")
            print(f"   Active: {job.get('is_active')}")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    print("   Is the backend running on port 8001?")
