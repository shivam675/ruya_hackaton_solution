"""
CV Shortlisting Agent Microservice
Port: 8002
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import logging
from agent_logic import cv_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CV Shortlisting Agent",
    description="Microservice for CV analysis and candidate shortlisting",
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
        "service": "CV Shortlisting Agent",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/shortlist")
async def get_shortlisted_candidates(job_id: str = Query(..., description="Job posting ID")):
    """
    Get shortlisted candidates for a job posting
    
    This endpoint is called by the main backend when the user clicks
    the "Fetch Candidates" button.
    
    Returns:
        JSON matching SLA_output_schema.json format
    """
    logger.info(f"📋 Received shortlist request for job: {job_id}")
    
    try:
        result = cv_agent.shortlist_candidates(job_id)
        logger.info(f"✅ Returning {len(result['shortlisted'])} candidates")
        return result
    except Exception as e:
        logger.error(f"❌ Error shortlisting candidates: {e}")
        return {
            "error": str(e),
            "shortlisted": []
        }


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting CV Shortlisting Agent on port 8002")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
