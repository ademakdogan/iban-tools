"""Tests for IBAN parser."""

import pytest

from iban_tools.parser import parse_iban


class TestParseIban:
    """Tests for the parse_iban function."""

    def test_valid_de_iban(self):
        result = parse_iban("DE89370400440532013000")
        assert result["is_valid"] is True
        assert result["iban"] == "DE89370400440532013000"
        assert result["country_code"] == "DE"
        assert result["check_digits"] == "89"
        assert result["bban"] == "370400440532013000"
        assert result["bank_code"] == "37040044"
        assert result["account_number"] == "0532013000"
        assert result["country_name"] == "Germany"

    def test_valid_tr_iban(self):
        result = parse_iban("TR330006100519786457841326")
        assert result["is_valid"] is True
        assert result["country_code"] == "TR"
        assert result["check_digits"] == "33"
        assert result["bank_code"] == "00061"
        assert result["account_number"] == "00519786457841326"
        assert result["country_name"] == "Turkey"

    def test_valid_gb_iban(self):
        result = parse_iban("GB29NWBK60161331926819")
        assert result["is_valid"] is True
        assert result["country_code"] == "GB"
        assert result["check_digits"] == "29"
        assert result["bank_code"] == "NWBK"
        assert result["account_number"] == "60161331926819"
        assert result["country_name"] == "United Kingdom"

    def test_valid_at_iban(self):
        result = parse_iban("AT611904300234573201")
        assert result["is_valid"] is True
        assert result["country_code"] == "AT"
        assert result["bank_code"] == "19043"
        assert result["country_name"] == "Austria"

    def test_valid_fr_iban(self):
        result = parse_iban("FR7630006000011234567890189")
        assert result["is_valid"] is True
        assert result["country_code"] == "FR"
        assert result["bank_code"] == "30006"
        assert result["country_name"] == "France"

    def test_valid_nl_iban(self):
        result = parse_iban("NL91ABNA0417164300")
        assert result["is_valid"] is True
        assert result["country_code"] == "NL"
        assert result["bank_code"] == "ABNA"
        assert result["country_name"] == "Netherlands"

    def test_valid_es_iban(self):
        result = parse_iban("ES9121000418450200051332")
        assert result["is_valid"] is True
        assert result["country_code"] == "ES"
        assert result["bank_code"] == "2100"
        assert result["country_name"] == "Spain"

    def test_valid_be_iban(self):
        result = parse_iban("BE68539007547034")
        assert result["is_valid"] is True
        assert result["country_code"] == "BE"
        assert result["bank_code"] == "539"
        assert result["country_name"] == "Belgium"

    def test_valid_lu_iban(self):
        result = parse_iban("LU280019400644750000")
        assert result["is_valid"] is True
        assert result["country_code"] == "LU"
        assert result["bank_code"] == "001"
        assert result["country_name"] == "Luxembourg"

    def test_iban_with_spaces(self):
        result = parse_iban("DE89 3704 0044 0532 0130 00")
        assert result["is_valid"] is True
        assert result["iban"] == "DE89370400440532013000"
        assert result["bank_code"] == "37040044"

    def test_lowercase_iban(self):
        result = parse_iban("de89370400440532013000")
        assert result["is_valid"] is True
        assert result["country_code"] == "DE"

    def test_invalid_checksum(self):
        result = parse_iban("DE00370400440532013000")
        assert result["is_valid"] is False
        assert result["country_code"] == "DE"
        assert result["bban"] == "370400440532013000"

    def test_short_input(self):
        result = parse_iban("DE")
        assert result["is_valid"] is False
        assert result["country_code"] == "DE"
        assert result["check_digits"] is None

    def test_empty_string(self):
        result = parse_iban("")
        assert result["is_valid"] is False
        assert result["country_code"] is None

    def test_all_fields_present(self):
        """Ensure all expected fields are in the result."""
        result = parse_iban("DE89370400440532013000")
        expected_keys = {
            "is_valid", "iban", "country_code", "check_digits",
            "bban", "bank_code", "account_number", "country_name",
        }
        assert set(result.keys()) == expected_keys

    @pytest.mark.parametrize(
        "iban,country",
        [
            ("CH9300762011623852957", "Switzerland"),
            ("PL61109010140000071219812874", "Poland"),
            ("IT60X0542811101000000123456", "Italy"),
        ],
        ids=["CH", "PL", "IT"],
    )
    def test_various_countries(self, iban, country):
        result = parse_iban(iban)
        assert result["is_valid"] is True
        assert result["country_name"] == country
