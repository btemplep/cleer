"""Unit tests for the FileStartWhitespaceFormatter."""

from cleer import FileStartWhitespaceFormatter


def test_format_returns_empty_string_for_whitespace():
    formatter = FileStartWhitespaceFormatter()
    result = formatter.format("\n\n  ")

    assert result == ""


def test_format_returns_empty_string_for_newlines():
    formatter = FileStartWhitespaceFormatter()
    result = formatter.format("\n\n\n")

    assert result == ""


def test_format_returns_empty_string_for_tabs():
    formatter = FileStartWhitespaceFormatter()
    result = formatter.format("\t\t")

    assert result == ""


def test_inspect_returns_none_for_empty_string():
    formatter = FileStartWhitespaceFormatter()
    result = formatter.inspect("")

    assert result is None


def test_inspect_returns_message_for_non_empty_string():
    formatter = FileStartWhitespaceFormatter()
    result = formatter.inspect("\n  ")

    assert result is not None
    assert "leading whitespace" in result.lower()


def test_accepts_token_types():
    formatter = FileStartWhitespaceFormatter()

    assert formatter.accepts_token_types == ["file_start_whitespace"]
