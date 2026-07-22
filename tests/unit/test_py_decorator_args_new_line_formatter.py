import pytest

from cleer import PyDecoratorArgsNewLineFormatter


def test_format_splits_3_args_to_multiple_lines():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@my_decorator(arg1, arg2, arg3)")

    assert result == "@my_decorator(arg1, arg2, arg3)"


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

    assert result == "    @my_decorator(arg1, arg2, arg3)"


def test_format_handles_keyword_args():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(a=1, b=2, c=3)")

    assert result == "@dec(a=1, b=2, c=3)"


def test_format_handles_nested_parens():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(a, func(1, 2), c)")

    assert result == "@dec(a, func(1, 2), c)"


def test_format_handles_string_args():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(\"a\", \"b\", \"c\")")

    assert result == "@dec(\"a\", \"b\", \"c\")"


def test_format_handles_string_with_comma():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(\"a,b\", \"c\", \"d\")")

    assert result == "@dec(\"a,b\", \"c\", \"d\")"


def test_inspect_returns_none_for_2_args():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.inspect("@my_decorator(arg1, arg2)")

    assert result is None


def test_inspect_returns_message_for_3_args():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.inspect("@my_decorator(arg1_long_name, arg2_long_name, arg3_long_name_here)")

    assert result is not None


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

    assert result == "@dec('a', 'b', 'c')"


def test_format_handles_nested_brackets():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec([1, 2], {3: 4}, (5, 6))")

    assert result == "@dec([1, 2], {3: 4}, (5, 6))"


def test_format_handles_escape_in_string():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(\"ab\", \"cd\", \"ef\")")

    assert result == "@dec(\"ab\", \"cd\", \"ef\")"


def test_format_suffix_after_paren():
    formatter = PyDecoratorArgsNewLineFormatter()
    token = "@dec(a, b, c)  # comment"
    result = formatter.format(token)

    assert result == "@dec(a, b, c)  # comment"


def test_format_handles_escape_in_single_quote():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(\"some\\nthing\", \"b\", \"c\")")

    assert result == "@dec(\"some\\nthing\", \"b\", \"c\")"


def test_format_handles_escape_in_double_quote():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@dec(\"a\\\\b\", \"c\", \"d\")")

    assert result == "@dec(\"a\\\\b\", \"c\", \"d\")"


def test_format_expands_long_decorator():
    formatter = PyDecoratorArgsNewLineFormatter()
    result = formatter.format("@my_decorator(first_long_argument, second_long_argument, third_long_argument)")

    assert "@my_decorator(\n" in result
    assert "    first_long_argument," in result
    assert "    second_long_argument," in result
    assert "    third_long_argument" in result
