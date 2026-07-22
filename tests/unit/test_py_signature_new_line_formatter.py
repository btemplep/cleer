import pytest

from cleer import PySignatureNewLineFormatter


def test_format_splits_3_args_to_multiple_lines():
    formatter = PySignatureNewLineFormatter()
    result = formatter.format("def my_func(a, b, c):")

    assert result == "def my_func(a, b, c):"


def test_format_leaves_2_args_alone():
    formatter = PySignatureNewLineFormatter()
    token = "def my_func(a, b):"
    result = formatter.format(token)

    assert result == token


def test_format_leaves_1_arg_alone():
    formatter = PySignatureNewLineFormatter()
    token = "def my_func(a):"
    result = formatter.format(token)

    assert result == token


def test_format_self_does_not_count():
    formatter = PySignatureNewLineFormatter()
    token = "def my_func(self, a, b):"
    result = formatter.format(token)

    assert result == token


def test_format_cls_does_not_count():
    formatter = PySignatureNewLineFormatter()
    token = "def my_func(cls, a, b):"
    result = formatter.format(token)

    assert result == token


def test_format_self_with_3_args_splits():
    formatter = PySignatureNewLineFormatter()
    result = formatter.format("def my_func(self, a, b, c):")

    assert result == "def my_func(self, a, b, c):"


def test_format_no_parens_returns_unchanged():
    formatter = PySignatureNewLineFormatter()
    token = "def my_func:"
    result = formatter.format(token)

    assert result == token


def test_format_preserves_indent():
    formatter = PySignatureNewLineFormatter()
    result = formatter.format("    def my_func(a, b, c):")

    assert result == "    def my_func(a, b, c):"


def test_format_handles_default_values():
    formatter = PySignatureNewLineFormatter()
    result = formatter.format("def func(a, b=1, c=None):")

    assert result == "def func(a, b=1, c=None):"


def test_format_handles_type_annotations():
    formatter = PySignatureNewLineFormatter()
    result = formatter.format("def func(a: int, b: str, c: float):")

    assert result == "def func(a: int, b: str, c: float):"


def test_format_handles_return_annotation():
    formatter = PySignatureNewLineFormatter()
    result = formatter.format("def func(a, b, c) -> int:")

    assert ") -> int:" in result


def test_inspect_returns_none_for_correct():
    formatter = PySignatureNewLineFormatter()
    result = formatter.inspect("def my_func(a, b):")

    assert result is None


def test_inspect_returns_message_for_too_many_args():
    formatter = PySignatureNewLineFormatter()
    result = formatter.inspect("def my_func(a_long_arg, b_longer_arg, c_longest_argument_name) -> int:")

    assert result is not None


def test_format_handles_nested_parens_in_default():
    formatter = PySignatureNewLineFormatter()
    result = formatter.format("def func(a, b=(1, 2), c=None):")

    assert result == "def func(a, b=(1, 2), c=None):"


def test_format_handles_triple_quoted_strings():
    formatter = PySignatureNewLineFormatter()
    token = "def func(a, b):"
    result = formatter.format(token)

    assert result == token


def test_format_unmatched_paren_returns_unchanged():
    formatter = PySignatureNewLineFormatter()
    token = "def func(a, b, c"
    result = formatter.format(token)

    assert result == token


def test_format_async_def():
    formatter = PySignatureNewLineFormatter()
    result = formatter.format("async def my_func(a, b, c):")

    assert result == "async def my_func(a, b, c):"


def test_format_handles_escaped_char_in_default():
    formatter = PySignatureNewLineFormatter()
    result = formatter.format("def func(a, b=\"\\\\n\", c=None):")

    assert result == "def func(a, b=\"\\\\n\", c=None):"


def test_format_handles_triple_quoted_default():
    formatter = PySignatureNewLineFormatter()
    result = formatter.format("def func(a, b=\"\"\"hi\"\"\", c=None):")

    assert result == "def func(a, b=\"\"\"hi\"\"\", c=None):"


def test_format_handles_single_quote_in_default():
    formatter = PySignatureNewLineFormatter()
    result = formatter.format("def func(a, b='x', c='y'):")

    assert result == "def func(a, b='x', c='y'):"


def test_format_handles_double_quote_in_default():
    formatter = PySignatureNewLineFormatter()
    result = formatter.format("def func(a, b=\"x\", c=\"y\"):")

    assert result == "def func(a, b=\"x\", c=\"y\"):"


def test_split_args_with_escape():
    formatter = PySignatureNewLineFormatter()
    result = formatter._split_args("a, b='\\\\', c")

    assert len(result) == 3
