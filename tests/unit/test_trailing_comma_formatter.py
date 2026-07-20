import pytest

from cleer import TrailingCommaFormatter


def test_inspect_detects_trailing_comma_before_paren():
    formatter = TrailingCommaFormatter()
    result = formatter.inspect(",\n)")

    assert result is not None
    assert "Trailing comma" in result


def test_inspect_detects_trailing_comma_before_bracket():
    formatter = TrailingCommaFormatter()
    result = formatter.inspect(",\n]")

    assert result is not None


def test_inspect_detects_trailing_comma_before_brace():
    formatter = TrailingCommaFormatter()
    result = formatter.inspect(",\n}")

    assert result is not None


def test_inspect_returns_none_for_normal_comma():
    formatter = TrailingCommaFormatter()
    result = formatter.inspect(", x")

    assert result is None


def test_format_removes_comma_before_close_paren():
    formatter = TrailingCommaFormatter()
    result = formatter.format(",\n)")

    assert result == "\n)"


def test_format_removes_comma_before_close_bracket():
    formatter = TrailingCommaFormatter()
    result = formatter.format(",\n]")

    assert result == "\n]"


def test_format_removes_comma_before_close_brace():
    formatter = TrailingCommaFormatter()
    result = formatter.format(",\n}")

    assert result == "\n}"


def test_format_leaves_normal_comma():
    formatter = TrailingCommaFormatter()
    result = formatter.format(", x")

    assert result == ", x"


def test_format_handles_comma_with_spaces_before_close():
    formatter = TrailingCommaFormatter()
    result = formatter.format(",    )")

    assert result == "    )"


def test_get_next_char_empty_string():
    formatter = TrailingCommaFormatter()
    result = formatter._get_next_char("")

    assert result == ""
