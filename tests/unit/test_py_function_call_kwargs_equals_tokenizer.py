"""Unit tests for PyFunctionCallKwargsEqualsTokenizer."""

import pytest

from cleer import PyFunctionCallKwargsEqualsTokenizer


def test_simple_kwargs():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(x=1, y=2)\n")

    assert len(result) == 2
    assert result[0]['token'] == "="
    assert result[1]['token'] == "="


def test_kwargs_with_spaces():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(x = 1, y = 2)\n")

    assert len(result) == 2
    assert result[0]['token'] == " = "
    assert result[1]['token'] == " = "


def test_no_kwargs():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(1, 2)\n")

    assert result == []


def test_assignment_not_in_call():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("x = 1\n")

    assert result == []


def test_def_signature_excluded():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x=1):\n    pass\n")

    assert result == []


def test_async_def_signature_excluded():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("async def func(x=1):\n    pass\n")

    assert result == []


def test_method_call():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("obj.method(key=value)\n")

    assert len(result) == 1
    assert result[0]['token'] == "="


def test_nested_function_call():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("outer(inner(x=1))\n")

    assert result == []


def test_skip_single_quote_string():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func('x=1')\n")

    assert result == []


def test_skip_double_quote_string():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(\"x=1\")\n")

    assert result == []


def test_skip_triple_single_quote():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func('''x=1''')\n")

    assert result == []


def test_skip_triple_double_quote():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(\"\"\"x=1\"\"\")\n")

    assert result == []


def test_skip_comment():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("# func(x=1)\nfunc(y=2)\n")

    assert len(result) == 1
    assert result[0]['token'] == "="


def test_comment_without_newline():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("# func(x=1)")

    assert result == []


def test_skip_double_equals():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(x==1)\n")

    assert result == []


def test_skip_not_equals():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(x!=1)\n")

    assert result == []


def test_skip_less_than_equals():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(x<=1)\n")

    assert result == []


def test_skip_greater_than_equals():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(x>=1)\n")

    assert result == []


def test_paren_not_function_call():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("(x=1)\n")

    assert result == []


def test_nested_brackets_in_call():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(x=[1, 2], y={\"a\": 1})\n")

    assert len(result) == 2


def test_empty_document():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_unmatched_paren():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(x=1\n")

    assert result == []


def test_string_with_escape():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(x='a\\'b', y=1)\n")

    assert len(result) == 2


def test_triple_quote_in_matching_paren():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(x='''val''')\n")

    assert len(result) == 1


def test_kwargs_with_tab_spaces():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(x\t=\t1)\n")

    assert len(result) == 1
    assert result[0]['token'] == "\t=\t"


def test_before_equals_is_not_identifier():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    result = tokenizer.tokenize("func(1 = 2)\n")

    assert len(result) == 1
    assert result[0]['token'] == " = "


def test_multiline_call():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    doc = "func(\n    x=1,\n    y=2\n)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 2


def test_single_quote_string_scanning():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    doc = "'string' + func(x=1)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_triple_quote_unterminated_in_inner():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    doc = "func('''unterminated, x=1)\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_nested_paren_depth():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    doc = "func(x=(1+2), y=3)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 2


def test_triple_single_in_find_matching():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    doc = "func('''text''', x=1)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_triple_double_in_find_matching():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    doc = "func(\"\"\"text\"\"\", x=1)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_unterminated_triple_quote_top_level():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    doc = "'''unterminated\nfunc(x=1)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_escape_in_string_top_level():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    doc = "\"a\\\"b\"\nfunc(x=1)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_is_function_call_with_underscore():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    doc = "my_func_(x=1)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_triple_quote_unterminated_in_inner_scan():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    doc = "func('''unterminated)\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_function_call_with_space_before_paren():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    doc = "func (x=1)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "=" in result[0]['token']


def test_triple_quote_string_before_call():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    doc = '"""hello"""\nfunc(x=1)\n'
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "=" in result[0]['token']


def test_unclosed_triple_quote_inside_call_arg():
    tokenizer = PyFunctionCallKwargsEqualsTokenizer()
    doc = "func(x=\"\"\"unterminated)\n"
    result = tokenizer.tokenize(doc)

    assert result == []
