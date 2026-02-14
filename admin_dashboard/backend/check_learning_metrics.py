"""
Check learning metrics in database
"""
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client.hr_recruitment_db

print("🔍 Checking agent learning metrics...\n")

# Check agent_metrics collection
metrics = list(db.agent_metrics.find())
print(f"📊 Agent Metrics: {len(metrics)} records")
for m in metrics:
    print(f"\n   Agent: {m.get('agent_type')}")
    print(f"   Total Actions: {m.get('total_actions', 0)}")
    print(f"   Successful: {m.get('successful_actions', 0)}")
    print(f"   Failed: {m.get('failed_actions', 0)}")
    print(f"   Average Rating: {m.get('average_rating', 0)}")
    print(f"   Improvement Rate: {m.get('improvement_rate', 0)}")
    print(f"   Patterns Learned: {m.get('patterns_learned', 0)}")

# Check agent_feedback collection  
feedback_count = db.agent_feedback.count_documents({})
print(f"\n💬 Agent Feedback: {feedback_count} records")

# Check learning_patterns collection
patterns_count = db.learning_patterns.count_documents({})
print(f"\n🧠 Learning Patterns: {patterns_count} records")

if metrics:
    print("\n✅ Metrics data exists")
else:
    print("\n❌ No metrics data found - creating sample data...")
    
    # Create sample metrics for each agent type
    sample_metrics = [
        {
            "agent_type": "cv_shortlisting",
            "version": "1.2.3",
            "total_actions": 45,
            "successful_actions": 38,
            "failed_actions": 7,
            "average_rating": 4.2,
            "improvement_rate": 15.5,
            "patterns_learned": 12,
            "baseline_performance": 0.7
        },
        {
            "agent_type": "interview",
            "version": "1.1.0",
            "total_actions": 23,
            "successful_actions": 19,
            "failed_actions": 4,
            "average_rating": 4.5,
            "improvement_rate": 8.3,
            "patterns_learned": 8,
            "baseline_performance": 0.75
        },
        {
            "agent_type": "email_scheduling",
            "version": "1.0.5",
            "total_actions": 67,
            "successful_actions": 62,
            "failed_actions": 5,
            "average_rating": 4.6,
            "improvement_rate": 12.1,
            "patterns_learned": 15,
            "baseline_performance": 0.8
        },
        {
            "agent_type": "hr_chat",
            "version": "1.3.1",
            "total_actions": 156,
            "successful_actions": 142,
            "failed_actions": 14,
            "average_rating": 4.3,
            "improvement_rate": 18.7,
            "patterns_learned": 24,
            "baseline_performance": 0.72
        }
    ]
    
    db.agent_metrics.insert_many(sample_metrics)
    print("✅ Sample metrics created!")

client.close()
