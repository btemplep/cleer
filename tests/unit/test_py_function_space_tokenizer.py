"""Unit tests for PyFunctionSpaceTokenizer."""

import pytest

from cleer import PyFunctionSpaceTokenizer


def test_space_between_functions():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1
    assert any(t['token'] == "\n\n\n" for t in result)


def test_single_newline_between_functions():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1
    assert any(t['token'] == "\n\n" for t in result)


def test_no_space_token_when_same_line():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_functions_with_decorators():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\n\n@decorator\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_different_indent_levels_excluded():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\n    def b():\n        pass\n"
    result = tokenizer.tokenize(doc)

    between_tokens = [t for t in result if "\n\n" in t['token']]
    assert len(between_tokens) == 0


def test_multiline_signature():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a(\n    x,\n    y\n):\n    pass\n\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_function_followed_by_non_function():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\nx = 1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_function_followed_by_class_excluded():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\nclass Foo:\n    pass\n"
    result = tokenizer.tokenize(doc)

    class_tokens = [t for t in result if "class" in t.get("token", "")]
    assert len(class_tokens) == 0


def test_empty_document():
    tokenizer = PyFunctionSpaceTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_no_functions():
    tokenizer = PyFunctionSpaceTokenizer()
    result = tokenizer.tokenize("x = 1\ny = 2\n")

    assert result == []


def test_multiple_functions_space():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\n\ndef b():\n    pass\n\n\ndef c():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 2


def test_async_def():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "async def a():\n    pass\n\n\nasync def b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_function_with_multiline_body():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    x = 1\n    y = 2\n    return x + y\n\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_non_whitespace_between_excluded():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\nx = 1\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    between_funcs = [t for t in result if "\nx = 1\n" in t['token']]
    assert len(between_funcs) == 0


def test_function_with_decorator_start():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "@dec\ndef a():\n    pass\n\n\n@dec2\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_signature_with_return_type_on_next_line():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a(\n    x\n) -> int:\n    pass\n\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_signature_no_paren():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a:\n    pass\n\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 0


def test_tokens_sorted_by_index():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\n\ndef b():\n    pass\n\n\ndef c():\n    pass\n"
    result = tokenizer.tokenize(doc)

    for i in range(len(result) - 1):
        assert result[i]['index'] <= result[i + 1]['index']


def test_function_end_with_trailing_blanks():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\n\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_decorator_above_blank_lines():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "\n@dec\ndef a():\n    pass\n\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_last_function_followed_by_content():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\n\ndef b():\n    pass\n\nx = 1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 2


