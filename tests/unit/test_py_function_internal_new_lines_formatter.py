import pytest

from cleer import PyFunctionInternalNewLinesFormatter


def test_format_reduces_triple_blank_lines():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    x = 1\n\n\n\n    return x\n"
    result = formatter.format(token)

    assert "\n\n\n" not in result
    assert "    x = 1\n\n    return x\n" in result


def test_format_removes_blank_after_def():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n\n    x = 1\n"
    result = formatter.format(token)

    assert result == "def func():\n    x = 1\n"


def test_format_removes_blank_after_if():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    if x:\n\n        pass\n"
    result = formatter.format(token)

    assert result == "def func():\n    if x:\n        pass\n"


def test_format_removes_blank_after_for():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    for i in range(10):\n\n        pass\n"
    result = formatter.format(token)

    assert result == "def func():\n    for i in range(10):\n        pass\n"


def test_format_removes_blank_after_while():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    while True:\n\n        pass\n"
    result = formatter.format(token)

    assert result == "def func():\n    while True:\n        pass\n"


def test_format_removes_blank_after_else():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    if x:\n        pass\n    else:\n\n        pass\n"
    result = formatter.format(token)

    assert "    else:\n        pass\n" in result


def test_format_removes_blank_after_try():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    try:\n\n        pass\n    except:\n        pass\n"
    result = formatter.format(token)

    assert "    try:\n        pass\n" in result


def test_format_removes_blank_after_except():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    try:\n        pass\n    except:\n\n        pass\n"
    result = formatter.format(token)

    assert "    except:\n        pass\n" in result


def test_format_removes_blank_after_finally():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    try:\n        pass\n    finally:\n\n        pass\n"
    result = formatter.format(token)

    assert "    finally:\n        pass\n" in result


def test_format_removes_blank_after_with():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    with open('f'):\n\n        pass\n"
    result = formatter.format(token)

    assert "    with open('f'):\n        pass\n" in result


def test_format_removes_blank_after_docstring():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    \"\"\"Docstring.\"\"\"\n\n    x = 1\n"
    result = formatter.format(token)

    assert result == "def func():\n    \"\"\"Docstring.\"\"\"\n    x = 1\n"


def test_format_removes_blank_after_multiline_docstring():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    \"\"\"\n    Docstring.\n    \"\"\"\n\n    x = 1\n"
    result = formatter.format(token)

    assert result == "def func():\n    \"\"\"\n    Docstring.\n    \"\"\"\n    x = 1\n"


def test_format_preserves_single_blank_between_statements():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    x = 1\n\n    y = 2\n"
    result = formatter.format(token)

    assert result == token


def test_format_no_change_when_correct():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    x = 1\n    y = 2\n"
    result = formatter.format(token)

    assert result == token


def test_inspect_returns_none_for_correct():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    x = 1\n"
    result = formatter.inspect(token)

    assert result is None


def test_inspect_returns_message_for_issues():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n\n    x = 1\n"
    result = formatter.inspect(token)

    assert result is not None
    assert "functions" in result.lower()


def test_format_async_def_removes_blank_after():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "async def func():\n\n    x = 1\n"
    result = formatter.format(token)

    assert result == "async def func():\n    x = 1\n"


def test_format_removes_blank_after_async_for():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    async for i in gen():\n\n        pass\n"
    result = formatter.format(token)

    assert "    async for i in gen():\n        pass\n" in result


def test_format_removes_blank_after_async_with():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    async with thing():\n\n        pass\n"
    result = formatter.format(token)

    assert "    async with thing():\n        pass\n" in result


def test_format_triple_single_quote_docstring():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    '''Docstring.'''\n\n    x = 1\n"
    result = formatter.format(token)

    assert result == "def func():\n    '''Docstring.'''\n    x = 1\n"


def test_format_multiline_triple_single_quote_docstring():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    '''\n    Docstring.\n    '''\n\n    x = 1\n"
    result = formatter.format(token)

    assert result == "def func():\n    '''\n    Docstring.\n    '''\n    x = 1\n"


def test_format_preserves_content_inside_docstring():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    \"\"\"\n    Line 1.\n\n    Line 2.\n    \"\"\"\n    x = 1\n"
    result = formatter.format(token)

    assert "\n\n    Line 2." in result


def test_format_elif_after_colon():
    formatter = PyFunctionInternalNewLinesFormatter()
    token = "def func():\n    if x:\n        pass\n    elif y:\n\n        pass\n"
    result = formatter.format(token)

    assert "    elif y:\n        pass\n" in result
