"""Unit tests for the FileEndWhitespaceFormatter."""

from cleer import FileEndWhitespaceFormatter


def test_format_returns_newline_for_multiple_newlines():
    formatter = FileEndWhitespaceFormatter()
    result = formatter.format("\n\n\n")

    assert result == "\n"


def test_format_returns_newline_for_empty_string():
    formatter = FileEndWhitespaceFormatter()
    result = formatter.format("")

    assert result == "\n"


def test_format_returns_newline_for_spaces():
    formatter = FileEndWhitespaceFormatter()
    result = formatter.format("   \n")

    assert result == "\n"


def test_inspect_returns_none_for_single_newline():
    formatter = FileEndWhitespaceFormatter()
    result = formatter.inspect("\n")

    assert result is None


def test_inspect_returns_message_for_empty_string():
    formatter = FileEndWhitespaceFormatter()
    result = formatter.inspect("")

    assert result is not None
    assert "trailing newline" in result.lower()


def test_inspect_returns_message_for_multiple_newlines():
    formatter = FileEndWhitespaceFormatter()
    result = formatter.inspect("\n\n")

    assert result is not None
    assert "trailing newline" in result.lower()


def test_accepts_token_types():
    formatter = FileEndWhitespaceFormatter()

    assert formatter.accepts_token_types == ["file_end_whitespace"]
