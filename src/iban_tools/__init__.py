"""iban-tools: A comprehensive Python toolkit for IBAN operations.

This package provides 6 core functions for IBAN validation, extraction,
generation, formatting, parsing, and BIC lookup.

Functions:
    extract_ibans_from_text: Extract valid IBANs from text strings
    extract_ibans_from_pdf: Extract valid IBANs from readable PDF files
    generate_mock_iban: Generate random but valid IBANs for testing
    generate_mock_ibans: Generate multiple random valid IBANs
    format_iban: Format IBAN into standard 4-character blocks
    sanitize_iban: Clean IBAN string for database storage
    parse_iban: Decompose IBAN into structural components
    iban_to_bic: Look up SWIFT BIC code from an IBAN
    validate_iban: Validate an IBAN using MOD-97 algorithm
"""

__version__ = "0.1.0"

from iban_tools.bic_lookup import (
    get_bic_data_stats,
    get_supported_countries,
    iban_to_bic,
)
from iban_tools.extractor import extract_ibans_from_pdf, extract_ibans_from_text
from iban_tools.formatter import format_iban, is_formatted, sanitize_iban
from iban_tools.generator import generate_mock_iban, generate_mock_ibans
from iban_tools.parser import parse_iban
from iban_tools.validator import validate_iban

__all__ = [
    # Extraction
    "extract_ibans_from_text",
    "extract_ibans_from_pdf",
    # Generation
    "generate_mock_iban",
    "generate_mock_ibans",
    # Formatting
    "format_iban",
    "sanitize_iban",
    "is_formatted",
    # Parsing
    "parse_iban",
    # BIC Lookup
    "iban_to_bic",
    "get_supported_countries",
    "get_bic_data_stats",
    # Validation
    "validate_iban",
]
