"""Unit tests for CommaTokenizer."""

import pytest

from cleer import CommaTokenizer


def test_simple_comma():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("a, b\n")

    assert result == [
        {
            "token": ", ",
            "index": 1,
            "length": 2
        }
    ]


def test_comma_no_space():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("a,b\n")

    assert result == [
        {
            "token": ",",
            "index": 1,
            "length": 1
        }
    ]


def test_space_before_comma():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("a , b\n")

    assert result == [
        {
            "token": " , ",
            "index": 1,
            "length": 3
        }
    ]


def test_multiple_commas():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("a, b, c\n")

    assert len(result) == 2
    assert result[0]['token'] == ", "
    assert result[1]['token'] == ", "


def test_comma_with_newline():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("a,\nb\n")

    assert result == [
        {
            "token": ",\n",
            "index": 1,
            "length": 2
        }
    ]


def test_comma_with_space_and_newline():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("a, \nb\n")

    assert result == [
        {
            "token": ", \n",
            "index": 1,
            "length": 3
        }
    ]


def test_comma_with_tab():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("a,\tb\n")

    assert result == [
        {
            "token": ",\t",
            "index": 1,
            "length": 2
        }
    ]


def test_skip_single_quote_string():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("x = 'a,b'\n")

    assert result == []


def test_skip_double_quote_string():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("x = \"a,b\"\n")

    assert result == []


def test_skip_triple_single_quote():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("x = '''a,b'''\n")

    assert result == []


def test_skip_triple_double_quote():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("x = \"\"\"a,b\"\"\"\n")

    assert result == []


def test_skip_comment():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("x = 1  # a,b\ny = 2\n")

    assert result == []


def test_escape_in_single_quote():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("x = 'a\\',b'\n")

    assert result == []


def test_escape_in_double_quote():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("x = \"a\\\",b\"\n")

    assert result == []


def test_empty_document():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_no_commas():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("x = 1\n")

    assert result == []


def test_comment_without_newline():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("x = 1 # end")

    assert result == []


def test_triple_single_not_terminated():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("'''a,b\n")

    assert result == []


def test_triple_double_not_terminated():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("\"\"\"a,b\n")

    assert result == []


def test_space_before_and_after_comma():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("a  ,  b\n")

    assert result == [
        {
            "token": "  ,  ",
            "index": 1,
            "length": 5
        }
    ]


def test_comma_followed_by_tab_then_newline():
    tokenizer = CommaTokenizer()
    result = tokenizer.tokenize("a,\t\n")

    assert result == [
        {
            "token": ",\t\n",
            "index": 1,
            "length": 3
        }
    ]
