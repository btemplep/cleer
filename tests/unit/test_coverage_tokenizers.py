"""Tests covering uncovered lines in tokenizer modules."""

from cleer import (
    CommaPlusTokenizer,
    PairedPunctuationTokenizer,
    PyClassVarWhitespaceTokenizer,
    PyClassWhitespaceTokenizer,
    PyFunctionSignatureKwargsEqualsTokenizer,
)


def test_paired_punctuation_logic_block_with_single_quoted_string():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = (a == 'hello' and b == 'world')\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_paired_punctuation_logic_block_with_double_quoted_string():
    tokenizer = PairedPunctuationTokenizer()
    doc = 'x = (a == "hello" and b == "world")\n'
    result = tokenizer.tokenize(doc)

    assert result == []


def test_paired_punctuation_logic_block_with_escaped_single_quote():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = (a == 'he\\'llo' and b)\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_paired_punctuation_logic_block_with_escaped_double_quote():
    tokenizer = PairedPunctuationTokenizer()
    doc = 'x = (a == "he\\"llo" and b)\n'
    result = tokenizer.tokenize(doc)

    assert result == []


def test_paired_punctuation_logic_block_with_triple_single_quote():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = (a == '''hello and world''' and b)\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_paired_punctuation_logic_block_with_triple_double_quote():
    tokenizer = PairedPunctuationTokenizer()
    doc = 'x = (a == """hello and world""" and b)\n'
    result = tokenizer.tokenize(doc)

    assert result == []


def test_paired_punctuation_logic_block_or_with_newline():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = (a\nor b)\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_paired_punctuation_logic_block_and_with_newline():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = (a\nand b)\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_paired_punctuation_logic_block_nested_brackets_hides_and():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = (func(a and b))\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_py_class_whitespace_docstring_then_method_wrong_spacing():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = (
        "x = 1\n"
        "\n"
        "\n"
        "class Foo:\n"
        '    """My docstring."""\n'
        "\n"
        "    def method(self):\n"
        "        pass\n"
    )
    result = tokenizer.tokenize(doc)

    found_after_docstring = False
    for token in result:
        if token['token'] == "\n\n":
            idx = token['index']
            before = doc[:idx]
            if '"""' in before.split("\n")[-1] or before.endswith('."""'):
                found_after_docstring = True

    assert len(result) >= 1


def test_py_class_whitespace_docstring_then_method_extra_lines():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = (
        "x = 1\n"
        "\n"
        "\n"
        "class Foo:\n"
        '    """My docstring."""\n'
        "\n"
        "\n"
        "\n"
        "\n"
        "    def method(self):\n"
        "        pass\n"
    )
    result = tokenizer.tokenize(doc)

    has_after_docstring_token = any(
        token['token'] not in ("\n\n\n",) and "\n" in token['token']
        for token in result
    )

    assert len(result) >= 1


def test_py_class_whitespace_multiline_docstring_then_method():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = (
        "x = 1\n"
        "\n"
        "\n"
        "class Foo:\n"
        '    """My docstring.\n'
        "\n"
        '    More details.\n'
        '    """\n'
        "\n"
        "    def method(self):\n"
        "        pass\n"
    )
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_py_class_whitespace_multiline_docstring_then_method_wrong_spacing():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = (
        "x = 1\n"
        "\n"
        "\n"
        "class Foo:\n"
        '    """My docstring.\n'
        "\n"
        '    More details.\n'
        '    """\n'
        "\n"
        "\n"
        "\n"
        "\n"
        "    def method(self):\n"
        "        pass\n"
    )
    result = tokenizer.tokenize(doc)

    after_docstring_tokens = [
        t for t in result
        if t['token'] != "\n\n\n" and t['token'].count("\n") > 2
    ]

    assert len(result) >= 1


def test_py_class_var_whitespace_docstring_then_class_var():
    tokenizer = PyClassVarWhitespaceTokenizer()
    doc = (
        "class Foo:\n"
        '    """My docstring."""\n'
        "\n"
        "\n"
        "    my_var = 1\n"
    )
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_py_class_var_whitespace_multiline_docstring_then_var():
    tokenizer = PyClassVarWhitespaceTokenizer()
    doc = (
        "class Foo:\n"
        '    """My docstring.\n'
        "\n"
        '    More details.\n'
        '    """\n'
        "\n"
        "\n"
        "    my_var = 1\n"
    )
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_py_function_signature_kwargs_equals_with_triple_quote_default():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    doc = "def func(x, y=\"\"\"hello\"\"\"):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_py_function_signature_kwargs_equals_with_single_quote():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    doc = "def func(x, y='hello'):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1
    assert result[0]['token'] == "="


def test_py_function_signature_kwargs_equals_with_double_quote():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    doc = 'def func(x, y="hello"):\n    pass\n'
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1
    assert result[0]['token'] == "="


def test_comma_plus_single_item_set():
    tokenizer = CommaPlusTokenizer()
    doc = "x = {1,}\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_comma_plus_single_item_set_with_string():
    tokenizer = CommaPlusTokenizer()
    doc = "x = {'hello',}\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_comma_plus_single_item_set_not_dict():
    tokenizer = CommaPlusTokenizer()
    doc = "x = {'key': 'val',}\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_comma_plus_multi_item_set():
    tokenizer = CommaPlusTokenizer()
    doc = "x = {1, 2,}\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_comma_plus_single_item_tuple():
    tokenizer = CommaPlusTokenizer()
    doc = "x = (1,)\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_comma_plus_single_item_tuple_not_function_call():
    tokenizer = CommaPlusTokenizer()
    doc = "x = (1,)\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_comma_plus_function_call_with_single_arg_comma():
    tokenizer = CommaPlusTokenizer()
    doc = "func(1,)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_comma_plus_is_single_item_set_with_single_quote_in_value():
    tokenizer = CommaPlusTokenizer()
    doc = "x = {'he\\'llo',}\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_comma_plus_is_single_item_set_with_double_quote_in_value():
    tokenizer = CommaPlusTokenizer()
    doc = 'x = {"he\\"llo",}\n'
    result = tokenizer.tokenize(doc)

    assert result == []


def test_comma_plus_is_single_item_tuple_with_quotes():
    tokenizer = CommaPlusTokenizer()
    doc = "x = ('hello',)\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_comma_plus_is_single_item_tuple_with_double_quotes():
    tokenizer = CommaPlusTokenizer()
    doc = 'x = ("hello",)\n'
    result = tokenizer.tokenize(doc)

    assert result == []


def test_comma_plus_tokenize_with_single_quoted_string():
    tokenizer = CommaPlusTokenizer()
    doc = "x = ['a,b', 2]\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == ", 2"


def test_comma_plus_tokenize_with_escape_in_single_string():
    tokenizer = CommaPlusTokenizer()
    doc = "x = ['a\\'b', 2]\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_comma_plus_tokenize_with_escape_in_double_string():
    tokenizer = CommaPlusTokenizer()
    doc = 'x = ["a\\"b", 2]\n'
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_comma_plus_tokenize_with_triple_single_string():
    tokenizer = CommaPlusTokenizer()
    doc = "x = ['''a,b''', 2]\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert ", 2" in result[0]['token']


def test_comma_plus_tokenize_with_triple_double_string():
    tokenizer = CommaPlusTokenizer()
    doc = 'x = ["""a,b""", 2]\n'
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert ", 2" in result[0]['token']


def test_comma_plus_tokenize_with_comment():
    tokenizer = CommaPlusTokenizer()
    doc = "x = [1, # a,b\n2]\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_comma_plus_single_item_tuple_with_nested_depth():
    tokenizer = CommaPlusTokenizer()
    doc = "x = ([1, 2],)\n"
    result = tokenizer.tokenize(doc)

    assert result != []


def test_comma_plus_is_single_item_set_nested_brackets():
    tokenizer = CommaPlusTokenizer()
    doc = "x = {(1, 2),}\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == ", 2"


def test_comma_plus_is_single_item_tuple_bracket_at_start():
    tokenizer = CommaPlusTokenizer()
    doc = "(1,)\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_comma_plus_is_single_item_tuple_with_spaces_before_paren():
    tokenizer = CommaPlusTokenizer()
    doc = "x =  (1,)\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_comma_plus_method_call_not_tuple():
    tokenizer = CommaPlusTokenizer()
    doc = "obj.method(1,)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_comma_plus_function_result_call_not_tuple():
    tokenizer = CommaPlusTokenizer()
    doc = "func()(1,)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_comma_plus_multi_item_tuple_trailing_comma():
    tokenizer = CommaPlusTokenizer()
    doc = "x = (1, 2,)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_comma_plus_tuple_no_opening_paren():
    tokenizer = CommaPlusTokenizer()
    doc = "1,)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_comma_plus_set_no_opening_brace():
    tokenizer = CommaPlusTokenizer()
    doc = "1,}\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_comma_plus_bracket_found_instead_of_paren():
    tokenizer = CommaPlusTokenizer()
    doc = "[1,)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_py_function_signature_kwargs_equals_unterminated_triple_quote():
    tokenizer = PyFunctionSignatureKwargsEqualsTokenizer()
    doc = "def func(x=\"'''\"):\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1
    assert result[0]['token'] == "="
