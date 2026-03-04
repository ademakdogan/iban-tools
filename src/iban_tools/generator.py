"""Mock IBAN generator for testing purposes.

This module generates random but mathematically valid IBANs that pass
MOD-97 checksum validation. Useful for QA, testing, and development.
"""

import random
import string

from iban_tools.validator import COUNTRY_SPECS


def _calculate_check_digits(country_code: str, bban: str) -> str:
    """Calculate the MOD-97 check digits for a given country code and BBAN.

    Steps:
    1. Construct preliminary IBAN: country_code + "00" + bban
    2. Rearrange: bban + country_code_numeric + "00"
    3. Calculate: 98 - (numeric_value mod 97)
    4. Return zero-padded 2-digit string
    """
    # Convert country code letters to numbers (A=10, B=11, ..., Z=35)
    country_numeric = ""
    for char in country_code.upper():
        country_numeric += str(ord(char) - ord("A") + 10)

    # Build numeric string: BBAN + country_numeric + "00"
    numeric_str = ""
    for char in bban:
        if char.isdigit():
            numeric_str += char
        else:
            numeric_str += str(ord(char.upper()) - ord("A") + 10)

    numeric_str += country_numeric + "00"

    # Calculate check digits: 98 - (numeric mod 97)
    check = 98 - (int(numeric_str) % 97)
    return f"{check:02d}"


def generate_mock_iban(country_code: str) -> str:
    """Generate a random but mathematically valid IBAN for testing.

    The generated IBAN will:
    - Follow the correct format for the specified country
    - Have the correct length
    - Pass MOD-97 checksum validation

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g., 'DE', 'TR', 'GB').

    Returns:
        A valid IBAN string in electronic format (no spaces).

    Raises:
        ValueError: If the country code is not supported.

    Examples:
        >>> iban = generate_mock_iban('DE')
        >>> len(iban) == 22
        True
        >>> iban[:2] == 'DE'
        True
    """
    code = country_code.upper()

    if code not in COUNTRY_SPECS:
        raise ValueError(
            f"Unsupported country code: '{country_code}'. "
            f"Supported codes: {', '.join(sorted(COUNTRY_SPECS.keys()))}"
        )

    spec = COUNTRY_SPECS[code]
    iban_length = spec["length"]

    # BBAN length = total length - 4 (country code + check digits)
    bban_length = iban_length - 4

    # Generate random BBAN
    # Most countries use numeric-only BBANs, but some (GB, IE, NL, etc.) use
    # alphanumeric bank codes
    alpha_bban_countries = {"GB", "IE", "NL", "FI", "BH", "KW", "LC", "MU", "SC"}

    if code in alpha_bban_countries:
        # Generate bank code as uppercase letters, rest as digits
        bank_code_len = spec["bank_code_length"]
        bank_code = "".join(random.choices(string.ascii_uppercase, k=bank_code_len))
        rest_len = bban_length - bank_code_len
        rest = "".join(random.choices(string.digits, k=rest_len))
        bban = bank_code + rest
    else:
        # Pure numeric BBAN
        bban = "".join(random.choices(string.digits, k=bban_length))

    # Calculate valid check digits
    check_digits = _calculate_check_digits(code, bban)

    return f"{code}{check_digits}{bban}"


def generate_mock_ibans(country_code: str, count: int = 5) -> list[str]:
    """Generate multiple random but valid IBANs for a country.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g., 'DE', 'TR').
        count: Number of IBANs to generate (default: 5).

    Returns:
        A list of valid IBAN strings.

    Raises:
        ValueError: If count is less than 1 or country code is not supported.
    """
    if count < 1:
        raise ValueError("Count must be at least 1")

    return [generate_mock_iban(country_code) for _ in range(count)]
