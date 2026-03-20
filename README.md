# IBAN Tools 🏦

A comprehensive Python toolkit for IBAN operations including validation, extraction, generation, formatting, parsing, and BIC lookup.

## Features (6 Core Functions)

| Function | Description |
|----------|-------------|
| `extract_ibans_from_text()` | Extract validated IBANs from any text |
| `extract_ibans_from_pdf()` | Extract validated IBANs from PDF files |
| `generate_mock_iban()` | Generate random but valid test IBANs |
| `format_iban()` / `sanitize_iban()` | Format or clean IBAN strings |
| `parse_iban()` | Decompose IBAN into structured components |
| `iban_to_bic()` | Look up SWIFT BIC code from IBAN |

## Quick Start

```python
from iban_tools import (
    validate_iban,
    extract_ibans_from_text,
    generate_mock_iban,
    format_iban,
    sanitize_iban,
    parse_iban,
    iban_to_bic,
)

# 1. Validate
validate_iban("DE89 3704 0044 0532 0130 00")  # True

# 2. Extract from text
text = "Transfer to DE89370400440532013000 or GB29NWBK60161331926819"
extract_ibans_from_text(text)
# ['DE89370400440532013000', 'GB29NWBK60161331926819']

# 3. Generate mock IBANs for testing
generate_mock_iban("TR")  # 'TR...' (valid random IBAN)

# 4. Format / Sanitize
format_iban("DE89370400440532013000")
# 'DE89 3704 0044 0532 0130 00'

sanitize_iban("DE89 3704-0044.0532/0130 00")
# 'DE89370400440532013000'

# 5. Parse
parse_iban("DE89370400440532013000")
# {
#   'is_valid': True,
#   'country_code': 'DE',
#   'check_digits': '89',
#   'bank_code': '37040044',
#   'account_number': '0532013000',
#   'bban': '370400440532013000',
#   'country_name': 'Germany'
# }

# 6. IBAN to BIC
iban_to_bic("DE89370400440532013000")  # 'COBADEFFXXX'
```

## Installation

```bash
pip install iban-tools
```

Or from source:

```bash
git clone https://github.com/ademakdogan/iban-tools.git
cd iban-tools
uv sync --all-extras
```

## Tech Stack

- Python 3.13
- uv package manager
- pypdf (PDF extraction)
- pytest (testing)

## Supported Countries

**BIC Lookup:** AT, BE, DE, ES, FR, LU, NL

**IBAN Validation & Generation:** 76 countries (full ISO 13616 registry)

## License

MIT
