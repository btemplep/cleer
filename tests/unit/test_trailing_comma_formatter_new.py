import pytest

from cleer import TrailingCommaFormatter


def test_removes_comma_before_close_paren():
    formatter = TrailingCommaFormatter()
    result = formatter.format(",\n)")

    assert result == "\n)"
    assert "," not in result


def test_removes_comma_before_close_bracket():
    formatter = TrailingCommaFormatter()
    result = formatter.format(",\n]")

    assert result == "\n]"
    assert "," not in result


def test_leaves_comma_before_normal_char():
    formatter = TrailingCommaFormatter()
    result = formatter.format(", x")

    assert result == ", x"


def test_removes_comma_before_close_brace():
    formatter = TrailingCommaFormatter()
    result = formatter.format(",\n}")

    assert result == "\n}"
    assert "," not in result
