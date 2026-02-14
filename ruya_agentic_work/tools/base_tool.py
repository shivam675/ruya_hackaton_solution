from pydantic import BaseModel
from typing import Dict, Any, Optional

class MCPResponse(BaseModel):
    role: str
    tool_name: str
    content: Dict[str, Any]
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = None

class BaseTool:
    tool_name: str

    def execute(self, query: str, user_id: str) -> MCPResponse:
        raise NotImplementedError
