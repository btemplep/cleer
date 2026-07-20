"""Unit tests for PyDecoratorTokenizer."""

import pytest

from cleer import PyDecoratorTokenizer


def test_simple_decorator():
    tokenizer = PyDecoratorTokenizer()
    result = tokenizer.tokenize("@my_decorator\ndef func():\n    pass\n")

    assert result == [
        {
            "token": "@my_decorator",
            "index": 0,
            "length": 13
        }
    ]


def test_decorator_with_args():
    tokenizer = PyDecoratorTokenizer()
    result = tokenizer.tokenize("@app.route('/path')\ndef handler():\n    pass\n")

    assert result == [
        {
            "token": "@app.route('/path')",
            "index": 0,
            "length": 19
        }
    ]


def test_decorator_with_multiline_args():
    tokenizer = PyDecoratorTokenizer()
    doc = "@decorator(\n    arg1,\n    arg2\n)\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "@decorator(\n    arg1,\n    arg2\n)"
    assert result[0]['index'] == 0


def test_multiple_decorators():
    tokenizer = PyDecoratorTokenizer()
    doc = "@first\n@second\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 2
    assert result[0]['token'] == "@first"
    assert result[1]['token'] == "@second"


def test_indented_decorator():
    tokenizer = PyDecoratorTokenizer()
    doc = "class Foo:\n    @staticmethod\n    def method():\n        pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "    @staticmethod"
    assert result[0]['index'] == 11


def test_decorator_with_string_containing_paren():
    tokenizer = PyDecoratorTokenizer()
    doc = "@app.route('/(path)')\ndef handler():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "@app.route('/(path)')"


def test_decorator_with_unmatched_paren():
    tokenizer = PyDecoratorTokenizer()
    doc = "@decorator(arg\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "@decorator(arg"


def test_decorator_no_args_no_newline():
    tokenizer = PyDecoratorTokenizer()
    doc = "@decorator"
    result = tokenizer.tokenize(doc)

    assert result == [
        {
            "token": "@decorator",
            "index": 0,
            "length": 10
        }
    ]


def test_decorator_with_double_quote_string():
    tokenizer = PyDecoratorTokenizer()
    doc = "@app.route(\"path\")\ndef handler():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "@app.route(\"path\")"


def test_decorator_with_nested_parens():
    tokenizer = PyDecoratorTokenizer()
    doc = "@decorator(func(1, 2))\ndef handler():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "@decorator(func(1, 2))"


def test_empty_document():
    tokenizer = PyDecoratorTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_no_decorators():
    tokenizer = PyDecoratorTokenizer()
    result = tokenizer.tokenize("def func():\n    pass\n")

    assert result == []


def test_decorator_with_escape_in_string():
    tokenizer = PyDecoratorTokenizer()
    doc = "@app.route('path\\'s')\ndef handler():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "@app.route('path\\'s')"
