import pytest

from cleer import PyReturnYieldNewLineFormatter


def test_format_adds_newline_before_return_with_preceding_statement():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n    x = 1\n    return x\n"
    result = formatter.format(token)

    assert "    x = 1\n\n    return x\n" in result


def test_format_no_newline_when_return_is_only_statement():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n    return 1\n"
    result = formatter.format(token)

    assert result == token


def test_format_removes_blank_line_before_only_return():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n\n    return 1\n"
    result = formatter.format(token)

    assert result == "def func():\n    return 1\n"


def test_format_adds_newline_before_yield_with_preceding_statement():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def gen():\n    x = 1\n    yield x\n"
    result = formatter.format(token)

    assert "    x = 1\n\n    yield x\n" in result


def test_format_adds_newline_after_yield_with_following_statement():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def gen():\n    x = 1\n    yield x\n    y = 2\n"
    result = formatter.format(token)

    assert "    yield x\n\n    y = 2\n" in result


def test_format_no_newline_when_yield_is_only_statement():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def gen():\n    yield 1\n"
    result = formatter.format(token)

    assert result == token


def test_format_preserves_already_correct():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n    x = 1\n\n    return x\n"
    result = formatter.format(token)

    assert result == token


def test_inspect_returns_none_for_correct():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n    x = 1\n\n    return x\n"
    result = formatter.inspect(token)

    assert result is None


def test_inspect_returns_message_for_missing_newline():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n    x = 1\n    return x\n"
    result = formatter.inspect(token)

    assert result is not None
    assert "Return/yield" in result


def test_format_nested_return():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n    if x:\n        return 1\n"
    result = formatter.format(token)

    assert result == token


def test_format_return_after_if_block_no_blank_when_no_prev_same_indent():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n    x = 1\n    if x:\n        y = 1\n    return y\n"
    result = formatter.format(token)

    assert result == "def func():\n    x = 1\n    if x:\n        y = 1\n\n    return y\n"


def test_format_multiple_returns():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n    if x:\n        a = 1\n        return a\n    b = 2\n    return b\n"
    result = formatter.format(token)

    assert "        a = 1\n\n        return a\n" in result
    assert "    b = 2\n\n    return b\n" in result


def test_format_yield_between_statements():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def gen():\n    x = 1\n    yield x\n    y = 2\n    yield y\n"
    result = formatter.format(token)

    assert "    x = 1\n\n    yield x\n\n    y = 2\n\n    yield y\n" in result


def test_format_return_none():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n    x = 1\n    return\n"
    result = formatter.format(token)

    assert "    x = 1\n\n    return\n" in result


def test_format_yield_none():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def gen():\n    x = 1\n    yield\n"
    result = formatter.format(token)

    assert "    x = 1\n\n    yield\n" in result


def test_is_return_or_yield_return():
    formatter = PyReturnYieldNewLineFormatter()

    assert formatter._is_return_or_yield("    return x") is True
    assert formatter._is_return_or_yield("    return") is True


def test_is_return_or_yield_yield():
    formatter = PyReturnYieldNewLineFormatter()

    assert formatter._is_return_or_yield("    yield x") is True
    assert formatter._is_return_or_yield("    yield") is True


def test_is_return_or_yield_false():
    formatter = PyReturnYieldNewLineFormatter()

    assert formatter._is_return_or_yield("    x = return_val") is False
    assert formatter._is_return_or_yield("    yielding = True") is False


def test_format_preserves_no_newline_for_single_yield():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def gen():\n    yield 1\n"
    result = formatter.format(token)

    assert result == "def gen():\n    yield 1\n"


def test_format_removes_extra_blank_before_only_return():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n\n\n    return 1\n"
    result = formatter.format(token)

    assert result == "def func():\n    return 1\n"


def test_get_block_indent_non_empty_line():
    formatter = PyReturnYieldNewLineFormatter()
    lines = [
        "def func():",
        "    return 1"
    ]
    result = formatter._get_block_indent(lines, 1)

    assert result == 4


def test_get_block_indent_empty_line():
    formatter = PyReturnYieldNewLineFormatter()
    lines = [
        "def func():",
        "",
        "    return 1"
    ]
    result = formatter._get_block_indent(lines, 1)

    assert result == 0


def test_is_only_statement_with_next_at_same_indent():
    formatter = PyReturnYieldNewLineFormatter()
    lines = [
        "def func():",
        "    yield 1",
        "    x = 2"
    ]
    result = formatter._is_only_statement_in_block(lines, 1)

    assert result is False


def test_format_yield_not_only_with_next_statement():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def gen():\n    yield 1\n    yield 2\n"
    result = formatter.format(token)

    assert "    yield 1\n\n    yield 2\n" in result


def test_is_only_statement_with_next_deeper_indent():
    formatter = PyReturnYieldNewLineFormatter()
    lines = [
        "def func():",
        "    if x:",
        "        return 1",
        "    y = 2"
    ]
    result = formatter._is_only_statement_in_block(lines, 2)

    assert result is True


def test_is_only_statement_with_oneline_docstring_before_return():
    formatter = PyReturnYieldNewLineFormatter()
    token = 'def func():\n    """Doc."""\n    return 1\n'
    result = formatter.format(token)

    assert result == 'def func():\n    """Doc."""\n    return 1\n'


def test_is_only_statement_with_oneline_single_quote_docstring_before_return():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n    '''Doc.'''\n    return 1\n"
    result = formatter.format(token)

    assert result == "def func():\n    '''Doc.'''\n    return 1\n"


def test_is_only_statement_with_multiline_docstring_before_return():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n    \"\"\"\n    Multi-line doc.\n    \"\"\"\n    return 1\n"
    result = formatter.format(token)

    assert result == "def func():\n    \"\"\"\n    Multi-line doc.\n    \"\"\"\n    return 1\n"


def test_is_only_statement_with_multiline_single_quote_docstring_before_return():
    formatter = PyReturnYieldNewLineFormatter()
    token = "def func():\n    '''\n    Multi-line doc.\n    '''\n    return 1\n"
    result = formatter.format(token)

    assert result == "def func():\n    '''\n    Multi-line doc.\n    '''\n    return 1\n"