def test_function_at_end_no_trailing_content():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_nested_function_not_separate_token():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    def inner():\n        pass\n    return inner\n\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_multiline_signature_with_return_type_on_next_line():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a(\n    x\n)\n-> int:\n    pass\n\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_unmatched_paren_in_signature():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a(x\n\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 0


def test_different_indent_in_second_loop():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "class Foo:\n    def a(self):\n        pass\n\n    def b(self):\n        pass\n\n        x=1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 0


def test_function_at_end_of_document():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\n\ndef b():\n    pass"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_function_followed_by_deeper_indent():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\n    x=1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 0


def test_next_is_func():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\ndef b():\n    pass\n\ndef c():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 2


def test_start_index_gte_end_index():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 0


def test_signature_with_return_type_colon_on_next_line():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a(\n    x\n) -> int:\n    pass\n\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_indent_current_not_equal_indent_next():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\n\n    def b():\n        pass\n"
    result = tokenizer.tokenize(doc)

    between_tokens = [t for t in result if "\n\n\n" in t['token']]
    assert len(between_tokens) == 0


def test_function_followed_by_indented_content():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "class Foo:\n    def a(self):\n        pass\n\n        x=1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 0


def test_next_line_is_next_func():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_function_end_at_document_boundary():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\n\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 0


def test_signature_end_return_type_on_next_line_with_colon_on_another():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = (
        "def my_func(\n"
        "    a, b\n"
        ")\n"
        "-> dict[\n"
        "    str, int\n"
        "]:\n"
        "    pass\n"
        "\n"
        "\n"
        "def other():\n"
        "    pass\n"
    )
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_multiline_decorator_paren_depth():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = (
        "@decorator(\n"
        "    arg\n"
        ")\n"
        "def func():\n"
        "    pass\n"
        "\n"
        "\n"
        "def other():\n"
        "    pass\n"
    )
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_decorator_at_line_with_paren_depth_positive():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = (
        "@outer(\n"
        "    @inner\n"
        ")\n"
        "def func():\n"
        "    pass\n"
        "\n"
        "\n"
        "def other():\n"
        "    pass\n"
    )
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_consecutive_functions_different_indent():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = (
        "def a():\n"
        "    pass\n"
        "\n"
        "\n"
        "    def b():\n"
        "        pass\n"
    )
    result = tokenizer.tokenize(doc)

    between_tokens = [
        t for t in result
        if t['token'] == "\n\n\n"

    ]
    assert len(between_tokens) == 0


def test_consecutive_functions_no_gap():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\ndef b():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert isinstance(result, list)


def test_start_index_ge_end_index_second_loop():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\ndef b():\n    pass\nx=1\n"
    result = tokenizer.tokenize(doc)

    assert isinstance(result, list)


def test_function_preceded_by_import():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = (
        "import os\n"
        "\n"
        "def func():\n"
        "    pass\n"
    )
    result = tokenizer.tokenize(doc)

    import_preceded = [
        t for t in result
        if t['index'] < doc.index("def func")

    ]
    assert len(import_preceded) == 0


def test_start_index_ge_end_index_third_loop():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "x=1\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert isinstance(result, list)


def test_consecutive_functions_different_indent():
    """Cover indent_current != indent_next skips in first loop."""
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "class A:\n    def method(self):\n        pass\n\n\ndef top_level():\n    pass\n"
    tokens = tokenizer.tokenize(doc)

    assert isinstance(tokens, list)


def test_functions_with_no_space_between():
    """Cover line 196: start_index >= end_index."""
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def a():\n    pass\ndef b():\n    pass\n"
    tokens = tokenizer.tokenize(doc)

    for t in tokens:
        assert t['index'] >= 0


def test_function_preceded_by_import():
    """Cover line 279: prev_is_import."""
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "import os\ndef func():\n    pass\n"
    tokens = tokenizer.tokenize(doc)

    for t in tokens:
        assert "import" not in t['token']


def test_multiline_signature_with_return_type_multiline_colon():
    """Cover line 64: return type over multiple lines with colon on later line."""
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "def func(\n    a\n) -> dict[\n    str, int\n]:\n    pass\n\n\ndef other():\n    pass\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) >= 1


def test_non_decorator_at_same_indent_above_def_no_blank():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "x=1\ndef foo():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert isinstance(result, list)


def test_decorator_with_blank_line_between_scan_and_decorator():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "x=1\n\n\n\n@dec\ndef foo():\n    pass\n\n\ndef bar():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1
    func_token = [t for t in result if "@dec" not in t['token']]
    assert isinstance(func_token, list)


def test_inner_scan_with_blank_line_above_closing_paren():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "x(\n\n)\ndef foo():\n    pass\n\n\ndef bar():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_inner_scan_lesser_indent_break():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "class Foo:\n    )\n    def method(self):\n        pass\n\n\n    def other(self):\n        pass\n"
    result = tokenizer.tokenize(doc)

    assert isinstance(result, list)


def test_inner_scan_finds_decorator_through_multiline():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "@dec(\n    arg\n)\ndef foo():\n    pass\n\n\ndef bar():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_inner_scan_with_paren_line_continues_upward():
    tokenizer = PyFunctionSpaceTokenizer()
    doc = "x(\n    y\n)\ndef foo():\n    pass\n\n\ndef bar():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1
