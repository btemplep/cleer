import pytest

from cleer import BinaryOperatorSpaceFormatter


def test_format_adds_spaces_around_equals():
    formatter = BinaryOperatorSpaceFormatter()
    result = formatter.format("=")

    assert result == " = "


def test_format_leaves_correct_spacing_alone():
    formatter = BinaryOperatorSpaceFormatter()
    result = formatter.format(" = ")

    assert result == " = "


def test_format_handles_multi_char_operator():
    formatter = BinaryOperatorSpaceFormatter()
    result = formatter.format("  ==  ")

    assert result == " == "


def test_format_handles_extra_whitespace():
    formatter = BinaryOperatorSpaceFormatter()
    result = formatter.format("   +   ")

    assert result == " + "


def test_format_handles_plus_equals():
    formatter = BinaryOperatorSpaceFormatter()
    result = formatter.format("+=")

    assert result == " += "


def test_format_handles_not_equals():
    formatter = BinaryOperatorSpaceFormatter()
    result = formatter.format("  !=  ")

    assert result == " != "


def test_inspect_returns_none_for_correct_spacing():
    formatter = BinaryOperatorSpaceFormatter()
    result = formatter.inspect(" + ")

    assert result is None


def test_inspect_returns_message_for_no_spaces():
    formatter = BinaryOperatorSpaceFormatter()
    result = formatter.inspect("=")

    assert result is not None
    assert "single space" in result


def test_inspect_returns_message_for_extra_spaces():
    formatter = BinaryOperatorSpaceFormatter()
    result = formatter.inspect("  =  ")

    assert result is not None
