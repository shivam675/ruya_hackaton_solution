"""
Example usage of Self-Improving AI Agents
Demonstrates how to use the learning API
"""

import requests
from typing import Dict, Any

# Base URL
BASE_URL = "http://localhost:8001"
TOKEN = ""  # Set after login


def login():
    """Login and get token"""
    global TOKEN
    import base64
    credentials = base64.b64encode(b"admin@admin.com:password123").decode()
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        headers={"Authorization": f"Basic {credentials}"}
    )
    TOKEN = response.json()["access_token"]
    print(f"✅ Logged in, token: {TOKEN[:20]}...")


def submit_interview_feedback():
    """Example: Submit feedback on an interview"""
    feedback = requests.post(
        f"{BASE_URL}/learning/feedback",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "agent_type": "interview",
            "feedback_type": "positive",
            "context": {
                "interview_id": "test_123",
                "questions": [
                    "Describe your experience with microservices",
                    "How do you handle production incidents?",
                    "Explain your approach to debugging"
                ],
                "job_level": "senior"
            },
            "outcome": {
                "candidate_hired": True,
                "interview_quality": "excellent"
            },
            "user_rating": 5,
            "user_comments": "Perfect questions for senior role, very insightful"
        }
    )
    print(f"✅ Feedback submitted: {feedback.json()}")


def rate_interview_question():
    """Example: Rate a specific interview question"""
    response = requests.post(
        f"{BASE_URL}/learning/interview/rate-question",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "interview_id": "test_123",
            "question": "Describe a challenging bug you debugged in production",
            "rating": 5,
            "comments": "Great question, revealed problem-solving skills"
        }
    )
    print(f"✅ Question rated: {response.json()}")


def record_hiring_outcome():
    """Example: Record whether a candidate was hired"""
    response = requests.post(
        f"{BASE_URL}/learning/cv/rate-candidate-selection",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "candidate_id": "candidate_456",
            "was_hired": True,
            "rating": 5,
            "candidate_data": {
                "name": "John Doe",
                "skills": ["Python", "FastAPI", "MongoDB", "Docker"],
                "experience": 6
            }
        }
    )
    print(f"✅ Hiring outcome recorded: {response.json()}")


def correct_email_parsing():
    """Example: Correct an email parsing mistake"""
    response = requests.post(
        f"{BASE_URL}/learning/email/correct-parsing",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "original_text": "I'm free next Thu 3pm-5pm EST",
            "incorrect_result": {},
            "correct_result": {
                "time_slots": [{
                    "day": "Thursday",
                    "start_time": "15:00",
                    "end_time": "17:00"
                }],
                "timezone": "EST"
            }
        }
    )
    print(f"✅ Correction recorded: {response.json()}")


def get_agent_metrics():
    """Example: View performance metrics for all agents"""
    response = requests.get(
        f"{BASE_URL}/learning/metrics",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    metrics = response.json()
    
    print("\n📊 Agent Performance Metrics:")
    for agent_metrics in metrics:
        print(f"\n{agent_metrics['agent_type'].upper()}:")
        print(f"  Total actions: {agent_metrics['total_actions']}")
        print(f"  Success rate: {agent_metrics['successful_actions'] / agent_metrics['total_actions'] * 100:.1f}%")
        print(f"  Average rating: {agent_metrics['average_rating']:.2f}/5")
        print(f"  Improvement: {agent_metrics['improvement_rate']:.1f}%")
        print(f"  Patterns learned: {agent_metrics['patterns_learned']}")


def get_learning_insights():
    """Example: Get detailed learning insights for Interview Agent"""
    response = requests.get(
        f"{BASE_URL}/learning/insights/interview",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    insights = response.json()
    
    print("\n🧠 Interview Agent Learning Insights:")
    print(f"Learning enabled: {insights['learning_state']['learning_enabled']}")
    print(f"Auto-adapt: {insights['learning_state']['auto_adapt']}")
    print(f"Exploration rate: {insights['learning_state']['exploration_rate']}")
    print(f"Performance trend: {insights['performance_trend']}")
    
    print("\nTop learned patterns:")
    for pattern in insights['top_patterns'][:5]:
        print(f"  - {pattern['pattern_data'].get('question', 'N/A')}")
        print(f"    Success rate: {pattern['success_rate']:.2%}")
        print(f"    Used {pattern['usage_count']} times")


def configure_learning():
    """Example: Configure learning behavior"""
    response = requests.put(
        f"{BASE_URL}/learning/state/interview",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "learning_enabled": True,
            "auto_adapt": True,
            "exploration_rate": 0.15  # 15% exploration
        }
    )
    print(f"✅ Learning configured: {response.json()}")


def view_evolution_history():
    """Example: View how the agent evolved over time"""
    response = requests.get(
        f"{BASE_URL}/learning/evolution/interview",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    evolution = response.json()
    
    print(f"\n📈 Evolution History ({evolution['total_versions']} versions):")
    for version in evolution['performance_trend']:
        print(f"  Version {version['version']}: Performance {version['performance_score']:.2f}")


def demo_full_workflow():
    """Demonstrate complete self-improvement workflow"""
    print("\n" + "="*60)
    print("🚀 SELF-IMPROVING AI AGENTS - DEMO")
    print("="*60)
    
    # 1. Login
    print("\n[1/8] Logging in...")
    login()
    
    # 2. Get baseline metrics
    print("\n[2/8] Getting baseline metrics...")
    get_agent_metrics()
    
    # 3. Submit interview feedback
    print("\n[3/8] Submitting interview feedback...")
    submit_interview_feedback()
    
    # 4. Rate specific question
    print("\n[4/8] Rating interview question...")
    rate_interview_question()
    
    # 5. Record hiring outcome
    print("\n[5/8] Recording hiring outcome...")
    record_hiring_outcome()
    
    # 6. Correct parsing error
    print("\n[6/8] Correcting parsing error...")
    correct_email_parsing()
    
    # 7. View updated metrics
    print("\n[7/8] Viewing updated metrics...")
    get_agent_metrics()
    
    # 8. Get learning insights
    print("\n[8/8] Getting learning insights...")
    get_learning_insights()
    
    print("\n" + "="*60)
    print("✅ Demo complete! Agents are now smarter.")
    print("="*60)


if __name__ == "__main__":
    # Run full demo
    demo_full_workflow()
    
    # Additional examples
    print("\n\n💡 Additional Examples:")
    configure_learning()
    view_evolution_history()
