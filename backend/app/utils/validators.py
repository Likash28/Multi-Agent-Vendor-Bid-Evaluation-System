"""
Validation utilities for Indian government procurement system
"""

import re


def validate_gstin(gstin: str) -> bool:
    """
    Validate Indian GST Identification Number (GSTIN)

    Format: 15 characters - 2 State Code + 10 PAN + 1 Entity + 1 Z + 1 Checksum
    Example: 22AAAAA0000A1Z5

    Args:
        gstin: GSTIN string to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not gstin or not isinstance(gstin, str):
        return False

    # Remove whitespace and convert to uppercase
    gstin = gstin.strip().upper()

    # Check length
    if len(gstin) != 15:
        return False

    # GSTIN pattern: 2-digit state code + 10-char PAN + entity number + Z + checksum
    # State code: 01-37
    # PAN: See validate_pan for pattern
    # Entity: 1-9, A-Z
    # 13th char: Always Z
    # Checksum: 0-9, A-Z
    pattern = r'^[0-3][0-9][A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'

    if not re.match(pattern, gstin):
        return False

    # Validate embedded PAN (characters 3-12)
    embedded_pan = gstin[2:12]
    if not validate_pan(embedded_pan):
        return False

    return True


def validate_pan(pan: str) -> bool:
    """
    Validate Indian Permanent Account Number (PAN)

    Format: 10 characters - AAAAA9999A
    - 3 letters (first 3 chars)
    - 1 letter indicating type of holder (4th char): C-Company, P-Person, H-HUF, F-Firm, A-AOP, T-Trust, B-BOI, L-Local Authority, J-Artificial Juridical Person, G-Government
    - 1 letter (5th char) - first character of surname/name
    - 4 digits (6-9 chars)
    - 1 letter (10th char) - check digit

    Example: ABCDE1234F

    Args:
        pan: PAN string to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not pan or not isinstance(pan, str):
        return False

    # Remove whitespace and convert to uppercase
    pan = pan.strip().upper()

    # Check length
    if len(pan) != 10:
        return False

    # PAN pattern: 3 letters + 1 type letter + 1 letter + 4 digits + 1 letter
    # 4th char must be one of: C, P, H, F, A, T, B, L, J, G
    pattern = r'^[A-Z]{3}[CPHFATBLJG]{1}[A-Z]{1}[0-9]{4}[A-Z]{1}$'

    return bool(re.match(pattern, pan))


def validate_tender_id(tender_id: str) -> bool:
    """
    Validate tender reference ID format

    Format: TENDER-YYYY-NNNNNN (TENDER- + 4-digit year + 6-digit number)
    Example: TENDER-2024-000001

    Args:
        tender_id: Tender ID string to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not tender_id or not isinstance(tender_id, str):
        return False

    # Remove whitespace and convert to uppercase
    tender_id = tender_id.strip().upper()

    # Pattern: TENDER-YYYY-NNNNNN
    pattern = r'^TENDER-[0-9]{4}-[0-9]{6}$'

    if not re.match(pattern, tender_id):
        return False

    # Validate year (should be reasonable range)
    year_str = tender_id.split('-')[1]
    year = int(year_str)

    # Year should be between 2000 and 2100
    if year < 2000 or year > 2100:
        return False

    return True


def validate_currency_amount(amount: int) -> bool:
    """
    Validate currency amount (in paisa - smallest unit)

    Args:
        amount: Amount in paisa (1 rupee = 100 paisa)

    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(amount, int):
        return False

    # Amount should be non-negative
    if amount < 0:
        return False

    # Maximum reasonable amount: 10 billion rupees (10,00,00,00,000 paisa)
    max_amount = 1_00_00_00_00_000  # 1 trillion paisa = 10 billion rupees
    if amount > max_amount:
        return False

    return True
