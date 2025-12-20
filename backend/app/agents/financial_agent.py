"""
Financial Agent - Evaluates financial proposals and pricing.
"""
import logging
import json
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent
from .schemas import (
    FinancialScore,
    ParsedBidDocument,
    EvaluationMethod
)
from .prompts import FINANCIAL_ANALYSIS_PROMPT, SYSTEM_PROMPTS


logger = logging.getLogger(__name__)


class FinancialAgent(BaseAgent):
    """
    Agent responsible for evaluating financial proposals.

    Evaluates:
    - Price competitiveness
    - Cost breakdown quality
    - Abnormally low bid detection
    - Financial risks
    - Value for money
    """

    # Threshold for abnormally low bid detection (% below average)
    ABNORMALLY_LOW_THRESHOLD = 25.0

    def __init__(self, **kwargs):
        """Initialize FinancialAgent."""
        super().__init__(agent_name="FinancialAgent", **kwargs)

    async def invoke(self, input_data: Dict[str, Any]) -> FinancialScore:
        """
        Evaluate financial proposal of a bid.

        Args:
            input_data: Dict containing:
                - bid_id: Unique identifier for the bid
                - parsed_document: ParsedBidDocument instance or dict
                - tender_requirements: Dict with tender requirements
                - all_bid_amounts: List of all bid amounts for comparison
                - evaluation_method: EvaluationMethod
                - budget: Optional tender budget
                - vendor_name: Optional vendor name

        Returns:
            FinancialScore: Detailed financial evaluation score

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
            all_bid_amounts = input_data.get("all_bid_amounts", [])
            evaluation_method = input_data.get("evaluation_method", EvaluationMethod.QCBS)
            budget = input_data.get("budget", tender_requirements.get("budget", 0))

            # Get parsed document or content
            if "parsed_document" in input_data:
                parsed_doc = input_data["parsed_document"]
                if isinstance(parsed_doc, ParsedBidDocument):
                    vendor_name = parsed_doc.vendor_info.name
                    bid_amount = parsed_doc.pricing_table.total
                    bid_content = self._format_bid_content(parsed_doc)
                else:
                    vendor_name = input_data.get("vendor_name", "Unknown Vendor")
                    bid_amount = input_data.get("bid_amount", 0)
                    bid_content = json.dumps(parsed_doc, indent=2)
            else:
                vendor_name = input_data.get("vendor_name", "Unknown Vendor")
                bid_amount = input_data.get("bid_amount", 0)
                bid_content = input_data.get("bid_content", "No content provided")

            self.log_info(
                f"Evaluating financial proposal for bid {bid_id} from {vendor_name}: "
                f"${bid_amount:,.2f}"
            )

            # Format all bid amounts for comparison
            bid_amounts_text = self._format_bid_amounts(all_bid_amounts)

            # Create prompt
            messages = self._create_prompt(
                system_prompt=SYSTEM_PROMPTS["financial_analyzer"],
                user_prompt=FINANCIAL_ANALYSIS_PROMPT,
                budget=f"{budget:,.2f}",
                evaluation_method=evaluation_method.value if isinstance(evaluation_method, EvaluationMethod) else evaluation_method,
                all_bid_amounts=bid_amounts_text,
                vendor_name=vendor_name,
                bid_id=bid_id,
                bid_amount=f"{bid_amount:,.2f}",
                bid_content=bid_content
            )

            # Invoke LLM
            financial_data = await self._invoke_llm(messages, parse_json=True)

            # Validate response structure
            self._validate_output(
                financial_data,
                required_fields=[
                    "total_bid_amount",
                    "normalized_score",
                    "price_competitiveness",
                    "cost_breakdown_quality",
                    "is_abnormally_low",
                    "summary"
                ]
            )

            # Build FinancialScore
            financial_score = self._build_financial_score(
                bid_id=bid_id,
                financial_data=financial_data
            )

            self.log_info(
                f"Financial evaluation completed for bid {bid_id}: "
                f"Normalized Score: {financial_score.normalized_score:.2f}/100"
            )

            return financial_score

        except Exception as e:
            self.log_error(f"Failed to evaluate financial proposal: {str(e)}")
            raise

    def _format_bid_content(self, parsed_doc: ParsedBidDocument) -> str:
        """
        Format parsed document for financial evaluation.

        Args:
            parsed_doc: ParsedBidDocument instance

        Returns:
            Formatted string representation
        """
        content_parts = []

        # Pricing table
        content_parts.append("=== PRICING BREAKDOWN ===")
        content_parts.append(f"Currency: {parsed_doc.pricing_table.currency}")
        content_parts.append(f"\nLine Items:")

        for i, item in enumerate(parsed_doc.pricing_table.items, 1):
            content_parts.append(f"\n{i}. {item.item_name}")
            if item.description:
                content_parts.append(f"   Description: {item.description}")
            if item.quantity:
                content_parts.append(f"   Quantity: {item.quantity} {item.unit or ''}")
            content_parts.append(f"   Unit Price: {item.unit_price:,.2f}")
            content_parts.append(f"   Total: {item.total_price:,.2f}")

        content_parts.append(f"\nSubtotal: {parsed_doc.pricing_table.subtotal:,.2f}")
        if parsed_doc.pricing_table.taxes:
            content_parts.append(f"Taxes: {parsed_doc.pricing_table.taxes:,.2f}")
        content_parts.append(f"TOTAL: {parsed_doc.pricing_table.total:,.2f}")

        # Look for financial sections in document
        if parsed_doc.sections:
            financial_sections = [
                s for s in parsed_doc.sections
                if any(keyword in s.section_name.lower()
                       for keyword in ["price", "cost", "financial", "budget"])
            ]
            if financial_sections:
                content_parts.append("\n=== FINANCIAL SECTIONS ===")
                for section in financial_sections:
                    content_parts.append(f"\n--- {section.section_name} ---")
                    content_parts.append(section.content)

        return "\n".join(content_parts)

    def _format_bid_amounts(self, all_bid_amounts: List[Dict[str, Any]]) -> str:
        """
        Format all bid amounts for comparison context.

        Args:
            all_bid_amounts: List of dicts with bid_id, vendor_name, amount

        Returns:
            Formatted string
        """
        if not all_bid_amounts:
            return "No other bids for comparison"

        lines = []
        for bid in sorted(all_bid_amounts, key=lambda x: x.get("amount", 0)):
            lines.append(
                f"- {bid.get('vendor_name', 'Unknown')}: ${bid.get('amount', 0):,.2f}"
            )

        # Add statistics
        amounts = [b.get("amount", 0) for b in all_bid_amounts]
        if amounts:
            avg_amount = sum(amounts) / len(amounts)
            min_amount = min(amounts)
            max_amount = max(amounts)

            lines.append(f"\nStatistics:")
            lines.append(f"- Lowest Bid: ${min_amount:,.2f}")
            lines.append(f"- Average Bid: ${avg_amount:,.2f}")
            lines.append(f"- Highest Bid: ${max_amount:,.2f}")

        return "\n".join(lines)

    def _build_financial_score(
        self,
        bid_id: str,
        financial_data: Dict[str, Any]
    ) -> FinancialScore:
        """
        Build FinancialScore from LLM output.

        Args:
            bid_id: Bid identifier
            financial_data: Financial evaluation data from LLM

        Returns:
            FinancialScore instance
        """
        try:
            # Build result
            financial_score = FinancialScore(
                bid_id=bid_id,
                total_bid_amount=float(financial_data["total_bid_amount"]),
                normalized_score=float(financial_data["normalized_score"]),
                price_competitiveness=float(financial_data["price_competitiveness"]),
                cost_breakdown_quality=float(financial_data["cost_breakdown_quality"]),
                is_abnormally_low=bool(financial_data["is_abnormally_low"]),
                abnormally_low_threshold=financial_data.get("abnormally_low_threshold"),
                price_analysis=financial_data.get("price_analysis", ""),
                cost_breakdown_analysis=financial_data.get("cost_breakdown_analysis", ""),
                risks=financial_data.get("risks", []),
                summary=financial_data["summary"],
                evaluated_at=datetime.utcnow()
            )

            return financial_score

        except Exception as e:
            self.log_error(f"Failed to build FinancialScore: {str(e)}")
            raise ValueError(f"Invalid financial evaluation data structure: {str(e)}")

    async def evaluate_multiple(
        self,
        bids: list[Dict[str, Any]],
        tender_requirements: Dict[str, Any],
        evaluation_method: EvaluationMethod = EvaluationMethod.QCBS
    ) -> list[FinancialScore]:
        """
        Evaluate financial proposals for multiple bids.

        Args:
            bids: List of bid data dicts (with parsed_document)
            tender_requirements: Tender requirements dict
            evaluation_method: Evaluation method to use

        Returns:
            List of FinancialScore instances
        """
        # Collect all bid amounts for comparison
        all_bid_amounts = []
        for bid_data in bids:
            if "parsed_document" in bid_data:
                parsed_doc = bid_data["parsed_document"]
                if isinstance(parsed_doc, ParsedBidDocument):
                    all_bid_amounts.append({
                        "bid_id": bid_data["bid_id"],
                        "vendor_name": parsed_doc.vendor_info.name,
                        "amount": parsed_doc.pricing_table.total
                    })
                else:
                    all_bid_amounts.append({
                        "bid_id": bid_data["bid_id"],
                        "vendor_name": bid_data.get("vendor_name", "Unknown"),
                        "amount": bid_data.get("bid_amount", 0)
                    })

        financial_scores = []

        for bid_data in bids:
            try:
                # Add context to each bid
                bid_input = {
                    **bid_data,
                    "tender_requirements": tender_requirements,
                    "all_bid_amounts": all_bid_amounts,
                    "evaluation_method": evaluation_method
                }
                financial_score = await self.invoke(bid_input)
                financial_scores.append(financial_score)
            except Exception as e:
                self.log_error(
                    f"Failed to evaluate financial proposal for bid {bid_data.get('bid_id', 'unknown')}: {str(e)}"
                )
                # Continue with other bids
                continue

        self.log_info(
            f"Evaluated financial proposals for {len(financial_scores)} out of {len(bids)} bids"
        )

        return financial_scores

    def calculate_normalized_scores(
        self,
        financial_scores: list[FinancialScore]
    ) -> list[FinancialScore]:
        """
        Recalculate normalized scores based on actual bid amounts.

        For QCBS: Lowest bid gets 100, others get (Lowest/Amount) * 100

        Args:
            financial_scores: List of FinancialScore instances

        Returns:
            Updated list of FinancialScore instances
        """
        if not financial_scores:
            return financial_scores

        # Find lowest bid amount
        lowest_amount = min(score.total_bid_amount for score in financial_scores)

        # Recalculate normalized scores
        for score in financial_scores:
            if score.total_bid_amount > 0:
                score.normalized_score = (lowest_amount / score.total_bid_amount) * 100
            else:
                score.normalized_score = 0

        self.log_info(
            f"Recalculated normalized scores for {len(financial_scores)} bids "
            f"(lowest bid: ${lowest_amount:,.2f})"
        )

        return financial_scores

    def extract_summary(self, financial_score: FinancialScore) -> Dict[str, Any]:
        """
        Extract a summary of the financial score.

        Args:
            financial_score: FinancialScore instance

        Returns:
            Dict with summary information
        """
        return {
            "bid_id": financial_score.bid_id,
            "total_bid_amount": financial_score.total_bid_amount,
            "normalized_score": round(financial_score.normalized_score, 2),
            "price_competitiveness": round(financial_score.price_competitiveness, 2),
            "cost_breakdown_quality": round(financial_score.cost_breakdown_quality, 2),
            "is_abnormally_low": financial_score.is_abnormally_low,
            "risks_count": len(financial_score.risks)
        }
