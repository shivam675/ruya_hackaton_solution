"""
Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config.settings import settings
from utils.database import Database, init_database
from utils.seed_sample_data import seed_sample_interview
from routes import auth, job_postings, candidates, interviews, learning, hr_chat, critic, dev

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting HR Recruitment System Backend")
    await Database.connect_db()
    await init_database()
    
    # Seed sample data for testing
    try:
        db = Database.get_db()
        result = await seed_sample_interview(db)
        if result.get("success"):
            logger.info(f"✅ Sample interview data ready: {result.get('message')}")
            logger.info(f"   📝 Candidate: {result.get('candidate_name')}")
            logger.info(f"   🎤 Interview ID: {result.get('interview_id')}")
    except Exception as e:
        logger.warning(f"⚠️  Could not seed sample data: {str(e)}")
    
    logger.info("✅ Backend ready!")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down backend")
    await Database.close_db()


# Create FastAPI application
app = FastAPI(
    title="HR Recruitment System API",
    description="Backend API with Self-Improving AI Agents that Learn, Adapt & Evolve",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.allowed_origins == "*" else settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(job_postings.router)
app.include_router(candidates.router)
app.include_router(interviews.router)
app.include_router(learning.router)
app.include_router(hr_chat.router)
app.include_router(critic.router)
app.include_router(dev.router)  # Development utilities


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HR Recruitment System API with Self-Improving AI Agents",
        "version": "2.0.0",
        "status": "running",
        "features": ["Learning", "Adaptation", "Evolution"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
