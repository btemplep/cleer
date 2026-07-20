"""Unit tests for CommaPlusTokenizer."""

import pytest

from cleer import CommaPlusTokenizer


def test_simple_comma_separated():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("[1, 2]\n")

    assert result == [
        {
            "token": ", 2",
            "index": 2,
            "length": 3
        }
    ]


def test_multiple_commas():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("[1, 2, 3]\n")

    assert len(result) == 2
    assert result[0]['token'] == ", 2"
    assert result[1]['token'] == ", 3"


def test_comma_with_newline():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("[1,\n2]\n")

    assert result == [
        {
            "token": ",\n2",
            "index": 2,
            "length": 3
        }
    ]


def test_comma_with_multiple_spaces():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("[1,   2]\n")

    assert result == [
        {
            "token": ",   2",
            "index": 2,
            "length": 5
        }
    ]


def test_comma_with_tab():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("[1,\t2]\n")

    assert result == [
        {
            "token": ",\t2",
            "index": 2,
            "length": 3
        }
    ]


def test_comma_at_end_no_following_char():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("[1,")

    assert result == []


def test_comma_followed_by_whitespace_only():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("[1,   ")

    assert result == []


def test_skip_single_quote_string():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("x = 'a,b'\n")

    assert result == []


def test_skip_double_quote_string():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("x = \"a,b\"\n")

    assert result == []


def test_skip_triple_single_quote_string():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("x = '''a,b'''\n")

    assert result == []


def test_skip_triple_double_quote_string():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("x = \"\"\"a,b\"\"\"\n")

    assert result == []


def test_skip_comment():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("x = 1  # a,b\ny = 2\n")

    assert result == []


def test_escape_in_single_quote():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("x = 'a\\',b'\n")

    assert result == []


def test_escape_in_double_quote():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("x = \"a\\\",b\"\n")

    assert result == []


def test_comma_after_string():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("[\"a\", \"b\"]\n")

    assert len(result) == 1
    assert result[0]['token'] == ", \""


def test_empty_document():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_no_commas():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("x = 1\n")

    assert result == []


def test_comment_without_newline():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("x = 1 # end")

    assert result == []


def test_triple_single_not_terminated():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("'''a,b\n")

    assert result == []


def test_triple_double_not_terminated():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("\"\"\"a,b\n")

    assert result == []


def test_comma_with_newline_and_indent():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("[1,\n    2]\n")

    assert result == [
        {
            "token": ",\n    2",
            "index": 2,
            "length": 7
        }
    ]


def test_trailing_comma_with_closing_bracket():
    tokenizer = CommaPlusTokenizer()
    result = tokenizer.tokenize("[1,\n]\n")

    assert result == [
        {
            "token": ",\n]",
            "index": 2,
            "length": 3
        }
    ]
