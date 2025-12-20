"""
Technical Agent - Evaluates technical quality of bid proposals.
"""
import logging
import json
from typing import Dict, Any
from datetime import datetime

from .base_agent import BaseAgent
from .schemas import (
    TechnicalScore,
    ScoreBreakdown,
    ParsedBidDocument
)
from .prompts import TECHNICAL_EVALUATION_PROMPT, SYSTEM_PROMPTS


logger = logging.getLogger(__name__)


class TechnicalAgent(BaseAgent):
    """
    Agent responsible for evaluating technical quality of bid proposals.

    Evaluation criteria:
    - Methodology: 30%
    - Team Qualifications: 25%
    - Past Experience: 25%
    - Innovation: 20%
    """

    # Default weights
    METHODOLOGY_WEIGHT = 30.0
    TEAM_QUALIFICATIONS_WEIGHT = 25.0
    PAST_EXPERIENCE_WEIGHT = 25.0
    INNOVATION_WEIGHT = 20.0

    def __init__(self, **kwargs):
        """Initialize TechnicalAgent."""
        super().__init__(agent_name="TechnicalAgent", **kwargs)

    async def invoke(self, input_data: Dict[str, Any]) -> TechnicalScore:
        """
        Evaluate technical quality of a bid proposal.

        Args:
            input_data: Dict containing:
                - bid_id: Unique identifier for the bid
                - parsed_document: ParsedBidDocument instance or dict
                - tender_requirements: Dict with tender requirements
                - vendor_name: Optional vendor name

        Returns:
            TechnicalScore: Detailed technical evaluation score

        Raises:
            ValueError: If required input fields are missing
            Exception: If evaluation fails
        """
        try:
            # Validate input
            if "bid_id" not in input_data:
                raise ValueError("bid_id is required")
            if "tender_requirements" not in input_data:
                raise ValueError("tender_requirements is required")

            bid_id = input_data["bid_id"]
            tender_requirements = input_data["tender_requirements"]

            # Get parsed document or content
            if "parsed_document" in input_data:
                parsed_doc = input_data["parsed_document"]
                if isinstance(parsed_doc, ParsedBidDocument):
                    vendor_name = parsed_doc.vendor_info.name
                    bid_content = self._format_bid_content(parsed_doc)
                else:
                    vendor_name = input_data.get("vendor_name", "Unknown Vendor")
                    bid_content = json.dumps(parsed_doc, indent=2)
            else:
                vendor_name = input_data.get("vendor_name", "Unknown Vendor")
                bid_content = input_data.get("bid_content", "No content provided")

            self.log_info(f"Evaluating technical proposal for bid {bid_id} from {vendor_name}")

            # Create prompt
            messages = self._create_prompt(
                system_prompt=SYSTEM_PROMPTS["technical_evaluator"],
                user_prompt=TECHNICAL_EVALUATION_PROMPT,
                tender_requirements=json.dumps(tender_requirements, indent=2),
                vendor_name=vendor_name,
                bid_id=bid_id,
                bid_content=bid_content
            )

            # Invoke LLM
            technical_data = await self._invoke_llm(messages, parse_json=True)

            # Validate response structure
            self._validate_output(
                technical_data,
                required_fields=[
                    "overall_score",
                    "methodology_score",
                    "team_qualifications_score",
                    "past_experience_score",
                    "innovation_score",
                    "summary"
                ]
            )

            # Build TechnicalScore
            technical_score = self._build_technical_score(
                bid_id=bid_id,
                technical_data=technical_data
            )

            self.log_info(
                f"Technical evaluation completed for bid {bid_id}: "
                f"Overall Score: {technical_score.overall_score:.2f}/100"
            )

            return technical_score

        except Exception as e:
            self.log_error(f"Failed to evaluate technical proposal: {str(e)}")
            raise

    def _format_bid_content(self, parsed_doc: ParsedBidDocument) -> str:
        """
        Format parsed document for technical evaluation.

        Args:
            parsed_doc: ParsedBidDocument instance

        Returns:
            Formatted string representation
        """
        content_parts = []

        # Vendor information
        content_parts.append("=== VENDOR INFORMATION ===")
        content_parts.append(f"Name: {parsed_doc.vendor_info.name}")
        if parsed_doc.vendor_info.years_in_business:
            content_parts.append(f"Years in Business: {parsed_doc.vendor_info.years_in_business}")

        # Technical specifications
        if parsed_doc.technical_specs:
            content_parts.append("\n=== TECHNICAL SPECIFICATIONS ===")
            for i, spec in enumerate(parsed_doc.technical_specs, 1):
                content_parts.append(f"\n{i}. Requirement: {spec.requirement}")
                content_parts.append(f"   Proposed Solution: {spec.proposed_solution}")
                content_parts.append(f"   Meets Requirement: {spec.meets_requirement}")
                if spec.notes:
                    content_parts.append(f"   Notes: {spec.notes}")

        # Document sections (look for methodology, team, experience sections)
        if parsed_doc.sections:
            content_parts.append("\n=== DETAILED PROPOSAL SECTIONS ===")
            for section in parsed_doc.sections:
                content_parts.append(f"\n--- {section.section_name} ---")
                content_parts.append(section.content)

        # Raw text if no structured sections
        if not parsed_doc.sections and parsed_doc.raw_text:
            content_parts.append("\n=== FULL PROPOSAL TEXT ===")
            content_parts.append(parsed_doc.raw_text[:5000])  # Limit to avoid token overflow

        return "\n".join(content_parts)

    def _build_technical_score(
        self,
        bid_id: str,
        technical_data: Dict[str, Any]
    ) -> TechnicalScore:
        """
        Build TechnicalScore from LLM output.

        Args:
            bid_id: Bid identifier
            technical_data: Technical evaluation data from LLM

        Returns:
            TechnicalScore instance
        """
        try:
            # Parse score breakdowns
            methodology_score = ScoreBreakdown(**technical_data["methodology_score"])
            team_qualifications_score = ScoreBreakdown(**technical_data["team_qualifications_score"])
            past_experience_score = ScoreBreakdown(**technical_data["past_experience_score"])
            innovation_score = ScoreBreakdown(**technical_data["innovation_score"])

            # Verify overall score calculation
            calculated_overall = (
                methodology_score.weighted_score +
                team_qualifications_score.weighted_score +
                past_experience_score.weighted_score +
                innovation_score.weighted_score
            )

            # Use calculated score if provided score is inconsistent
            overall_score = technical_data.get("overall_score", calculated_overall)
            if abs(overall_score - calculated_overall) > 1.0:  # Allow 1 point tolerance
                self.log_warning(
                    f"Overall score mismatch for bid {bid_id}: "
                    f"Provided: {overall_score}, Calculated: {calculated_overall}. "
                    f"Using calculated score."
                )
                overall_score = calculated_overall

            # Build result
            technical_score = TechnicalScore(
                bid_id=bid_id,
                overall_score=float(overall_score),
                methodology_score=methodology_score,
                team_qualifications_score=team_qualifications_score,
                past_experience_score=past_experience_score,
                innovation_score=innovation_score,
                strengths=technical_data.get("strengths", []),
                weaknesses=technical_data.get("weaknesses", []),
                summary=technical_data["summary"],
                evaluated_at=datetime.utcnow()
            )

            return technical_score

        except Exception as e:
            self.log_error(f"Failed to build TechnicalScore: {str(e)}")
            raise ValueError(f"Invalid technical evaluation data structure: {str(e)}")

    async def evaluate_multiple(
        self,
        bids: list[Dict[str, Any]],
        tender_requirements: Dict[str, Any]
    ) -> list[TechnicalScore]:
        """
        Evaluate technical proposals for multiple bids.

        Args:
            bids: List of bid data dicts (with parsed_document)
            tender_requirements: Tender requirements dict

        Returns:
            List of TechnicalScore instances
        """
        technical_scores = []

        for bid_data in bids:
            try:
                # Add tender requirements to each bid
                bid_input = {**bid_data, "tender_requirements": tender_requirements}
                technical_score = await self.invoke(bid_input)
                technical_scores.append(technical_score)
            except Exception as e:
                self.log_error(
                    f"Failed to evaluate technical proposal for bid {bid_data.get('bid_id', 'unknown')}: {str(e)}"
                )
                # Continue with other bids
                continue

        self.log_info(
            f"Evaluated technical proposals for {len(technical_scores)} out of {len(bids)} bids"
        )

        return technical_scores

    def get_top_technical_bids(
        self,
        technical_scores: list[TechnicalScore],
        threshold: float = 60.0,
        top_n: int = None
    ) -> list[str]:
        """
        Get list of bid IDs that meet technical threshold.

        Args:
            technical_scores: List of TechnicalScore instances
            threshold: Minimum technical score (default: 60.0)
            top_n: Optional limit to top N bids

        Returns:
            List of qualified bid IDs
        """
        # Filter by threshold and sort by score
        qualified = [
            score for score in technical_scores
            if score.overall_score >= threshold
        ]
        qualified.sort(key=lambda x: x.overall_score, reverse=True)

        # Limit to top N if specified
        if top_n:
            qualified = qualified[:top_n]

        qualified_ids = [score.bid_id for score in qualified]

        self.log_info(
            f"Found {len(qualified_ids)} bids meeting technical threshold of {threshold}"
        )

        return qualified_ids

    def extract_summary(self, technical_score: TechnicalScore) -> Dict[str, Any]:
        """
        Extract a summary of the technical score.

        Args:
            technical_score: TechnicalScore instance

        Returns:
            Dict with summary information
        """
        return {
            "bid_id": technical_score.bid_id,
            "overall_score": round(technical_score.overall_score, 2),
            "methodology_score": round(technical_score.methodology_score.score, 2),
            "team_qualifications_score": round(technical_score.team_qualifications_score.score, 2),
            "past_experience_score": round(technical_score.past_experience_score.score, 2),
            "innovation_score": round(technical_score.innovation_score.score, 2),
            "strengths_count": len(technical_score.strengths),
            "weaknesses_count": len(technical_score.weaknesses)
        }
