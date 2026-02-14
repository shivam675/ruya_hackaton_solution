import json
from pathlib import Path

FEEDBACK_FILE = Path("memory/feedback_store.json")

class ReflectionAgent:
    def __init__(self):
        FEEDBACK_FILE.parent.mkdir(exist_ok=True)
        if not FEEDBACK_FILE.exists():
            FEEDBACK_FILE.write_text(json.dumps([]))

    def store_feedback(self, query, response, rating, correction=None):
        data = json.loads(FEEDBACK_FILE.read_text())
        data.append({
            "query": query,
            "response": response,
            "rating": rating,
            "correction": correction
        })
        FEEDBACK_FILE.write_text(json.dumps(data, indent=2))
