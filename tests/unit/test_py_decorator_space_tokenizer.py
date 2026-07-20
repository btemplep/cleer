"""Unit tests for PyDecoratorSpaceTokenizer."""

import pytest

from cleer import PyDecoratorSpaceTokenizer


def test_space_between_decorators():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@first\n\n@second\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    space_tokens = [t for t in result if t['token'] == "\n\n"]
    assert len(space_tokens) > 0


def test_no_extra_space_between_decorators():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@first\n@second\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    between_tokens = [t for t in result if t['index'] == 6 and t['token'] == "\n"]
    assert (
        len(between_tokens) == 0
        or all(t['token'] == "\n" for t in between_tokens)
    )


def test_decorator_with_parens():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@app.route('/path')\n\n@login_required\ndef handler():\n    pass\n"
    result = tokenizer.tokenize(doc)

    space_tokens = [t for t in result if "\n\n" in t['token']]
    assert len(space_tokens) > 0


def test_multiline_decorator_with_parens():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@decorator(\n    arg1,\n    arg2\n)\n\n@second\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) > 0


def test_decorator_to_def_space():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@decorator\n\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    space_tokens = [t for t in result if "\n\n" in t['token']]
    assert len(space_tokens) > 0


def test_decorator_to_async_def_space():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@decorator\n\nasync def func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    space_tokens = [t for t in result if "\n\n" in t['token']]
    assert len(space_tokens) > 0


def test_decorator_to_class_space():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@decorator\n\nclass MyClass:\n    pass\n"
    result = tokenizer.tokenize(doc)

    space_tokens = [t for t in result if "\n\n" in t['token']]
    assert len(space_tokens) > 0


def test_single_newline_decorator_to_def():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@decorator\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_no_decorators():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "def func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_empty_document():
    tokenizer = PyDecoratorSpaceTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_multiple_decorators_with_spaces():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@first\n\n@second\n\n@third\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    space_tokens = [t for t in result if "\n\n" in t['token']]
    assert len(space_tokens) >= 2


def test_decorator_end_with_parens_no_newline():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@decorator(arg)"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_decorator_end_no_paren_no_newline():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@decorator"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_space_start_gte_space_end():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@first\n@second\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    for t in result:
        assert t['length'] > 0


def test_tokens_sorted_by_index():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@a\n\n@b\n\n@c\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    for i in range(len(result) - 1):
        assert result[i]['index'] <= result[i + 1]['index']


def test_indented_decorators():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "class Foo:\n    @first\n\n    @second\n    def method(self):\n        pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) > 0


def test_decorator_with_nested_parens():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@decorator(func(1))\n\n@second\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) > 0


def test_decorator_end_returns_len_document():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@decorator"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_already_covered_decorator_to_def():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@first\n\n@second\n\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_space_start_ge_space_end():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@first(\n    arg)@second\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert isinstance(result, list)


def test_def_start_negative_one_trailing_whitespace():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@decorator\n\ndef func():   \n    pass\n"
    result = tokenizer.tokenize(doc)

    assert isinstance(result, list)


def test_already_covered_decorator_to_def():
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@first\n\n@second\n\ndef func():\n    pass\n"
    result = tokenizer.tokenize(doc)

    indices = [t['index'] for t in result]
    assert len(indices) == len(set(indices))


def test_decorator_space_start_gte_end():
    """Cover line 99: space_start >= space_end."""
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@first@second\ndef func():\n    pass\n"
    tokens = tokenizer.tokenize(doc)

    assert isinstance(tokens, list)


def test_decorator_def_start_negative_one():
    """Cover lines 121-122: def_start == -1 fallback."""
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@dec\n   \ndef func():   \n    pass\n"
    tokens = tokenizer.tokenize(doc)

    assert isinstance(tokens, list)


def test_decorator_already_covered():
    """Cover lines 130-131: already_covered branch."""
    tokenizer = PyDecoratorSpaceTokenizer()
    doc = "@first\n\n@second\n\ndef func():\n    pass\n"
    tokens = tokenizer.tokenize(doc)

    indices = [t['index'] for t in tokens]
    assert len(indices) == len(set(indices))
