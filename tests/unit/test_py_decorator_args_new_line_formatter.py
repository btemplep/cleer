import pytest

from cleer import PyDecoratorArgsNewLineFormatter


def test_format_splits_3_args_to_multiple_lines():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@my_decorator(arg1, arg2, arg3)")

    assert "@my_decorator(\n" in result
    assert "    arg1," in result
    assert "    arg2," in result
    assert "    arg3" in result
    assert result.endswith(")")


def test_format_leaves_2_args_alone():
    formatter = PyDecoratorArgsNewLineFormatter()
    token = "@my_decorator(arg1, arg2)"
    result = formatter.format(token)

    assert result == token


def test_format_leaves_1_arg_alone():
    formatter = PyDecoratorArgsNewLineFormatter()
    token = "@my_decorator(arg1)"
    result = formatter.format(token)

    assert result == token


def test_format_no_parens_returns_unchanged():
    formatter = PyDecoratorArgsNewLineFormatter()
    token = "@my_decorator"
    result = formatter.format(token)

    assert result == token


def test_format_preserves_indent():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("    @my_decorator(arg1, arg2, arg3)")

    assert result.startswith("    @my_decorator(\n")
    assert "        arg1," in result


def test_format_handles_keyword_args():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(a=1, b=2, c=3)")

    assert "    a=1," in result
    assert "    b=2," in result
    assert "    c=3" in result


def test_format_handles_nested_parens():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(a, func(1, 2), c)")

    assert "    a," in result
    assert "    func(1, 2)," in result
    assert "    c" in result


def test_format_handles_string_args():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(\"a\", \"b\", \"c\")")

    assert "    \"a\"," in result
    assert "    \"b\"," in result
    assert "    \"c\"" in result


def test_format_handles_string_with_comma():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(\"a,b\", \"c\", \"d\")")

    assert "    \"a,b\"," in result
    assert "    \"c\"," in result
    assert "    \"d\"" in result


def test_inspect_returns_none_for_2_args():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.inspect("@my_decorator(arg1, arg2)")

    assert result is None


def test_inspect_returns_message_for_3_args():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.inspect("@my_decorator(arg1, arg2, arg3)")

    assert result is not None
    assert "more than 2" in result


def test_inspect_returns_none_for_no_args():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.inspect("@my_decorator")

    assert result is None


def test_format_unmatched_paren_returns_unchanged():
    formatter = PyDecoratorArgsNewLineFormatter()
    token = "@dec(arg1, arg2, arg3"
    result = formatter.format(token)

    assert result == token


def test_format_handles_single_quote_in_arg():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec('a', 'b', 'c')")

    assert "    'a'," in result
    assert "    'b'," in result
    assert "    'c'" in result


def test_format_handles_nested_brackets():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec([1, 2], {3: 4}, (5, 6))")

    assert "    [1, 2]," in result
    assert "    {3: 4}," in result
    assert "    (5, 6)" in result


def test_format_handles_escape_in_string():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(\"ab\", \"cd\", \"ef\")")

    assert "    \"ab\"," in result
    assert "    \"cd\"," in result
    assert "    \"ef\"" in result


def test_format_suffix_after_paren():
    formatter = PyDecoratorArgsNewLineFormatter()
    token = "@dec(a, b, c)  # comment"
    result = formatter.format(token)

    assert result.endswith(")  # comment")


def test_format_handles_escape_in_single_quote():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(\"some\\nthing\", \"b\", \"c\")")

    assert "    \"some\\nthing\"," in result
    assert "    \"b\"," in result
    assert "    \"c\"" in result


def test_format_handles_escape_in_double_quote():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(\"a\\\\b\", \"c\", \"d\")")

    assert "    \"a\\\\b\"," in result
    assert "    \"c\"," in result
