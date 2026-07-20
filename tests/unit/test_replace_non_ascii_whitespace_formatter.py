"""Unit tests for ReplaceNonAsciiWhitespaceFormatter."""

import pytest

from cleer import ReplaceNonAsciiWhitespaceFormatter


def test_inspect_no_non_ascii_whitespace():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.inspect("hello world")

    assert result is None


def test_inspect_non_breaking_space():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.inspect("\u00a0")

    assert result is not None
    assert "non-ascii whitespace" in result.lower()


def test_inspect_em_space():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.inspect("\u2003")

    assert result is not None
    assert "non-ascii whitespace" in result.lower()


def test_inspect_ideographic_space():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.inspect("\u3000")

    assert result is not None
    assert "non-ascii whitespace" in result.lower()


def test_inspect_thin_space():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.inspect("\u2009")

    assert result is not None
    assert "non-ascii whitespace" in result.lower()


def test_inspect_empty_string():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.inspect("")

    assert result is None


def test_inspect_ascii_whitespace_only():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.inspect(" \t\n")

    assert result is None


def test_inspect_regular_unicode_text():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.inspect("café résumé")

    assert result is None


def test_format_single_non_breaking_space():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.format("\u00a0")

    assert result == " "


def test_format_em_space():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.format("\u2003")

    assert result == " "


def test_format_ideographic_space():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.format("\u3000")

    assert result == " "


def test_format_multiple_non_ascii_whitespace():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.format("\u00a0\u2003\u3000")

    assert result == "   "


def test_format_preserves_ascii_whitespace():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.format(" \u00a0\t")

    assert result == "  \t"


def test_format_empty_string():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.format("")

    assert result == ""


def test_format_no_non_ascii_whitespace():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.format("hello world")

    assert result == "hello world"


def test_format_mixed_content():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.format("hello\u00a0world\u2003end")

    assert result == "hello world end"


def test_format_contiguous_sequence():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.format("\u00a0\u00a0\u00a0")

    assert result == "   "


def test_format_preserves_regular_unicode():
    formatter = ReplaceNonAsciiWhitespaceFormatter()
    result = formatter.format("café\u00a0résumé")

    assert result == "café résumé"
