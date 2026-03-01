"""IBAN country specifications and validation engine.

This module provides MOD-97 (ISO 7064) IBAN validation and a comprehensive
country registry with IBAN lengths and bank code extraction offsets.
"""

import re

# Country specifications: country_code -> (iban_length, bank_code_offset, bank_code_length)
# Bank code offset is always 4 (after country code + check digits)
# Source: https://en.wikipedia.org/wiki/International_Bank_Account_Number#IBAN_formats_by_country
COUNTRY_SPECS: dict[str, dict] = {
    "AD": {"length": 24, "bank_code_offset": 4, "bank_code_length": 4, "name": "Andorra"},
    "AE": {"length": 23, "bank_code_offset": 4, "bank_code_length": 3, "name": "United Arab Emirates"},
    "AL": {"length": 28, "bank_code_offset": 4, "bank_code_length": 3, "name": "Albania"},
    "AT": {"length": 20, "bank_code_offset": 4, "bank_code_length": 5, "name": "Austria"},
    "AZ": {"length": 28, "bank_code_offset": 4, "bank_code_length": 4, "name": "Azerbaijan"},
    "BA": {"length": 20, "bank_code_offset": 4, "bank_code_length": 3, "name": "Bosnia and Herzegovina"},
    "BE": {"length": 16, "bank_code_offset": 4, "bank_code_length": 3, "name": "Belgium"},
    "BG": {"length": 22, "bank_code_offset": 4, "bank_code_length": 4, "name": "Bulgaria"},
    "BH": {"length": 22, "bank_code_offset": 4, "bank_code_length": 4, "name": "Bahrain"},
    "BR": {"length": 29, "bank_code_offset": 4, "bank_code_length": 8, "name": "Brazil"},
    "BY": {"length": 28, "bank_code_offset": 4, "bank_code_length": 4, "name": "Belarus"},
    "CH": {"length": 21, "bank_code_offset": 4, "bank_code_length": 5, "name": "Switzerland"},
    "CR": {"length": 22, "bank_code_offset": 4, "bank_code_length": 4, "name": "Costa Rica"},
    "CY": {"length": 28, "bank_code_offset": 4, "bank_code_length": 3, "name": "Cyprus"},
    "CZ": {"length": 24, "bank_code_offset": 4, "bank_code_length": 4, "name": "Czech Republic"},
    "DE": {"length": 22, "bank_code_offset": 4, "bank_code_length": 8, "name": "Germany"},
    "DK": {"length": 18, "bank_code_offset": 4, "bank_code_length": 4, "name": "Denmark"},
    "DO": {"length": 28, "bank_code_offset": 4, "bank_code_length": 4, "name": "Dominican Republic"},
    "EE": {"length": 20, "bank_code_offset": 4, "bank_code_length": 2, "name": "Estonia"},
    "EG": {"length": 29, "bank_code_offset": 4, "bank_code_length": 4, "name": "Egypt"},
    "ES": {"length": 24, "bank_code_offset": 4, "bank_code_length": 4, "name": "Spain"},
    "FI": {"length": 18, "bank_code_offset": 4, "bank_code_length": 3, "name": "Finland"},
    "FO": {"length": 18, "bank_code_offset": 4, "bank_code_length": 4, "name": "Faroe Islands"},
    "FR": {"length": 27, "bank_code_offset": 4, "bank_code_length": 5, "name": "France"},
    "GB": {"length": 22, "bank_code_offset": 4, "bank_code_length": 4, "name": "United Kingdom"},
    "GE": {"length": 22, "bank_code_offset": 4, "bank_code_length": 2, "name": "Georgia"},
    "GI": {"length": 23, "bank_code_offset": 4, "bank_code_length": 4, "name": "Gibraltar"},
    "GL": {"length": 18, "bank_code_offset": 4, "bank_code_length": 4, "name": "Greenland"},
    "GR": {"length": 27, "bank_code_offset": 4, "bank_code_length": 3, "name": "Greece"},
    "GT": {"length": 28, "bank_code_offset": 4, "bank_code_length": 4, "name": "Guatemala"},
    "HR": {"length": 21, "bank_code_offset": 4, "bank_code_length": 7, "name": "Croatia"},
    "HU": {"length": 28, "bank_code_offset": 4, "bank_code_length": 3, "name": "Hungary"},
    "IE": {"length": 22, "bank_code_offset": 4, "bank_code_length": 4, "name": "Ireland"},
    "IL": {"length": 23, "bank_code_offset": 4, "bank_code_length": 3, "name": "Israel"},
    "IQ": {"length": 23, "bank_code_offset": 4, "bank_code_length": 4, "name": "Iraq"},
    "IS": {"length": 26, "bank_code_offset": 4, "bank_code_length": 4, "name": "Iceland"},
    "IT": {"length": 27, "bank_code_offset": 4, "bank_code_length": 5, "name": "Italy"},
    "JO": {"length": 30, "bank_code_offset": 4, "bank_code_length": 4, "name": "Jordan"},
    "KW": {"length": 30, "bank_code_offset": 4, "bank_code_length": 4, "name": "Kuwait"},
    "KZ": {"length": 20, "bank_code_offset": 4, "bank_code_length": 3, "name": "Kazakhstan"},
    "LB": {"length": 28, "bank_code_offset": 4, "bank_code_length": 4, "name": "Lebanon"},
    "LC": {"length": 32, "bank_code_offset": 4, "bank_code_length": 4, "name": "Saint Lucia"},
    "LI": {"length": 21, "bank_code_offset": 4, "bank_code_length": 5, "name": "Liechtenstein"},
    "LT": {"length": 20, "bank_code_offset": 4, "bank_code_length": 5, "name": "Lithuania"},
    "LU": {"length": 20, "bank_code_offset": 4, "bank_code_length": 3, "name": "Luxembourg"},
    "LV": {"length": 21, "bank_code_offset": 4, "bank_code_length": 4, "name": "Latvia"},
    "MC": {"length": 27, "bank_code_offset": 4, "bank_code_length": 5, "name": "Monaco"},
    "MD": {"length": 24, "bank_code_offset": 4, "bank_code_length": 2, "name": "Moldova"},
    "ME": {"length": 22, "bank_code_offset": 4, "bank_code_length": 3, "name": "Montenegro"},
    "MK": {"length": 19, "bank_code_offset": 4, "bank_code_length": 3, "name": "North Macedonia"},
    "MR": {"length": 27, "bank_code_offset": 4, "bank_code_length": 5, "name": "Mauritania"},
    "MT": {"length": 31, "bank_code_offset": 4, "bank_code_length": 4, "name": "Malta"},
    "MU": {"length": 30, "bank_code_offset": 4, "bank_code_length": 6, "name": "Mauritius"},
    "NL": {"length": 18, "bank_code_offset": 4, "bank_code_length": 4, "name": "Netherlands"},
    "NO": {"length": 15, "bank_code_offset": 4, "bank_code_length": 4, "name": "Norway"},
    "PK": {"length": 24, "bank_code_offset": 4, "bank_code_length": 4, "name": "Pakistan"},
    "PL": {"length": 28, "bank_code_offset": 4, "bank_code_length": 8, "name": "Poland"},
    "PS": {"length": 29, "bank_code_offset": 4, "bank_code_length": 4, "name": "Palestine"},
    "PT": {"length": 25, "bank_code_offset": 4, "bank_code_length": 4, "name": "Portugal"},
    "QA": {"length": 29, "bank_code_offset": 4, "bank_code_length": 4, "name": "Qatar"},
    "RO": {"length": 24, "bank_code_offset": 4, "bank_code_length": 4, "name": "Romania"},
    "RS": {"length": 22, "bank_code_offset": 4, "bank_code_length": 3, "name": "Serbia"},
    "SA": {"length": 24, "bank_code_offset": 4, "bank_code_length": 2, "name": "Saudi Arabia"},
    "SC": {"length": 31, "bank_code_offset": 4, "bank_code_length": 4, "name": "Seychelles"},
    "SE": {"length": 24, "bank_code_offset": 4, "bank_code_length": 3, "name": "Sweden"},
    "SI": {"length": 19, "bank_code_offset": 4, "bank_code_length": 5, "name": "Slovenia"},
    "SK": {"length": 24, "bank_code_offset": 4, "bank_code_length": 4, "name": "Slovakia"},
    "SM": {"length": 27, "bank_code_offset": 4, "bank_code_length": 5, "name": "San Marino"},
    "ST": {"length": 25, "bank_code_offset": 4, "bank_code_length": 4, "name": "São Tomé and Príncipe"},
    "SV": {"length": 28, "bank_code_offset": 4, "bank_code_length": 4, "name": "El Salvador"},
    "TL": {"length": 23, "bank_code_offset": 4, "bank_code_length": 3, "name": "East Timor"},
    "TN": {"length": 24, "bank_code_offset": 4, "bank_code_length": 2, "name": "Tunisia"},
    "TR": {"length": 26, "bank_code_offset": 4, "bank_code_length": 5, "name": "Turkey"},
    "UA": {"length": 29, "bank_code_offset": 4, "bank_code_length": 6, "name": "Ukraine"},
    "VA": {"length": 22, "bank_code_offset": 4, "bank_code_length": 3, "name": "Vatican City"},
    "VG": {"length": 24, "bank_code_offset": 4, "bank_code_length": 4, "name": "British Virgin Islands"},
    "XK": {"length": 20, "bank_code_offset": 4, "bank_code_length": 4, "name": "Kosovo"},
}


