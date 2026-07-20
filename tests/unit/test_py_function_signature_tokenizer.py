"""Unit tests for PyFunctionSignatureTokenizer."""

import pytest

from cleer import PyFunctionSignatureTokenizer


def test_simple_signature():
    tokenizer = PyFunctionSignatureTokenizer()
    result = tokenizer.tokenize("def my_func(a, b, c):\n    pass\n")

    assert result == [
        {
            "token": "def my_func(a, b, c):",
            "index": 0,
            "length": 21
        }
    ]


def test_async_signature():
    tokenizer = PyFunctionSignatureTokenizer()
    result = tokenizer.tokenize("async def my_func(a):\n    pass\n")

    assert result[0]['token'] == "async def my_func(a):"


def test_signature_with_return_type():
    tokenizer = PyFunctionSignatureTokenizer()
    result = tokenizer.tokenize("def my_func(a) -> int:\n    pass\n")

    assert result[0]['token'] == "def my_func(a) -> int:"


def test_multiline_signature():
    tokenizer = PyFunctionSignatureTokenizer()
    doc = "def func(\n    a,\n    b\n):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "def func(\n    a,\n    b\n):"


def test_no_paren():
    tokenizer = PyFunctionSignatureTokenizer()
    result = tokenizer.tokenize("def func:\n    pass\n")

    assert result == []


def test_unmatched_paren():
    tokenizer = PyFunctionSignatureTokenizer()
    result = tokenizer.tokenize("def func(a, b\n    pass\n")

    assert result == []


def test_indented_function():
    tokenizer = PyFunctionSignatureTokenizer()
    doc = "class Foo:\n    def method(self):\n        pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "    def method(self):"
    assert result[0]['index'] == 11


def test_multiple_functions():
    tokenizer = PyFunctionSignatureTokenizer()
    doc = "def a(x):\n    pass\n\ndef b(y):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 2
    assert result[0]['token'] == "def a(x):"
    assert result[1]['token'] == "def b(y):"


def test_empty_document():
    tokenizer = PyFunctionSignatureTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_no_functions():
    tokenizer = PyFunctionSignatureTokenizer()
    result = tokenizer.tokenize("x = 1\ny = 2\n")

    assert result == []


def test_string_in_signature():
    tokenizer = PyFunctionSignatureTokenizer()
    doc = "def func(x='hello'):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "def func(x='hello'):"


def test_triple_quote_in_signature():
    tokenizer = PyFunctionSignatureTokenizer()
    doc = "def func(x='''val'''):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "def func(x='''val'''):"


def test_nested_parens():
    tokenizer = PyFunctionSignatureTokenizer()
    doc = "def func(x=(1, 2)):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "def func(x=(1, 2)):"


def test_colon_not_immediately_after_paren():
    tokenizer = PyFunctionSignatureTokenizer()
    doc = "def func(a) -> str:\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "def func(a) -> str:"


def test_escape_in_string_param():
    tokenizer = PyFunctionSignatureTokenizer()
    doc = "def func(x=\"a\\\"b\"):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "def func(x=\"a\\\"b\"):"
