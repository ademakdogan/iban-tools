"""Tests for IBAN validation module."""

import pytest

from iban_tools.validator import (
    COUNTRY_SPECS,
    _mod97_check,
    _sanitize,
    get_country_spec,
    validate_iban,
)


class TestSanitize:
    """Tests for the _sanitize helper function."""

    def test_removes_spaces(self):
        assert _sanitize("DE89 3704 0044 0532 0130 00") == "DE89370400440532013000"

    def test_removes_hyphens(self):
        assert _sanitize("DE89-3704-0044-0532-0130-00") == "DE89370400440532013000"

    def test_uppercases(self):
        assert _sanitize("de89370400440532013000") == "DE89370400440532013000"

    def test_removes_mixed_special_chars(self):
        assert _sanitize("DE89 3704.0044/0532-0130 00") == "DE89370400440532013000"

    def test_empty_string(self):
        assert _sanitize("") == ""


class TestMod97Check:
    """Tests for the MOD-97 checksum algorithm."""

    def test_valid_de_iban(self):
        assert _mod97_check("DE89370400440532013000") is True

    def test_valid_gb_iban(self):
        assert _mod97_check("GB29NWBK60161331926819") is True

    def test_valid_fr_iban(self):
        assert _mod97_check("FR7630006000011234567890189") is True

    def test_invalid_checksum(self):
        assert _mod97_check("DE00370400440532013000") is False


class TestValidateIban:
    """Tests for the main validate_iban function."""

    # Valid IBANs from various countries
    @pytest.mark.parametrize(
        "iban",
        [
            "DE89370400440532013000",
            "GB29NWBK60161331926819",
            "FR7630006000011234567890189",
            "AT611904300234573201",
            "BE68539007547034",
            "NL91ABNA0417164300",
            "ES9121000418450200051332",
            "TR330006100519786457841326",
            "IT60X0542811101000000123456",
            "LU280019400644750000",
            "CH9300762011623852957",
            "PL61109010140000071219812874",
        ],
        ids=[
            "DE", "GB", "FR", "AT", "BE", "NL", "ES", "TR", "IT", "LU", "CH", "PL",
        ],
    )
    def test_valid_ibans(self, iban):
        assert validate_iban(iban) is True

    # Valid IBANs with formatting
    def test_valid_iban_with_spaces(self):
        assert validate_iban("DE89 3704 0044 0532 0130 00") is True

    def test_valid_iban_with_hyphens(self):
        assert validate_iban("DE89-3704-0044-0532-0130-00") is True

    def test_valid_iban_lowercase(self):
        assert validate_iban("de89370400440532013000") is True

    # Invalid IBANs
    def test_too_short(self):
        assert validate_iban("DE893704004") is False

    def test_too_long(self):
        assert validate_iban("DE89370400440532013000123456789012345") is False

    def test_invalid_country_code(self):
        assert validate_iban("1289370400440532013000") is False

    def test_invalid_check_digits(self):
        assert validate_iban("DEAB370400440532013000") is False

    def test_wrong_checksum(self):
        assert validate_iban("DE00370400440532013000") is False

    def test_wrong_length_for_country(self):
        # DE should be 22 chars, this is 21
        assert validate_iban("DE8937040044053201300") is False

    def test_empty_string(self):
        assert validate_iban("") is False

    def test_garbage_input(self):
        assert validate_iban("not an iban at all") is False


class TestGetCountrySpec:
    """Tests for country spec lookup."""

    def test_known_country(self):
        spec = get_country_spec("DE")
        assert spec is not None
        assert spec["length"] == 22
        assert spec["bank_code_length"] == 8
        assert spec["name"] == "Germany"

    def test_known_country_tr(self):
        spec = get_country_spec("TR")
        assert spec is not None
        assert spec["length"] == 26
        assert spec["bank_code_length"] == 5
        assert spec["name"] == "Turkey"

    def test_case_insensitive(self):
        spec = get_country_spec("de")
        assert spec is not None
        assert spec["name"] == "Germany"

    def test_unknown_country(self):
        assert get_country_spec("XX") is None

    def test_country_specs_completeness(self):
        """Ensure all major EU countries are covered."""
        eu_countries = ["AT", "BE", "DE", "ES", "FR", "IT", "NL", "LU", "PT", "GR", "IE"]
        for code in eu_countries:
            assert code in COUNTRY_SPECS, f"Missing EU country: {code}"
