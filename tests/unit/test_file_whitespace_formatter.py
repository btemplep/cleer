import pytest

from cleer import FileWhitespaceFormatter


def test_removes_leading_whitespace():
    formatter = FileWhitespaceFormatter()
    result = formatter.format("\n\n  import os\n")

    assert result == "import os\n"


def test_ensures_single_trailing_newline():
    formatter = FileWhitespaceFormatter()
    result = formatter.format("import os\n\n\n")

    assert result == "import os\n"


def test_ensures_trailing_newline_when_missing():
    formatter = FileWhitespaceFormatter()
    result = formatter.format("import os")

    assert result == "import os\n"


def test_inspect_detects_leading_whitespace():
    formatter = FileWhitespaceFormatter()
    result = formatter.inspect("\nimport os\n")

    assert result is not None
    assert "leading" in result.lower()


def test_inspect_detects_missing_trailing_newline():
    formatter = FileWhitespaceFormatter()
    result = formatter.inspect("import os")

    assert result is not None
    assert "newline" in result.lower()


def test_inspect_detects_extra_trailing_newlines():
    formatter = FileWhitespaceFormatter()
    result = formatter.inspect("import os\n\n")

    assert result is not None


def test_inspect_passes_correct_file():
    formatter = FileWhitespaceFormatter()
    result = formatter.inspect("import os\n")

    assert result is None


def test_format_already_correct():
    formatter = FileWhitespaceFormatter()
    result = formatter.format("import os\n")

    assert result == "import os\n"
