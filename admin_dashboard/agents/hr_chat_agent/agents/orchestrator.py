class HROrchestrator:
    def __init__(self, tools, reflector):
        self.tools = tools
        self.reflector = reflector

    def detect_tool(self, query: str):
        query_lower = query.lower()
        employee_keywords = ["leave", "holiday", "balance", "employee info", "leave history", "apply leave", "my info", "my details", "remaining leave"]
        if any(k in query_lower for k in employee_keywords):
            return "employee_db"
        return "policy_rag"

    def handle_query(self, query: str, user_id: str, feedback=None):
        tool_name = self.detect_tool(query)
        tool = self.tools[tool_name]
        response = tool.execute(query, user_id)
        text = response.content.get("text")

        if not text:  # fallback to RAG if employee_db returns None
            response = self.tools["policy_rag"].execute(query, user_id)
            text = response.content.get("text")

        if feedback:
            rating, correction = feedback.get("rating"), feedback.get("correction")
            self.reflector.store_feedback(query, text, rating, correction)

        return text
