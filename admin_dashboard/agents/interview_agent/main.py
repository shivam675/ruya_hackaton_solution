"""
Interview Agent Microservice
Port: 8004
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import json
import base64

from interview_controller import interview_controller
from tts_service import tts_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Interview Agent",
    description="AI-powered interview agent with STT, LLM, and TTS",
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


class StartInterviewRequest(BaseModel):
    """Request to start interview"""
    interview_id: str
    job_description: str


class ProcessResponseRequest(BaseModel):
    """Request to process candidate response"""
    interview_id: str
    candidate_text: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Interview Agent",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/start-interview")
async def start_interview(request: StartInterviewRequest):
    """
    Start a new interview session
    
    Args:
        request: Interview ID and job description
        
    Returns:
        Interview session data with initial greeting
    """
    try:
        result = interview_controller.start_interview(
            request.interview_id,
            request.job_description
        )
        
        # Generate audio for greeting
        audio_bytes = tts_service.synthesize_to_bytes(result["greeting"])
        
        return {
            **result,
            "greeting_audio": base64.b64encode(audio_bytes).decode() if audio_bytes else None
        }
    except Exception as e:
        logger.error(f"❌ Error starting interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-response")
async def process_response(request: ProcessResponseRequest):
    """
    Process candidate's text response
    
    Args:
        request: Interview ID and candidate's text
        
    Returns:
        Interviewer's response with audio
    """
    try:
        result = interview_controller.process_candidate_response(
            request.interview_id,
            request.candidate_text
        )
        
        # For now, return text response
        # Audio streaming happens via WebSocket
        return result
    except Exception as e:
        logger.error(f"❌ Error processing response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/end-interview/{interview_id}")
async def end_interview(interview_id: str):
    """
    End an interview session
    
    Args:
        interview_id: Interview ID
        
    Returns:
        Final interview data with transcript
    """
    try:
        result = interview_controller.end_interview(interview_id)
        return result
    except Exception as e:
        logger.error(f"❌ Error ending interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/interview-status/{interview_id}")
async def get_interview_status(interview_id: str):
    """Get current interview status"""
    status = interview_controller.get_interview_status(interview_id)
    return status


@app.websocket("/ws/interview/{interview_id}")
async def interview_websocket(websocket: WebSocket, interview_id: str):
    """
    WebSocket endpoint for real-time interview
    
    Message format:
    Client -> Server:
    {
        "type": "audio" | "text" | "control",
        "data": <audio_bytes_base64> | <text> | <control_command>
    }
    
    Server -> Client:
    {
        "type": "audio" | "text" | "transcript" | "status",
        "data": <response_data>
    }
    """
    await websocket.accept()
    logger.info(f"🔌 WebSocket connected for interview: {interview_id}")
    
    connection_closed = False
    
    try:
        # Send initial greeting
        status = interview_controller.get_interview_status(interview_id)
        if status.get("status") == "not_found":
            await websocket.send_json({
                "type": "error",
                "data": "Interview not found. Please start interview first."
            })
            await websocket.close()
            connection_closed = True
            return
        
        # WebSocket message handling loop
        while True:
            try:
                # Receive message from client
                message = await websocket.receive_text()
                data = json.loads(message)
                
                msg_type = data.get("type")
                msg_data = data.get("data")
                
                if msg_type == "text":
                    # Process text input (transcribed by client)
                    result = interview_controller.process_candidate_response(
                        interview_id,
                        msg_data
                    )
                    
                    # Send interviewer's response
                    await websocket.send_json({
                        "type": "text",
                        "data": result["interviewer_response"]
                    })
                    
                    # Send audio for each sentence
                    for sentence in result["sentences"]:
                        audio_bytes = tts_service.synthesize_to_bytes(sentence)
                        if audio_bytes:
                            await websocket.send_json({
                                "type": "audio",
                                "data": base64.b64encode(audio_bytes).decode(),
                                "sentence": sentence
                            })
                    
                    # Send transcript update
                    await websocket.send_json({
                        "type": "transcript",
                        "data": result["transcript_entry"]
                    })
                
                elif msg_type == "audio":
                    # Handle raw audio (future: transcribe here)
                    await websocket.send_json({
                        "type": "status",
                        "data": "Audio received, transcription not yet implemented"
                    })
                
                elif msg_type == "control":
                    if msg_data == "end":
                        # End interview
                        result = interview_controller.end_interview(interview_id)
                        await websocket.send_json({
                            "type": "status",
                            "data": "Interview ended",
                            "transcript_path": result["transcript_path"]
                        })
                        break
                
            except WebSocketDisconnect:
                logger.info(f"🔌 WebSocket disconnected: {interview_id}")
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"❌ WebSocket error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "data": str(e)
                })
    
    finally:
        if not connection_closed:
            try:
                await websocket.close()
            except RuntimeError:
                pass  # Already closed
        logger.info(f"🔌 WebSocket closed: {interview_id}")


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Interview Agent on port 8004")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )
