import pytest

from cleer import PyCodeBlockNewLinesFormatter


def test_format_adds_newline_after_if_block():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        pass\n    print(y)\n"
    result = formatter.format(token)

    assert "        pass\n\n    print(y)\n" in result


def test_format_no_extra_newlines_between_if_elif_else():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        pass\n\n\n    elif y:\n        pass\n\n\n    else:\n        pass\n    z = 1\n"
    result = formatter.format(token)

    assert "    if x:\n        pass\n    elif y:" in result
    assert "    elif y:\n        pass\n    else:" in result


def test_format_no_extra_newlines_between_try_except_finally():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    try:\n        pass\n\n\n    except:\n        pass\n\n\n    finally:\n        pass\n    z = 1\n"
    result = formatter.format(token)

    assert "    try:\n        pass\n    except:" in result
    assert "    except:\n        pass\n    finally:" in result


def test_format_adds_newline_after_for_block():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    for i in range(10):\n        pass\n    x = 1\n"
    result = formatter.format(token)

    assert "        pass\n\n    x = 1\n" in result


def test_format_adds_newline_after_while_block():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    while True:\n        pass\n    x = 1\n"
    result = formatter.format(token)

    assert "        pass\n\n    x = 1\n" in result


def test_format_adds_newline_after_with_block():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    with open('f'):\n        pass\n    x = 1\n"
    result = formatter.format(token)

    assert "        pass\n\n    x = 1\n" in result


def test_format_no_change_when_correct():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        pass\n\n    y = 1\n"
    result = formatter.format(token)

    assert result == token


def test_format_removes_extra_newlines_after_block():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        pass\n\n\n    y = 1\n"
    result = formatter.format(token)

    assert "        pass\n\n    y = 1\n" in result


def test_format_nested_if_blocks():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        if y:\n            pass\n    z = 1\n"
    result = formatter.format(token)

    assert "            pass\n\n    z = 1\n" in result


def test_format_leaves_non_block_code_unchanged():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    x = 1\n    y = 2\n"
    result = formatter.format(token)

    assert result == token


def test_inspect_returns_none_for_correct():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        pass\n\n    y = 1\n"
    result = formatter.inspect(token)

    assert result is None


def test_inspect_returns_message_for_issues():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        pass\n    y = 1\n"
    result = formatter.inspect(token)

    assert result is not None
    assert "Code block" in result


def test_format_does_not_modify_blocks_in_nested_func():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def outer():\n    def inner():\n        if x:\n            pass\n        y = 1\n"
    result = formatter.format(token)

    assert "            pass\n\n        y = 1" in result


def test_format_does_not_modify_blocks_in_nested_class():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def outer():\n    class Inner:\n        if x:\n            pass\n        y = 1\n"
    result = formatter.format(token)

    assert "            pass\n\n        y = 1" in result


def test_format_removes_blank_after_block_colon():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n\n        y = 1\n    z = 2\n"
    result = formatter.format(token)

    assert "    if x:\n        y = 1\n" in result


def test_format_handles_except_with_type():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    try:\n        pass\n\n    except ValueError:\n        pass\n    x = 1\n"
    result = formatter.format(token)

    assert "    try:\n        pass\n    except ValueError:" in result


def test_format_if_block_at_function_body_level():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    x = 1\n    if x:\n        pass\n    y = 2\n"
    result = formatter.format(token)

    assert "        pass\n\n    y = 2\n" in result


def test_format_no_newline_needed_at_end_of_function():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        pass\n"
    result = formatter.format(token)

    assert result == token


def test_format_block_followed_by_deeper_indent():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        y = 1\n        if z:\n            pass\n    w = 2\n"
    result = formatter.format(token)

    assert "\n\n    w = 2\n" in result


def test_format_empty_lines_inside_block_before_connected():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    try:\n        x = 1\n\n    except Exception:\n        pass\n    y = 2\n"
    result = formatter.format(token)

    assert "        x = 1\n    except Exception:" in result


def test_is_inside_function_or_class_with_empty_line():
    formatter = PyCodeBlockNewLinesFormatter()
    lines = [
        "def func():",
        "    if x:",
        "        pass",
        "",
        "    y = 1"
    ]
    result = formatter._is_inside_function_or_class(lines, 3)

    assert result is False


def test_is_inside_function_or_class_at_indent_zero():
    formatter = PyCodeBlockNewLinesFormatter()
    lines = [
        "if x:",
        "    pass",
        "y = 1"
    ]
    result = formatter._is_inside_function_or_class(lines, 2)

    assert result is False


def test_is_inside_function_or_class_in_nested_def():
    formatter = PyCodeBlockNewLinesFormatter()
    lines = [
        "def outer():",
        "    def inner():",
        "        if x:",
        "            pass"
    ]
    result = formatter._is_inside_function_or_class(lines, 2)

    assert result is True


def test_is_inside_function_or_class_in_nested_class():
    formatter = PyCodeBlockNewLinesFormatter()
    lines = [
        "def outer():",
        "    class Inner:",
        "        if x:",
        "            pass"
    ]
    result = formatter._is_inside_function_or_class(lines, 2)

    assert result is True


def test_is_inside_function_or_class_not_nested():
    formatter = PyCodeBlockNewLinesFormatter()
    lines = [
        "def outer():",
        "    x = 1",
        "    if y:",
        "        pass"
    ]
    result = formatter._is_inside_function_or_class(lines, 2)

    assert result is False


def test_format_non_function_token_with_nested_def():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "x = 1\ndef inner():\n    if y:\n        pass\n    z = 2\n"
    result = formatter.format(token)

    assert "        pass\n\n    z = 2" in result


def test_format_block_with_blank_lines_at_end_of_block():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        y = 1\n\n\n    z = 2\n"
    result = formatter.format(token)

    assert "        y = 1\n\n    z = 2\n" in result


def test_format_blank_line_inside_block_with_deeper_next():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        y = 1\n\n        z = 2\n    w = 3\n"
    result = formatter.format(token)

    assert "        y = 1\n\n        z = 2" in result


def test_format_block_with_prev_ending_in_colon():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    for i in range(10):\n\n        if i > 5:\n            pass\n    x = 1\n"
    result = formatter.format(token)

    assert "    for i in range(10):\n        if i > 5:" in result


def test_is_inside_function_or_class_non_function_token_with_class():
    formatter = PyCodeBlockNewLinesFormatter()
    lines = [
        "class Foo:",
        "    if x:",
        "        pass"
    ]
    result = formatter._is_inside_function_or_class(lines, 1)

    assert result is True


def test_format_block_at_end_no_following_code():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    x = 1\n    if x:\n        pass\n"
    result = formatter.format(token)

    assert result == token


def test_format_block_with_multiple_blank_lines_between_connected():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        pass\n\n\n    else:\n        pass\n    y = 1\n"
    result = formatter.format(token)

    assert "    if x:\n        pass\n    else:" in result


def test_is_inside_function_or_class_async_def_nested():
    formatter = PyCodeBlockNewLinesFormatter()
    lines = [
        "def outer():",
        "    async def inner():",
        "        if x:",
        "            pass"
    ]
    result = formatter._is_inside_function_or_class(lines, 2)

    assert result is True


def test_format_non_function_token_not_nested():
    formatter = PyCodeBlockNewLinesFormatter()
    lines = [
        "x = 1",
        "    if y:",
        "        pass"
    ]
    result = formatter._is_inside_function_or_class(lines, 1)

    assert result is False


def test_is_inside_function_with_blank_line_before_nested():
    formatter = PyCodeBlockNewLinesFormatter()
    lines = [
        "def outer():",
        "    def inner():",
        "",
        "        if x:",
        "            pass"
    ]
    result = formatter._is_inside_function_or_class(lines, 3)

    assert result is True


def test_is_inside_function_body_not_nested():
    formatter = PyCodeBlockNewLinesFormatter()
    lines = [
        "def outer():",
        "    x = 1",
        "        if y:",
        "            pass"
    ]
    result = formatter._is_inside_function_or_class(lines, 2)

    assert result is False


def test_format_block_with_trailing_blanks_past_end():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    for i in range(10):\n        x = 1\n\n    y = 2\n"
    result = formatter.format(token)

    assert "        x = 1\n\n    y = 2\n" in result


def test_format_if_block_with_blank_before_deeper_code():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        a = 1\n\n        b = 2\n    c = 3\n"
    result = formatter.format(token)

    assert "        a = 1\n\n        b = 2\n" in result


def test_non_function_token_with_blank_line_scanning():
    formatter = PyCodeBlockNewLinesFormatter()
    lines = [
        "class Foo:",
        "",
        "    if x:",
        "        pass"
    ]
    result = formatter._is_inside_function_or_class(lines, 2)

    assert result is True


def test_format_block_with_consecutive_blanks_inside():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    if x:\n        a = 1\n\n\n        b = 2\n    z = 3\n"
    result = formatter.format(token)

    assert "        a = 1\n\n" in result
    assert "        b = 2" in result


def test_empty_line_at_end_of_block_before_block_end():
    formatter = PyCodeBlockNewLinesFormatter()
    token = "def func():\n    for x in items:\n        a = 1\n\n\n    z = 1\n"
    result = formatter.format(token)

    assert "a = 1" in result
    assert "z = 1" in result
