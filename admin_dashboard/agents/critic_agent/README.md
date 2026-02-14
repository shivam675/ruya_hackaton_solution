# Critic Agent - System Prompt Optimization

## Overview

The Critic Agent is an AI-powered system that evaluates the performance of all 4 agents (CV Shortlisting, HR Chat, Email Scheduling, and Interview) and suggests improvements to their system prompts based on real performance data.

## Architecture

```
critic_agent/
├── agent_logic.py          # Core critic agent logic (using ministral-3:3b)
├── prompts/                # Current system prompts for each agent
│   ├── cv_shortlisting_prompt.txt
│   ├── hr_chat_prompt.txt
│   ├── email_scheduling_prompt.txt
│   └── interview_prompt.txt
├── evaluations/            # Evaluation history (JSON files)
│   └── {agent_type}_{timestamp}.json
└── __init__.py
```

## How It Works

### 1. **Data Collection**
   - Gathers performance metrics for each agent:
     - Average user feedback ratings (1-5 stars)
     - Task success rate (0-1)
     - Total interactions
     - Sample input-output pairs

### 2. **Evaluation Process**
   - Admin manually triggers evaluation from UI (Agent Learning tab)
   - Critic agent analyzes:
     - Current system prompt
     - Recent agent performance
     - Low-rated interactions
     - Common failure patterns
   
### 3. **Prompt Improvement**
   - Uses Ollama (ministral-3:3b) to:
     - Identify weaknesses in current prompt
     - Generate improved prompt
     - Explain reasoning for changes
     - Predict expected improvements
   
### 4. **Review & Approval**
   - Admin reviews improvements in UI:
     - Side-by-side prompt comparison (old vs new)
     - Evaluation score (1-10)
     - Issues identified
     - Expected improvements
   - Admin can:
     - **Approve**: Apply improved prompt immediately
     - **Reject**: Decline improvement with optional reason

### 5. **Queue System**
   - Evaluations are stored as JSON files
   - Each evaluation has status:
     - `pending_review`: Awaiting admin decision
     - `approved`: Applied to agent
     - `rejected`: Declined by admin
   - All evaluations are visible in UI for tracking

## API Endpoints

### Trigger Evaluation
```http
POST /critic/evaluate
{
  "agent_type": "cv_shortlisting",
  "limit_samples": 10
}
```

### List Improvements
```http
GET /critic/improvements?agent_type=hr_chat&status=pending_review
```

### Get Specific Improvement
```http
GET /critic/improvements/{evaluation_id}
```

### Approve Improvement
```http
POST /critic/improvements/{evaluation_id}/approve
```

### Reject Improvement
```http
POST /critic/improvements/{evaluation_id}/reject
{
  "evaluation_id": "cv_shortlisting_20260214_153045",
  "reason": "Not aligned with business requirements"
}
```

### Get Current Prompt
```http
GET /critic/prompt/cv_shortlisting
```

## UI Features

### Agent Learning Tab → Critic Agent Section

1. **Evaluate Agent Button**
   - Click to trigger evaluation for selected agent
   - Shows loading state during evaluation (uses LLM, takes 10-30 seconds)

2. **Improvements List**
   - Shows all evaluations across all agents
   - Filter by agent type
   - Color-coded status badges:
     - Yellow: Pending review
     - Green: Approved
     - Red: Rejected

3. **Improvement Details (Click to Expand)**
   - Issues identified by critic
   - Expected improvements
   - Side-by-side prompt comparison:
     - Red box: Previous prompt
     - Green box: Improved prompt
   - Performance metrics used
   - Evaluation score (1-10)

4. **Action Buttons (Pending Reviews)**
   - **Approve & Apply**: Immediately apply improved prompt
   - **Reject**: Decline improvement (requires reason)

## Evaluation Metrics

The critic uses three key metrics:

1. **User Feedback Ratings** (1-5 stars)
   - Low ratings indicate prompt issues
   - Target: ≥4.0 average

2. **Task Success Rate** (0-1)
   - Percentage of successful outcomes
   - Target: ≥0.80 (80%)

3. **LLM Quality Evaluation**
   - Critic's own assessment of response quality
   - Identifies patterns in failures

## Example Workflow

1. **Admin notices CV agent has 3.5/5 rating**
   - Goes to Agent Learning tab
   - Selects CV Shortlisting agent
   
2. **Clicks "Evaluate Agent"**
   - Critic gathers last 10 interactions
   - Analyzes failures and low ratings
   - Generates improved prompt (takes ~20 seconds)
   
3. **Reviews Improvement**
   - Sees issues: "Too generic", "Lacks scoring criteria"
   - Reads improved prompt with specific scoring rubric
   - Expected improvements: "More consistent scoring", "Better ranking"
   
4. **Approves Improvement**
   - Clicks "Approve & Apply"
   - New prompt is immediately active
   - CV agent uses improved prompt for next shortlisting

5. **Monitors Results**
   - Watches metrics improve over next few days
   - Rating increases to 4.2/5
   - Success rate improves from 75% → 85%

## Configuration

### Environment Variables
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=ministral-3:3b
```

### Critic System Prompt
Located in `agent_logic.py` - can be customized to change evaluation style.

## File Storage

- **Prompts**: `agents/critic_agent/prompts/{agent_type}_prompt.txt`
- **Evaluations**: `agents/critic_agent/evaluations/{agent_type}_{timestamp}.json`

## Dependencies

```bash
# Backend
pip install httpx  # For Ollama API calls

# Ollama must be running
ollama run ministral-3:3b
```

## Future Enhancements

1. **Automated Evaluation**: Schedule periodic evaluations
2. **A/B Testing**: Test old vs new prompts side-by-side
3. **Performance Tracking**: Chart prompt improvement impact over time
4. **Multi-version Management**: Rollback to previous prompts
5. **Collaborative Review**: Multiple admins can vote on improvements
