"""
Utility modules for file handling, parsing, validation, and normalization
"""

from app.utils.file_utils import (
    save_upload_file,
    get_file_hash,
    validate_file_type,
    get_mime_type,
    ensure_directory,
)
from app.utils.pdf_parser import PDFParser, DocumentContent
from app.utils.docx_parser import DocxParser
from app.utils.validators import (
    validate_gstin,
    validate_pan,
    validate_tender_id,
    validate_currency_amount,
)
from app.utils.normalization import (
    normalize_currency_to_paisa,
    paisa_to_rupees,
    normalize_date_to_utc,
    utc_to_ist,
    format_indian_currency,
)

__all__ = [
    # File utilities
    "save_upload_file",
    "get_file_hash",
    "validate_file_type",
    "get_mime_type",
    "ensure_directory",
    # Parsers
    "PDFParser",
    "DocxParser",
    "DocumentContent",
    # Validators
    "validate_gstin",
    "validate_pan",
    "validate_tender_id",
    "validate_currency_amount",
    # Normalization
    "normalize_currency_to_paisa",
    "paisa_to_rupees",
    "normalize_date_to_utc",
    "utc_to_ist",
    "format_indian_currency",
]
