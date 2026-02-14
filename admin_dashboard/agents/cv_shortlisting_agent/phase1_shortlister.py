"""
Phase 1 Shortlister: Keyword-based and experience-based shortlisting
No LLM required - fast filtering based on skills and experience
"""
from typing import List, Dict, Tuple


class Phase1Shortlister:
    """
    Phase 1: Keyword-based and experience-based shortlisting
    No LLM required
    """

    def __init__(self):
        pass

    def shortlist(
        self,
        candidates: List[Dict],
        required_skills: List[str],
        minimum_experience: int,
        target_count: int = 20
    ) -> List[Dict]:
        """
        Shortlist candidates based on:
        1. Keyword matching with required tech stack
        2. Minimum experience requirement
        
        Args:
            candidates: List of candidate dictionaries with keys: name, email, skills, experience
            required_skills: List of required technology/skill keywords
            minimum_experience: Minimum years of experience required
            target_count: Number of candidates to shortlist (default: 20)
        
        Returns:
            List of shortlisted candidates with scores
        """

        scored_candidates = []

        for candidate in candidates:
            score = self.calculate_score(candidate, required_skills, minimum_experience)
            candidate_copy = candidate.copy()
            candidate_copy['phase1_score'] = score
            scored_candidates.append((candidate_copy, score))

        # Sort by score (descending)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Filter by minimum experience
        filtered_candidates = [
            (candidate, score) for candidate, score in scored_candidates
            if candidate.get('experience') is not None and candidate.get('experience', 0) >= minimum_experience
        ]

        # If not enough candidates meet minimum experience, include those without specified experience
        if len(filtered_candidates) < target_count:
            no_exp_candidates = [
                (candidate, score) for candidate, score in scored_candidates
                if candidate.get('experience') is None or candidate.get('experience', 0) < minimum_experience
            ]
            filtered_candidates.extend(no_exp_candidates)

        # Take top N candidates
        shortlisted = [candidate for candidate, score in filtered_candidates[:target_count]]

        return shortlisted

    def calculate_score(self, candidate: Dict, required_skills: List[str], minimum_experience: int) -> float:
        """
        Calculate match score based on:
        - Tech stack keyword matching (70% weight)
        - Experience level (30% weight)
        
        Args:
            candidate: Candidate dictionary with 'skills' and 'experience' keys
            required_skills: List of required skills
            minimum_experience: Minimum years of experience
        
        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.0

        # Keyword matching (70% weight)
        required_skills_lower = set([skill.lower().strip() for skill in required_skills])
        candidate_skills = candidate.get('skills', [])
        
        if isinstance(candidate_skills, str):
            candidate_skills = [s.strip() for s in candidate_skills.split(',')]
        
        candidate_skills_lower = set([skill.lower().strip() for skill in candidate_skills])

        if required_skills_lower:
            matched_skills = required_skills_lower.intersection(candidate_skills_lower)
            keyword_score = len(matched_skills) / len(required_skills_lower)
            score += keyword_score * 0.7

        # Experience matching (30% weight)
        experience = candidate.get('experience')
        if experience is not None:
            if minimum_experience == 0:
                # If no experience required, give full score for any experience
                score += 0.3
            elif experience >= minimum_experience:
                # Give full score if meets minimum
                experience_score = min(1.0, experience / (minimum_experience * 2))
                score += experience_score * 0.3

        return score
