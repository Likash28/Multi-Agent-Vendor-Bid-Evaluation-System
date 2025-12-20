"""
DOCX parsing utilities using python-docx
"""

from pathlib import Path
from typing import List, Dict, Any
from docx import Document as DocxDocument
from dataclasses import dataclass


@dataclass
class DocumentContent:
    """Document content data structure"""
    text: str
    tables: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    page_count: int


class DocxParser:
    """DOCX document parser using python-docx"""

    def extract_text(self, file_path: Path) -> str:
        """
        Extract all text from a DOCX file

        Args:
            file_path: Path to the DOCX file

        Returns:
            str: Extracted text from all paragraphs

        Raises:
            FileNotFoundError: If file does not exist
            Exception: If DOCX cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {file_path}")

        try:
            doc = DocxDocument(file_path)
            paragraphs = []

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text)

            return "\n\n".join(paragraphs)
        except Exception as e:
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")

    def extract_tables(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract all tables from a DOCX file

        Args:
            file_path: Path to the DOCX file

        Returns:
            List[Dict]: List of tables with data

        Raises:
            FileNotFoundError: If file does not exist
            Exception: If DOCX cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {file_path}")

        try:
            doc = DocxDocument(file_path)
            tables = []

            for table_num, table in enumerate(doc.tables, start=1):
                # Extract table data
                table_data = []
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    table_data.append(row_data)

                if table_data:
                    headers = table_data[0] if table_data else []
                    rows = table_data[1:] if len(table_data) > 1 else []

                    table_dict = {
                        "table_number": table_num,
                        "headers": headers,
                        "rows": rows,
                        "row_count": len(rows),
                        "column_count": len(headers)
                    }
                    tables.append(table_dict)

            return tables
        except Exception as e:
            raise Exception(f"Failed to extract tables from DOCX: {str(e)}")

    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from a DOCX file

        Args:
            file_path: Path to the DOCX file

        Returns:
            Dict: DOCX metadata

        Raises:
            FileNotFoundError: If file does not exist
            Exception: If DOCX cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {file_path}")

        try:
            doc = DocxDocument(file_path)
            core_props = doc.core_properties

            return {
                "page_count": len(doc.sections),  # Approximate
                "paragraph_count": len(doc.paragraphs),
                "table_count": len(doc.tables),
                "title": core_props.title or "",
                "author": core_props.author or "",
                "subject": core_props.subject or "",
                "keywords": core_props.keywords or "",
                "comments": core_props.comments or "",
                "category": core_props.category or "",
                "created": str(core_props.created) if core_props.created else "",
                "modified": str(core_props.modified) if core_props.modified else "",
                "last_modified_by": core_props.last_modified_by or "",
                "file_size": file_path.stat().st_size,
            }
        except Exception as e:
            raise Exception(f"Failed to extract metadata from DOCX: {str(e)}")

    def parse_document(self, file_path: Path) -> DocumentContent:
        """
        Parse a DOCX document and extract all content

        Args:
            file_path: Path to the DOCX file

        Returns:
            DocumentContent: Complete document content

        Raises:
            FileNotFoundError: If file does not exist
            Exception: If DOCX cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {file_path}")

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
            raise Exception(f"Failed to parse DOCX document: {str(e)}")
