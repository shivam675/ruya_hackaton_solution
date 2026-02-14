"""
Test learning metrics API endpoint
"""
import requests

print("🔍 Testing learning metrics API...\n")

try:
    response = requests.get("http://localhost:8001/learning/metrics")
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data)} agent metrics\n")
        for agent in data:
            print(f"Agent: {agent.get('agent_type')}")
            print(f"  Total Actions: {agent.get('total_actions')}")
            print(f"  Success Rate: {agent.get('successful_actions')}/{agent.get('total_actions')} = {(agent.get('successful_actions', 0) / agent.get('total_actions', 1) * 100):.1f}%")
            print(f"  Improvement: {agent.get('improvement_rate')}%")
            print(f"  Patterns: {agent.get('patterns_learned')}")
            print(f"  Rating: {agent.get('average_rating')}/5")
            print()
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    print("   Is the backend running on port 8001?")
