"""Unit tests for PyFunctionTokenizer."""

import pytest

from cleer import PyFunctionTokenizer


def test_simple_function():
    tokenizer = PyFunctionTokenizer()
    result = tokenizer.tokenize("def func():\n    pass\n")

    assert result == [
        {
            "token": "def func():\n    pass",
            "index": 0,
            "length": 20
        }
    ]


def test_function_with_decorator():
    tokenizer = PyFunctionTokenizer()
    doc = "@decorator\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "@decorator\ndef func():\n    pass"


def test_function_with_multiple_decorators():
    tokenizer = PyFunctionTokenizer()
    doc = "@first\n@second\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "@first\n@second\ndef func():\n    pass"


def test_async_function():
    tokenizer = PyFunctionTokenizer()
    doc = "async def func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "async def func():\n    pass"


def test_multiline_signature():
    tokenizer = PyFunctionTokenizer()
    doc = "def func(\n    a,\n    b\n):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert "def func(" in result[0]['token']
    assert "pass" in result[0]['token']


def test_multiple_functions():
    tokenizer = PyFunctionTokenizer()
    doc = "def a():\n    pass\n\ndef b():\n    return 1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 2


def test_indented_function():
    tokenizer = PyFunctionTokenizer()
    doc = "class Foo:\n    def method(self):\n        pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "    def method(self):\n        pass"


def test_function_with_multiline_body():
    tokenizer = PyFunctionTokenizer()
    doc = "def func():\n    x = 1\n    y = 2\n    return x + y\n"
    result = tokenizer.tokenize(doc)

    assert "x = 1" in result[0]['token']
    assert "return x + y" in result[0]['token']


def test_nested_function_included_in_parent():
    tokenizer = PyFunctionTokenizer()
    doc = "def outer():\n    def inner():\n        pass\n    return inner\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "def inner" in result[0]['token']


def test_empty_document():
    tokenizer = PyFunctionTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_no_functions():
    tokenizer = PyFunctionTokenizer()
    result = tokenizer.tokenize("x = 1\ny = 2\n")

    assert result == []


def test_decorator_with_multiline_args():
    tokenizer = PyFunctionTokenizer()
    doc = "@decorator(\n    arg1,\n    arg2\n)\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "@decorator(\n    arg1,\n    arg2\n)\ndef func():\n    pass"
    assert result[0]['index'] == 0


def test_decorator_with_blank_line_above():
    tokenizer = PyFunctionTokenizer()
    doc = "x = 1\n\n@decorator\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "@decorator\ndef func():\n    pass"


def test_function_with_no_paren():
    tokenizer = PyFunctionTokenizer()
    doc = "def func:\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_function_with_return_type():
    tokenizer = PyFunctionTokenizer()
    doc = "def func(\n    x\n) -> int:\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_trailing_blank_lines_not_included():
    tokenizer = PyFunctionTokenizer()
    doc = "def func():\n    pass\n\n\nx = 1\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "def func():\n    pass"


def test_function_body_with_blank_lines():
    tokenizer = PyFunctionTokenizer()
    doc = "def func():\n    x = 1\n\n    y = 2\n"
    result = tokenizer.tokenize(doc)

    assert "x = 1" in result[0]['token']
    assert "y = 2" in result[0]['token']


def test_multiline_signature_return_type_next_line():
    tokenizer = PyFunctionTokenizer()
    doc = "def func(\n    x\n)\n-> int:\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "pass" in result[0]['token']


def test_unmatched_paren_in_signature():
    tokenizer = PyFunctionTokenizer()
    doc = "def func(x\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_decorator_with_multiline_paren_args():
    tokenizer = PyFunctionTokenizer()
    doc = "@decorator(arg1, arg2)\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert "@decorator(arg1, arg2)" in result[0]['token']
    assert "pass" in result[0]['token']


def test_decorator_multiline_paren_scan():
    tokenizer = PyFunctionTokenizer()
    doc = "@multi(arg\n@second\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert "@multi(arg" in result[0]['token']
    assert "@second" in result[0]['token']
    assert "pass" in result[0]['token']


def test_decorator_multiline_paren_with_nested():
    tokenizer = PyFunctionTokenizer()
    doc = "@multi(arg(\n    x)\n@second\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert "@multi(arg(" in result[0]['token']


def test_signature_end_return_annotation_next_line_colon_later():
    tokenizer = PyFunctionTokenizer()
    doc = (
        "def my_func(\n"
        "    a, b\n"
        ")\n"
        "-> dict[\n"
        "    str, int\n"
        "]:\n"
        "    pass\n"
    )
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "def my_func" in result[0]['token']
    assert "pass" in result[0]['token']


def test_signature_paren_no_colon_no_arrow():
    """Cover line 67: paren balanced but no colon and no -> on next line."""
    tokenizer = PyFunctionTokenizer()
    doc = "def func(\n    a\n)\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "def func(" in result[0]['token']


def test_non_decorator_at_same_indent_above_def():
    tokenizer = PyFunctionTokenizer()
    doc = "x=1\ndef foo():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == "def foo():\n    pass"
    assert result[0]['index'] == 4


def test_decorator_start_line_is_blank():
    tokenizer = PyFunctionTokenizer()
    doc = "x=1\n\n@dec\ndef foo():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == "@dec\ndef foo():\n    pass"
    assert result[0]['index'] == 5


def test_inner_scan_blank_line_above_paren():
    tokenizer = PyFunctionTokenizer()
    doc = "x(\n\n)\ndef foo():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "def foo" in result[0]['token']


def test_inner_scan_lesser_indent_during_scan():
    tokenizer = PyFunctionTokenizer()
    doc = "class Foo:\n    )\n    def method(self):\n        pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "def method" in result[0]['token']


def test_inner_scan_continues_upward_past_non_paren_line():
    tokenizer = PyFunctionTokenizer()
    doc = "x(\n    y\n)\ndef foo():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "def foo" in result[0]['token']
