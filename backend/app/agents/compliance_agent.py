"""
Compliance Agent - Evaluates bid compliance against tender requirements.
"""
import logging
import json
from typing import Dict, Any
from datetime import datetime

from .base_agent import BaseAgent
from .schemas import (
    ComplianceResult,
    ComplianceIssue,
    ComplianceStatus,
    ParsedBidDocument
)
from .prompts import COMPLIANCE_CHECK_PROMPT, SYSTEM_PROMPTS


logger = logging.getLogger(__name__)


class ComplianceAgent(BaseAgent):
    """
    Agent responsible for checking bid compliance against tender requirements.

    Evaluates:
    - Document completeness
    - Mandatory criteria compliance
    - Eligibility requirements
    - Format and procedural compliance
    - Technical baseline compliance
    """

    def __init__(self, **kwargs):
        """Initialize ComplianceAgent."""
        super().__init__(agent_name="ComplianceAgent", **kwargs)

    async def invoke(self, input_data: Dict[str, Any]) -> ComplianceResult:
        """
        Evaluate bid compliance against tender requirements.

        Args:
            input_data: Dict containing:
                - bid_id: Unique identifier for the bid
                - parsed_document: ParsedBidDocument instance or dict
                - tender_requirements: Dict with tender requirements
                - vendor_name: Optional vendor name

        Returns:
            ComplianceResult: Detailed compliance evaluation

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

            self.log_info(f"Checking compliance for bid {bid_id} from {vendor_name}")

            # Create prompt
            messages = self._create_prompt(
                system_prompt=SYSTEM_PROMPTS["compliance_checker"],
                user_prompt=COMPLIANCE_CHECK_PROMPT,
                tender_requirements=json.dumps(tender_requirements, indent=2),
                vendor_name=vendor_name,
                bid_id=bid_id,
                bid_content=bid_content
            )

            # Invoke LLM
            compliance_data = await self._invoke_llm(messages, parse_json=True)

            # Validate response structure
            self._validate_output(
                compliance_data,
                required_fields=["status", "overall_score", "is_eligible", "summary"]
            )

            # Build ComplianceResult
            compliance_result = self._build_compliance_result(
                bid_id=bid_id,
                compliance_data=compliance_data
            )

            self.log_info(
                f"Compliance check completed for bid {bid_id}: "
                f"{compliance_result.status.value} - "
                f"Score: {compliance_result.overall_score}/100"
            )

            return compliance_result

        except Exception as e:
            self.log_error(f"Failed to check compliance: {str(e)}")
            raise

    def _format_bid_content(self, parsed_doc: ParsedBidDocument) -> str:
        """
        Format parsed document for compliance evaluation.

        Args:
            parsed_doc: ParsedBidDocument instance

        Returns:
            Formatted string representation
        """
        content_parts = []

        # Vendor information
        content_parts.append("=== VENDOR INFORMATION ===")
        content_parts.append(f"Name: {parsed_doc.vendor_info.name}")
        if parsed_doc.vendor_info.registration_number:
            content_parts.append(f"Registration: {parsed_doc.vendor_info.registration_number}")
        if parsed_doc.vendor_info.years_in_business:
            content_parts.append(f"Years in Business: {parsed_doc.vendor_info.years_in_business}")

        # Pricing summary
        content_parts.append("\n=== PRICING SUMMARY ===")
        content_parts.append(f"Total Amount: {parsed_doc.pricing_table.currency} {parsed_doc.pricing_table.total:,.2f}")
        content_parts.append(f"Number of Items: {len(parsed_doc.pricing_table.items)}")

        # Technical specifications
        if parsed_doc.technical_specs:
            content_parts.append("\n=== TECHNICAL SPECIFICATIONS ===")
            for i, spec in enumerate(parsed_doc.technical_specs, 1):
                content_parts.append(f"{i}. {spec.requirement}")
                content_parts.append(f"   Solution: {spec.proposed_solution}")
                content_parts.append(f"   Meets Requirement: {spec.meets_requirement}")

        # Compliance statements
        if parsed_doc.compliance_statements:
            content_parts.append("\n=== COMPLIANCE STATEMENTS ===")
            for i, statement in enumerate(parsed_doc.compliance_statements, 1):
                content_parts.append(f"{i}. {statement}")

        # Document sections
        if parsed_doc.sections:
            content_parts.append("\n=== DOCUMENT SECTIONS ===")
            for section in parsed_doc.sections:
                content_parts.append(f"\n--- {section.section_name} ---")
                content_parts.append(section.content[:500] + "..." if len(section.content) > 500 else section.content)

        return "\n".join(content_parts)

    def _build_compliance_result(
        self,
        bid_id: str,
        compliance_data: Dict[str, Any]
    ) -> ComplianceResult:
        """
        Build ComplianceResult from LLM output.

        Args:
            bid_id: Bid identifier
            compliance_data: Compliance data from LLM

        Returns:
            ComplianceResult instance
        """
        try:
            # Parse status
            status = ComplianceStatus(compliance_data["status"])

            # Parse issues
            issues = []
            if "issues" in compliance_data:
                for issue_data in compliance_data["issues"]:
                    issues.append(ComplianceIssue(**issue_data))

            # Build result
            compliance_result = ComplianceResult(
                bid_id=bid_id,
                status=status,
                overall_score=float(compliance_data["overall_score"]),
                issues=issues,
                passed_criteria=compliance_data.get("passed_criteria", []),
                failed_criteria=compliance_data.get("failed_criteria", []),
                recommendations=compliance_data.get("recommendations", []),
                is_eligible=bool(compliance_data["is_eligible"]),
                summary=compliance_data["summary"],
                checked_at=datetime.utcnow()
            )

            return compliance_result

        except Exception as e:
            self.log_error(f"Failed to build ComplianceResult: {str(e)}")
            raise ValueError(f"Invalid compliance data structure: {str(e)}")

    async def evaluate_multiple(
        self,
        bids: list[Dict[str, Any]],
        tender_requirements: Dict[str, Any]
    ) -> list[ComplianceResult]:
        """
        Evaluate compliance for multiple bids.

        Args:
            bids: List of bid data dicts (with parsed_document)
            tender_requirements: Tender requirements dict

        Returns:
            List of ComplianceResult instances
        """
        compliance_results = []

        for bid_data in bids:
            try:
                # Add tender requirements to each bid
                bid_input = {**bid_data, "tender_requirements": tender_requirements}
                compliance_result = await self.invoke(bid_input)
                compliance_results.append(compliance_result)
            except Exception as e:
                self.log_error(
                    f"Failed to evaluate compliance for bid {bid_data.get('bid_id', 'unknown')}: {str(e)}"
                )
                # Continue with other bids
                continue

        self.log_info(
            f"Evaluated compliance for {len(compliance_results)} out of {len(bids)} bids"
        )

        return compliance_results

    def get_compliant_bids(
        self,
        compliance_results: list[ComplianceResult]
    ) -> list[str]:
        """
        Get list of compliant bid IDs.

        Args:
            compliance_results: List of ComplianceResult instances

        Returns:
            List of compliant bid IDs
        """
        compliant_ids = [
            result.bid_id
            for result in compliance_results
            if result.is_eligible and result.status == ComplianceStatus.PASSED
        ]

        self.log_info(
            f"Found {len(compliant_ids)} compliant bids out of {len(compliance_results)}"
        )

        return compliant_ids

    def extract_summary(self, compliance_result: ComplianceResult) -> Dict[str, Any]:
        """
        Extract a summary of the compliance result.

        Args:
            compliance_result: ComplianceResult instance

        Returns:
            Dict with summary information
        """
        return {
            "bid_id": compliance_result.bid_id,
            "status": compliance_result.status.value,
            "overall_score": compliance_result.overall_score,
            "is_eligible": compliance_result.is_eligible,
            "issues_count": len(compliance_result.issues),
            "critical_issues": len([
                issue for issue in compliance_result.issues
                if issue.severity == "critical"
            ]),
            "passed_criteria_count": len(compliance_result.passed_criteria),
            "failed_criteria_count": len(compliance_result.failed_criteria)
        }
