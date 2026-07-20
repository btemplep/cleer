import pytest

from cleer import PyClassWhitespaceFormatter


def test_inspect_returns_none_for_correct_spacing():
    formatter = PyClassWhitespaceFormatter()
    result = formatter.inspect("\n\n\n")

    assert result is None


def test_inspect_returns_message_for_single_newline():
    formatter = PyClassWhitespaceFormatter()
    result = formatter.inspect("\n")

    assert result is not None
    assert "2 blank lines" in result


def test_inspect_returns_message_for_too_many_newlines():
    formatter = PyClassWhitespaceFormatter()
    result = formatter.inspect("\n\n\n\n")

    assert result is not None


def test_format_returns_three_newlines():
    formatter = PyClassWhitespaceFormatter()
    result = formatter.format("\n")

    assert result == "\n\n\n"


def test_format_reduces_extra_newlines():
    formatter = PyClassWhitespaceFormatter()
    result = formatter.format("\n\n\n\n\n")

    assert result == "\n\n\n"


def test_format_already_correct():
    formatter = PyClassWhitespaceFormatter()
    result = formatter.format("\n\n\n")

    assert result == "\n\n\n"
