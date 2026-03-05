"""Tests for mock IBAN generator."""

import pytest

from iban_tools.generator import (
    _calculate_check_digits,
    generate_mock_iban,
    generate_mock_ibans,
)
from iban_tools.validator import COUNTRY_SPECS, validate_iban


class TestCalculateCheckDigits:
    """Tests for check digit calculation."""

    def test_known_de_iban(self):
        # DE89370400440532013000 -> check digits should be "89"
        bban = "370400440532013000"
        assert _calculate_check_digits("DE", bban) == "89"

    def test_known_gb_iban(self):
        # GB29NWBK60161331926819 -> check digits should be "29"
        bban = "NWBK60161331926819"
        assert _calculate_check_digits("GB", bban) == "29"

    def test_known_fr_iban(self):
        # FR7630006000011234567890189 -> check digits should be "76"
        bban = "30006000011234567890189"
        assert _calculate_check_digits("FR", bban) == "76"

    def test_known_at_iban(self):
        # AT611904300234573201 -> check digits should be "61"
        bban = "1904300234573201"
        assert _calculate_check_digits("AT", bban) == "61"

    def test_known_tr_iban(self):
        # TR330006100519786457841326 -> check digits should be "33"
        bban = "0006100519786457841326"
        assert _calculate_check_digits("TR", bban) == "33"


class TestGenerateMockIban:
    """Tests for single IBAN generation."""

    @pytest.mark.parametrize(
        "country_code",
        ["DE", "AT", "FR", "GB", "TR", "ES", "IT", "NL", "BE", "CH", "PL", "LU"],
        ids=["DE", "AT", "FR", "GB", "TR", "ES", "IT", "NL", "BE", "CH", "PL", "LU"],
    )
    def test_generated_iban_is_valid(self, country_code):
        """Generated IBANs must pass MOD-97 validation."""
        iban = generate_mock_iban(country_code)
        assert validate_iban(iban), f"Generated IBAN {iban} failed validation"

    @pytest.mark.parametrize("country_code", ["DE", "TR", "GB", "FR", "AT"])
    def test_correct_length(self, country_code):
        iban = generate_mock_iban(country_code)
        expected_length = COUNTRY_SPECS[country_code]["length"]
        assert len(iban) == expected_length

    @pytest.mark.parametrize("country_code", ["DE", "TR", "FR", "NL"])
    def test_correct_country_prefix(self, country_code):
        iban = generate_mock_iban(country_code)
        assert iban[:2] == country_code

    def test_lowercase_country_code(self):
        iban = generate_mock_iban("de")
        assert iban[:2] == "DE"
        assert validate_iban(iban)

    def test_unsupported_country_raises(self):
        with pytest.raises(ValueError, match="Unsupported country code"):
            generate_mock_iban("XX")

    def test_uniqueness(self):
        """Multiple generations should produce different IBANs."""
        ibans = {generate_mock_iban("DE") for _ in range(10)}
        # With 18-digit random BBAN, collision is practically impossible
        assert len(ibans) > 1

    def test_all_supported_countries(self):
        """Ensure generation works for every registered country."""
        for code in COUNTRY_SPECS:
            iban = generate_mock_iban(code)
            assert validate_iban(iban), f"Failed for {code}: {iban}"


class TestGenerateMockIbans:
    """Tests for batch IBAN generation."""

    def test_generates_correct_count(self):
        ibans = generate_mock_ibans("DE", count=10)
        assert len(ibans) == 10

    def test_all_valid(self):
        ibans = generate_mock_ibans("TR", count=5)
        for iban in ibans:
            assert validate_iban(iban)

    def test_default_count(self):
        ibans = generate_mock_ibans("FR")
        assert len(ibans) == 5

    def test_count_zero_raises(self):
        with pytest.raises(ValueError, match="Count must be at least 1"):
            generate_mock_ibans("DE", count=0)

    def test_count_negative_raises(self):
        with pytest.raises(ValueError, match="Count must be at least 1"):
            generate_mock_ibans("DE", count=-1)
