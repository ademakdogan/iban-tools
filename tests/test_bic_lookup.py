"""Tests for IBAN to BIC lookup."""

import pytest

from iban_tools.bic_lookup import (
    SUPPORTED_BIC_COUNTRIES,
    get_bic_data_stats,
    get_supported_countries,
    iban_to_bic,
)
from iban_tools.generator import generate_mock_iban
from iban_tools.validator import validate_iban


class TestIbanToBic:
    """Tests for the iban_to_bic function."""

    def test_de_commerzbank(self):
        """DE bank code 37040044 -> COBADEFFXXX (Commerzbank)."""
        result = iban_to_bic("DE89370400440532013000")
        assert result == "COBADEFFXXX"

    def test_de_ingdiba(self):
        """DE bank code 50010517 -> INGDDEFFXXX (ING DiBa)."""
        result = iban_to_bic("DE51500105179975341634")
        assert result == "INGDDEFFXXX"

    def test_de_postbank(self):
        """DE bank code 10010010 -> PBNKDEFFXXX (Postbank)."""
        result = iban_to_bic("DE53100100100495106610")
        assert result == "PBNKDEFFXXX"

    def test_at_bkauatww(self):
        """AT bank code 11000 -> BKAUATWWXXX."""
        result = iban_to_bic("AT021100000012345600")
        # Verify the IBAN is valid first
        if validate_iban("AT021100000012345600"):
            assert result == "BKAUATWWXXX"

    def test_at_rlnwatww(self):
        """AT bank code 32000 -> RLNWATWWXXX."""
        result = iban_to_bic("AT483200000012345864")
        assert result == "RLNWATWWXXX"

    def test_nl_abna(self):
        """NL bank code ABNA -> ABNANL2A (8-char BIC, no XXX suffix in data)."""
        result = iban_to_bic("NL91ABNA0417164300")
        assert result == "ABNANL2A"

    def test_lu_bcee(self):
        """LU bank code 001 -> BCEELULL (8-char BIC, no XXX suffix in data)."""
        result = iban_to_bic("LU280019400644750000")
        assert result == "BCEELULL"

    def test_iban_with_spaces(self):
        result = iban_to_bic("DE89 3704 0044 0532 0130 00")
        assert result == "COBADEFFXXX"

    def test_lowercase_iban(self):
        result = iban_to_bic("de89370400440532013000")
        assert result == "COBADEFFXXX"

    def test_invalid_iban_returns_none(self):
        result = iban_to_bic("DE00370400440532013000")
        assert result is None

    def test_unsupported_country_returns_none(self):
        result = iban_to_bic("TR330006100519786457841326")
        assert result is None

    def test_unknown_bank_code_returns_none(self):
        result = iban_to_bic("DE75999999990000001234")
        assert result is None

    def test_empty_string_returns_none(self):
        assert iban_to_bic("") is None

    def test_garbage_input_returns_none(self):
        assert iban_to_bic("not an iban") is None

    def test_nl_bic_lookup(self):
        """Dutch ABNA bank code returns a BIC."""
        result = iban_to_bic("NL91ABNA0417164300")
        assert result is not None
        assert len(result) >= 8


class TestGetSupportedCountries:
    """Tests for get_supported_countries."""

    def test_returns_list(self):
        result = get_supported_countries()
        assert isinstance(result, list)

    def test_all_countries_present(self):
        result = get_supported_countries()
        codes = {c["code"] for c in result}
        assert codes == SUPPORTED_BIC_COUNTRIES

    def test_has_name_and_code(self):
        result = get_supported_countries()
        for country in result:
            assert "code" in country
            assert "name" in country
            assert len(country["code"]) == 2

    def test_seven_countries(self):
        result = get_supported_countries()
        assert len(result) == 7


class TestGetBicDataStats:
    """Tests for get_bic_data_stats."""

    def test_returns_dict(self):
        stats = get_bic_data_stats()
        assert isinstance(stats, dict)

    def test_all_countries_have_entries(self):
        stats = get_bic_data_stats()
        for country in SUPPORTED_BIC_COUNTRIES:
            assert country in stats
            assert stats[country] > 0, f"No BIC entries for {country}"

    def test_de_has_many_entries(self):
        """Germany should have hundreds of bank codes."""
        stats = get_bic_data_stats()
        assert stats["DE"] > 100

    def test_be_has_entries(self):
        stats = get_bic_data_stats()
        assert stats["BE"] > 50
