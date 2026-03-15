"""Edge case and boundary tests for the validator module."""

import pytest

from iban_tools.validator import COUNTRY_SPECS, validate_iban


class TestValidatorEdgeCases:
    """Additional edge case tests for comprehensive validation coverage."""

    def test_all_zeros_bban_de(self):
        """IBAN with all zeros in BBAN should still be valid if MOD-97 passes."""
        # DE51000000000000000000 -> check if MOD-97 passes with all zeros
        from iban_tools.generator import _calculate_check_digits
        bban = "0" * 18  # DE has 18-char BBAN
        check = _calculate_check_digits("DE", bban)
        iban = f"DE{check}{bban}"
        assert validate_iban(iban)

    def test_max_length_iban(self):
        """Test with maximum length IBAN (34 chars - LC is 32)."""
        from iban_tools.generator import generate_mock_iban
        iban = generate_mock_iban("LC")  # 32 chars
        assert validate_iban(iban)
        assert len(iban) == 32

    def test_min_length_iban(self):
        """Test with minimum length IBAN (15 chars - NO is 15)."""
        from iban_tools.generator import generate_mock_iban
        iban = generate_mock_iban("NO")  # 15 chars
        assert validate_iban(iban)
        assert len(iban) == 15

    def test_unicode_input(self):
        """Unicode characters are stripped by sanitizer, underlying IBAN stays valid."""
        assert validate_iban("DE89370400440532013000™") is True

    def test_tab_characters(self):
        """Tabs should be treated as separators."""
        assert validate_iban("DE89\t3704\t0044\t0532\t0130\t00") is True

    def test_newline_in_iban(self):
        """Newlines in IBAN should be stripped."""
        assert validate_iban("DE89370400440532\n013000") is True

    @pytest.mark.parametrize("country_code", list(COUNTRY_SPECS.keys()))
    def test_all_country_specs_have_required_fields(self, country_code):
        """Every country spec must have all required fields."""
        spec = COUNTRY_SPECS[country_code]
        assert "length" in spec
        assert "bank_code_offset" in spec
        assert "bank_code_length" in spec
        assert "name" in spec
        assert spec["bank_code_offset"] == 4  # Always 4 for IBAN
        assert spec["length"] >= 15
        assert spec["length"] <= 34
        assert spec["bank_code_length"] > 0


class TestExceptionModule:
    """Tests for custom exception classes."""

    def test_invalid_iban_error(self):
        from iban_tools.exceptions import InvalidIbanError
        err = InvalidIbanError("DE00", "Wrong checksum")
        assert "DE00" in str(err)
        assert err.iban == "DE00"

    def test_unsupported_country_error(self):
        from iban_tools.exceptions import UnsupportedCountryError
        err = UnsupportedCountryError("XX")
        assert "XX" in str(err)
        assert err.country_code == "XX"

    def test_bic_not_found_error(self):
        from iban_tools.exceptions import BicNotFoundError
        err = BicNotFoundError("DE89370400440532013000", "37040044")
        assert "37040044" in str(err)
        assert err.bank_code == "37040044"

    def test_exception_hierarchy(self):
        from iban_tools.exceptions import (
            BicNotFoundError,
            IbanToolsError,
            InvalidIbanError,
            UnsupportedCountryError,
        )
        assert issubclass(InvalidIbanError, IbanToolsError)
        assert issubclass(UnsupportedCountryError, IbanToolsError)
        assert issubclass(BicNotFoundError, IbanToolsError)
        assert issubclass(IbanToolsError, Exception)
