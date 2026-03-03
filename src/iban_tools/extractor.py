"""IBAN extraction from text and PDF documents.

This module provides functions to find and extract valid IBANs from
arbitrary text strings and readable PDF files.
"""

import re
from pathlib import Path

from iban_tools.validator import _sanitize, validate_iban

# Regex pattern that matches potential IBAN-like strings
# IBANs start with 2 letters + 2 digits, followed by 11-30 alphanumeric chars
# We also allow spaces, hyphens within the IBAN
_IBAN_CANDIDATE_PATTERN = re.compile(
    r"\b([A-Z]{2}\d{2}(?:[\s\-]?[A-Z0-9]{4}){2,8}(?:[\s\-]?[A-Z0-9]{1,4})?)\b",
    re.IGNORECASE,
)


def extract_ibans_from_text(text: str) -> list[str]:
    """Extract all valid IBANs from a text string.

    Scans the input text for IBAN-like patterns, validates each candidate
    using the MOD-97 algorithm, and returns a deduplicated list of valid IBANs
    in their sanitized (uppercase, no spaces) form.

    Args:
        text: The input text to search for IBANs.

    Returns:
        A list of unique, validated IBAN strings in electronic format.
    """
    if not text:
        return []

    candidates = _IBAN_CANDIDATE_PATTERN.findall(text)
    valid_ibans: list[str] = []
    seen: set[str] = set()

    for candidate in candidates:
        sanitized = _sanitize(candidate)

        # Skip if already found
        if sanitized in seen:
            continue

        # Validate and add
        if validate_iban(sanitized):
            valid_ibans.append(sanitized)
            seen.add(sanitized)

    return valid_ibans


def extract_ibans_from_pdf(pdf_path: str | Path) -> list[str]:
    """Extract all valid IBANs from a readable PDF file.

    Extracts text from all pages of the PDF, then finds and validates
    IBAN patterns using the same logic as extract_ibans_from_text.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        A list of unique, validated IBAN strings in electronic format.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If the file cannot be read as a PDF.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    if not path.suffix.lower() == ".pdf":
        raise ValueError(f"Expected a PDF file, got: {path.suffix}")

    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"

        return extract_ibans_from_text(full_text)

    except Exception as e:
        if isinstance(e, (FileNotFoundError, ValueError)):
            raise
        raise ValueError(f"Failed to read PDF file: {e}") from e
