from tools.employee_db_tool import EmployeeDBTool
from tools.rag_policy_tool import RAGPolicyTool
from agents.reflection import ReflectionAgent
from agents.orchestrator import HROrchestrator

employee_tool = EmployeeDBTool()
rag_tool = RAGPolicyTool(db_dir="chroma_db")

tools = {
    "employee_db": employee_tool,
    "policy_rag": rag_tool
}

reflector = ReflectionAgent()
orchestrator = HROrchestrator(tools, reflector)

user_id = "E001"
print("HR Agent (Ollama Mistral 3B) running. Type 'exit' to quit.\n")

while True:
    query = input("You: ")
    if query.lower() in ["exit", "quit"]:
        break

    response = orchestrator.handle_query(query, user_id)
    print(f"Agent: {response}\n")

    feedback = input("Rate 1-5 (or enter to skip): ").strip()
    if feedback:
        rating = int(feedback)
        correction = input("Correction (optional): ").strip() or None
        orchestrator.handle_query(query, user_id, feedback={"rating": rating, "correction": correction})
