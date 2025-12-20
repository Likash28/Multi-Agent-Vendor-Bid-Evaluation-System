"""
Comparison Agent - Compares all bids and generates rankings.
"""
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent
from .schemas import (
    ComparisonResult,
    BidRanking,
    CartelFlag,
    EvaluationMethod,
    ComplianceResult,
    TechnicalScore,
    FinancialScore
)
from .prompts import COMPARISON_PROMPT, SYSTEM_PROMPTS


logger = logging.getLogger(__name__)


class ComparisonAgent(BaseAgent):
    """
    Agent responsible for comparing all bids and generating rankings.

    Responsibilities:
    - Apply evaluation method (L1, QCBS, Two-Stage)
    - Calculate combined scores
    - Generate rankings
    - Identify winner
    - Detect potential cartel patterns
    """

    def __init__(self, **kwargs):
        """Initialize ComparisonAgent."""
        super().__init__(agent_name="ComparisonAgent", **kwargs)

    async def invoke(self, input_data: Dict[str, Any]) -> ComparisonResult:
        """
        Compare all bids and generate rankings.

        Args:
            input_data: Dict containing:
                - evaluation_id: Unique identifier for the evaluation
                - evaluation_method: EvaluationMethod (L1, QCBS, TWO_STAGE)
                - compliance_results: List of ComplianceResult instances or dicts
                - technical_scores: List of TechnicalScore instances or dicts
                - financial_scores: List of FinancialScore instances or dicts
                - tender_requirements: Dict with tender requirements
                - technical_weight: Optional weight for QCBS (default: 70)
                - financial_weight: Optional weight for QCBS (default: 30)

        Returns:
            ComparisonResult: Rankings and winner determination

        Raises:
            ValueError: If required input fields are missing
            Exception: If comparison fails
        """
        try:
            # Validate input
            if "evaluation_id" not in input_data:
                raise ValueError("evaluation_id is required")
            if "evaluation_method" not in input_data:
                raise ValueError("evaluation_method is required")
            if "compliance_results" not in input_data:
                raise ValueError("compliance_results is required")
            if "technical_scores" not in input_data:
                raise ValueError("technical_scores is required")
            if "financial_scores" not in input_data:
                raise ValueError("financial_scores is required")

            evaluation_id = input_data["evaluation_id"]
            evaluation_method = input_data["evaluation_method"]
            if isinstance(evaluation_method, str):
                evaluation_method = EvaluationMethod(evaluation_method)

            compliance_results = input_data["compliance_results"]
            technical_scores = input_data["technical_scores"]
            financial_scores = input_data["financial_scores"]
            tender_requirements = input_data.get("tender_requirements", {})

            # Weights for QCBS
            technical_weight = input_data.get("technical_weight", 70.0)
            financial_weight = input_data.get("financial_weight", 30.0)

            self.log_info(
                f"Comparing bids for evaluation {evaluation_id} using {evaluation_method.value} method"
            )

            # Format data for LLM
            compliance_text = self._format_compliance_results(compliance_results)
            technical_text = self._format_technical_scores(technical_scores)
            financial_text = self._format_financial_scores(financial_scores)

            # Create prompt
            messages = self._create_prompt(
                system_prompt=SYSTEM_PROMPTS["comparison_expert"],
                user_prompt=COMPARISON_PROMPT,
                evaluation_method=evaluation_method.value,
                tender_requirements=json.dumps(tender_requirements, indent=2),
                compliance_results=compliance_text,
                technical_scores=technical_text,
                financial_scores=financial_text,
                technical_weight=technical_weight,
                financial_weight=financial_weight
            )

            # Invoke LLM
            comparison_data = await self._invoke_llm(messages, parse_json=True)

            # Validate response structure
            self._validate_output(
                comparison_data,
                required_fields=[
                    "evaluation_method",
                    "rankings",
                    "total_bids_evaluated",
                    "summary"
                ]
            )

            # Build ComparisonResult
            comparison_result = self._build_comparison_result(
                evaluation_id=evaluation_id,
                comparison_data=comparison_data,
                technical_weight=technical_weight,
                financial_weight=financial_weight
            )

            self.log_info(
                f"Comparison completed for evaluation {evaluation_id}: "
                f"Winner: {comparison_result.winner_vendor_name or 'None'}"
            )

            return comparison_result

        except Exception as e:
            self.log_error(f"Failed to compare bids: {str(e)}")
            raise

    def _format_compliance_results(
        self,
        compliance_results: List[Any]
    ) -> str:
        """Format compliance results for LLM."""
        lines = []
        for result in compliance_results:
            if isinstance(result, ComplianceResult):
                lines.append(
                    f"- Bid {result.bid_id}: {result.status.value} "
                    f"(Score: {result.overall_score}/100, Eligible: {result.is_eligible})"
                )
                if result.issues:
                    lines.append(f"  Issues: {len(result.issues)}")
                    for issue in result.issues[:3]:  # Top 3 issues
                        lines.append(f"    - [{issue.severity}] {issue.description}")
            else:
                lines.append(json.dumps(result, indent=2))

        return "\n".join(lines)

    def _format_technical_scores(
        self,
        technical_scores: List[Any]
    ) -> str:
        """Format technical scores for LLM."""
        lines = []
        for score in technical_scores:
            if isinstance(score, TechnicalScore):
                lines.append(
                    f"- Bid {score.bid_id}: {score.overall_score:.2f}/100"
                )
                lines.append(f"  Methodology: {score.methodology_score.score:.2f}")
                lines.append(f"  Team Qualifications: {score.team_qualifications_score.score:.2f}")
                lines.append(f"  Past Experience: {score.past_experience_score.score:.2f}")
                lines.append(f"  Innovation: {score.innovation_score.score:.2f}")
            else:
                lines.append(json.dumps(score, indent=2))

        return "\n".join(lines)

    def _format_financial_scores(
        self,
        financial_scores: List[Any]
    ) -> str:
        """Format financial scores for LLM."""
        lines = []
        for score in financial_scores:
            if isinstance(score, FinancialScore):
                lines.append(
                    f"- Bid {score.bid_id}: ${score.total_bid_amount:,.2f} "
                    f"(Normalized Score: {score.normalized_score:.2f}/100)"
                )
                lines.append(f"  Price Competitiveness: {score.price_competitiveness:.2f}")
                lines.append(f"  Cost Breakdown Quality: {score.cost_breakdown_quality:.2f}")
                if score.is_abnormally_low:
                    lines.append(f"  WARNING: Abnormally low bid")
            else:
                lines.append(json.dumps(score, indent=2))

        return "\n".join(lines)

    def _build_comparison_result(
        self,
        evaluation_id: str,
        comparison_data: Dict[str, Any],
        technical_weight: float,
        financial_weight: float
    ) -> ComparisonResult:
        """
        Build ComparisonResult from LLM output.

        Args:
            evaluation_id: Evaluation identifier
            comparison_data: Comparison data from LLM
            technical_weight: Technical weight percentage
            financial_weight: Financial weight percentage

        Returns:
            ComparisonResult instance
        """
        try:
            # Parse evaluation method
            evaluation_method = EvaluationMethod(comparison_data["evaluation_method"])

            # Parse rankings
            rankings = []
            for ranking_data in comparison_data["rankings"]:
                rankings.append(BidRanking(**ranking_data))

            # Parse cartel flags
            cartel_flags = []
            if "cartel_flags" in comparison_data:
                for flag_data in comparison_data["cartel_flags"]:
                    cartel_flags.append(CartelFlag(**flag_data))

            # Get winner information
            winner_bid_id = comparison_data.get("winner_bid_id")
            winner_vendor_name = comparison_data.get("winner_vendor_name")

            # Count compliant bids
            compliant_bids_count = sum(1 for r in rankings if r.is_compliant)

            # Build result
            comparison_result = ComparisonResult(
                evaluation_id=evaluation_id,
                evaluation_method=evaluation_method,
                rankings=rankings,
                winner_bid_id=winner_bid_id,
                winner_vendor_name=winner_vendor_name,
                cartel_flags=cartel_flags,
                technical_weight=technical_weight,
                financial_weight=financial_weight,
                total_bids_evaluated=comparison_data["total_bids_evaluated"],
                compliant_bids_count=compliant_bids_count,
                summary=comparison_data["summary"],
                compared_at=datetime.utcnow()
            )

            return comparison_result

        except Exception as e:
            self.log_error(f"Failed to build ComparisonResult: {str(e)}")
            raise ValueError(f"Invalid comparison data structure: {str(e)}")

    async def calculate_rankings(
        self,
        evaluation_method: EvaluationMethod,
        compliance_results: List[ComplianceResult],
        technical_scores: List[TechnicalScore],
        financial_scores: List[FinancialScore],
        technical_weight: float = 70.0,
        financial_weight: float = 30.0
    ) -> List[BidRanking]:
        """
        Calculate rankings directly without LLM (for verification or fallback).

        Args:
            evaluation_method: Evaluation method to use
            compliance_results: List of compliance results
            technical_scores: List of technical scores
            financial_scores: List of financial scores
            technical_weight: Technical weight for QCBS
            financial_weight: Financial weight for QCBS

        Returns:
            List of BidRanking instances
        """
        # Create lookup dicts
        compliance_map = {r.bid_id: r for r in compliance_results}
        technical_map = {s.bid_id: s for s in technical_scores}
        financial_map = {s.bid_id: s for s in financial_scores}

        # Get all bid IDs
        all_bid_ids = set(compliance_map.keys()) | set(technical_map.keys()) | set(financial_map.keys())

        rankings = []

        for bid_id in all_bid_ids:
            compliance = compliance_map.get(bid_id)
            technical = technical_map.get(bid_id)
            financial = financial_map.get(bid_id)

            # Skip if missing critical data
            if not all([compliance, technical, financial]):
                self.log_warning(f"Skipping bid {bid_id} due to missing evaluation data")
                continue

            is_compliant = compliance.is_eligible and compliance.status.value == "PASSED"
            technical_score = technical.overall_score
            financial_score = financial.normalized_score

            # Calculate combined score based on method
            if evaluation_method == EvaluationMethod.L1:
                # L1: Only price matters for compliant bids
                combined_score = financial_score if is_compliant else 0
            elif evaluation_method == EvaluationMethod.QCBS:
                # QCBS: Weighted combination
                combined_score = (
                    (technical_score * technical_weight / 100) +
                    (financial_score * financial_weight / 100)
                )
            elif evaluation_method == EvaluationMethod.TWO_STAGE:
                # Two-stage: Technical threshold, then price
                if technical_score >= 60.0:  # Technical threshold
                    combined_score = financial_score
                else:
                    combined_score = 0
            else:
                combined_score = 0

            # Get vendor name from financial score or technical score
            vendor_name = "Unknown"
            # Note: We would need to pass vendor names through or extract from parsed docs

            ranking = BidRanking(
                rank=0,  # Will be set after sorting
                bid_id=bid_id,
                vendor_name=vendor_name,
                technical_score=technical_score,
                financial_score=financial_score,
                combined_score=combined_score,
                is_compliant=is_compliant,
                is_winner=False  # Will be set for top rank
            )

            rankings.append(ranking)

        # Sort by combined score (descending)
        rankings.sort(key=lambda x: x.combined_score, reverse=True)

        # Assign ranks and mark winner
        for i, ranking in enumerate(rankings, 1):
            ranking.rank = i
            if i == 1 and ranking.is_compliant:
                ranking.is_winner = True

        return rankings

    def detect_cartel_patterns(
        self,
        financial_scores: List[FinancialScore],
        threshold_similarity: float = 0.02  # 2% price similarity
    ) -> List[CartelFlag]:
        """
        Detect potential cartel or collusion patterns.

        Args:
            financial_scores: List of financial scores
            threshold_similarity: Threshold for price similarity (as decimal)

        Returns:
            List of CartelFlag instances
        """
        flags = []

        if len(financial_scores) < 2:
            return flags

        # Sort by bid amount
        sorted_scores = sorted(financial_scores, key=lambda x: x.total_bid_amount)

        # Check for suspiciously similar pricing
        for i in range(len(sorted_scores) - 1):
            for j in range(i + 1, len(sorted_scores)):
                amount_i = sorted_scores[i].total_bid_amount
                amount_j = sorted_scores[j].total_bid_amount

                if amount_j == 0:
                    continue

                # Calculate percentage difference
                diff_percent = abs(amount_i - amount_j) / amount_j

                if diff_percent <= threshold_similarity:
                    flags.append(CartelFlag(
                        flag_type="identical_pricing",
                        severity="high",
                        description=f"Suspicious price similarity: {diff_percent * 100:.2f}% difference",
                        involved_bids=[sorted_scores[i].bid_id, sorted_scores[j].bid_id],
                        evidence=f"Amounts: ${amount_i:,.2f} vs ${amount_j:,.2f}"
                    ))

        return flags

    def extract_summary(self, comparison_result: ComparisonResult) -> Dict[str, Any]:
        """
        Extract a summary of the comparison result.

        Args:
            comparison_result: ComparisonResult instance

        Returns:
            Dict with summary information
        """
        return {
            "evaluation_id": comparison_result.evaluation_id,
            "evaluation_method": comparison_result.evaluation_method.value,
            "total_bids": comparison_result.total_bids_evaluated,
            "compliant_bids": comparison_result.compliant_bids_count,
            "winner_bid_id": comparison_result.winner_bid_id,
            "winner_vendor_name": comparison_result.winner_vendor_name,
            "cartel_flags_count": len(comparison_result.cartel_flags),
            "high_severity_flags": len([
                f for f in comparison_result.cartel_flags
                if f.severity == "high"
            ])
        }
