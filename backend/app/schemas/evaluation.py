"""
Evaluation Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from enum import Enum


class EvaluationMethodEnum(str, Enum):
    """Evaluation method enum"""
    L1 = "l1"
    QCBS = "qcbs"
    TWO_STAGE = "two_stage"


class EvaluationConfig(BaseModel):
    """Schema for evaluation configuration"""
    method: EvaluationMethodEnum = EvaluationMethodEnum.QCBS
    technical_weight: int = Field(70, ge=0, le=100)
    financial_weight: int = Field(30, ge=0, le=100)
    qualification_threshold: int = Field(75, ge=0, le=100)
    enable_compliance_check: bool = True
    enable_justifications: bool = True
    enable_cartel_detection: bool = False

    @model_validator(mode='after')
    def validate_weights_sum_to_100(self):
        """Ensure technical + financial weights equal 100%"""
        if self.technical_weight + self.financial_weight != 100:
            raise ValueError(
                f"Weights must sum to 100 (got {self.technical_weight} + {self.financial_weight} = "
                f"{self.technical_weight + self.financial_weight})"
            )
        return self


class EvaluationCreate(BaseModel):
    """Schema for creating evaluation"""
    tender_document_id: Optional[str] = None
    title: str = Field(..., min_length=10, max_length=500)
    config: Optional[EvaluationConfig] = None


class BidAdd(BaseModel):
    """Schema for adding a bid"""
    vendor_id: str
    document_id: Optional[str] = None


class EvaluationSummary(BaseModel):
    """Schema for evaluation summary in list"""
    id: str
    reference_id: str
    title: str
    status: str
    created_at: datetime
    vendor_count: int = 0

    class Config:
        from_attributes = True


class EvaluationResponse(BaseModel):
    """Schema for evaluation response"""
    id: str
    reference_id: str
    title: str
    status: str
    config: Dict[str, Any] = {}
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    results_summary: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EvaluationListResponse(BaseModel):
    """Schema for evaluation list response"""
    items: List[EvaluationResponse]
    total: int
    page: int
    pages: int


class VendorScore(BaseModel):
    """Schema for vendor score"""
    vendor_id: str
    vendor_name: str
    compliance_status: str
    technical_score: Optional[float] = None
    financial_score: Optional[float] = None
    total_score: Optional[float] = None
    rank: Optional[int] = None
    is_winner: bool = False


class EvaluationResults(BaseModel):
    """Schema for evaluation results"""
    evaluation_id: str
    status: str
    method: EvaluationMethodEnum
    total_bids: int
    qualified_bids: int
    disqualified_bids: int
    winner: Optional[VendorScore] = None
    rankings: List[VendorScore] = []
    score_distribution: Dict[str, Any] = {}
    processing_time_seconds: int = 0
    completed_at: Optional[datetime] = None
