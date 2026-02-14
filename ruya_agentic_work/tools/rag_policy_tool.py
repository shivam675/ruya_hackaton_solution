import subprocess
import chromadb
from chromadb.utils import embedding_functions
from .base_tool import BaseTool, MCPResponse

class RAGPolicyTool(BaseTool):
    tool_name = "policy_rag"

    def __init__(self, db_dir="chroma_db"):
        self.client = chromadb.PersistentClient(path=db_dir)
        self.collection_name = "hr_policies"

        existing_collections = [c.name for c in self.client.list_collections()]
        if self.collection_name in existing_collections:
            self.collection = self.client.get_collection(self.collection_name)
        else:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            )

    def query_ollama(self, prompt: str) -> str:
        try:
            result = subprocess.run(
                ["ollama", "run", "ministral-3:3b", prompt],
                capture_output=True,
                text=True,
                encoding="utf-8",      # <-- force UTF-8 decoding
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"

    def execute(self, query: str, user_id: str) -> MCPResponse:
        results = self.collection.query(
            query_texts=[query],
            n_results=3,
            include=["documents"]
        )

        context_docs = results.get("documents", [[]])[0]
        context = " ".join(context_docs) if context_docs else ""

        prompt = f"""You are a helpful HR assistant.
Use the context below to answer the question in clear, normal English.

CONTEXT:
{context}

QUESTION:
{query}
"""
        answer = self.query_ollama(prompt)

        return MCPResponse(
            role="tool",
            tool_name=self.tool_name,
            content={"text": answer},
            confidence=0.92
        )
