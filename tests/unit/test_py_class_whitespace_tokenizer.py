"""Unit tests for PyClassWhitespaceTokenizer."""

import pytest

from cleer import PyClassWhitespaceTokenizer


def test_whitespace_before_class():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "x = 1\n\n\nclass Foo:\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert any(t['index'] == 5 for t in result)
    before_token = [t for t in result if t['index'] == 5][0]
    assert before_token['token'] == "\n\n\n"


def test_whitespace_after_class():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "class Foo:\n    pass\n\n\ny = 2\n"
    result = tokenizer.tokenize(doc)

    after_tokens = [t for t in result if t['index'] > 10]
    assert len(after_tokens) > 0


def test_whitespace_before_and_after_class():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "x = 1\n\n\nclass Foo:\n    pass\n\n\ny = 2\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 2


def test_no_preceding_content():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "class Foo:\n    pass\n\ny = 2\n"
    result = tokenizer.tokenize(doc)

    after_tokens = [t for t in result if t['index'] >= 18]
    assert len(after_tokens) > 0


def test_no_following_content():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "x = 1\n\nclass Foo:\n    pass\n"
    result = tokenizer.tokenize(doc)

    before_tokens = [t for t in result if t['index'] == 5]
    assert len(before_tokens) > 0


def test_multiple_classes():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "class Foo:\n    pass\n\n\nclass Bar:\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_class_with_methods():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "x = 1\n\n\nclass Foo:\n    def method(self):\n        pass\n\n\ny = 2\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 2


def test_class_body_with_blank_lines_after_def():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "class Foo:\n\n    x = 1\n"
    result = tokenizer.tokenize(doc)

    body_tokens = [t for t in result if "\n\n" in t['token']]
    assert len(body_tokens) == 0


def test_class_body_no_blank_line():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "class Foo:\n    x = 1\n"
    result = tokenizer.tokenize(doc)

    body_tokens = [t for t in result if t['token'] == "\n"]
    assert len(body_tokens) == 0


def test_empty_document():
    tokenizer = PyClassWhitespaceTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_no_classes():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "x = 1\ny = 2\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_indented_class():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "if True:\n    class Inner:\n        pass\n    x = 1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_class_with_empty_trailing_lines_in_body():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "x = 1\n\nclass Foo:\n    pass\n\ny = 2\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 2


def test_class_end_detection_skips_blank_lines():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "class Foo:\n    x = 1\n\n\n    y = 2\n\nz = 3\n"
    result = tokenizer.tokenize(doc)

    after_tokens = [t for t in result if "z" not in t['token']]
    assert len(after_tokens) >= 1


def test_overlap_prevention():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "x = 1\n\nclass Foo:\n    pass\n\n\nclass Bar:\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_tokens_sorted_by_index():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "a = 1\n\nclass Foo:\n    pass\n\nclass Bar:\n    pass\n\nb = 2\n"
    result = tokenizer.tokenize(doc)

    for i in range(len(result) - 1):
        assert result[i]['index'] <= result[i + 1]['index']


def test_class_at_end_of_file():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "x = 1\n\nclass Foo:\n    pass\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_class_with_multiple_methods_end():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = "class Foo:\n    def a(self):\n        pass\n    def b(self):\n        pass\n\nx = 1\n"
    result = tokenizer.tokenize(doc)

    assert any(t for t in result if t['index'] > 50)


def test_overlap_between_class_end_and_next_class_start():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = (
        "class Foo:\n"
        "    x = 1\n"
        "\n"
        "class Bar:\n"
        "    y = 2\n"
    )
    result = tokenizer.tokenize(doc)

    assert isinstance(result, list)
    assert len(result) >= 1


def test_class_with_oneliner_docstring_and_member():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = 'class Foo:\n    """Short doc."""\n    x = 1\n'
    result = tokenizer.tokenize(doc)

    body_tokens = [t for t in result if t['token'] == "\n"]
    assert len(body_tokens) == 0


def test_class_with_multiline_docstring_and_member():
    tokenizer = PyClassWhitespaceTokenizer()
    doc = 'class Foo:\n    """\n    Multi-line doc.\n    """\n\n    x = 1\n'
    result = tokenizer.tokenize(doc)

    space_tokens = [t for t in result if "\n\n" in t['token']]
    assert len(space_tokens) == 0
