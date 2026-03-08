"""IBAN parser — decompose an IBAN into its structural components.

This module provides detailed IBAN parsing that extracts country code,
check digits, bank code, account number, and BBAN from any valid IBAN.
"""

from iban_tools.validator import COUNTRY_SPECS, _sanitize, validate_iban


def parse_iban(iban: str) -> dict:
    """Parse an IBAN and return its structural components.

    Validates the IBAN and then extracts all constituent parts based on
    the country-specific IBAN format specification.

    Args:
        iban: The IBAN string to parse (may contain spaces, hyphens).

    Returns:
        A dictionary containing:
        - is_valid (bool): Whether the IBAN passes MOD-97 validation
        - iban (str): The sanitized IBAN string
        - country_code (str): ISO 3166-1 alpha-2 country code
        - check_digits (str): The 2-digit check value
        - bban (str): Basic Bank Account Number (everything after check digits)
        - bank_code (str | None): Bank identifier extracted from BBAN
        - account_number (str | None): Account number portion of BBAN
        - country_name (str | None): Human-readable country name

    Examples:
        >>> result = parse_iban("DE89370400440532013000")
        >>> result["country_code"]
        'DE'
        >>> result["bank_code"]
        '37040044'
        >>> result["is_valid"]
        True
    """
    cleaned = _sanitize(iban)

    # Base result for invalid/unparseable IBANs
    if len(cleaned) < 4:
        return {
            "is_valid": False,
            "iban": cleaned,
            "country_code": cleaned[:2] if len(cleaned) >= 2 else None,
            "check_digits": None,
            "bban": None,
            "bank_code": None,
            "account_number": None,
            "country_name": None,
        }

    country_code = cleaned[:2]
    check_digits = cleaned[2:4]
    bban = cleaned[4:]
    is_valid = validate_iban(cleaned)

    # Look up country spec for detailed parsing
    spec = COUNTRY_SPECS.get(country_code)

    if spec:
        bank_code_length = spec["bank_code_length"]
        bank_code = bban[:bank_code_length]
        account_number = bban[bank_code_length:]
        country_name = spec["name"]
    else:
        bank_code = None
        account_number = None
        country_name = None

    return {
        "is_valid": is_valid,
        "iban": cleaned,
        "country_code": country_code,
        "check_digits": check_digits,
        "bban": bban,
        "bank_code": bank_code,
        "account_number": account_number,
        "country_name": country_name,
    }
