import pytest

from cleer import PyImportSectionSpaceFormatter


def test_inspect_returns_none_for_correct():
    formatter = PyImportSectionSpaceFormatter()
    result = formatter.inspect("\n\n\n")

    assert result is None


def test_inspect_returns_message_for_single_newline():
    formatter = PyImportSectionSpaceFormatter()
    result = formatter.inspect("\n")

    assert result is not None
    assert "2 blank lines" in result


def test_inspect_returns_message_for_double_newline():
    formatter = PyImportSectionSpaceFormatter()
    result = formatter.inspect("\n\n")

    assert result is not None
    assert "2 blank lines" in result


def test_inspect_returns_message_for_too_many():
    formatter = PyImportSectionSpaceFormatter()
    result = formatter.inspect("\n\n\n\n")

    assert result is not None
    assert "2 blank lines" in result


def test_format_single_newline():
    formatter = PyImportSectionSpaceFormatter()
    result = formatter.format("\n")

    assert result == "\n\n\n"


def test_format_double_newline():
    formatter = PyImportSectionSpaceFormatter()
    result = formatter.format("\n\n")

    assert result == "\n\n\n"


def test_format_too_many_newlines():
    formatter = PyImportSectionSpaceFormatter()
    result = formatter.format("\n\n\n\n\n")

    assert result == "\n\n\n"


def test_format_already_correct():
    formatter = PyImportSectionSpaceFormatter()
    result = formatter.format("\n\n\n")

    assert result == "\n\n\n"
