"""
Manually seed sample data
"""
import requests
import json

print("🌱 Seeding sample data...\n")

url = "http://localhost:8001/dev/seed-sample-interview"

try:
    response = requests.post(url)
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Success!")
        result = response.json()
        print(f"\n📋 Response:")
        print(json.dumps(result, indent=2, default=str))
        
        if result.get("success"):
            print(f"\n🎯 Use this to test:")
            print(f"   Candidate Name: {result.get('candidate_name')}")
            print(f"   Interview Portal: http://localhost:5173/interview")
    else:
        print("❌ Error!")
        print(f"\n📋 Response:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Request failed: {str(e)}")
