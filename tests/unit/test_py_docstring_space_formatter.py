from cleer import PyDocstringSpaceFormatter


def test_inspect_returns_none_for_correct_spacing():
    formatter = PyDocstringSpaceFormatter()
    result = formatter.inspect("\n    ")

    assert result is None


def test_inspect_returns_message_for_extra_blank():
    formatter = PyDocstringSpaceFormatter()
    result = formatter.inspect("\n\n    ")

    assert result is not None
    assert (
        "blank lines" in result.lower()
        or "no blank lines" in result.lower()
    )


def test_inspect_returns_message_for_multiple_blanks():
    formatter = PyDocstringSpaceFormatter()
    result = formatter.inspect("\n\n\n        ")

    assert result is not None


def test_format_removes_extra_blank_line():
    formatter = PyDocstringSpaceFormatter()
    result = formatter.format("\n\n    ")

    assert result == "\n    "


def test_format_removes_multiple_blank_lines():
    formatter = PyDocstringSpaceFormatter()
    result = formatter.format("\n\n\n        ")

    assert result == "\n        "


def test_format_preserves_indentation():
    formatter = PyDocstringSpaceFormatter()
    result = formatter.format("\n\n            ")

    assert result == "\n            "


def test_format_no_indentation():
    formatter = PyDocstringSpaceFormatter()
    result = formatter.format("\n\n")

    assert result == "\n"
