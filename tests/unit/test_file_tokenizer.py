"""Unit tests for FileTokenizer."""

import pytest

from cleer import FileTokenizer


def test_empty_document():
    tokenizer = FileTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_single_line_no_newline():
    tokenizer = FileTokenizer()
    result = tokenizer.tokenize("hello world")

    assert result == [
        {
            "token": "hello world",
            "index": 0,
            "length": 11
        }
    ]


def test_single_line_with_newline():
    tokenizer = FileTokenizer()
    result = tokenizer.tokenize("hello world\n")

    assert result == [
        {
            "token": "hello world\n",
            "index": 0,
            "length": 12
        }
    ]


def test_multiple_lines():
    tokenizer = FileTokenizer()
    document = "line one\nline two\nline three\n"
    result = tokenizer.tokenize(document)

    assert result == [
        {
            "token": document,
            "index": 0,
            "length": len(document)
        }
    ]


def test_only_newline():
    tokenizer = FileTokenizer()
    result = tokenizer.tokenize("\n")

    assert result == [
        {
            "token": "\n",
            "index": 0,
            "length": 1
        }
    ]


def test_returns_single_token():
    tokenizer = FileTokenizer()
    result = tokenizer.tokenize("anything here")

    assert len(result) == 1


def test_token_index_is_zero():
    tokenizer = FileTokenizer()
    result = tokenizer.tokenize("some content\nmore content\n")

    assert result[0]['index'] == 0


def test_token_length_matches_document():
    tokenizer = FileTokenizer()
    document = "abc\ndef\nghi\n"
    result = tokenizer.tokenize(document)

    assert result[0]['length'] == len(document)


def test_token_value_is_entire_document():
    tokenizer = FileTokenizer()
    document = "    indented\n\tnested\n"
    result = tokenizer.tokenize(document)

    assert result[0]['token'] == document


def test_token_indices_are_correct_for_replacement():
    tokenizer = FileTokenizer()
    document = "abc\ndef\nghi\n"
    tokens = tokenizer.tokenize(document)

    for token_result in tokens:
        idx = token_result['index']
        length = token_result['length']
        assert document[idx:idx + length] == token_result['token']
