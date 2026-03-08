"""Tests for IBAN formatter and sanitizer."""

from iban_tools.formatter import format_iban, is_formatted, sanitize_iban


class TestSanitizeIban:
    """Tests for the sanitize_iban function."""

    def test_removes_spaces(self):
        assert sanitize_iban("DE89 3704 0044 0532 0130 00") == "DE89370400440532013000"

    def test_removes_hyphens(self):
        assert sanitize_iban("DE89-3704-0044-0532-0130-00") == "DE89370400440532013000"

    def test_removes_dots(self):
        assert sanitize_iban("DE89.3704.0044.0532.0130.00") == "DE89370400440532013000"

    def test_removes_slashes(self):
        assert sanitize_iban("DE89/3704/0044") == "DE8937040044"

    def test_uppercases(self):
        assert sanitize_iban("de89370400440532013000") == "DE89370400440532013000"

    def test_mixed_special_chars(self):
        assert sanitize_iban("  DE89-3704.0044/0532 0130-00  ") == "DE89370400440532013000"

    def test_already_clean(self):
        assert sanitize_iban("DE89370400440532013000") == "DE89370400440532013000"

    def test_empty_string(self):
        assert sanitize_iban("") == ""

    def test_turkish_iban(self):
        assert sanitize_iban("TR33 0006 1005 1978 6457 8413 26") == "TR330006100519786457841326"


class TestFormatIban:
    """Tests for the format_iban function."""

    def test_de_iban(self):
        assert format_iban("DE89370400440532013000") == "DE89 3704 0044 0532 0130 00"

    def test_tr_iban(self):
        assert format_iban("TR330006100519786457841326") == "TR33 0006 1005 1978 6457 8413 26"

    def test_be_iban(self):
        assert format_iban("BE68539007547034") == "BE68 5390 0754 7034"

    def test_gb_iban(self):
        assert format_iban("GB29NWBK60161331926819") == "GB29 NWBK 6016 1331 9268 19"

    def test_at_iban(self):
        assert format_iban("AT611904300234573201") == "AT61 1904 3002 3457 3201"

    def test_already_formatted(self):
        result = format_iban("DE89 3704 0044 0532 0130 00")
        assert result == "DE89 3704 0044 0532 0130 00"

    def test_with_hyphens(self):
        result = format_iban("DE89-3704-0044-0532-0130-00")
        assert result == "DE89 3704 0044 0532 0130 00"

    def test_lowercase_input(self):
        result = format_iban("de89370400440532013000")
        assert result == "DE89 3704 0044 0532 0130 00"

    def test_empty_string(self):
        assert format_iban("") == ""

    def test_exact_multiple_of_four(self):
        result = format_iban("AT611904300234573201")
        assert result == "AT61 1904 3002 3457 3201"
        # 20 chars = 5 groups of 4, should have no trailing short group


class TestIsFormatted:
    """Tests for the is_formatted function."""

    def test_properly_formatted(self):
        assert is_formatted("DE89 3704 0044 0532 0130 00") is True

    def test_not_formatted_no_spaces(self):
        assert is_formatted("DE89370400440532013000") is False

    def test_not_formatted_hyphens(self):
        assert is_formatted("DE89-3704-0044") is False

    def test_exact_multiple_of_four(self):
        assert is_formatted("AT61 1904 3002 3457 3201") is True

    def test_single_block(self):
        # Unusual but technically a valid format with just one block
        assert is_formatted("DE89") is True
