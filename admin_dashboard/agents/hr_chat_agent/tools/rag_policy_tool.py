import subprocess
import chromadb
from chromadb.utils import embedding_functions
from base_tool import BaseTool, MCPResponse
import os

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
                encoding="utf-8",
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"
        except FileNotFoundError:
            return "Ollama is not installed or not in PATH. Please install Ollama to use RAG features."

    def execute(self, query: str, user_id: str) -> MCPResponse:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=3,
                include=["documents"]
            )

            context_docs = results.get("documents", [[]])[0]
            context = " ".join(context_docs) if context_docs else ""

            if not context:
                # Fallback response if no context found
                answer = f"I don't have specific information about '{query}' in our HR policies. Could you please rephrase your question or contact HR directly?"
            else:
                prompt = f"""You are a helpful HR assistant.
Use the context below to answer the question in clear, normal English.

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:"""
                answer = self.query_ollama(prompt)

            return MCPResponse(
                role="tool",
                tool_name=self.tool_name,
                content={"text": answer},
                confidence=0.92
            )
        except Exception as e:
            return MCPResponse(
                role="tool",
                tool_name=self.tool_name,
                content={"text": f"I apologize, but I encountered an error: {str(e)}. Please try again or contact HR support."},
                confidence=0.5
            )
