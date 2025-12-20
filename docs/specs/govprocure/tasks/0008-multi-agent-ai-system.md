# Task 0008: Multi-Agent AI System

## Overview
Implement the complete multi-agent AI system including AWS Bedrock LLM service, all evaluation agents, orchestrator, and error recovery.

## Subtasks

### 8.1 Set up AWS Bedrock LLM service
- Create `app/services/bedrock_llm_service.py`
- Configure ChatBedrockConverse with Claude Sonnet 4.5 model
- Set temperature to 0.2 for consistent scoring
- Implement connection and error handling
- Reference: Section 3.3 (AI/ML Stack), Section 8.2 (Orchestrator - LLM setup)

### 8.2 Create EvaluationState class
- Create `app/agents/__init__.py` with EvaluationState dataclass
- Include all state fields: tender_data, vendor_bids, compliance_results, technical_scores, financial_scores, comparison_matrix, final_report, logs, current_step, error
- Add error recovery fields: retry_count, max_retries, failed_step, partial_results_saved
- Reference: Section 8.2 (EvaluationState class)

### 8.3 Implement Document Parser Agent
- Create `app/agents/document_parser.py`
- Implement `parse_tender()` method to extract requirements, sections, criteria from tender documents
- Implement `parse_bid()` method to extract vendor proposal content
- Reference: Section 8.1 (Agent Architecture - Document Parser)

### 8.4 Implement Compliance Agent
- Create `app/agents/compliance_agent.py`
- Implement `verify()` method to check document compliance (GST, Bank Guarantee, etc.)
- Return compliance status, document checklist, AI notes with justification
- Reference: Section 8.1 (Agent Architecture - Compliance Agent), Section 5.2.5 (Compliance View)

### 8.5 Implement Technical Evaluation Agent
- Create `app/agents/technical_agent.py`
- Implement technical criteria evaluation with LLM prompts from Section 8.3
- Score against: Previous Experience, Technical Team, Methodology, QA Plan, Timeline
- Calculate weighted total score and qualification status (threshold = 75)
- Reference: Section 8.3 (Technical Evaluation Agent)

### 8.6 Implement Financial Evaluation Agent
- Create `app/agents/financial_agent.py`
- Parse bid amounts and normalize to paisa
- Calculate L1 winner (lowest price method)
- Apply financial scoring formula for QCBS method
- Reference: Section 8.1 (Agent Architecture - Financial Agent)

### 8.7 Implement Comparison Agent
- Create `app/agents/comparison_agent.py`
- Perform cross-vendor analysis and generate comparison matrix
- Implement cartel detection (Beta - advisory only, flag patterns for human review)
- Reference: Section 8.1 (Agent Architecture - Comparison Agent)

### 8.8 Implement Report Agent
- Create `app/agents/report_agent.py`
- Generate evaluation summaries with AI-generated justifications
- Prepare data for PDF report export
- Include winner recommendation with detailed justification
- Reference: Section 8.1 (Agent Architecture - Report Agent)

### 8.9 Implement Orchestrator Agent with LangGraph
- Create `app/agents/orchestrator.py` with EvaluationOrchestrator class
- Build LangGraph StateGraph with all workflow nodes
- Define edges and conditional routing (e.g., skip financial if no qualified bids)
- Implement progress callback for WebSocket updates
- Reference: Section 8.2 (Orchestrator Implementation)

### 8.10 Implement error recovery workflow
- Add retry logic with exponential backoff (3 attempts)
- Save partial results on failure
- Enable restart from failed step
- Reference: Section 8.2 (Error Recovery Workflow)

## References
- Section 3.3 (AI/ML Stack)
- Section 5.2.5 (Compliance View)
- Section 8.1 (Agent Architecture)
- Section 8.2 (Orchestrator Implementation)
- Section 8.2 (EvaluationState class)
- Section 8.2 (Error Recovery Workflow)
- Section 8.3 (Technical Evaluation Agent)