def _sanitize(iban: str) -> str:
    """Remove all whitespace, hyphens, and special characters from IBAN, uppercase it."""
    return re.sub(r"[^A-Za-z0-9]", "", iban).upper()


def _mod97_check(iban: str) -> bool:
    """Validate IBAN using MOD-97 algorithm (ISO 7064).

    Steps:
    1. Move the first 4 characters to the end
    2. Convert letters to numbers (A=10, B=11, ..., Z=35)
    3. Check that the remainder when divided by 97 equals 1
    """
    # Move first 4 chars (country code + check digits) to end
    rearranged = iban[4:] + iban[:4]

    # Convert letters to numbers
    numeric_str = ""
    for char in rearranged:
        if char.isdigit():
            numeric_str += char
        else:
            numeric_str += str(ord(char) - ord("A") + 10)

    return int(numeric_str) % 97 == 1


def validate_iban(iban: str) -> bool:
    """Validate an IBAN string.

    Performs the following checks:
    1. Sanitize (remove spaces, hyphens, uppercase)
    2. Check minimum length (>= 15)
    3. Check country code format (2 uppercase letters)
    4. Check digits format (2 digits after country code)
    5. Check country-specific length (if country is known)
    6. Validate MOD-97 checksum

    Args:
        iban: The IBAN string to validate (may contain spaces, hyphens).

    Returns:
        True if the IBAN is valid, False otherwise.
    """
    cleaned = _sanitize(iban)

    # Basic format checks
    if len(cleaned) < 15 or len(cleaned) > 34:
        return False

    # Country code must be 2 uppercase letters
    if not cleaned[:2].isalpha():
        return False

    # Check digits must be 2 digits
    if not cleaned[2:4].isdigit():
        return False

    # Check country-specific length
    country_code = cleaned[:2]
    if country_code in COUNTRY_SPECS:
        expected_length = COUNTRY_SPECS[country_code]["length"]
        if len(cleaned) != expected_length:
            return False

    # MOD-97 checksum validation
    return _mod97_check(cleaned)


def get_country_spec(country_code: str) -> dict | None:
    """Get the IBAN specification for a given country code.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g., 'DE', 'TR').

    Returns:
        Dictionary with 'length', 'bank_code_offset', 'bank_code_length', 'name'
        or None if country is not supported.
    """
    return COUNTRY_SPECS.get(country_code.upper())
