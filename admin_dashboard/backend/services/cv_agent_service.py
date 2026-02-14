"""
CV Shortlisting Agent Service
"""
import httpx
from typing import List
from config.settings import settings
from models.candidate import CandidateFromCV
import logging

logger = logging.getLogger(__name__)


class CVAgentService:
    """Service to communicate with CV Shortlisting Agent"""
    
    @staticmethod
    async def get_shortlisted_candidates(job_posting_id: str) -> List[CandidateFromCV]:
        """
        Call CV Shortlisting Agent to get shortlisted candidates
        
        Args:
            job_posting_id: ID of the job posting
            
        Returns:
            List of shortlisted candidates
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    f"{settings.cv_agent_url}/shortlist",
                    params={"job_id": job_posting_id}
                )
                response.raise_for_status()
                
                data = response.json()
                candidates = []
                
                # Parse response based on schema
                if "shortlisted" in data:
                    for candidate_data in data["shortlisted"]:
                        candidates.append(CandidateFromCV(**candidate_data))
                
                logger.info(f"✅ Retrieved {len(candidates)} candidates from CV agent")
                return candidates
                
        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to call CV agent: {e}")
            raise Exception(f"Failed to get shortlisted candidates: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Unexpected error calling CV agent: {e}")
            raise


cv_agent_service = CVAgentService()
