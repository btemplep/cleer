import pytest

from cleer import CommaSpaceFormatter


def test_format_adds_space_after_comma():
    formatter = CommaSpaceFormatter()
    result = formatter.format(",")

    assert result == ", "


def test_format_removes_space_before_comma():
    formatter = CommaSpaceFormatter()
    result = formatter.format(" ,")

    assert result == ", "


def test_format_preserves_newline_after_comma():
    formatter = CommaSpaceFormatter()
    result = formatter.format(",\n    ")

    assert result == ",\n    "


def test_format_removes_space_before_comma_with_newline():
    formatter = CommaSpaceFormatter()
    result = formatter.format(" ,\n    ")

    assert result == ",\n    "


def test_format_leaves_correct_spacing():
    formatter = CommaSpaceFormatter()
    result = formatter.format(", ")

    assert result == ", "


def test_inspect_returns_none_for_correct():
    formatter = CommaSpaceFormatter()
    result = formatter.inspect(", ")

    assert result is None


def test_inspect_returns_message_for_no_space():
    formatter = CommaSpaceFormatter()
    result = formatter.inspect(",")

    assert result is not None
    assert "space" in result.lower()


def test_inspect_returns_message_for_space_before():
    formatter = CommaSpaceFormatter()
    result = formatter.inspect(" ,")

    assert result is not None


def test_format_with_extra_spaces_before_newline():
    formatter = CommaSpaceFormatter()
    result = formatter.format(",   \n    ")

    assert result == ",\n    "
