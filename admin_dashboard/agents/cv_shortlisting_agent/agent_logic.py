"""
CV Shortlisting Agent - Intelligent Two-Phase Shortlisting
Phase 1: Keyword-based filtering (fast, no LLM)
Phase 2: LLM-based comprehensive review (accurate)
"""
from typing import List, Dict, Any
import logging
import json
import os
import asyncio
from pathlib import Path

# Import phase shortlisters
from phase1_shortlister import Phase1Shortlister
from phase2_shortlister import Phase2Shortlister

logger = logging.getLogger(__name__)


class CVShortlistingAgent:
    """
    CV Shortlisting Agent Logic
    Uses a two-phase approach:
    1. Phase 1: Quick keyword filtering
    2. Phase 2: Detailed LLM review
    """
    
    def __init__(self):
        self.phase1_shortlister = Phase1Shortlister()
        self.phase2_shortlister = Phase2Shortlister(
            ollama_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model_name=os.getenv("OLLAMA_MODEL", "ministral-3:3b")
        )
        
        # Path to candidate data JSON
        self.candidates_json_path = Path(__file__).parent.parent.parent / "storage" / "candidates_pool.json"
        
    def load_candidate_pool(self) -> List[Dict]:
        """
        Load candidate pool from JSON file
        
        Returns:
            List of candidate dictionaries
        """
        try:
            if self.candidates_json_path.exists():
                with open(self.candidates_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('candidates', [])
            else:
                logger.warning(f"Candidate pool file not found: {self.candidates_json_path}")
                # Return mock data as fallback
                return self._get_mock_candidates()
        except Exception as e:
            logger.error(f"Error loading candidate pool: {e}")
            return self._get_mock_candidates()
    
    def _get_mock_candidates(self) -> List[Dict]:
        """Fallback mock candidates if JSON not found"""
        return [
            {
                "name": "Aarav Mehta",
                "email": "aarav.mehta.dev@gmail.com",
                "skills": ["Python", "Go", "React", "Node.js", "Express", "SQL", "PostgreSQL", "MongoDB", "AWS", "Docker", "Git", "REST API"],
                "experience": 3
            },
            {
                "name": "Priya Nair",
                "email": "priya.nair.dev@gmail.com",
                "skills": ["Python", "React", "Node.js", "FastAPI", "SQL", "MongoDB", "Docker", "Git"],
                "experience": 4
            },
            {
                "name": "Kabir Sharma",
                "email": "kabir.sharma.dev@gmail.com",
                "skills": ["Python", "Go", "React", "Node.js", "FastAPI", "Express", "MongoDB", "AWS", "Docker", "Git", "CSS"],
                "experience": 3
            },
            {
                "name": "Ananya Singh",
                "email": "ananya.singh.tech@gmail.com",
                "skills": ["JavaScript", "React", "Vue.js", "Node.js", "Express", "MySQL", "Git", "CSS"],
                "experience": 2
            },
            {
                "name": "Rohan Verma",
                "email": "rohan.verma.code@gmail.com",
                "skills": ["Python", "Django", "Flask", "PostgreSQL", "Docker", "AWS", "Redis"],
                "experience": 5
            }
        ]
    
    async def fetch_job_details_from_db(self, job_id: str) -> Dict:
        """
        Fetch job posting details from the database
        
        Args:
            job_id: MongoDB ObjectId of the job posting
        
        Returns:
            Dictionary with job details
        """
        try:
            # Import here to avoid circular imports
            import sys
            sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))
            from utils.database import get_db
            from bson import ObjectId
            
            db = get_db()
            job = await db.job_postings.find_one({"_id": ObjectId(job_id)})
            
            if not job:
                raise Exception(f"Job posting not found: {job_id}")
            
            return {
                "title": job.get("title", ""),
                "description": job.get("description", ""),
                "requirements": job.get("requirements", ""),
                "required_skills": job.get("required_skills", []),
                "minimum_experience": job.get("minimum_experience", 0)
            }
        except Exception as e:
            logger.error(f"Error fetching job details: {e}")
            # Return default job details for testing
            return {
                "title": "Software Engineer",
                "description": "We are looking for a talented software engineer",
                "requirements": "Strong programming skills",
                "required_skills": ["Python", "React", "Docker"],
                "minimum_experience": 2
            }
    
    async def shortlist_candidates_async(self, job_id: str) -> Dict[str, Any]:
        """
        Asynchronous shortlisting process
        
        Args:
            job_id: ID of the job posting
            
        Returns:
            Dictionary with shortlisted candidates
        """
        logger.info(f"🔍 Starting two-phase shortlisting for job: {job_id}")
        
        try:
            # Step 1: Load candidate pool
            logger.info("📂 Loading candidate pool...")
            all_candidates = self.load_candidate_pool()
            logger.info(f"   Found {len(all_candidates)} candidates in pool")
            
            # Step 2: Fetch job details
            logger.info("📋 Fetching job details...")
            job_details = await self.fetch_job_details_from_db(job_id)
            logger.info(f"   Job: {job_details['title']}")
            logger.info(f"   Required Skills: {', '.join(job_details['required_skills'])}")
            logger.info(f"   Minimum Experience: {job_details['minimum_experience']} years")
            
            # Step 3: Phase 1 - Keyword filtering
            logger.info("🔎 Phase 1: Keyword-based shortlisting...")
            phase1_candidates = self.phase1_shortlister.shortlist(
                candidates=all_candidates,
                required_skills=job_details['required_skills'],
                minimum_experience=job_details['minimum_experience'],
                target_count=20  # Select top 20 for Phase 2
            )
            logger.info(f"   ✅ Phase 1 complete: {len(phase1_candidates)} candidates selected")
            
            # Step 4: Phase 2 - LLM review
            logger.info("🤖 Phase 2: LLM-based comprehensive review...")
            job_description = f"{job_details['title']}\\n\\n{job_details['description']}\\n\\nRequirements: {job_details['requirements']}"
            
            final_candidates = await self.phase2_shortlister.shortlist(
                candidates=phase1_candidates,
                job_description=job_description,
                required_skills=job_details['required_skills'],
                target_count=10  # Final top 10
            )
            logger.info(f"   ✅ Phase 2 complete: {len(final_candidates)} candidates shortlisted")
            
            # Format output
            return {
                "job_id": job_id,
                "job_title": job_details['title'],
                "total_candidates_reviewed": len(all_candidates),
                "phase1_count": len(phase1_candidates),
                "shortlisted_count": len(final_candidates),
                "shortlisted": final_candidates
            }
            
        except Exception as e:
            logger.error(f"❌ Error in shortlisting process: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def shortlist_candidates(self, job_id: str) -> Dict[str, Any]:
        """
        Synchronous wrapper for shortlisting candidates
        
        Args:
            job_id: ID of the job posting
            
        Returns:
            Dictionary with shortlisted candidates
        """
        # Run async function in event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.shortlist_candidates_async(job_id))


# Global agent instance
cv_agent = CVShortlistingAgent()
