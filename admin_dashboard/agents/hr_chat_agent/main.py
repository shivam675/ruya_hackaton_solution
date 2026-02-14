"""
HR Chat Agent Microservice (Scaffold for Future Development)
Port: 8005

This is a placeholder for your team member's Internal HR Chat Agent.
It provides a basic WebSocket endpoint for streaming chat responses.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HR Chat Agent",
    description="Internal HR chatbot for employee queries (Scaffold)",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "HR Chat Agent",
        "version": "1.0.0",
        "status": "running (scaffold)",
        "note": "This is a placeholder for future HR chat functionality"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for HR chat
    Designed for Flutter frontend streaming
    
    Message format:
    Client -> Server:
    {
        "message": "user query"
    }
    
    Server -> Client:
    {
        "type": "text" | "error",
        "data": "response text"
    }
    """
    await websocket.accept()
    logger.info("🔌 HR Chat WebSocket connected")
    
    try:
        while True:
            try:
                # Receive message from client
                message = await websocket.receive_text()
                data = json.loads(message)
                
                user_message = data.get("message", "")
                logger.info(f"💬 User: {user_message}")
                
                # Mock response (replace with actual HR chat logic)
                response = f"Echo: {user_message}"
                
                # Stream response (character by character for demo)
                for char in response:
                    await websocket.send_json({
                        "type": "text",
                        "data": char
                    })
                
                # Send completion signal
                await websocket.send_json({
                    "type": "complete",
                    "data": ""
                })
                
            except WebSocketDisconnect:
                logger.info("🔌 HR Chat WebSocket disconnected")
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"❌ Chat error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "data": str(e)
                })
    
    finally:
        await websocket.close()
        logger.info("🔌 HR Chat WebSocket closed")


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting HR Chat Agent on port 8005")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="info"
    )
