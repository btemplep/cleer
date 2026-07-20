import pytest

from cleer import PyClassTokenizer


def test_finds_simple_class():
    tokenizer = PyClassTokenizer()
    doc = "class MyClass:\n    pass\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 1
    assert "class MyClass:" in tokens[0]['token']


def test_includes_class_body():
    tokenizer = PyClassTokenizer()
    doc = "class MyClass:\n    x = 1\n    def method(self):\n        pass\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 1
    assert "x = 1" in tokens[0]['token']
    assert "def method(self):" in tokens[0]['token']


def test_multiple_classes_dont_overlap():
    tokenizer = PyClassTokenizer()
    doc = "class A:\n    pass\n\nclass B:\n    pass\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 2
    assert "class A:" in tokens[0]['token']
    assert "class B:" in tokens[1]['token']
    assert "class B:" not in tokens[0]['token']
