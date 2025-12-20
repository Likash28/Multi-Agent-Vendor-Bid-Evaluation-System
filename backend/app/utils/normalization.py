"""
Data normalization utilities for currency and datetime handling
"""

from datetime import datetime
from typing import Optional
import pytz


def normalize_currency_to_paisa(amount: float, currency: str = "INR") -> int:
    """
    Normalize currency amount to smallest unit (paisa for INR)

    In India: 1 Rupee = 100 Paisa
    This stores amounts as integers in the smallest unit to avoid floating point errors

    Args:
        amount: Amount in main currency unit (e.g., rupees)
        currency: Currency code (default: "INR")

    Returns:
        int: Amount in smallest unit (paisa)

    Examples:
        >>> normalize_currency_to_paisa(100.50)
        10050
        >>> normalize_currency_to_paisa(1000.00)
        100000
    """
    if currency != "INR":
        raise ValueError(f"Unsupported currency: {currency}. Only INR is supported.")

    # Convert to paisa (multiply by 100) and round to nearest integer
    paisa = round(amount * 100)

    return int(paisa)


def paisa_to_rupees(paisa: int) -> float:
    """
    Convert paisa (smallest unit) back to rupees

    Args:
        paisa: Amount in paisa

    Returns:
        float: Amount in rupees

    Examples:
        >>> paisa_to_rupees(10050)
        100.50
        >>> paisa_to_rupees(100000)
        1000.00
    """
    if not isinstance(paisa, int):
        raise TypeError("Paisa amount must be an integer")

    return paisa / 100.0


def normalize_date_to_utc(date_str: str, timezone: str = "Asia/Kolkata") -> datetime:
    """
    Normalize a date string to UTC datetime

    Args:
        date_str: Date string in ISO format (e.g., "2024-01-15 14:30:00")
        timezone: Source timezone (default: "Asia/Kolkata" for IST)

    Returns:
        datetime: UTC datetime object

    Raises:
        ValueError: If date string is invalid or timezone is unsupported

    Examples:
        >>> normalize_date_to_utc("2024-01-15 14:30:00")
        datetime.datetime(2024, 1, 15, 9, 0, tzinfo=<UTC>)
    """
    try:
        # Parse the date string (assume it's in the given timezone)
        local_tz = pytz.timezone(timezone)

        # Try to parse various date formats
        date_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
        ]

        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue

        if parsed_date is None:
            raise ValueError(f"Unable to parse date string: {date_str}")

        # Localize to source timezone (make timezone-aware)
        local_dt = local_tz.localize(parsed_date)

        # Convert to UTC
        utc_dt = local_dt.astimezone(pytz.UTC)

        return utc_dt

    except pytz.exceptions.UnknownTimeZoneError:
        raise ValueError(f"Unknown timezone: {timezone}")
    except Exception as e:
        raise ValueError(f"Failed to normalize date: {str(e)}")


def utc_to_ist(utc_dt: datetime) -> datetime:
    """
    Convert UTC datetime to IST (Indian Standard Time)

    Args:
        utc_dt: UTC datetime object

    Returns:
        datetime: IST datetime object

    Examples:
        >>> utc_dt = datetime(2024, 1, 15, 9, 0, tzinfo=pytz.UTC)
        >>> utc_to_ist(utc_dt)
        datetime.datetime(2024, 1, 15, 14, 30, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)
    """
    if utc_dt.tzinfo is None:
        # Assume UTC if no timezone info
        utc_dt = pytz.UTC.localize(utc_dt)
    elif utc_dt.tzinfo != pytz.UTC:
        # Convert to UTC first if in different timezone
        utc_dt = utc_dt.astimezone(pytz.UTC)

    # Convert to IST
    ist_tz = pytz.timezone("Asia/Kolkata")
    ist_dt = utc_dt.astimezone(ist_tz)

    return ist_dt


def format_indian_currency(paisa: int) -> str:
    """
    Format amount in Indian currency notation

    Indian number system uses lakhs and crores:
    - 1,00,000 (1 lakh)
    - 10,00,000 (10 lakhs)
    - 1,00,00,000 (1 crore)

    Args:
        paisa: Amount in paisa

    Returns:
        str: Formatted currency string

    Examples:
        >>> format_indian_currency(10050)
        '₹100.50'
        >>> format_indian_currency(1000000)
        '₹10,000.00'
        >>> format_indian_currency(100000000)
        '₹10,00,000.00'
    """
    rupees = paisa_to_rupees(paisa)

    # Format with 2 decimal places
    amount_str = f"{rupees:,.2f}"

    # Convert to Indian numbering system
    # Split into integer and decimal parts
    parts = amount_str.split('.')
    integer_part = parts[0].replace(',', '')
    decimal_part = parts[1] if len(parts) > 1 else '00'

    # Apply Indian numbering (comma after every 2 digits from right, except first 3)
    if len(integer_part) <= 3:
        formatted = integer_part
    else:
        # Last 3 digits
        last_three = integer_part[-3:]
        # Remaining digits grouped by 2
        remaining = integer_part[:-3]

        # Add commas every 2 digits from right to left
        groups = []
        while remaining:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]

        formatted = ','.join(groups) + ',' + last_three

    return f"₹{formatted}.{decimal_part}"
