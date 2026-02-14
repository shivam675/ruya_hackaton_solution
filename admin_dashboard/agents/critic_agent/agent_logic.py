"""
Critic Agent - Evaluates and Improves Agent System Prompts
Uses Ollama ministral-3:3b to analyze agent performance and suggest improvements
"""
from typing import Dict, Any, List
import logging
import json
import httpx
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class CriticAgent:
    """
    Critic Agent that evaluates agent performance and improves system prompts
    """
    
    # System prompt for the critic agent
    CRITIC_SYSTEM_PROMPT = """You are an expert AI prompt engineer and quality evaluator. Your role is to:
1. Analyze agent performance based on input-output pairs and metrics
2. Identify weaknesses in agent responses
3. Propose specific, actionable improvements to the agent's system prompt
4. Provide clear reasoning for each improvement

When evaluating:
- Consider user feedback ratings (1-5 stars)
- Analyze task success rates
- Review response quality, accuracy, and helpfulness
- Identify patterns in failures or low ratings

When improving prompts:
- Be specific and actionable
- Preserve core agent functionality
- Add guardrails for common failure modes
- Improve clarity and instruction structure
- Keep prompts concise but comprehensive

Respond in JSON format:
{
    "evaluation_score": <1-10>,
    "issues_identified": ["issue1", "issue2", ...],
    "improvement_reasoning": "Clear explanation of why changes are needed",
    "improved_prompt": "The complete improved system prompt",
    "expected_improvements": ["improvement1", "improvement2", ...]
}
"""
    
    def __init__(self, ollama_url: str = None, model_name: str = None):
        """
        Initialize Critic Agent
        
        Args:
            ollama_url: Ollama API base URL
            model_name: Model to use (default: ministral-3:3b)
        """
        self.ollama_url = ollama_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "ministral-3:3b")
        
        # Agent prompts storage
        self.prompts_dir = Path(__file__).parent / "prompts"
        self.prompts_dir.mkdir(exist_ok=True)
        
        # Evaluation history storage
        self.evaluations_dir = Path(__file__).parent / "evaluations"
        self.evaluations_dir.mkdir(exist_ok=True)
        
        logger.info(f"✅ Critic Agent initialized with model: {self.model_name}")
    
    async def evaluate_agent(
        self,
        agent_type: str,
        current_prompt: str,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate an agent's performance and suggest prompt improvements
        
        Args:
            agent_type: Type of agent (cv_shortlisting, hr_chat, email_scheduling, interview)
            current_prompt: Current system prompt of the agent
            performance_data: Dict containing:
                - input_output_pairs: List of {input, output, rating, success}
                - avg_feedback_rating: Average user rating
                - success_rate: Task success rate (0-1)
                - total_interactions: Total number of interactions
                
        Returns:
            Dict containing evaluation results and improved prompt
        """
        logger.info(f"🔍 Evaluating {agent_type} agent")
        
        # Prepare evaluation context
        evaluation_context = self._prepare_evaluation_context(
            agent_type,
            current_prompt,
            performance_data
        )
        
        # Call Ollama to evaluate
        try:
            improved_data = await self._call_ollama_for_evaluation(evaluation_context)
            
            # Store evaluation
            evaluation_id = self._store_evaluation(
                agent_type,
                current_prompt,
                improved_data,
                performance_data
            )
            
            return {
                "evaluation_id": evaluation_id,
                "agent_type": agent_type,
                "timestamp": datetime.utcnow().isoformat(),
                "current_prompt": current_prompt,
                "evaluation_score": improved_data.get("evaluation_score"),
                "issues_identified": improved_data.get("issues_identified", []),
                "improvement_reasoning": improved_data.get("improvement_reasoning"),
                "improved_prompt": improved_data.get("improved_prompt"),
                "expected_improvements": improved_data.get("expected_improvements", []),
                "performance_metrics": {
                    "avg_feedback_rating": performance_data.get("avg_feedback_rating"),
                    "success_rate": performance_data.get("success_rate"),
                    "total_interactions": performance_data.get("total_interactions")
                },
                "status": "pending_review"
            }
            
        except Exception as e:
            logger.error(f"❌ Error evaluating {agent_type}: {str(e)}")
            raise
    
    def _prepare_evaluation_context(
        self,
        agent_type: str,
        current_prompt: str,
        performance_data: Dict[str, Any]
    ) -> str:
        """Prepare context for LLM evaluation"""
        
        # Get sample input-output pairs
        samples = performance_data.get("input_output_pairs", [])[:10]  # Limit to 10
        
        context = f"""
# Agent Evaluation Request

**Agent Type:** {agent_type}
**Current System Prompt:**
```
{current_prompt}
```

**Performance Metrics:**
- Average Feedback Rating: {performance_data.get('avg_feedback_rating', 'N/A')}/5.0
- Task Success Rate: {performance_data.get('success_rate', 'N/A')*100:.1f}%
- Total Interactions: {performance_data.get('total_interactions', 0)}

**Sample Interactions:**
"""
        
        for i, sample in enumerate(samples, 1):
            context += f"""
---
**Interaction {i}:**
- Input: {sample.get('input', 'N/A')}
- Output: {sample.get('output', 'N/A')}
- User Rating: {sample.get('rating', 'N/A')}/5
- Success: {sample.get('success', 'N/A')}
"""
        
        context += """
---

Please analyze this agent's performance and suggest improvements to the system prompt.
Focus on addressing low-rated interactions and improving overall success rate.
"""
        
        return context
    
    async def _call_ollama_for_evaluation(self, context: str) -> Dict[str, Any]:
        """
        Call Ollama API to evaluate and improve prompt
        
        Args:
            context: Evaluation context
            
        Returns:
            Dict with evaluation results
        """
        url = f"{self.ollama_url}/api/chat"
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.CRITIC_SYSTEM_PROMPT},
                {"role": "user", "content": context}
            ],
            "stream": False,
            "format": "json"
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            message_content = result.get("message", {}).get("content", "{}")
            
            try:
                return json.loads(message_content)
            except json.JSONDecodeError:
                # Fallback parsing - try to extract useful information
                logger.warning("⚠️ Failed to parse JSON response, using fallback")
                
                # Try to extract the improved prompt from text if present
                improved_prompt_text = message_content
                if "improved_prompt" in message_content.lower():
                    # Try to extract text after "improved_prompt"
                    try:
                        parts = message_content.split('"improved_prompt"')
                        if len(parts) > 1:
                            # Get text after the key
                            after_key = parts[1].split('",')[0].strip(': "')
                            if after_key and len(after_key) > 20:
                                improved_prompt_text = after_key
                    except:
                        pass
                
                return {
                    "evaluation_score": 5,
                    "issues_identified": ["JSON parsing failed - manual review recommended"],
                    "improvement_reasoning": f"The LLM response could not be parsed as JSON. Raw response:\n\n{message_content[:500]}...",
                    "improved_prompt": improved_prompt_text if len(improved_prompt_text) > 20 else "Please review the improvement_reasoning field for details. Consider triggering a new evaluation.",
                    "expected_improvements": ["Improved response quality", "Better structured output"]
                }
    
    def _store_evaluation(
        self,
        agent_type: str,
        current_prompt: str,
        improved_data: Dict[str, Any],
        performance_data: Dict[str, Any]
    ) -> str:
        """
        Store evaluation to file system
        
        Returns:
            evaluation_id
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        evaluation_id = f"{agent_type}_{timestamp}"
        
        evaluation_record = {
            "evaluation_id": evaluation_id,
            "agent_type": agent_type,
            "timestamp": datetime.utcnow().isoformat(),
            "current_prompt": current_prompt,
            "improved_prompt": improved_data.get("improved_prompt"),
            "evaluation_score": improved_data.get("evaluation_score"),
            "issues_identified": improved_data.get("issues_identified", []),
            "improvement_reasoning": improved_data.get("improvement_reasoning"),
            "expected_improvements": improved_data.get("expected_improvements", []),
            "performance_metrics": performance_data,
            "status": "pending_review"
        }
        
        # Save to file
        file_path = self.evaluations_dir / f"{evaluation_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(evaluation_record, f, indent=2)
        
        logger.info(f"💾 Saved evaluation: {evaluation_id}")
        return evaluation_id
    
    def get_evaluation(self, evaluation_id: str) -> Dict[str, Any]:
        """Get evaluation by ID"""
        file_path = self.evaluations_dir / f"{evaluation_id}.json"
        
        if not file_path.exists():
            raise ValueError(f"Evaluation not found: {evaluation_id}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_evaluations(self, agent_type: str = None, status: str = None) -> List[Dict[str, Any]]:
        """
        List all evaluations, optionally filtered by agent_type and status
        
        Args:
            agent_type: Filter by agent type
            status: Filter by status (pending_review, approved, rejected)
            
        Returns:
            List of evaluation records
        """
        evaluations = []
        
        for file_path in self.evaluations_dir.glob("*.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                eval_data = json.load(f)
                
                # Apply filters
                if agent_type and eval_data.get("agent_type") != agent_type:
                    continue
                if status and eval_data.get("status") != status:
                    continue
                
                evaluations.append(eval_data)
        
        # Sort by timestamp (newest first)
        evaluations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return evaluations
    
    def approve_improvement(self, evaluation_id: str) -> Dict[str, Any]:
        """
        Approve and apply an improvement
        
        Args:
            evaluation_id: ID of evaluation to approve
            
        Returns:
            Updated evaluation record
        """
        # Load evaluation
        eval_data = self.get_evaluation(evaluation_id)
        
        # Update status
        eval_data["status"] = "approved"
        eval_data["approved_at"] = datetime.utcnow().isoformat()
        
        # Save updated evaluation
        file_path = self.evaluations_dir / f"{evaluation_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(eval_data, f, indent=2)
        
        # Save improved prompt as current prompt
        agent_type = eval_data["agent_type"]
        self._save_current_prompt(agent_type, eval_data["improved_prompt"])
        
        logger.info(f"✅ Approved improvement: {evaluation_id}")
        return eval_data
    
    def reject_improvement(self, evaluation_id: str, reason: str = None) -> Dict[str, Any]:
        """
        Reject an improvement
        
        Args:
            evaluation_id: ID of evaluation to reject
            reason: Optional reason for rejection
            
        Returns:
            Updated evaluation record
        """
        # Load evaluation
        eval_data = self.get_evaluation(evaluation_id)
        
        # Update status
        eval_data["status"] = "rejected"
        eval_data["rejected_at"] = datetime.utcnow().isoformat()
        if reason:
            eval_data["rejection_reason"] = reason
        
        # Save updated evaluation
        file_path = self.evaluations_dir / f"{evaluation_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(eval_data, f, indent=2)
        
        logger.info(f"❌ Rejected improvement: {evaluation_id}")
        return eval_data
    
    def _save_current_prompt(self, agent_type: str, prompt: str):
        """Save prompt as current for agent type"""
        prompt_file = self.prompts_dir / f"{agent_type}_prompt.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        logger.info(f"💾 Saved current prompt for {agent_type}")
    
    def get_current_prompt(self, agent_type: str) -> str:
        """Get current prompt for agent type"""
        prompt_file = self.prompts_dir / f"{agent_type}_prompt.txt"
        
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return self._get_default_prompt(agent_type)
    
    def _get_default_prompt(self, agent_type: str) -> str:
        """Get default prompt for agent type"""
        defaults = {
            "cv_shortlisting": "You are an expert CV screening specialist. Review candidate resumes and match them to job requirements based on skills, experience, and qualifications.",
            "hr_chat": "You are a helpful HR assistant. Answer employee questions about policies, leave balance, and company procedures. Be professional, accurate, and empathetic.",
            "email_scheduling": "You are an email scheduling assistant. Parse availability from emails and coordinate interview schedules efficiently while being polite and professional.",
            "interview": "You are an AI interviewer. Conduct professional job interviews by asking relevant questions, evaluating responses, and providing a fair assessment of candidates."
        }
        
        return defaults.get(agent_type, "You are a helpful AI assistant.")


# Global instance
critic_agent = CriticAgent()
