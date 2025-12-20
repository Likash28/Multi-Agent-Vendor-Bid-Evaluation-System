"""
PDF parsing utilities using pdfplumber
"""

from pathlib import Path
from typing import List, Dict, Any
import pdfplumber
from dataclasses import dataclass


@dataclass
class DocumentContent:
    """Document content data structure"""
    text: str
    tables: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    page_count: int


class PDFParser:
    """PDF document parser using pdfplumber"""

    def extract_text(self, file_path: Path) -> str:
        """
        Extract all text from a PDF file

        Args:
            file_path: Path to the PDF file

        Returns:
            str: Extracted text from all pages

        Raises:
            FileNotFoundError: If file does not exist
            Exception: If PDF cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            with pdfplumber.open(file_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                return "\n\n".join(text_parts)
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    def extract_tables(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract all tables from a PDF file

        Args:
            file_path: Path to the PDF file

        Returns:
            List[Dict]: List of tables with page number and data

        Raises:
            FileNotFoundError: If file does not exist
            Exception: If PDF cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            tables = []
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_tables = page.extract_tables()
                    for table_num, table in enumerate(page_tables, start=1):
                        if table:
                            # Convert table to dict format with headers
                            headers = table[0] if table else []
                            rows = table[1:] if len(table) > 1 else []

                            table_data = {
                                "page": page_num,
                                "table_number": table_num,
                                "headers": headers,
                                "rows": rows,
                                "row_count": len(rows),
                                "column_count": len(headers)
                            }
                            tables.append(table_data)

            return tables
        except Exception as e:
            raise Exception(f"Failed to extract tables from PDF: {str(e)}")

    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from a PDF file

        Args:
            file_path: Path to the PDF file

        Returns:
            Dict: PDF metadata

        Raises:
            FileNotFoundError: If file does not exist
            Exception: If PDF cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            with pdfplumber.open(file_path) as pdf:
                metadata = pdf.metadata or {}

                return {
                    "page_count": len(pdf.pages),
                    "title": metadata.get("Title", ""),
                    "author": metadata.get("Author", ""),
                    "subject": metadata.get("Subject", ""),
                    "creator": metadata.get("Creator", ""),
                    "producer": metadata.get("Producer", ""),
                    "creation_date": metadata.get("CreationDate", ""),
                    "modification_date": metadata.get("ModDate", ""),
                    "file_size": file_path.stat().st_size,
                }
        except Exception as e:
            raise Exception(f"Failed to extract metadata from PDF: {str(e)}")

    def parse_document(self, file_path: Path) -> DocumentContent:
        """
        Parse a PDF document and extract all content

        Args:
            file_path: Path to the PDF file

        Returns:
            DocumentContent: Complete document content

        Raises:
            FileNotFoundError: If file does not exist
            Exception: If PDF cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            text = self.extract_text(file_path)
            tables = self.extract_tables(file_path)
            metadata = self.extract_metadata(file_path)

            return DocumentContent(
                text=text,
                tables=tables,
                metadata=metadata,
                page_count=metadata.get("page_count", 0)
            )
        except Exception as e:
            raise Exception(f"Failed to parse PDF document: {str(e)}")
