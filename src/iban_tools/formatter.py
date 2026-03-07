"""IBAN formatting and sanitization utilities.

This module provides functions to format IBANs into human-readable blocks
and to sanitize user input into clean, database-ready strings.
"""

import re


def sanitize_iban(iban: str) -> str:
    """Sanitize an IBAN by removing all non-alphanumeric characters and uppercasing.

    Strips spaces, hyphens, dots, slashes, and any other special characters,
    returning a clean uppercase string suitable for storage in a database.

    Args:
        iban: The raw IBAN input string.

    Returns:
        A clean, uppercase IBAN string with only alphanumeric characters.

    Examples:
        >>> sanitize_iban("DE89 3704 0044 0532 0130 00")
        'DE89370400440532013000'
        >>> sanitize_iban("de89-3704.0044/0532-0130 00")
        'DE89370400440532013000'
    """
    return re.sub(r"[^A-Za-z0-9]", "", iban).upper()


def format_iban(iban: str) -> str:
    """Format an IBAN into standard 4-character blocks.

    First sanitizes the input, then groups characters into blocks of 4,
    separated by spaces. The last block may have fewer than 4 characters.

    Args:
        iban: The IBAN string (may contain spaces, hyphens, etc.).

    Returns:
        The IBAN formatted in 4-character blocks separated by spaces.

    Examples:
        >>> format_iban("DE89370400440532013000")
        'DE89 3704 0044 0532 0130 00'
        >>> format_iban("TR330006100519786457841326")
        'TR33 0006 1005 1978 6457 8413 26'
    """
    cleaned = sanitize_iban(iban)

    if not cleaned:
        return ""

    # Split into groups of 4
    blocks = [cleaned[i : i + 4] for i in range(0, len(cleaned), 4)]
    return " ".join(blocks)


def is_formatted(iban: str) -> bool:
    """Check if an IBAN is already in standard 4-character block format.

    Args:
        iban: The IBAN string to check.

    Returns:
        True if the IBAN is properly formatted with 4-character blocks.
    """
    # Pattern: groups of exactly 4 chars separated by single spaces, last group 1-4
    pattern = r"^[A-Z0-9]{4}( [A-Z0-9]{4})*( [A-Z0-9]{1,4})?$"
    return bool(re.match(pattern, iban.strip().upper()))
