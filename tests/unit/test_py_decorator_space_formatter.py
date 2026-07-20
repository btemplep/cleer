import pytest

from cleer import PyDecoratorSpaceFormatter


def test_inspect_returns_none_for_single_newline():
    formatter = PyDecoratorSpaceFormatter()
    result = formatter.inspect("\n")

    assert result is None


def test_inspect_returns_message_for_double_newline():
    formatter = PyDecoratorSpaceFormatter()
    result = formatter.inspect("\n\n")

    assert result is not None
    assert "blank lines" in result


def test_inspect_returns_message_for_multiple_newlines():
    formatter = PyDecoratorSpaceFormatter()
    result = formatter.inspect("\n\n\n")

    assert result is not None


def test_format_reduces_double_newline():
    formatter = PyDecoratorSpaceFormatter()
    result = formatter.format("\n\n")

    assert result == "\n"


def test_format_reduces_multiple_newlines():
    formatter = PyDecoratorSpaceFormatter()
    result = formatter.format("\n\n\n\n")

    assert result == "\n"


def test_format_preserves_single_newline():
    formatter = PyDecoratorSpaceFormatter()
    result = formatter.format("\n")

    assert result == "\n"
