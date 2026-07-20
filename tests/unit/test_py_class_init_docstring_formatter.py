import pytest

from cleer import PyClassInitDocstringFormatter


def test_inspect_detects_init_docstring():
    formatter = PyClassInitDocstringFormatter()
    token = "class Foo:\n    def __init__(self):\n        \"\"\"Init doc.\"\"\"\n        pass\n"
    result = formatter.inspect(token)

    assert result is not None
    assert "__init__" in result


def test_inspect_passes_no_init_docstring():
    formatter = PyClassInitDocstringFormatter()
    token = "class Foo:\n    def __init__(self):\n        pass\n"
    result = formatter.inspect(token)

    assert result is None


def test_inspect_passes_class_without_init():
    formatter = PyClassInitDocstringFormatter()
    token = "class Foo:\n    pass\n"
    result = formatter.inspect(token)

    assert result is None


def test_format_removes_init_docstring():
    formatter = PyClassInitDocstringFormatter()
    token = "class Foo:\n    def __init__(self):\n        \"\"\"Init doc.\"\"\"\n        pass\n"
    result = formatter.format(token)

    assert "\"\"\"Init doc.\"\"\"" not in result
    assert "def __init__(self):" in result
    assert "pass" in result


def test_format_removes_multiline_init_docstring():
    formatter = PyClassInitDocstringFormatter()
    token = "class Foo:\n    def __init__(self):\n        \"\"\"Init doc.\n\n        More info.\n        \"\"\"\n        pass\n"
    result = formatter.format(token)

    assert "Init doc." not in result
    assert "pass" in result


def test_format_removes_single_quote_docstring():
    formatter = PyClassInitDocstringFormatter()
    token = "class Foo:\n    def __init__(self):\n        '''Init doc.'''\n        pass\n"
    result = formatter.format(token)

    assert "'''Init doc.'''" not in result


def test_format_leaves_non_init_docstrings():
    formatter = PyClassInitDocstringFormatter()
    token = "class Foo:\n    \"\"\"Class doc.\"\"\"\n    def __init__(self):\n        pass\n"
    result = formatter.format(token)

    assert "\"\"\"Class doc.\"\"\"" in result


def test_format_no_change_when_no_init_docstring():
    formatter = PyClassInitDocstringFormatter()
    token = "class Foo:\n    def __init__(self):\n        pass\n"
    result = formatter.format(token)

    assert result == token


def test_format_handles_init_with_args():
    formatter = PyClassInitDocstringFormatter()
    token = "class Foo:\n    def __init__(self, a, b):\n        \"\"\"Init.\"\"\"\n        self.a = a\n"
    result = formatter.format(token)

    assert "\"\"\"Init.\"\"\"" not in result
    assert "self.a = a" in result
