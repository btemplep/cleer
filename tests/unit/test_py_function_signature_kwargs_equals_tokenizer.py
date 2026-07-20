"""Unit tests for PyFunctionSignatureKwargsEqualsTokenizer."""

import pytest

from cleer import PyFunctionSignatureKwargsEqualsTokenizer


def test_simple_default():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x=1):\n    pass\n")

    assert len(result) == 1
    assert result[0]['token'] == "="


def test_default_with_spaces():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x=1):\n    pass\n")

    assert len(result) == 1
    assert result[0]['token'] == "="


def test_multiple_defaults():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x=1, y=2, z=3):\n    pass\n")

    assert len(result) == 3


def test_async_def():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("async def func(x=1):\n    pass\n")

    assert len(result) == 1
    assert result[0]['token'] == "="


def test_no_defaults():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x, y):\n    pass\n")

    assert result == []


def test_no_function():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("x = 1\n")

    assert result == []


def test_skip_double_equals():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x==1):\n    pass\n")

    assert result == []


def test_skip_not_equals():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x!=1):\n    pass\n")

    assert result == []


def test_skip_less_than_equals():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x<=1):\n    pass\n")

    assert result == []


def test_skip_greater_than_equals():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x>=1):\n    pass\n")

    assert result == []


def test_nested_brackets():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x=[1, 2], y={\"a\": 1}):\n    pass\n")

    assert len(result) == 2


def test_string_in_default():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x='hello=world'):\n    pass\n")

    assert len(result) == 1


def test_triple_quote_in_default():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x='''a=b'''):\n    pass\n")

    assert len(result) == 1


def test_triple_double_quote_in_default():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x=\"\"\"a=b\"\"\"):\n    pass\n")

    assert len(result) == 1


def test_unmatched_paren():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x=1\n")

    assert result == []


def test_empty_document():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_multiline_signature():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    doc = "def func(\n    x=1,\n    y=2\n):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 2


def test_default_with_tab_spaces():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x\t=\t1):\n    pass\n")

    assert len(result) == 1
    assert result[0]['token'] == "\t=\t"


def test_escape_in_string():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x='a\\'b=c'):\n    pass\n")

    assert len(result) == 1


def test_triple_quote_unterminated():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x='''unterminated):\n    pass\n")

    assert result == []


def test_nested_parens_in_default():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x=(1+2), y=3):\n    pass\n")

    assert len(result) == 2


def test_find_matching_paren_with_triple_quotes():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x='''val''', y=1):\n    pass\n")

    assert len(result) == 2


def test_find_matching_paren_escape():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    result = tokenizer.tokenize("def func(x='\\\\', y=1):\n    pass\n")

    assert len(result) == 2


def test_multiple_functions():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    doc = "def a(x=1):\n    pass\n\ndef b(y=2):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 2


def test_def_without_paren():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    doc = "def func:\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_unterminated_triple_quote_in_inner():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    doc = "def func(x='''unterminated):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_unclosed_triple_double_quote_in_signature():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    doc = 'def func(x=\"\"\"unterminated):\n    pass\n'
    result = tokenizer.tokenize(doc)

    assert result == []


def test_escaped_char_in_string_default():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    doc = "def func(x='he\\'llo', y=1):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1
    equals_tokens = [t for t in result if "=" in t['token']]
    assert len(equals_tokens) >= 1
