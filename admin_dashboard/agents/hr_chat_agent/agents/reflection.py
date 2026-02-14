import json
from pathlib import Path

class ReflectionAgent:
    def __init__(self, feedback_file="memory/feedback_store.json"):
        self.feedback_file = Path(feedback_file)
        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.feedback_file.exists():
            self.feedback_file.write_text(json.dumps([]))

    def store_feedback(self, query, response, rating, correction=None):
        data = json.loads(self.feedback_file.read_text())
        data.append({
            "query": query,
            "response": response,
            "rating": rating,
            "correction": correction
        })
        self.feedback_file.write_text(json.dumps(data, indent=2))
