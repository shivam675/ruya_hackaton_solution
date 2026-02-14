"""
Phase 2 Shortlister: LLM-based comprehensive review using Ollama
Uses AI to deeply analyze candidate fit beyond keyword matching
"""
import json
from typing import List, Dict, Optional
import httpx
import asyncio


class Phase2Shortlister:
    """
    Phase 2: LLM-based comprehensive review using Ollama
    """

    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "ministral-3:3b"):
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.client = httpx.AsyncClient(timeout=120.0)

    async def shortlist(
        self,
        candidates: List[Dict],
        job_description: str,
        required_skills: List[str],
        target_count: int = 10
    ) -> List[Dict]:
        """
        Use LLM to comprehensively review candidates and shortlist the best matches
        
        Args:
            candidates: List of candidate dictionaries from Phase 1
            job_description: Full job description text
            required_skills: List of required skills/technologies
            target_count: Number of final candidates to select
        
        Returns:
            List of shortlisted candidates with confidence scores and cover letters
        """

        shortlisted_candidates = []

        print(f"Phase 2: Starting LLM review of {len(candidates)} candidates...")

        for i, candidate in enumerate(candidates, 1):
            try:
                print(f"  [{i}/{len(candidates)}] Reviewing {candidate.get('name', 'Unknown')}...")
                result = await self.review_candidate(candidate, job_description, required_skills)
                if result:
                    shortlisted_candidates.append(result)
                    print(f"    ✅ Shortlisted with confidence {result['confidence']:.2f}")
                else:
                    print(f"    ❌ Not suitable")
            except Exception as e:
                import traceback
                print(f"    ⚠️ Error reviewing {candidate.get('name', 'Unknown')}: {e}")
                print(f"    Traceback: {traceback.format_exc()}")
                continue

        print(f"Phase 2: Completed. {len(shortlisted_candidates)} candidates shortlisted.")

        # Sort by confidence score
        shortlisted_candidates.sort(key=lambda x: x['confidence'], reverse=True)

        # Take top N candidates
        final_shortlist = shortlisted_candidates[:target_count]

        return final_shortlist

    async def review_candidate(
        self,
        candidate: Dict,
        job_description: str,
        required_skills: List[str]
    ) -> Optional[Dict]:
        """
        Review a single candidate using LLM
        
        Args:
            candidate: Dictionary with keys: name, email, skills, experience, phase1_score
            job_description: Job description text
            required_skills: List of required skills
        
        Returns:
            Enhanced candidate dict with confidence and cover_letter, or None if not suitable
        """

        prompt = self.create_review_prompt(candidate, job_description, required_skills)

        # Call Ollama API
        response = await self.call_ollama(prompt)

        # Parse LLM response
        result = self.parse_llm_response(response, candidate)

        return result

    def create_review_prompt(self, candidate: Dict, job_description: str, required_skills: List[str]) -> str:
        """
        Create a comprehensive prompt for LLM to review the candidate
        """

        skills_str = ', '.join(candidate.get('skills', []))
        experience = candidate.get('experience', 'Not specified')
        
        prompt = f"""You are an expert HR recruiter. Review the following candidate against the job requirements and provide a detailed assessment.

Job Description:
{job_description}

Required Skills: {', '.join(required_skills)}

Candidate Information:
Name: {candidate.get('name', 'Unknown')}
Email: {candidate.get('email', 'Not provided')}
Skills: {skills_str}
Experience: {experience} years
Phase 1 Match Score: {candidate.get('phase1_score', 0.0):.2f}

Based on this information, provide your assessment in the following JSON format:
{{
    "is_suitable": true or false,
    "confidence": 0.0 to 1.0 (confidence score - how well does this candidate match the job?),
    "reasoning": "Brief explanation of your decision (2-3 sentences)",
    "cover_letter": "A personalized cover letter (3-4 sentences) highlighting the candidate's relevant experience and skills for this specific position"
}}

Respond ONLY with the JSON object, no additional text."""

        return prompt

    async def call_ollama(self, prompt: str) -> str:
        """
        Call Ollama API with the prompt
        """

        try:
            print(f"      Calling Ollama API ({self.model_name})...")
            response = await self.client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )

            response.raise_for_status()
            result = response.json()

            llm_response = result.get("response", "")
            print(f"      Ollama responded with {len(llm_response)} characters")

            return llm_response

        except Exception as e:
            import traceback
            print(f"      ❌ Error calling Ollama: {e}")
            print(f"      Traceback: {traceback.format_exc()}")
            raise

    def parse_llm_response(self, llm_response: str, candidate: Dict) -> Optional[Dict]:
        """
        Parse LLM response and add confidence and cover letter to candidate
        """

        try:
            # Parse JSON response
            print(f"      Parsing LLM response...")
            data = json.loads(llm_response)

            # Check if candidate is suitable
            is_suitable = data.get("is_suitable", False)
            confidence = float(data.get("confidence", 0.5))

            print(f"      LLM Decision: is_suitable={is_suitable}, confidence={confidence}")

            if not is_suitable:
                print(f"      Candidate not suitable according to LLM")
                return None

            cover_letter = data.get("cover_letter", "")
            reasoning = data.get("reasoning", "")

            # Enhance candidate dict
            enhanced_candidate = candidate.copy()
            enhanced_candidate['confidence'] = confidence
            enhanced_candidate['cover_letter'] = cover_letter
            enhanced_candidate['llm_reasoning'] = reasoning

            return enhanced_candidate

        except json.JSONDecodeError as e:
            print(f"      ⚠️ Error parsing LLM response: {e}")
            print(f"      Response was: {llm_response[:200]}...")

            # Fallback: create candidate with lower confidence
            print(f"      Using fallback - accepting with 0.5 confidence")
            enhanced_candidate = candidate.copy()
            enhanced_candidate['confidence'] = 0.5
            enhanced_candidate['cover_letter'] = f"I am interested in applying for this position. With my experience in {', '.join(candidate.get('skills', [])[:3])}, I believe I would be a good fit for your team."
            enhanced_candidate['llm_reasoning'] = "Fallback response due to parsing error"
            
            return enhanced_candidate

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
