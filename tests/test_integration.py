"""Integration tests for the full iban-tools pipeline."""

from iban_tools import (
    extract_ibans_from_text,
    format_iban,
    generate_mock_iban,
    generate_mock_ibans,
    iban_to_bic,
    parse_iban,
    sanitize_iban,
    validate_iban,
)


class TestPublicApiImports:
    """Verify all public functions are importable from the top-level package."""

    def test_validate_iban_importable(self):
        assert callable(validate_iban)

    def test_extract_from_text_importable(self):
        assert callable(extract_ibans_from_text)

    def test_generate_mock_iban_importable(self):
        assert callable(generate_mock_iban)

    def test_format_iban_importable(self):
        assert callable(format_iban)

    def test_sanitize_iban_importable(self):
        assert callable(sanitize_iban)

    def test_parse_iban_importable(self):
        assert callable(parse_iban)

    def test_iban_to_bic_importable(self):
        assert callable(iban_to_bic)


class TestEndToEndPipeline:
    """Integration tests combining multiple functions."""

    def test_generate_validate_parse_format_pipeline(self):
        """Generate → Validate → Parse → Format full pipeline."""
        for country in ["DE", "TR", "FR", "GB", "AT", "NL"]:
            # Generate
            iban = generate_mock_iban(country)

            # Validate
            assert validate_iban(iban), f"Generated {country} IBAN failed validation"

            # Parse
            parsed = parse_iban(iban)
            assert parsed["is_valid"] is True
            assert parsed["country_code"] == country
            assert parsed["bank_code"] is not None

            # Format
            formatted = format_iban(iban)
            assert " " in formatted  # Should have spaces
            assert sanitize_iban(formatted) == iban  # Round-trip

    def test_extract_from_generated_ibans(self):
        """Generate IBANs, embed in text, extract them back."""
        ibans = generate_mock_ibans("DE", count=3)

        # Build a text with the IBANs
        text = f"Payment 1: {ibans[0]}, Payment 2: {ibans[1]}, Payment 3: {ibans[2]}"

        # Extract
        extracted = extract_ibans_from_text(text)
        assert len(extracted) == 3
        for iban in ibans:
            assert iban in extracted

    def test_extract_validate_bic_pipeline(self):
        """Extract → Validate → BIC lookup pipeline."""
        text = "Transfer to DE89370400440532013000 (Commerzbank)"

        extracted = extract_ibans_from_text(text)
        assert len(extracted) == 1

        iban = extracted[0]
        assert validate_iban(iban)

        bic = iban_to_bic(iban)
        assert bic == "COBADEFFXXX"

    def test_format_roundtrip(self):
        """format → sanitize should return original."""
        original = "DE89370400440532013000"
        formatted = format_iban(original)
        restored = sanitize_iban(formatted)
        assert restored == original

    def test_batch_generate_all_valid(self):
        """Batch generation produces all valid IBANs."""
        ibans = generate_mock_ibans("TR", count=20)
        assert len(ibans) == 20
        for iban in ibans:
            assert validate_iban(iban)
            parsed = parse_iban(iban)
            assert parsed["country_code"] == "TR"
            assert parsed["country_name"] == "Turkey"

    def test_version_available(self):
        """Package version is accessible."""
        from iban_tools import __version__
        assert __version__ == "0.1.0"
