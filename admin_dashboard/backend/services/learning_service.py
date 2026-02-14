"""
Self-Improvement Learning Service
Enables agents to learn from feedback, adapt behavior, and evolve over time
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import random
import json
from models.agent_learning import (
    AgentType, FeedbackType, AgentFeedback, LearningPattern,
    AgentMetrics, AgentLearningState, InterviewQuestionPattern,
    CVScoringPattern, PromptEvolution
)


class LearningService:
    """Central service for agent self-improvement"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.feedback_collection = db.agent_feedback
        self.patterns_collection = db.learning_patterns
        self.metrics_collection = db.agent_metrics
        self.learning_state_collection = db.agent_learning_state
        self.prompt_evolution_collection = db.prompt_evolution
        
    async def record_feedback(
        self,
        agent_type: AgentType,
        feedback_type: FeedbackType,
        context: Dict[str, Any],
        outcome: Dict[str, Any],
        user_rating: Optional[int] = None,
        user_comments: Optional[str] = None
    ) -> str:
        """Record feedback for an agent action"""
        feedback = AgentFeedback(
            agent_type=agent_type,
            feedback_type=feedback_type,
            context=context,
            outcome=outcome,
            user_rating=user_rating,
            user_comments=user_comments
        )
        
        result = await self.feedback_collection.insert_one(feedback.dict())
        feedback_id = str(result.inserted_id)
        
        # Update metrics
        await self._update_metrics(agent_type, feedback_type, user_rating)
        
        # Process learning if auto-learning enabled
        state = await self.get_learning_state(agent_type)
        if state.auto_adapt:
            await self._process_learning(feedback_id, feedback)
        
        return feedback_id
    
    async def _process_learning(self, feedback_id: str, feedback: AgentFeedback):
        """Process feedback to extract learnings"""
        # Extract patterns based on feedback type
        if feedback.feedback_type == FeedbackType.POSITIVE and feedback.user_rating and feedback.user_rating >= 4:
            # Learn from successful patterns
            await self._learn_successful_pattern(feedback)
        elif feedback.feedback_type == FeedbackType.NEGATIVE or (feedback.user_rating and feedback.user_rating <= 2):
            # Learn from failures
            await self._learn_from_failure(feedback)
        elif feedback.feedback_type == FeedbackType.CORRECTION:
            # Direct correction - highest priority learning
            await self._apply_correction(feedback)
        
        # Mark as processed
        await self.feedback_collection.update_one(
            {"feedback_id": feedback_id},
            {"$set": {"processed": True}}
        )
    
    async def _learn_successful_pattern(self, feedback: AgentFeedback):
        """Extract and store successful patterns"""
        if feedback.agent_type == AgentType.INTERVIEW:
            # Learn which questions work well
            await self._learn_interview_pattern(feedback, success=True)
        elif feedback.agent_type == AgentType.CV_SHORTLISTING:
            # Learn which candidate attributes correlate with success
            await self._learn_cv_scoring_pattern(feedback, success=True)
        elif feedback.agent_type == AgentType.EMAIL_SCHEDULING:
            # Learn successful parsing patterns
            await self._learn_parsing_pattern(feedback, success=True)
    
    async def _learn_from_failure(self, feedback: AgentFeedback):
        """Learn from failures to avoid repeating them"""
        # Decrease weight/probability of failed patterns
        pattern_id = feedback.context.get("pattern_id")
        if pattern_id:
            await self.patterns_collection.update_one(
                {"pattern_id": pattern_id},
                {
                    "$inc": {"usage_count": 1},
                    "$mul": {"success_rate": 0.8}  # Reduce success rate
                }
            )
    
    async def _apply_correction(self, feedback: AgentFeedback):
        """Apply direct corrections from users"""
        correction_data = feedback.outcome.get("correction")
        if correction_data:
            # Create new pattern from correction
            pattern = LearningPattern(
                pattern_id=f"{feedback.agent_type}_{datetime.utcnow().timestamp()}",
                agent_type=feedback.agent_type,
                pattern_type="correction",
                pattern_data=correction_data,
                success_rate=1.0  # Trust user corrections
            )
            await self.patterns_collection.insert_one(pattern.dict())
    
    async def _update_metrics(
        self,
        agent_type: AgentType,
        feedback_type: FeedbackType,
        user_rating: Optional[int]
    ):
        """Update agent performance metrics"""
        metrics = await self.metrics_collection.find_one({"agent_type": agent_type})
        
        if not metrics:
            metrics = AgentMetrics(agent_type=agent_type).dict()
        
        # Update counts
        metrics["total_actions"] += 1
        if feedback_type == FeedbackType.POSITIVE:
            metrics["successful_actions"] += 1
        elif feedback_type == FeedbackType.NEGATIVE:
            metrics["failed_actions"] += 1
        
        # Update average rating
        if user_rating:
            current_avg = metrics.get("average_rating", 0)
            total = metrics["total_actions"]
            metrics["average_rating"] = ((current_avg * (total - 1)) + user_rating) / total
        
        # Calculate improvement rate
        success_rate = metrics["successful_actions"] / metrics["total_actions"] if metrics["total_actions"] > 0 else 0
        baseline = metrics.get("baseline_performance", 0.5)
        if baseline > 0:
            metrics["improvement_rate"] = ((success_rate - baseline) / baseline) * 100
        
        metrics["updated_at"] = datetime.utcnow()
        
        await self.metrics_collection.update_one(
            {"agent_type": agent_type},
            {"$set": metrics},
            upsert=True
        )
    
    async def get_best_pattern(
        self,
        agent_type: AgentType,
        pattern_type: str,
        context: Dict[str, Any] = None
    ) -> Optional[LearningPattern]:
        """Get best learned pattern for a given context using exploration-exploitation"""
        state = await self.get_learning_state(agent_type)
        
        # Exploration vs Exploitation
        if random.random() < state.exploration_rate:
            # Explore: try random pattern
            patterns = await self.patterns_collection.find({
                "agent_type": agent_type,
                "pattern_type": pattern_type,
                "is_active": True
            }).to_list(length=100)
            return random.choice(patterns) if patterns else None
        else:
            # Exploit: use best pattern
            pattern = await self.patterns_collection.find_one(
                {
                    "agent_type": agent_type,
                    "pattern_type": pattern_type,
                    "is_active": True
                },
                sort=[("success_rate", -1), ("usage_count", -1)]
            )
            return LearningPattern(**pattern) if pattern else None
    
    async def evolve_prompt(
        self,
        agent_type: AgentType,
        current_prompt: str,
        performance_feedback: float
    ) -> str:
        """Evolve prompt based on performance"""
        # Get current prompt version
        current_version = await self.prompt_evolution_collection.find_one(
            {"agent_type": agent_type, "is_active": True}
        )
        
        if not current_version:
            # Initialize first version
            current_version = PromptEvolution(
                agent_type=agent_type,
                prompt_version="1.0.0",
                prompt_template=current_prompt,
                performance_score=performance_feedback
            )
            await self.prompt_evolution_collection.insert_one(current_version.dict())
            return current_prompt
        
        # If performance is declining, try evolution
        if performance_feedback < current_version.get("performance_score", 0):
            # Get learned patterns to improve prompt
            patterns = await self.patterns_collection.find({
                "agent_type": agent_type,
                "success_rate": {"$gte": 0.7}
            }).to_list(length=10)
            
            # Evolve prompt by incorporating successful patterns
            evolved_prompt = await self._generate_evolved_prompt(
                current_prompt,
                patterns,
                agent_type
            )
            
            # Save new version
            version_parts = current_version["prompt_version"].split(".")
            new_version = f"{version_parts[0]}.{int(version_parts[1]) + 1}.0"
            
            new_prompt_version = PromptEvolution(
                agent_type=agent_type,
                prompt_version=new_version,
                prompt_template=evolved_prompt,
                performance_score=0.0,
                parent_version=current_version["prompt_version"],
                improvements=["Incorporated high success rate patterns"]
            )
            
            # Deactivate old version
            await self.prompt_evolution_collection.update_one(
                {"agent_type": agent_type, "is_active": True},
                {"$set": {"is_active": False}}
            )
            
            # Activate new version
            await self.prompt_evolution_collection.insert_one(new_prompt_version.dict())
            
            return evolved_prompt
        
        return current_prompt
    
    async def _generate_evolved_prompt(
        self,
        base_prompt: str,
        successful_patterns: List[Dict],
        agent_type: AgentType
    ) -> str:
        """Generate improved prompt from successful patterns"""
        # Simple evolution: append best practices from patterns
        improvements = []
        
        for pattern in successful_patterns[:3]:  # Top 3 patterns
            if pattern.get("pattern_type") == "prompt_enhancement":
                improvements.append(pattern["pattern_data"].get("enhancement", ""))
        
        if improvements:
            evolved = base_prompt + "\n\nLearned best practices:\n" + "\n".join(improvements)
            return evolved
        
        return base_prompt
    
    async def get_learning_state(self, agent_type: AgentType) -> AgentLearningState:
        """Get current learning state of an agent"""
        state = await self.learning_state_collection.find_one({"agent_type": agent_type})
        
        if not state:
            # Initialize default state
            state = AgentLearningState(agent_type=agent_type)
            await self.learning_state_collection.insert_one(state.dict())
        
        return AgentLearningState(**state)
    
    async def update_learning_state(
        self,
        agent_type: AgentType,
        **updates
    ):
        """Update learning configuration for an agent"""
        await self.learning_state_collection.update_one(
            {"agent_type": agent_type},
            {"$set": {**updates, "updated_at": datetime.utcnow()}},
            upsert=True
        )
    
    async def get_agent_metrics(self, agent_type: AgentType) -> AgentMetrics:
        """Get performance metrics for an agent"""
        metrics = await self.metrics_collection.find_one({"agent_type": agent_type})
        return AgentMetrics(**metrics) if metrics else AgentMetrics(agent_type=agent_type)
    
    async def get_all_metrics(self) -> List[AgentMetrics]:
        """Get metrics for all agents"""
        metrics_list = await self.metrics_collection.find().to_list(length=100)
        return [AgentMetrics(**m) for m in metrics_list]
    
    async def _learn_interview_pattern(self, feedback: AgentFeedback, success: bool):
        """Learn from interview feedback"""
        questions_asked = feedback.context.get("questions", [])
        job_level = feedback.context.get("job_level", "mid")
        
        for question in questions_asked:
            pattern_id = f"interview_q_{hash(question) % 10000}"
            
            existing = await self.patterns_collection.find_one({"pattern_id": pattern_id})
            
            if existing:
                # Update existing pattern
                new_usage = existing["usage_count"] + 1
                if success:
                    new_success_rate = (existing["success_rate"] * existing["usage_count"] + 1) / new_usage
                else:
                    new_success_rate = (existing["success_rate"] * existing["usage_count"]) / new_usage
                
                await self.patterns_collection.update_one(
                    {"pattern_id": pattern_id},
                    {
                        "$set": {
                            "success_rate": new_success_rate,
                            "usage_count": new_usage,
                            "last_used_at": datetime.utcnow()
                        }
                    }
                )
            else:
                # Create new pattern
                pattern = LearningPattern(
                    pattern_id=pattern_id,
                    agent_type=AgentType.INTERVIEW,
                    pattern_type="question_template",
                    pattern_data={
                        "question": question,
                        "job_level": job_level,
                        "success": success
                    },
                    success_rate=1.0 if success else 0.0,
                    usage_count=1
                )
                await self.patterns_collection.insert_one(pattern.dict())
    
    async def _learn_cv_scoring_pattern(self, feedback: AgentFeedback, success: bool):
        """Learn from CV shortlisting feedback"""
        candidate = feedback.context.get("candidate", {})
        skills = candidate.get("skills", [])
        
        for skill in skills:
            pattern_id = f"cv_skill_{skill.lower().replace(' ', '_')}"
            
            existing = await self.patterns_collection.find_one({"pattern_id": pattern_id})
            
            if existing:
                # Update correlation
                pattern_data = existing["pattern_data"]
                pattern_data["times_evaluated"] = pattern_data.get("times_evaluated", 0) + 1
                if success:
                    pattern_data["hired_count"] = pattern_data.get("hired_count", 0) + 1
                else:
                    pattern_data["rejected_count"] = pattern_data.get("rejected_count", 0) + 1
                
                # Calculate hire correlation
                total = pattern_data["times_evaluated"]
                hired = pattern_data["hired_count"]
                correlation = hired / total if total > 0 else 0.5
                
                await self.patterns_collection.update_one(
                    {"pattern_id": pattern_id},
                    {
                        "$set": {
                            "pattern_data": pattern_data,
                            "success_rate": correlation,
                            "usage_count": total
                        }
                    }
                )
            else:
                # Create new pattern
                pattern = LearningPattern(
                    pattern_id=pattern_id,
                    agent_type=AgentType.CV_SHORTLISTING,
                    pattern_type="skill_weight",
                    pattern_data={
                        "skill": skill,
                        "times_evaluated": 1,
                        "hired_count": 1 if success else 0,
                        "rejected_count": 0 if success else 1
                    },
                    success_rate=1.0 if success else 0.0,
                    usage_count=1
                )
                await self.patterns_collection.insert_one(pattern.dict())
    
    async def _learn_parsing_pattern(self, feedback: AgentFeedback, success: bool):
        """Learn from email parsing feedback"""
        pattern_id = f"parsing_{datetime.utcnow().timestamp()}"
        
        pattern = LearningPattern(
            pattern_id=pattern_id,
            agent_type=AgentType.EMAIL_SCHEDULING,
            pattern_type="parsing_pattern",
            pattern_data={
                "original_text": feedback.context.get("email_text", ""),
                "parsed_result": feedback.outcome.get("parsed_slots", []),
                "success": success
            },
            success_rate=1.0 if success else 0.0,
            usage_count=1
        )
        await self.patterns_collection.insert_one(pattern.dict())
    
    async def get_learning_insights(self, agent_type: AgentType) -> Dict[str, Any]:
        """Get insights about what an agent has learned"""
        metrics = await self.get_agent_metrics(agent_type)
        state = await self.get_learning_state(agent_type)
        
        # Get top patterns
        top_patterns = await self.patterns_collection.find({
            "agent_type": agent_type,
            "is_active": True
        }).sort("success_rate", -1).limit(10).to_list(length=10)
        
        # Get recent feedback
        recent_feedback = await self.feedback_collection.find({
            "agent_type": agent_type
        }).sort("created_at", -1).limit(20).to_list(length=20)
        
        return {
            "agent_type": agent_type,
            "metrics": metrics.dict(),
            "learning_state": state.dict(),
            "top_patterns": top_patterns,
            "recent_feedback_count": len(recent_feedback),
            "learning_enabled": state.learning_enabled,
            "performance_trend": "improving" if metrics.improvement_rate > 0 else "declining"
        }
