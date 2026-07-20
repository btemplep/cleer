"""Unit tests for NonAsciiWhitespaceTokenizer."""

import pytest

from cleer import NonAsciiWhitespaceTokenizer


def test_empty_document():
    tokenizer = NonAsciiWhitespaceTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_no_non_ascii_whitespace():
    tokenizer = NonAsciiWhitespaceTokenizer()
    result = tokenizer.tokenize("hello world\n\ttab")

    assert result == []


def test_single_non_breaking_space():
    tokenizer = NonAsciiWhitespaceTokenizer()
    result = tokenizer.tokenize("hello\u00a0world")

    assert result == [
        {
            "token": "\u00a0",
            "index": 5,
            "length": 1
        }
    ]


def test_em_space():
    tokenizer = NonAsciiWhitespaceTokenizer()
    result = tokenizer.tokenize("hello\u2003world")

    assert result == [
        {
            "token": "\u2003",
            "index": 5,
            "length": 1
        }
    ]


def test_multiple_different_non_ascii_whitespace():
    tokenizer = NonAsciiWhitespaceTokenizer()
    result = tokenizer.tokenize("a\u00a0b\u2003c")

    assert result == [
        {
            "token": "\u00a0",
            "index": 1,
            "length": 1
        },
        {
            "token": "\u2003",
            "index": 3,
            "length": 1
        }
    ]


def test_contiguous_non_ascii_whitespace():
    tokenizer = NonAsciiWhitespaceTokenizer()
    result = tokenizer.tokenize("hello\u00a0\u00a0\u2003world")

    assert result == [
        {
            "token": "\u00a0\u00a0\u2003",
            "index": 5,
            "length": 3
        }
    ]


def test_non_ascii_whitespace_at_start():
    tokenizer = NonAsciiWhitespaceTokenizer()
    result = tokenizer.tokenize("\u00a0hello")

    assert result == [
        {
            "token": "\u00a0",
            "index": 0,
            "length": 1
        }
    ]


def test_non_ascii_whitespace_at_end():
    tokenizer = NonAsciiWhitespaceTokenizer()
    result = tokenizer.tokenize("hello\u00a0")

    assert result == [
        {
            "token": "\u00a0",
            "index": 5,
            "length": 1
        }
    ]


def test_mixed_ascii_and_non_ascii_whitespace():
    tokenizer = NonAsciiWhitespaceTokenizer()
    result = tokenizer.tokenize("hello \u00a0 world")

    assert result == [
        {
            "token": "\u00a0",
            "index": 6,
            "length": 1
        }
    ]


def test_ideographic_space():
    tokenizer = NonAsciiWhitespaceTokenizer()
    result = tokenizer.tokenize("hello\u3000world")

    assert result == [
        {
            "token": "\u3000",
            "index": 5,
            "length": 1
        }
    ]


def test_thin_space():
    tokenizer = NonAsciiWhitespaceTokenizer()
    result = tokenizer.tokenize("hello\u2009world")

    assert result == [
        {
            "token": "\u2009",
            "index": 5,
            "length": 1
        }
    ]


def test_only_non_ascii_whitespace():
    tokenizer = NonAsciiWhitespaceTokenizer()
    result = tokenizer.tokenize("\u00a0\u2003\u3000")

    assert result == [
        {
            "token": "\u00a0\u2003\u3000",
            "index": 0,
            "length": 3
        }
    ]


def test_token_indices_are_correct_for_replacement():
    tokenizer = NonAsciiWhitespaceTokenizer()
    document = "abc\u00a0def\u2003ghi"
    tokens = tokenizer.tokenize(document)

    for token_result in tokens:
        idx = token_result['index']
        length = token_result['length']
        assert document[idx:idx + length] == token_result['token']


def test_non_ascii_whitespace_does_not_tokenize_regular_unicode():
    tokenizer = NonAsciiWhitespaceTokenizer()
    result = tokenizer.tokenize("café résumé naïve")

    assert result == []
