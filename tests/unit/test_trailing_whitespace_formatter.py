"""Unit tests for TrailingWhitespaceFormatter."""

import pytest

from cleer import TrailingWhitespaceFormatter


def test_inspect_no_trailing_whitespace():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.inspect("hello world")

    assert result is None


def test_inspect_trailing_spaces():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.inspect("hello world   ")

    assert result is not None
    assert "trail" in result.lower()


def test_inspect_trailing_tabs():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.inspect("hello world\t\t")

    assert result is not None
    assert "trail" in result.lower()


def test_inspect_trailing_mixed():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.inspect("hello world \t ")

    assert result is not None
    assert "trail" in result.lower()


def test_inspect_empty_string():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.inspect("")

    assert result is None


def test_inspect_only_spaces():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.inspect("   ")

    assert result is not None


def test_inspect_leading_whitespace_only():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.inspect("   hello")

    assert result is None


def test_format_no_trailing_whitespace():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.format("hello world")

    assert result == "hello world"


def test_format_trailing_spaces():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.format("hello world   ")

    assert result == "hello world"


def test_format_trailing_tabs():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.format("hello world\t\t")

    assert result == "hello world"


def test_format_trailing_mixed():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.format("hello world \t ")

    assert result == "hello world"


def test_format_preserves_leading_whitespace():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.format("    hello world   ")

    assert result == "    hello world"


def test_format_empty_string():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.format("")

    assert result == ""


def test_format_only_spaces():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.format("   ")

    assert result == ""


def test_format_preserves_internal_whitespace():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.format("hello   world   ")

    assert result == "hello   world"


def test_format_tab_indented_line():
    formatter = TrailingWhitespaceFormatter()
    result = formatter.format("\thello world\t")

    assert result == "\thello world"
