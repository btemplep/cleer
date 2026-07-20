"""Unit tests for QuotationTokenizer."""

import pytest

from cleer import QuotationTokenizer


def test_double_quote_string():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("x = \"hello\"\n")

    assert result == [
        {
            "token": "\"hello\"",
            "index": 4,
            "length": 7
        }
    ]


def test_single_quote_string():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("x = 'hello'\n")

    assert result == [
        {
            "token": "'hello'",
            "index": 4,
            "length": 7
        }
    ]


def test_triple_double_quote():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("x = \"\"\"hello\"\"\"\n")

    assert result == [
        {
            "token": "\"\"\"hello\"\"\"",
            "index": 4,
            "length": 11
        }
    ]


def test_triple_single_quote():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("x = '''hello'''\n")

    assert result == [
        {
            "token": "'''hello'''",
            "index": 4,
            "length": 11
        }
    ]


def test_excludes_dict_keys_by_default():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("d['key']\n")

    assert result == []


def test_includes_dict_keys_when_disabled():
    tokenizer = QuotationTokenizer(exclude_dict_keys=False)
    result = tokenizer.tokenize("d['key']\n")

    assert len(result) == 1
    assert result[0]['token'] == "'key'"


def test_multiple_strings():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("x = \"hello\"\ny = \"world\"\n")

    assert len(result) == 2


def test_skip_comment():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("# x = \"hello\"\ny = 1\n")

    assert result == []


def test_comment_without_newline():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("# x = \"hello\"")

    assert result == []


def test_escape_in_double_quote():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("x = \"he\\\"llo\"\n")

    assert len(result) == 1
    assert result[0]['token'] == "\"he\\\"llo\""


def test_escape_in_single_quote():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("x = 'he\\'llo'\n")

    assert len(result) == 1
    assert result[0]['token'] == "'he\\'llo'"


def test_unterminated_triple_double():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("x = \"\"\"unterminated\n")

    assert result == []


def test_unterminated_triple_single():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("x = '''unterminated\n")

    assert result == []


def test_unterminated_single_quote():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("x = 'unterminated\n")

    assert result == []


def test_empty_document():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_no_strings():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("x = 1\n")

    assert result == []


def test_dict_key_with_double_quote():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("d[\"key\"]\n")

    assert result == []


def test_dict_key_bracket_after_bracket():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("a[0]['key']\n")

    assert result == []


def test_dict_key_context_at_start():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("['key']\n")

    assert len(result) == 1
    assert result[0]['token'] == "'key'"


def test_multiline_triple_string():
    tokenizer = QuotationTokenizer()
    doc = "x = \"\"\"line1\nline2\"\"\"\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "line1\nline2" in result[0]['token']


def test_empty_string():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("x = \"\"\n")

    assert len(result) == 1
    assert result[0]['token'] == "\"\""


def test_string_after_comment_on_new_line():
    tokenizer = QuotationTokenizer()
    doc = "# comment\nx = \"hello\"\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == "\"hello\""


def test_string_at_start_of_document():
    tokenizer = QuotationTokenizer()
    result = tokenizer.tokenize("\"hello\"\n")

    assert len(result) == 1
    assert result[0]['token'] == "\"hello\""
    assert result[0]['index'] == 0
