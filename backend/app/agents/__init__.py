"""
Multi-Agent AI System for Vendor Bid Evaluation.

This package provides a comprehensive AI-powered evaluation system for government
procurement bids using LangChain, LangGraph, and AWS Bedrock.

Main Components:
- DocumentParserAgent: Extracts structured data from bid documents
- ComplianceAgent: Checks bids against tender requirements
- TechnicalAgent: Evaluates technical proposal quality
- FinancialAgent: Analyzes financial proposals and pricing
- ComparisonAgent: Compares bids and generates rankings
- ReportAgent: Generates comprehensive evaluation reports
- EvaluationOrchestrator: Orchestrates the complete workflow using LangGraph

Usage:
    from app.agents import EvaluationOrchestrator, EvaluationMethod

    # Initialize orchestrator
    orchestrator = EvaluationOrchestrator(
        model_id="anthropic.claude-sonnet-4-20250514-v1:0",
        progress_callback=my_progress_handler
    )

    # Run evaluation
    result = await orchestrator.run(
        evaluation_id="eval-001",
        bids=[
            {"bid_id": "bid-1", "document_content": "..."},
            {"bid_id": "bid-2", "document_content": "..."}
        ],
        tender_requirements={
            "tender_reference": "RFP-2024-001",
            "tender_title": "IT Infrastructure Upgrade",
            "budget": 1000000,
            ...
        },
        evaluation_method=EvaluationMethod.QCBS
    )

    # Access report
    if result.status == "completed":
        report = result.report
        markdown_report = ReportAgent().export_to_markdown(report)
"""

# Base agent
from .base_agent import BaseAgent

# Individual agents
from .document_parser_agent import DocumentParserAgent
from .compliance_agent import ComplianceAgent
from .technical_agent import TechnicalAgent
from .financial_agent import FinancialAgent
from .comparison_agent import ComparisonAgent
from .report_agent import ReportAgent

# Orchestrator
from .orchestrator import EvaluationOrchestrator

# Schemas
from .schemas import (
    # Enums
    EvaluationMethod,
    ComplianceStatus,

    # Document models
    ParsedBidDocument,
    VendorInfo,
    PricingTable,
    PricingItem,
    TechnicalSpecification,
    DocumentSection,

    # Result models
    ComplianceResult,
    ComplianceIssue,
    TechnicalScore,
    ScoreBreakdown,
    FinancialScore,
    ComparisonResult,
    BidRanking,
    CartelFlag,
    EvaluationReport,

    # Workflow models
    AgentState,
    ProgressUpdate,
    EvaluationResult,
)

# Prompts (for advanced usage)
from .prompts import (
    DOCUMENT_PARSING_PROMPT,
    COMPLIANCE_CHECK_PROMPT,
    TECHNICAL_EVALUATION_PROMPT,
    FINANCIAL_ANALYSIS_PROMPT,
    COMPARISON_PROMPT,
    REPORT_GENERATION_PROMPT,
    SYSTEM_PROMPTS,
)


__all__ = [
    # Base
    "BaseAgent",

    # Agents
    "DocumentParserAgent",
    "ComplianceAgent",
    "TechnicalAgent",
    "FinancialAgent",
    "ComparisonAgent",
    "ReportAgent",

    # Orchestrator
    "EvaluationOrchestrator",

    # Enums
    "EvaluationMethod",
    "ComplianceStatus",

    # Document models
    "ParsedBidDocument",
    "VendorInfo",
    "PricingTable",
    "PricingItem",
    "TechnicalSpecification",
    "DocumentSection",

    # Result models
    "ComplianceResult",
    "ComplianceIssue",
    "TechnicalScore",
    "ScoreBreakdown",
    "FinancialScore",
    "ComparisonResult",
    "BidRanking",
    "CartelFlag",
    "EvaluationReport",

    # Workflow models
    "AgentState",
    "ProgressUpdate",
    "EvaluationResult",

    # Prompts
    "DOCUMENT_PARSING_PROMPT",
    "COMPLIANCE_CHECK_PROMPT",
    "TECHNICAL_EVALUATION_PROMPT",
    "FINANCIAL_ANALYSIS_PROMPT",
    "COMPARISON_PROMPT",
    "REPORT_GENERATION_PROMPT",
    "SYSTEM_PROMPTS",
]


__version__ = "1.0.0"
__author__ = "GovProcure AI Team"
__description__ = "Multi-Agent AI System for Government Procurement Bid Evaluation"
