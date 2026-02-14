"""
Test the candidate auth endpoint
"""
import requests
import json

url = "http://localhost:8001/interviews/candidate-auth"
data = {"name": "John Smith"}

print(f"🔍 Testing: POST {url}")
print(f"📤 Payload: {json.dumps(data, indent=2)}\n")

try:
    response = requests.post(url, json=data)
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Success!")
        result = response.json()
        print(f"\n📋 Response:")
        print(json.dumps(result, indent=2, default=str))
    else:
        print("❌ Error!")
        print(f"\n📋 Response:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Request failed: {str(e)}")
