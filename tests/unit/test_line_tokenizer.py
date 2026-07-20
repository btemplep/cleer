"""Unit tests for LineTokenizer."""

import pytest

from cleer import LineTokenizer


def test_single_line_no_newline():
    tokenizer = LineTokenizer()
    result = tokenizer.tokenize("hello world")

    assert result == [
        {
            "token": "hello world",
            "index": 0,
            "length": 11
        }
    ]


def test_single_line_with_newline():
    tokenizer = LineTokenizer()
    result = tokenizer.tokenize("hello world\n")

    assert result == [
        {
            "token": "hello world",
            "index": 0,
            "length": 11
        }
    ]


def test_multiple_lines():
    tokenizer = LineTokenizer()
    result = tokenizer.tokenize("line one\nline two\nline three\n")

    assert result == [
        {
            "token": "line one",
            "index": 0,
            "length": 8
        },
        {
            "token": "line two",
            "index": 9,
            "length": 8
        },
        {
            "token": "line three",
            "index": 18,
            "length": 10
        }
    ]


def test_multiple_lines_no_trailing_newline():
    tokenizer = LineTokenizer()
    result = tokenizer.tokenize("line one\nline two")

    assert result == [
        {
            "token": "line one",
            "index": 0,
            "length": 8
        },
        {
            "token": "line two",
            "index": 9,
            "length": 8
        }
    ]


def test_empty_lines_between_content():
    tokenizer = LineTokenizer()
    result = tokenizer.tokenize("first\n\nsecond\n")

    assert result == [
        {
            "token": "first",
            "index": 0,
            "length": 5
        },
        {
            "token": "",
            "index": 6,
            "length": 0
        },
        {
            "token": "second",
            "index": 7,
            "length": 6
        }
    ]


def test_empty_document():
    tokenizer = LineTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_only_newline():
    tokenizer = LineTokenizer()
    result = tokenizer.tokenize("\n")

    assert result == [
        {
            "token": "",
            "index": 0,
            "length": 0
        }
    ]


def test_multiple_empty_lines():
    tokenizer = LineTokenizer()
    result = tokenizer.tokenize("\n\n\n")

    assert result == [
        {
            "token": "",
            "index": 0,
            "length": 0
        },
        {
            "token": "",
            "index": 1,
            "length": 0
        },
        {
            "token": "",
            "index": 2,
            "length": 0
        }
    ]


def test_lines_with_trailing_whitespace():
    tokenizer = LineTokenizer()
    result = tokenizer.tokenize("hello   \nworld\t\n")

    assert result == [
        {
            "token": "hello   ",
            "index": 0,
            "length": 8
        },
        {
            "token": "world\t",
            "index": 9,
            "length": 6
        }
    ]


def test_lines_with_indentation():
    tokenizer = LineTokenizer()
    result = tokenizer.tokenize("    indented\n\tnested\n")

    assert result == [
        {
            "token": "    indented",
            "index": 0,
            "length": 12
        },
        {
            "token": "\tnested",
            "index": 13,
            "length": 7
        }
    ]


def test_token_indices_are_correct_for_replacement():
    tokenizer = LineTokenizer()
    document = "abc\ndef\nghi\n"
    tokens = tokenizer.tokenize(document)

    for token_result in tokens:
        idx = token_result['index']
        length = token_result['length']
        assert document[idx:idx + length] == token_result['token']
