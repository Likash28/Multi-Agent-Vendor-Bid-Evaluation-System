"""
Evaluation Orchestrator - Manages the entire evaluation workflow using LangGraph.
"""
import logging
import asyncio
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
import time

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, Dict, Any
from operator import add

from .schemas import (
    AgentState,
    AgentStateModel,
    EvaluationResult,
    ProgressUpdate,
    EvaluationMethod,
    ParsedBidDocument,
    ComplianceResult,
    TechnicalScore,
    FinancialScore,
    ComparisonResult,
    EvaluationReport
)
from .document_parser_agent import DocumentParserAgent
from .compliance_agent import ComplianceAgent
from .technical_agent import TechnicalAgent
from .financial_agent import FinancialAgent
from .comparison_agent import ComparisonAgent
from .report_agent import ReportAgent
from app.utils.logger import get_logger, log_agent_event

logger = get_logger(__name__)


class EvaluationOrchestrator:
    """
    Orchestrates the complete bid evaluation workflow using LangGraph.

    Workflow:
    1. parse_documents: Parse all bid documents
    2. compliance_check: Check compliance for all bids
    3. parallel_evaluation: Technical and financial evaluation (parallel)
    4. comparison: Compare all bids and generate rankings
    5. report_generation: Generate final report
    """

    def __init__(
        self,
        model_id: str = "anthropic.claude-sonnet-4-20250514-v1:0",
        region_name: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ):
        """
        Initialize the orchestrator.

        Args:
            model_id: AWS Bedrock model ID
            region_name: AWS region
            progress_callback: Optional callback for progress updates
        """
        self.model_id = model_id
        self.region_name = region_name
        self.progress_callback = progress_callback

        # Initialize agents
        agent_kwargs = {"model_id": model_id}
        if region_name:
            agent_kwargs["region_name"] = region_name

        self.document_parser = DocumentParserAgent(**agent_kwargs)
        self.compliance_agent = ComplianceAgent(**agent_kwargs)
        self.technical_agent = TechnicalAgent(**agent_kwargs)
        self.financial_agent = FinancialAgent(**agent_kwargs)
        self.comparison_agent = ComparisonAgent(**agent_kwargs)
        self.report_agent = ReportAgent(**agent_kwargs)

        # Build workflow
        self.workflow = self._build_workflow()

        logger.info("EvaluationOrchestrator initialized")

    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow.

        Returns:
            StateGraph instance
        """
        # Create state graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("parse_documents", self._parse_documents_node)
        workflow.add_node("compliance_check", self._compliance_check_node)
        workflow.add_node("technical_evaluation", self._technical_evaluation_node)
        workflow.add_node("financial_evaluation", self._financial_evaluation_node)
        workflow.add_node("comparison", self._comparison_node)
        workflow.add_node("report_generation", self._report_generation_node)

        # Set entry point
        workflow.set_entry_point("parse_documents")

        # Add edges
        workflow.add_edge("parse_documents", "compliance_check")
        workflow.add_edge("compliance_check", "technical_evaluation")
        workflow.add_edge("compliance_check", "financial_evaluation")
        workflow.add_edge("technical_evaluation", "comparison")
        workflow.add_edge("financial_evaluation", "comparison")
        workflow.add_edge("comparison", "report_generation")
        workflow.add_edge("report_generation", END)

        # Compile with checkpointer for state persistence
        checkpointer = MemorySaver()
        compiled_workflow = workflow.compile(checkpointer=checkpointer)

        logger.info("Workflow built successfully")

        return compiled_workflow

    async def _parse_documents_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Parse all bid documents.

        Args:
            state: Current agent state (TypedDict)

        Returns:
            Partial state dict with only updated fields
        """
        try:
            logger.info(f"Starting document parsing for {len(state['raw_bids'])} bids")

            await self._emit_progress(
                state["evaluation_id"],
                "parse_documents",
                10.0,
                f"Parsing {len(state['raw_bids'])} bid documents..."
            )

            # Parse all documents
            parsed_documents = await self.document_parser.parse_multiple(state["raw_bids"])

            await self._emit_progress(
                state["evaluation_id"],
                "parse_documents",
                20.0,
                f"Successfully parsed {len(parsed_documents)} documents",
                {"parsed_count": len(parsed_documents)}
            )

            logger.info(f"Document parsing completed: {len(parsed_documents)} documents")

            # Return only updated fields
            return {
                "parsed_documents": parsed_documents,
                "current_step": "parse_documents",
                "progress": 20.0
            }

        except Exception as e:
            logger.error(f"Document parsing failed: {str(e)}")
            return {
                "errors": state.get("errors", []) + [f"Document parsing error: {str(e)}"]
            }

    async def _compliance_check_node(self, state: AgentState) -> AgentState:
        """
        Check compliance for all parsed bids.

        Args:
            state: Current agent state

        Returns:
            Updated agent state
        """
        try:
            logger.info(f"Starting compliance check for {len(state.parsed_documents)} bids")
            state.current_step = "compliance_check"
            state.progress = 30.0

            await self._emit_progress(
                state.evaluation_id,
                "compliance_check",
                30.0,
                f"Checking compliance for {len(state.parsed_documents)} bids..."
            )

            # Prepare bid data for compliance check
            bids_data = [
                {
                    "bid_id": doc.bid_id,
                    "parsed_document": doc,
                    "vendor_name": doc.vendor_info.name
                }
                for doc in state.parsed_documents
            ]

            # Evaluate compliance
            compliance_results = await self.compliance_agent.evaluate_multiple(
                bids_data,
                state.tender_requirements
            )

            # Get compliant bid IDs
            compliant_ids = self.compliance_agent.get_compliant_bids(compliance_results)

            state.compliance_results = compliance_results
            state.compliant_bid_ids = compliant_ids
            state.progress = 40.0

            await self._emit_progress(
                state.evaluation_id,
                "compliance_check",
                40.0,
                f"Compliance check completed: {len(compliant_ids)} compliant bids",
                {
                    "total_bids": len(compliance_results),
                    "compliant_bids": len(compliant_ids)
                }
            )

            logger.info(f"Compliance check completed: {len(compliant_ids)}/{len(compliance_results)} compliant")

            return state

        except Exception as e:
            logger.error(f"Compliance check failed: {str(e)}")
            state.errors.append(f"Compliance check error: {str(e)}")
            return state

    async def _technical_evaluation_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Evaluate technical proposals.

        Args:
            state: Current agent state (TypedDict)

        Returns:
            Partial state dict with only updated fields (excludes immutable fields)
        """
        try:
            # Only evaluate compliant bids for QCBS and Two-Stage
            # For L1, technical is pass/fail so we can skip or do minimal eval
            evaluation_method = state["evaluation_method"]
            if evaluation_method == EvaluationMethod.L1:
                logger.info("L1 method: Skipping detailed technical evaluation")
                bids_to_evaluate = state["compliant_bid_ids"]
            else:
                bids_to_evaluate = state["compliant_bid_ids"]

            logger.info(f"Starting technical evaluation for {len(bids_to_evaluate)} bids")

            await self._emit_progress(
                state["evaluation_id"],
                "technical_evaluation",
                50.0,
                f"Evaluating technical proposals for {len(bids_to_evaluate)} bids..."
            )

            # Prepare bid data
            parsed_docs_map = {doc.bid_id: doc for doc in state["parsed_documents"]}
            bids_data = [
                {
                    "bid_id": bid_id,
                    "parsed_document": parsed_docs_map[bid_id],
                    "vendor_name": parsed_docs_map[bid_id].vendor_info.name
                }
                for bid_id in bids_to_evaluate
                if bid_id in parsed_docs_map
            ]

            # Evaluate technical proposals
            technical_scores = await self.technical_agent.evaluate_multiple(
                bids_data,
                state["tender_requirements"]
            )

            await self._emit_progress(
                state["evaluation_id"],
                "technical_evaluation",
                60.0,
                f"Technical evaluation completed for {len(technical_scores)} bids",
                {"evaluated_count": len(technical_scores)}
            )

            logger.info(f"Technical evaluation completed: {len(technical_scores)} scores")

            # Return only the fields we're updating (exclude immutable fields)
            return {
                "technical_scores": technical_scores,
                "current_step": "technical_evaluation",
                "progress": 60.0
            }

        except Exception as e:
            logger.error(f"Technical evaluation failed: {str(e)}")
            # Return error in the update
            return {
                "errors": state.get("errors", []) + [f"Technical evaluation error: {str(e)}"]
            }

    async def _financial_evaluation_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Evaluate financial proposals.

        Args:
            state: Current agent state (TypedDict)

        Returns:
            Partial state dict with only updated fields (excludes immutable fields)
        """
        try:
            # Evaluate all compliant bids
            bids_to_evaluate = state["compliant_bid_ids"]

            logger.info(f"Starting financial evaluation for {len(bids_to_evaluate)} bids")

            await self._emit_progress(
                state["evaluation_id"],
                "financial_evaluation",
                50.0,
                f"Evaluating financial proposals for {len(bids_to_evaluate)} bids..."
            )

            # Prepare bid data
            parsed_docs_map = {doc.bid_id: doc for doc in state["parsed_documents"]}
            bids_data = [
                {
                    "bid_id": bid_id,
                    "parsed_document": parsed_docs_map[bid_id],
                    "vendor_name": parsed_docs_map[bid_id].vendor_info.name
                }
                for bid_id in bids_to_evaluate
                if bid_id in parsed_docs_map
            ]

            # Evaluate financial proposals
            financial_scores = await self.financial_agent.evaluate_multiple(
                bids_data,
                state["tender_requirements"],
                state["evaluation_method"]
            )

            # Recalculate normalized scores
            financial_scores = self.financial_agent.calculate_normalized_scores(financial_scores)

            await self._emit_progress(
                state["evaluation_id"],
                "financial_evaluation",
                60.0,
                f"Financial evaluation completed for {len(financial_scores)} bids",
                {"evaluated_count": len(financial_scores)}
            )

            logger.info(f"Financial evaluation completed: {len(financial_scores)} scores")

            # Return only the fields we're updating (exclude immutable fields)
            return {
                "financial_scores": financial_scores,
                "current_step": "financial_evaluation",
                "progress": 60.0
            }

        except Exception as e:
            logger.error(f"Financial evaluation failed: {str(e)}")
            # Return error in the update
            return {
                "errors": state.get("errors", []) + [f"Financial evaluation error: {str(e)}"]
            }

    async def _comparison_node(self, state: AgentState) -> AgentState:
        """
        Compare all bids and generate rankings.

        Args:
            state: Current agent state

        Returns:
            Updated agent state
        """
        try:
            logger.info("Starting bid comparison and ranking")
            state.current_step = "comparison"
            state.progress = 70.0

            await self._emit_progress(
                state.evaluation_id,
                "comparison",
                70.0,
                "Comparing bids and generating rankings..."
            )

            # Prepare comparison input
            comparison_input = {
                "evaluation_id": state.evaluation_id,
                "evaluation_method": state.evaluation_method,
                "compliance_results": state.compliance_results,
                "technical_scores": state.technical_scores,
                "financial_scores": state.financial_scores,
                "tender_requirements": state.tender_requirements
            }

            # Get technical and financial weights from tender requirements
            if state.evaluation_method == EvaluationMethod.QCBS:
                comparison_input["technical_weight"] = state.tender_requirements.get("technical_weight", 70.0)
                comparison_input["financial_weight"] = state.tender_requirements.get("financial_weight", 30.0)

            # Perform comparison
            comparison_result = await self.comparison_agent.invoke(comparison_input)

            state.comparison_result = comparison_result
            state.progress = 80.0

            winner_info = f"Winner: {comparison_result.winner_vendor_name}" if comparison_result.winner_vendor_name else "No winner"

            await self._emit_progress(
                state.evaluation_id,
                "comparison",
                80.0,
                f"Comparison completed. {winner_info}",
                {
                    "winner": comparison_result.winner_vendor_name,
                    "total_bids": comparison_result.total_bids_evaluated,
                    "compliant_bids": comparison_result.compliant_bids_count
                }
            )

            logger.info(f"Comparison completed: {winner_info}")

            return state

        except Exception as e:
            logger.error(f"Comparison failed: {str(e)}")
            state.errors.append(f"Comparison error: {str(e)}")
            return state

    async def _report_generation_node(self, state: AgentState) -> AgentState:
        """
        Generate final evaluation report.

        Args:
            state: Current agent state

        Returns:
            Updated agent state
        """
        try:
            logger.info("Generating final evaluation report")
            state.current_step = "report_generation"
            state.progress = 90.0

            await self._emit_progress(
                state.evaluation_id,
                "report_generation",
                90.0,
                "Generating comprehensive evaluation report..."
            )

            # Get tender info from requirements
            tender_reference = state.tender_requirements.get("tender_reference", state.evaluation_id)
            tender_title = state.tender_requirements.get("tender_title", "Procurement Evaluation")

            # Prepare report input
            report_input = {
                "evaluation_id": state.evaluation_id,
                "tender_reference": tender_reference,
                "tender_title": tender_title,
                "evaluation_method": state.evaluation_method,
                "compliance_results": state.compliance_results,
                "technical_scores": state.technical_scores,
                "financial_scores": state.financial_scores,
                "comparison_result": state.comparison_result,
                "metadata": {
                    "started_at": state.started_at.isoformat(),
                    "errors": state.errors
                }
            }

            # Generate report
            final_report = await self.report_agent.invoke(report_input)

            state.final_report = final_report
            state.progress = 100.0
            state.completed_at = datetime.utcnow()

            await self._emit_progress(
                state.evaluation_id,
                "report_generation",
                100.0,
                "Evaluation completed successfully!",
                {"report_id": state.evaluation_id}
            )

            logger.info("Report generation completed")

            return state

        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            state.errors.append(f"Report generation error: {str(e)}")
            return state

    async def _emit_progress(
        self,
        evaluation_id: str,
        step: str,
        progress: float,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Emit progress update via callback.

        Args:
            evaluation_id: Evaluation ID
            step: Current step name
            progress: Progress percentage (0-100)
            message: Progress message
            data: Optional additional data
        """
        if self.progress_callback:
            update = ProgressUpdate(
                evaluation_id=evaluation_id,
                step=step,
                progress=progress,
                message=message,
                data=data
            )
            try:
                if asyncio.iscoroutinefunction(self.progress_callback):
                    await self.progress_callback(update)
                else:
                    self.progress_callback(update)
            except Exception as e:
                logger.error(f"Progress callback failed: {str(e)}")

    async def run(
        self,
        evaluation_id: str,
        bids: List[Dict[str, Any]],
        tender_requirements: Dict[str, Any],
        evaluation_method: EvaluationMethod = EvaluationMethod.QCBS
    ) -> EvaluationResult:
        """
        Execute the complete evaluation workflow.

        Args:
            evaluation_id: Unique identifier for this evaluation
            bids: List of bid documents (dict with bid_id, document_content)
            tender_requirements: Tender requirements and criteria
            evaluation_method: Evaluation method to use

        Returns:
            EvaluationResult with report and status
        """
        start_time = time.time()

        try:
            logger.info(f"Starting evaluation {evaluation_id} with {len(bids)} bids")

            # Initialize state using Pydantic model, then convert to TypedDict for LangGraph
            state_model = AgentStateModel(
                evaluation_id=evaluation_id,
                tender_requirements=tender_requirements,
                evaluation_method=evaluation_method,
                raw_bids=bids,
                current_step="initialized",
                progress=0.0,
                started_at=datetime.utcnow()
            )
            initial_state = state_model.to_typed_dict()

            # Run workflow
            config = {"configurable": {"thread_id": evaluation_id}}
            logger.info(f"Starting workflow.ainvoke() call for evaluation {evaluation_id}")
            logger.info(f"Workflow invoke call is happening now with {len(bids)} bids")
            logger.debug(f"Workflow config: {config}")
            logger.debug(f"Initial state step: {initial_state.current_step}, progress: {initial_state.progress}")
            
            final_state = await self.workflow.ainvoke(initial_state, config)
            
            logger.info(f"Workflow.ainvoke() call completed successfully for evaluation {evaluation_id}")
            logger.info(f"Final state step: {final_state.current_step}, progress: {final_state.progress}")

            # Calculate execution time
            execution_time = time.time() - start_time

            # Build result
            if final_state.final_report and not final_state.errors:
                status = "completed"
            elif final_state.errors:
                status = "failed" if not final_state.final_report else "partial"
            else:
                status = "failed"

            result = EvaluationResult(
                evaluation_id=evaluation_id,
                status=status,
                report=final_state.final_report,
                errors=final_state.errors,
                execution_time_seconds=execution_time,
                completed_at=datetime.utcnow()
            )

            logger.info(
                f"Evaluation {evaluation_id} completed with status '{status}' "
                f"in {execution_time:.2f}s"
            )

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Evaluation {evaluation_id} failed: {str(e)}", exc_info=True)

            return EvaluationResult(
                evaluation_id=evaluation_id,
                status="failed",
                report=None,
                errors=[f"Orchestration error: {str(e)}"],
                execution_time_seconds=execution_time,
                completed_at=datetime.utcnow()
            )
