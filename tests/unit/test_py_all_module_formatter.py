import pytest

from cleer import PyAllModuleFormatter


def test_inspect_returns_error_when_no_all():
    formatter = PyAllModuleFormatter()
    result = formatter.inspect("import os\n")

    assert result is not None
    assert "__all__" in result


def test_inspect_returns_none_when_all_exists():
    formatter = PyAllModuleFormatter()
    result = formatter.inspect("__all__ = []\n\nimport os\n")

    assert result is None


def test_format_adds_all_when_missing():
    formatter = PyAllModuleFormatter()
    result = formatter.format("import os\n")

    assert "__all__ = []" in result
    assert "import os" in result


def test_format_leaves_all_when_present():
    formatter = PyAllModuleFormatter()
    source = "__all__ = [\"MyClass\"]\n\n\nimport os\n"
    result = formatter.format(source)

    assert result == source


def test_format_adds_all_after_docstring_when_no_all():
    formatter = PyAllModuleFormatter()
    source = '"""Module docstring."""\n\nimport os\n'
    result = formatter.format(source)

    assert result == '"""Module docstring."""\n\n__all__ = []\n\n\nimport os\n'


def test_format_no_trailing_newline_after_all():
    formatter = PyAllModuleFormatter()
    source = "__all__ = []"
    result = formatter.format(source)

    assert result == "__all__ = []\n"


def test_format_multiline_all_ensures_spacing():
    formatter = PyAllModuleFormatter()
    source = '__all__ = [\n    "Thing"\n]\nimport os\n'
    result = formatter.format(source)

    assert '__all__ = [\n    "Thing"\n]\n\n\nimport os\n' == result


def test_format_file_is_only_all_no_trailing_newline():
    formatter = PyAllModuleFormatter()
    source = "__all__ = []"
    result = formatter.format(source)

    assert result == "__all__ = []\n"


def test_format_multiline_all_no_newline_after_bracket():
    formatter = PyAllModuleFormatter()
    source = '__all__ = [\n    "Thing"\n]import os\n'
    result = formatter.format(source)

    assert '__all__ = [\n    "Thing"\n]\n\n\n import os\n' != result
    assert '__all__ = [\n    "Thing"\n]\n\n\nimport os\n' == result


def test_format_docstring_with_wrong_spacing_before_all():
    formatter = PyAllModuleFormatter()
    source = '"""Module docstring."""\n\n\n__all__ = ["Thing"]\n\n\nimport os\n'
    result = formatter.format(source)

    assert result == '"""Module docstring."""\n\n__all__ = ["Thing"]\n\n\nimport os\n'
