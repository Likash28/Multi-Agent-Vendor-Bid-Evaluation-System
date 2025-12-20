"""
Pydantic schemas for agent inputs and outputs in the evaluation workflow.
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class EvaluationMethod(str, Enum):
    """Supported evaluation methods for procurement."""
    L1 = "L1"  # Lowest price
    QCBS = "QCBS"  # Quality and Cost Based Selection
    TWO_STAGE = "TWO_STAGE"  # Two-stage evaluation


class ComplianceStatus(str, Enum):
    """Compliance check status."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    CONDITIONAL = "CONDITIONAL"


class DocumentSection(BaseModel):
    """Represents a section of a parsed document."""
    section_name: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VendorInfo(BaseModel):
    """Vendor information extracted from bid."""
    name: str
    registration_number: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    years_in_business: Optional[int] = None


class PricingItem(BaseModel):
    """Individual pricing item."""
    item_name: str
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: float
    total_price: float
    unit: Optional[str] = None


class PricingTable(BaseModel):
    """Pricing table extracted from bid."""
    items: List[PricingItem]
    subtotal: float
    taxes: Optional[float] = None
    total: float
    currency: str = "USD"


class TechnicalSpecification(BaseModel):
    """Technical specification item."""
    requirement: str
    proposed_solution: str
    meets_requirement: bool
    notes: Optional[str] = None


class ParsedBidDocument(BaseModel):
    """Complete parsed bid document."""
    bid_id: str
    vendor_info: VendorInfo
    pricing_table: PricingTable
    technical_specs: List[TechnicalSpecification] = Field(default_factory=list)
    compliance_statements: List[str] = Field(default_factory=list)
    sections: List[DocumentSection] = Field(default_factory=list)
    raw_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    parsed_at: datetime = Field(default_factory=datetime.utcnow)


class ComplianceIssue(BaseModel):
    """Individual compliance issue."""
    issue_type: str  # e.g., "missing_document", "invalid_format", "failed_criterion"
    severity: str  # "critical", "major", "minor"
    description: str
    requirement: str
    recommendation: Optional[str] = None


class ComplianceResult(BaseModel):
    """Result of compliance check."""
    bid_id: str
    status: ComplianceStatus
    overall_score: float = Field(ge=0, le=100)  # Percentage
    issues: List[ComplianceIssue] = Field(default_factory=list)
    passed_criteria: List[str] = Field(default_factory=list)
    failed_criteria: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    is_eligible: bool
    summary: str
    checked_at: datetime = Field(default_factory=datetime.utcnow)


class ScoreBreakdown(BaseModel):
    """Breakdown of a score component."""
    category: str
    weight: float  # Percentage
    score: float  # Out of 100
    weighted_score: float
    justification: str


class TechnicalScore(BaseModel):
    """Technical evaluation score."""
    bid_id: str
    overall_score: float = Field(ge=0, le=100)
    methodology_score: ScoreBreakdown
    team_qualifications_score: ScoreBreakdown
    past_experience_score: ScoreBreakdown
    innovation_score: ScoreBreakdown
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    summary: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


class FinancialScore(BaseModel):
    """Financial evaluation score."""
    bid_id: str
    total_bid_amount: float
    normalized_score: float = Field(ge=0, le=100)  # Relative to other bids
    price_competitiveness: float = Field(ge=0, le=100)
    cost_breakdown_quality: float = Field(ge=0, le=100)
    is_abnormally_low: bool
    abnormally_low_threshold: Optional[float] = None
    price_analysis: str
    cost_breakdown_analysis: str
    risks: List[str] = Field(default_factory=list)
    summary: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


class CartelFlag(BaseModel):
    """Potential cartel or collusion indicator."""
    flag_type: str  # e.g., "identical_pricing", "pattern_rotation", "suspicious_similarity"
    severity: str  # "high", "medium", "low"
    description: str
    involved_bids: List[str]
    evidence: str


class BidRanking(BaseModel):
    """Individual bid ranking."""
    rank: int
    bid_id: str
    vendor_name: str
    technical_score: float
    financial_score: float
    combined_score: float
    is_compliant: bool
    is_winner: bool
    notes: Optional[str] = None


class ComparisonResult(BaseModel):
    """Result of comparing all bids."""
    evaluation_id: str
    evaluation_method: EvaluationMethod
    rankings: List[BidRanking]
    winner_bid_id: Optional[str] = None
    winner_vendor_name: Optional[str] = None
    cartel_flags: List[CartelFlag] = Field(default_factory=list)
    technical_weight: float = 70.0  # Percentage for QCBS
    financial_weight: float = 30.0  # Percentage for QCBS
    total_bids_evaluated: int
    compliant_bids_count: int
    summary: str
    compared_at: datetime = Field(default_factory=datetime.utcnow)


class EvaluationReport(BaseModel):
    """Complete evaluation report."""
    evaluation_id: str
    tender_reference: str
    tender_title: str
    evaluation_method: EvaluationMethod
    executive_summary: str
    methodology_description: str
    bids_summary: List[Dict[str, Any]]  # Summary of each bid
    compliance_results: List[ComplianceResult]
    technical_scores: List[TechnicalScore]
    financial_scores: List[FinancialScore]
    comparison_result: ComparisonResult
    recommendations: List[str]
    risks_and_concerns: List[str] = Field(default_factory=list)
    cartel_analysis: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentState(BaseModel):
    """State object for LangGraph workflow."""
    evaluation_id: str
    tender_requirements: Dict[str, Any]
    evaluation_method: EvaluationMethod

    # Input bids
    raw_bids: List[Dict[str, Any]] = Field(default_factory=list)

    # Parsed documents
    parsed_documents: List[ParsedBidDocument] = Field(default_factory=list)

    # Compliance results
    compliance_results: List[ComplianceResult] = Field(default_factory=list)
    compliant_bid_ids: List[str] = Field(default_factory=list)

    # Technical scores
    technical_scores: List[TechnicalScore] = Field(default_factory=list)

    # Financial scores
    financial_scores: List[FinancialScore] = Field(default_factory=list)

    # Comparison result
    comparison_result: Optional[ComparisonResult] = None

    # Final report
    final_report: Optional[EvaluationReport] = None

    # Workflow metadata
    current_step: str = "initialized"
    errors: List[str] = Field(default_factory=list)
    progress: float = 0.0  # 0-100
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True


class ProgressUpdate(BaseModel):
    """Progress update for WebSocket notifications."""
    evaluation_id: str
    step: str
    progress: float  # 0-100
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Optional[Dict[str, Any]] = None


class EvaluationResult(BaseModel):
    """Final evaluation result returned by orchestrator."""
    evaluation_id: str
    status: str  # "completed", "failed", "partial"
    report: Optional[EvaluationReport] = None
    errors: List[str] = Field(default_factory=list)
    execution_time_seconds: float
    completed_at: datetime = Field(default_factory=datetime.utcnow)
