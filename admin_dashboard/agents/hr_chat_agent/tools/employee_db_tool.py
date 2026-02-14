import json
from datetime import datetime
from base_tool import BaseTool, MCPResponse

class EmployeeDBTool(BaseTool):
    tool_name = "employee_db"

    def __init__(self, db_path="employee_db.json"):
        self.db_path = db_path
        with open(db_path, "r") as f:
            self.employee_db = json.load(f)

    def get_employee(self, employee_id):
        return next((e for e in self.employee_db["employees"] if e["employee_id"] == employee_id), None)

    def save_db(self):
        with open(self.db_path, "w") as f:
            json.dump(self.employee_db, f, indent=2)

    def apply_leave(self, employee_id, leave_type, start_date, end_date, notes=""):
        employee = self.get_employee(employee_id)
        if not employee:
            return "Employee not found."

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        duration_days = (end_dt - start_dt).days + 1

        leave_id = f"L{len(employee['leave_history']) + 1:03d}"
        new_leave = {
            "leave_id": leave_id,
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "duration_days": duration_days,
            "status": "Pending",
            "request_date": datetime.today().strftime("%Y-%m-%d"),
            "notes": notes
        }

        employee["leave_history"].append(new_leave)
        employee["remaining_leave"] -= duration_days
        self.save_db()
        return f"Leave applied for {duration_days} day(s). Remaining leave: {employee['remaining_leave']}"

    def execute(self, query: str, user_id: str) -> MCPResponse:
        employee = self.get_employee(user_id)
        if not employee:
            return MCPResponse(role="tool", tool_name=self.tool_name, content={"text": "Employee not found."}, confidence=0.9)

        query_lower = query.lower()

        if any(k in query_lower for k in ["leave balance", "remaining leave", "leaves left", "how many leave"]):
            text = f"{employee['first_name']} has {employee['remaining_leave']} leaves remaining."
        elif any(k in query_lower for k in ["apply leave", "request leave", "holiday request"]):
            text = self.apply_leave(employee_id=user_id, leave_type="Annual",
                                    start_date="2026-02-20", end_date="2026-02-22",
                                    notes="Vacation")
        elif any(k in query_lower for k in ["leave history", "past leaves"]):
            leaves = employee["leave_history"]
            if not leaves:
                text = "No leave history found."
            else:
                text = "\n".join([f"{l['leave_type']} from {l['start_date']} to {l['end_date']} ({l['duration_days']} days) - {l['status']}" for l in leaves])
        elif any(k in query_lower for k in ["my info", "employee info", "my details"]):
            text = f"Name: {employee['first_name']} {employee['last_name']}\nDepartment: {employee['department']}\nRole: {employee['role']}\nJoined: {employee['date_joined']}"
        else:
            text = None  # fallback to RAG

        return MCPResponse(role="tool", tool_name=self.tool_name, content={"text": text}, confidence=0.95)
