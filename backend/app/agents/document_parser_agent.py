"""
Document Parser Agent - Extracts structured data from bid documents.
"""
import logging
from typing import Dict, Any
from datetime import datetime

from .base_agent import BaseAgent
from .schemas import ParsedBidDocument, VendorInfo, PricingTable, TechnicalSpecification, DocumentSection
from .prompts import DOCUMENT_PARSING_PROMPT, SYSTEM_PROMPTS


logger = logging.getLogger(__name__)


class DocumentParserAgent(BaseAgent):
    """
    Agent responsible for parsing bid documents and extracting structured information.

    Extracts:
    - Vendor information (name, contact, registration)
    - Pricing tables and cost breakdowns
    - Technical specifications
    - Compliance statements
    - Document sections
    """

    def __init__(self, **kwargs):
        """Initialize DocumentParserAgent."""
        super().__init__(agent_name="DocumentParserAgent", **kwargs)

    async def invoke(self, input_data: Dict[str, Any]) -> ParsedBidDocument:
        """
        Parse a bid document and extract structured information.

        Args:
            input_data: Dict containing:
                - bid_id: Unique identifier for the bid
                - document_content: Raw text content of the bid document
                - metadata: Optional metadata about the document

        Returns:
            ParsedBidDocument: Structured bid document data

        Raises:
            ValueError: If required input fields are missing
            Exception: If parsing fails
        """
        try:
            # Validate input
            if "bid_id" not in input_data:
                raise ValueError("bid_id is required")
            if "document_content" not in input_data:
                raise ValueError("document_content is required")

            bid_id = input_data["bid_id"]
            document_content = input_data["document_content"]
            metadata = input_data.get("metadata", {})

            self.log_info(f"Parsing bid document {bid_id}")

            # Create prompt
            messages = self._create_prompt(
                system_prompt=SYSTEM_PROMPTS["document_parser"],
                user_prompt=DOCUMENT_PARSING_PROMPT,
                document_content=document_content
            )

            # Invoke LLM
            parsed_data = await self._invoke_llm(messages, parse_json=True)

            # Validate response structure
            self._validate_output(
                parsed_data,
                required_fields=["vendor_info", "pricing_table"]
            )

            # Build ParsedBidDocument
            parsed_document = self._build_parsed_document(
                bid_id=bid_id,
                parsed_data=parsed_data,
                raw_text=document_content,
                metadata=metadata
            )

            self.log_info(f"Successfully parsed bid {bid_id} from vendor {parsed_document.vendor_info.name}")

            return parsed_document

        except Exception as e:
            self.log_error(f"Failed to parse bid document: {str(e)}")
            raise

    def _build_parsed_document(
        self,
        bid_id: str,
        parsed_data: Dict[str, Any],
        raw_text: str,
        metadata: Dict[str, Any]
    ) -> ParsedBidDocument:
        """
        Build ParsedBidDocument from parsed data.

        Args:
            bid_id: Bid identifier
            parsed_data: Parsed data from LLM
            raw_text: Original document text
            metadata: Additional metadata

        Returns:
            ParsedBidDocument instance
        """
        try:
            # Parse vendor info
            vendor_info = VendorInfo(**parsed_data["vendor_info"])

            # Parse pricing table
            pricing_data = parsed_data["pricing_table"]
            pricing_table = PricingTable(**pricing_data)

            # Parse technical specifications
            technical_specs = []
            if "technical_specs" in parsed_data:
                for spec_data in parsed_data["technical_specs"]:
                    technical_specs.append(TechnicalSpecification(**spec_data))

            # Parse compliance statements
            compliance_statements = parsed_data.get("compliance_statements", [])

            # Parse document sections
            sections = []
            if "sections" in parsed_data:
                for section_data in parsed_data["sections"]:
                    sections.append(DocumentSection(**section_data))

            # Build complete document
            parsed_document = ParsedBidDocument(
                bid_id=bid_id,
                vendor_info=vendor_info,
                pricing_table=pricing_table,
                technical_specs=technical_specs,
                compliance_statements=compliance_statements,
                sections=sections,
                raw_text=raw_text,
                metadata=metadata,
                parsed_at=datetime.utcnow()
            )

            return parsed_document

        except Exception as e:
            self.log_error(f"Failed to build ParsedBidDocument: {str(e)}")
            raise ValueError(f"Invalid parsed data structure: {str(e)}")

    async def parse_multiple(self, bids: list[Dict[str, Any]]) -> list[ParsedBidDocument]:
        """
        Parse multiple bid documents.

        Args:
            bids: List of bid input data dicts

        Returns:
            List of ParsedBidDocument instances
        """
        parsed_documents = []

        for bid_data in bids:
            try:
                parsed_doc = await self.invoke(bid_data)
                parsed_documents.append(parsed_doc)
            except Exception as e:
                self.log_error(f"Failed to parse bid {bid_data.get('bid_id', 'unknown')}: {str(e)}")
                # Continue with other bids even if one fails
                continue

        self.log_info(f"Parsed {len(parsed_documents)} out of {len(bids)} bid documents")

        return parsed_documents

    def extract_summary(self, parsed_document: ParsedBidDocument) -> Dict[str, Any]:
        """
        Extract a summary of the parsed document.

        Args:
            parsed_document: ParsedBidDocument instance

        Returns:
            Dict with summary information
        """
        return {
            "bid_id": parsed_document.bid_id,
            "vendor_name": parsed_document.vendor_info.name,
            "total_amount": parsed_document.pricing_table.total,
            "currency": parsed_document.pricing_table.currency,
            "technical_specs_count": len(parsed_document.technical_specs),
            "compliance_statements_count": len(parsed_document.compliance_statements),
            "parsed_at": parsed_document.parsed_at.isoformat()
        }
