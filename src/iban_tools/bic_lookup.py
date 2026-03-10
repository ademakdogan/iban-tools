"""IBAN to BIC (SWIFT) lookup engine.

This module provides IBAN-to-BIC resolution by extracting the bank code
from an IBAN and looking it up against embedded datasets for supported
European countries (AT, BE, DE, ES, FR, LU, NL).
"""

import json
from functools import lru_cache
from pathlib import Path

from iban_tools.validator import COUNTRY_SPECS, _sanitize, validate_iban

# Directory containing the BIC data JSON files
_DATA_DIR = Path(__file__).parent / "data"

# Countries that have BIC data available
SUPPORTED_BIC_COUNTRIES = frozenset({"AT", "BE", "DE", "ES", "FR", "LU", "NL"})


@lru_cache(maxsize=None)
def _load_bic_data(country_code: str) -> dict[str, str]:
    """Load BIC data for a specific country from the embedded JSON file.

    Uses LRU cache to avoid re-reading files on subsequent calls.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (uppercase).

    Returns:
        Dictionary mapping bank codes to BIC strings.
    """
    data_file = _DATA_DIR / f"{country_code.lower()}.json"

    if not data_file.exists():
        return {}

    with data_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def iban_to_bic(iban: str) -> str | None:
    """Look up the SWIFT BIC code for a given IBAN.

    Validates the IBAN, extracts the country code and bank code, then
    looks up the BIC from the embedded dataset.

    Currently supports 7 European countries: AT, BE, DE, ES, FR, LU, NL.

    Args:
        iban: The IBAN string (may contain spaces, hyphens).

    Returns:
        The BIC/SWIFT code as a string, or None if:
        - The IBAN is invalid
        - The country is not supported for BIC lookup
        - The bank code is not found in the dataset

    Examples:
        >>> iban_to_bic("DE89370400440532013000")
        'COBADEFFXXX'
        >>> iban_to_bic("XX123456789")  # Invalid
        None
    """
    cleaned = _sanitize(iban)

    # Validate IBAN
    if not validate_iban(cleaned):
        return None

    country_code = cleaned[:2]

    # Check if we have BIC data for this country
    if country_code not in SUPPORTED_BIC_COUNTRIES:
        return None

    # Get country spec to extract bank code
    spec = COUNTRY_SPECS.get(country_code)
    if not spec:
        return None

    # Extract bank code from IBAN
    bank_code_offset = spec["bank_code_offset"]
    bank_code_length = spec["bank_code_length"]
    bank_code = cleaned[bank_code_offset : bank_code_offset + bank_code_length]

    # Look up BIC
    bic_data = _load_bic_data(country_code)
    return bic_data.get(bank_code)


def get_supported_countries() -> list[dict[str, str]]:
    """Get a list of countries supported for BIC lookup.

    Returns:
        A list of dictionaries with 'code' and 'name' keys.
    """
    result = []
    for code in sorted(SUPPORTED_BIC_COUNTRIES):
        spec = COUNTRY_SPECS.get(code, {})
        result.append({
            "code": code,
            "name": spec.get("name", code),
        })
    return result


def get_bic_data_stats() -> dict[str, int]:
    """Get statistics about the loaded BIC datasets.

    Returns:
        Dictionary mapping country codes to the number of bank code entries.
    """
    stats = {}
    for country in sorted(SUPPORTED_BIC_COUNTRIES):
        data = _load_bic_data(country)
        stats[country] = len(data)
    return stats
