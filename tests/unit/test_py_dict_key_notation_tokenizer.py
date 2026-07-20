"""Unit tests for PyDictKeyNotationTokenizer."""

import pytest

from cleer import PyDictKeyNotationTokenizer


def test_single_quote_key():
    tokenizer = PyDictKeyNotationTokenizer()
    result = tokenizer.tokenize("my_dict['my_key']\n")

    assert result == [
        {
            "token": "'my_key'",
            "index": 8,
            "length": 8
        }
    ]


def test_double_quote_key():
    tokenizer = PyDictKeyNotationTokenizer()
    result = tokenizer.tokenize("my_dict[\"my_key\"]\n")

    assert result == [
        {
            "token": "\"my_key\"",
            "index": 8,
            "length": 8
        }
    ]


def test_multiple_dict_keys():
    tokenizer = PyDictKeyNotationTokenizer()
    result = tokenizer.tokenize("x = my_dict['key']\ny = other['name']\n")

    assert len(result) == 2
    assert result[0]['token'] == "'key'"
    assert result[1]['token'] == "'name'"


def test_chained_dict_access():
    tokenizer = PyDictKeyNotationTokenizer()
    result = tokenizer.tokenize("my_dict['a']['b']\n")

    assert len(result) == 2
    assert result[0]['token'] == "'a'"
    assert result[1]['token'] == "'b'"


def test_no_dict_keys():
    tokenizer = PyDictKeyNotationTokenizer()
    result = tokenizer.tokenize("x = 'hello'\n")

    assert result == []


def test_empty_document():
    tokenizer = PyDictKeyNotationTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_key_with_escape():
    tokenizer = PyDictKeyNotationTokenizer()
    result = tokenizer.tokenize("d['key\\'s']\n")

    assert result == [
        {
            "token": "'key\\'s'",
            "index": 2,
            "length": 8
        }
    ]


def test_bracket_after_paren():
    tokenizer = PyDictKeyNotationTokenizer()
    result = tokenizer.tokenize("func()['key']\n")

    assert result == [
        {
            "token": "'key'",
            "index": 7,
            "length": 5
        }
    ]


def test_bracket_after_bracket():
    tokenizer = PyDictKeyNotationTokenizer()
    result = tokenizer.tokenize("a[0]['key']\n")

    assert result == [
        {
            "token": "'key'",
            "index": 5,
            "length": 5
        }
    ]
