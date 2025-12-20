"""
Report Agent - Generates comprehensive evaluation reports.
"""
import logging
import json
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent
from .schemas import (
    EvaluationReport,
    ComplianceResult,
    TechnicalScore,
    FinancialScore,
    ComparisonResult,
    EvaluationMethod
)
from .prompts import REPORT_GENERATION_PROMPT, SYSTEM_PROMPTS


logger = logging.getLogger(__name__)


class ReportAgent(BaseAgent):
    """
    Agent responsible for generating comprehensive evaluation reports.

    Generates:
    - Executive summary
    - Methodology description
    - Bids summary
    - Detailed findings
    - Recommendations
    - Risk analysis
    - Cartel analysis
    """

    def __init__(self, **kwargs):
        """Initialize ReportAgent."""
        super().__init__(
            agent_name="ReportAgent",
            max_tokens=8192,  # Reports need more tokens
            **kwargs
        )

    async def invoke(self, input_data: Dict[str, Any]) -> EvaluationReport:
        """
        Generate comprehensive evaluation report.

        Args:
            input_data: Dict containing:
                - evaluation_id: Unique identifier for the evaluation
                - tender_reference: Tender reference number
                - tender_title: Tender title
                - evaluation_method: EvaluationMethod
                - compliance_results: List of ComplianceResult instances
                - technical_scores: List of TechnicalScore instances
                - financial_scores: List of FinancialScore instances
                - comparison_result: ComparisonResult instance
                - metadata: Optional additional metadata

        Returns:
            EvaluationReport: Comprehensive evaluation report

        Raises:
            ValueError: If required input fields are missing
            Exception: If report generation fails
        """
        try:
            # Validate input
            required_fields = [
                "evaluation_id", "tender_reference", "tender_title",
                "evaluation_method", "compliance_results", "technical_scores",
                "financial_scores", "comparison_result"
            ]
            for field in required_fields:
                if field not in input_data:
                    raise ValueError(f"{field} is required")

            evaluation_id = input_data["evaluation_id"]
            tender_reference = input_data["tender_reference"]
            tender_title = input_data["tender_title"]
            evaluation_method = input_data["evaluation_method"]
            if isinstance(evaluation_method, str):
                evaluation_method = EvaluationMethod(evaluation_method)

            compliance_results = input_data["compliance_results"]
            technical_scores = input_data["technical_scores"]
            financial_scores = input_data["financial_scores"]
            comparison_result = input_data["comparison_result"]
            metadata = input_data.get("metadata", {})

            self.log_info(f"Generating evaluation report for {evaluation_id}")

            # Format data for LLM
            compliance_text = self._format_compliance_results(compliance_results)
            technical_text = self._format_technical_scores(technical_scores)
            financial_text = self._format_financial_scores(financial_scores)
            comparison_text = self._format_comparison_result(comparison_result)

            # Create prompt
            messages = self._create_prompt(
                system_prompt=SYSTEM_PROMPTS["report_writer"],
                user_prompt=REPORT_GENERATION_PROMPT,
                evaluation_id=evaluation_id,
                tender_reference=tender_reference,
                tender_title=tender_title,
                evaluation_method=evaluation_method.value,
                compliance_results=compliance_text,
                technical_scores=technical_text,
                financial_scores=financial_text,
                comparison_result=comparison_text
            )

            # Invoke LLM
            report_data = await self._invoke_llm(messages, parse_json=True)

            # Validate response structure
            self._validate_output(
                report_data,
                required_fields=[
                    "executive_summary",
                    "methodology_description",
                    "recommendations"
                ]
            )

            # Build EvaluationReport
            evaluation_report = self._build_evaluation_report(
                evaluation_id=evaluation_id,
                tender_reference=tender_reference,
                tender_title=tender_title,
                evaluation_method=evaluation_method,
                report_data=report_data,
                compliance_results=compliance_results,
                technical_scores=technical_scores,
                financial_scores=financial_scores,
                comparison_result=comparison_result,
                metadata=metadata
            )

            self.log_info(f"Report generated successfully for evaluation {evaluation_id}")

            return evaluation_report

        except Exception as e:
            self.log_error(f"Failed to generate report: {str(e)}")
            raise

    def _format_compliance_results(
        self,
        compliance_results: List[Any]
    ) -> str:
        """Format compliance results for report."""
        lines = ["# Compliance Results\n"]

        for result in compliance_results:
            if isinstance(result, ComplianceResult):
                lines.append(f"## Bid: {result.bid_id}")
                lines.append(f"- Status: **{result.status.value}**")
                lines.append(f"- Overall Score: {result.overall_score}/100")
                lines.append(f"- Eligible: {result.is_eligible}")
                lines.append(f"- Passed Criteria: {len(result.passed_criteria)}")
                lines.append(f"- Failed Criteria: {len(result.failed_criteria)}")

                if result.issues:
                    lines.append(f"\n**Issues ({len(result.issues)}):**")
                    for issue in result.issues:
                        lines.append(f"- [{issue.severity}] {issue.description}")

                lines.append(f"\n**Summary:** {result.summary}\n")
            else:
                lines.append(json.dumps(result, indent=2))

        return "\n".join(lines)

    def _format_technical_scores(
        self,
        technical_scores: List[Any]
    ) -> str:
        """Format technical scores for report."""
        lines = ["# Technical Evaluation Scores\n"]

        for score in technical_scores:
            if isinstance(score, TechnicalScore):
                lines.append(f"## Bid: {score.bid_id}")
                lines.append(f"- Overall Score: **{score.overall_score:.2f}/100**")
                lines.append(f"\n**Score Breakdown:**")
                lines.append(f"- Methodology: {score.methodology_score.score:.2f} (Weight: {score.methodology_score.weight}%)")
                lines.append(f"- Team Qualifications: {score.team_qualifications_score.score:.2f} (Weight: {score.team_qualifications_score.weight}%)")
                lines.append(f"- Past Experience: {score.past_experience_score.score:.2f} (Weight: {score.past_experience_score.weight}%)")
                lines.append(f"- Innovation: {score.innovation_score.score:.2f} (Weight: {score.innovation_score.weight}%)")

                if score.strengths:
                    lines.append(f"\n**Strengths:**")
                    for strength in score.strengths:
                        lines.append(f"- {strength}")

                if score.weaknesses:
                    lines.append(f"\n**Weaknesses:**")
                    for weakness in score.weaknesses:
                        lines.append(f"- {weakness}")

                lines.append(f"\n**Summary:** {score.summary}\n")
            else:
                lines.append(json.dumps(score, indent=2))

        return "\n".join(lines)

    def _format_financial_scores(
        self,
        financial_scores: List[Any]
    ) -> str:
        """Format financial scores for report."""
        lines = ["# Financial Evaluation Scores\n"]

        for score in financial_scores:
            if isinstance(score, FinancialScore):
                lines.append(f"## Bid: {score.bid_id}")
                lines.append(f"- Total Bid Amount: **${score.total_bid_amount:,.2f}**")
                lines.append(f"- Normalized Score: {score.normalized_score:.2f}/100")
                lines.append(f"- Price Competitiveness: {score.price_competitiveness:.2f}/100")
                lines.append(f"- Cost Breakdown Quality: {score.cost_breakdown_quality:.2f}/100")

                if score.is_abnormally_low:
                    lines.append(f"- **WARNING: Abnormally Low Bid**")

                if score.risks:
                    lines.append(f"\n**Financial Risks:**")
                    for risk in score.risks:
                        lines.append(f"- {risk}")

                lines.append(f"\n**Price Analysis:** {score.price_analysis}")
                lines.append(f"\n**Cost Breakdown Analysis:** {score.cost_breakdown_analysis}")
                lines.append(f"\n**Summary:** {score.summary}\n")
            else:
                lines.append(json.dumps(score, indent=2))

        return "\n".join(lines)

    def _format_comparison_result(
        self,
        comparison_result: Any
    ) -> str:
        """Format comparison result for report."""
        lines = ["# Bid Comparison and Rankings\n"]

        if isinstance(comparison_result, ComparisonResult):
            lines.append(f"- Evaluation Method: **{comparison_result.evaluation_method.value}**")
            lines.append(f"- Total Bids Evaluated: {comparison_result.total_bids_evaluated}")
            lines.append(f"- Compliant Bids: {comparison_result.compliant_bids_count}")
            lines.append(f"- Winner: **{comparison_result.winner_vendor_name or 'None'}** (Bid ID: {comparison_result.winner_bid_id or 'N/A'})")

            lines.append(f"\n## Rankings\n")
            for ranking in comparison_result.rankings:
                lines.append(f"### Rank {ranking.rank}: {ranking.vendor_name}")
                lines.append(f"- Bid ID: {ranking.bid_id}")
                lines.append(f"- Technical Score: {ranking.technical_score:.2f}/100")
                lines.append(f"- Financial Score: {ranking.financial_score:.2f}/100")
                lines.append(f"- Combined Score: {ranking.combined_score:.2f}/100")
                lines.append(f"- Compliant: {ranking.is_compliant}")
                lines.append(f"- Winner: {ranking.is_winner}")
                if ranking.notes:
                    lines.append(f"- Notes: {ranking.notes}")
                lines.append("")

            if comparison_result.cartel_flags:
                lines.append(f"## Cartel/Collusion Flags ({len(comparison_result.cartel_flags)})\n")
                for flag in comparison_result.cartel_flags:
                    lines.append(f"### [{flag.severity.upper()}] {flag.flag_type}")
                    lines.append(f"- Description: {flag.description}")
                    lines.append(f"- Involved Bids: {', '.join(flag.involved_bids)}")
                    lines.append(f"- Evidence: {flag.evidence}")
                    lines.append("")

            lines.append(f"\n**Summary:** {comparison_result.summary}")
        else:
            lines.append(json.dumps(comparison_result, indent=2))

        return "\n".join(lines)

    def _build_evaluation_report(
        self,
        evaluation_id: str,
        tender_reference: str,
        tender_title: str,
        evaluation_method: EvaluationMethod,
        report_data: Dict[str, Any],
        compliance_results: List[ComplianceResult],
        technical_scores: List[TechnicalScore],
        financial_scores: List[FinancialScore],
        comparison_result: ComparisonResult,
        metadata: Dict[str, Any]
    ) -> EvaluationReport:
        """
        Build EvaluationReport from LLM output and evaluation data.

        Args:
            evaluation_id: Evaluation identifier
            tender_reference: Tender reference number
            tender_title: Tender title
            evaluation_method: Evaluation method used
            report_data: Report data from LLM
            compliance_results: Compliance results
            technical_scores: Technical scores
            financial_scores: Financial scores
            comparison_result: Comparison result
            metadata: Additional metadata

        Returns:
            EvaluationReport instance
        """
        try:
            # Build bids summary
            bids_summary = []
            if "bids_summary" in report_data:
                bids_summary = report_data["bids_summary"]
            else:
                # Generate from available data
                for ranking in comparison_result.rankings:
                    bids_summary.append({
                        "bid_id": ranking.bid_id,
                        "vendor_name": ranking.vendor_name,
                        "summary": f"Rank {ranking.rank} - Combined Score: {ranking.combined_score:.2f}",
                        "status": "Compliant" if ranking.is_compliant else "Non-compliant"
                    })

            # Cartel analysis
            cartel_analysis = report_data.get("cartel_analysis")
            if not cartel_analysis and comparison_result.cartel_flags:
                cartel_analysis = f"Detected {len(comparison_result.cartel_flags)} potential cartel/collusion indicators requiring further investigation."

            # Build report
            evaluation_report = EvaluationReport(
                evaluation_id=evaluation_id,
                tender_reference=tender_reference,
                tender_title=tender_title,
                evaluation_method=evaluation_method,
                executive_summary=report_data["executive_summary"],
                methodology_description=report_data["methodology_description"],
                bids_summary=bids_summary,
                compliance_results=compliance_results,
                technical_scores=technical_scores,
                financial_scores=financial_scores,
                comparison_result=comparison_result,
                recommendations=report_data["recommendations"],
                risks_and_concerns=report_data.get("risks_and_concerns", []),
                cartel_analysis=cartel_analysis,
                generated_at=datetime.utcnow(),
                metadata=metadata
            )

            return evaluation_report

        except Exception as e:
            self.log_error(f"Failed to build EvaluationReport: {str(e)}")
            raise ValueError(f"Invalid report data structure: {str(e)}")

    def export_to_markdown(self, report: EvaluationReport) -> str:
        """
        Export evaluation report to markdown format.

        Args:
            report: EvaluationReport instance

        Returns:
            Markdown formatted report
        """
        lines = []

        # Header
        lines.append(f"# Evaluation Report: {report.tender_title}")
        lines.append(f"\n**Tender Reference:** {report.tender_reference}")
        lines.append(f"**Evaluation ID:** {report.evaluation_id}")
        lines.append(f"**Evaluation Method:** {report.evaluation_method.value}")
        lines.append(f"**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("\n---\n")

        # Executive Summary
        lines.append("## Executive Summary\n")
        lines.append(report.executive_summary)
        lines.append("\n")

        # Methodology
        lines.append("## Methodology\n")
        lines.append(report.methodology_description)
        lines.append("\n")

        # Bids Summary
        lines.append("## Bids Summary\n")
        for bid_summary in report.bids_summary:
            lines.append(f"### {bid_summary.get('vendor_name', 'Unknown Vendor')}")
            lines.append(f"- Bid ID: {bid_summary.get('bid_id', 'N/A')}")
            lines.append(f"- Status: {bid_summary.get('status', 'N/A')}")
            lines.append(f"- {bid_summary.get('summary', '')}")
            lines.append("")

        # Winner Recommendation
        lines.append("## Winner Recommendation\n")
        if report.comparison_result.winner_vendor_name:
            lines.append(f"**Recommended Winner:** {report.comparison_result.winner_vendor_name}")
            lines.append(f"**Bid ID:** {report.comparison_result.winner_bid_id}")
        else:
            lines.append("**No winner recommended** - No compliant bids met requirements.")
        lines.append("\n")

        # Recommendations
        lines.append("## Recommendations\n")
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("\n")

        # Risks and Concerns
        if report.risks_and_concerns:
            lines.append("## Risks and Concerns\n")
            for risk in report.risks_and_concerns:
                lines.append(f"- {risk}")
            lines.append("\n")

        # Cartel Analysis
        if report.cartel_analysis:
            lines.append("## Cartel/Collusion Analysis\n")
            lines.append(report.cartel_analysis)
            lines.append("\n")

        # Detailed Rankings
        lines.append("## Detailed Rankings\n")
        for ranking in report.comparison_result.rankings:
            lines.append(f"### Rank {ranking.rank}: {ranking.vendor_name}")
            lines.append(f"- **Combined Score:** {ranking.combined_score:.2f}/100")
            lines.append(f"- **Technical Score:** {ranking.technical_score:.2f}/100")
            lines.append(f"- **Financial Score:** {ranking.financial_score:.2f}/100")
            lines.append(f"- **Compliant:** {ranking.is_compliant}")
            lines.append("")

        return "\n".join(lines)

    def extract_summary(self, report: EvaluationReport) -> Dict[str, Any]:
        """
        Extract a summary of the evaluation report.

        Args:
            report: EvaluationReport instance

        Returns:
            Dict with summary information
        """
        return {
            "evaluation_id": report.evaluation_id,
            "tender_reference": report.tender_reference,
            "tender_title": report.tender_title,
            "evaluation_method": report.evaluation_method.value,
            "total_bids": len(report.bids_summary),
            "compliant_bids": report.comparison_result.compliant_bids_count,
            "winner": report.comparison_result.winner_vendor_name,
            "cartel_flags": len(report.comparison_result.cartel_flags),
            "generated_at": report.generated_at.isoformat()
        }
