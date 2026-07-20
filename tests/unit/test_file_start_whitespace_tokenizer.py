"""Unit tests for the FileStartWhitespaceTokenizer."""

from cleer import FileStartWhitespaceTokenizer


def test_empty_document():
    tokenizer = FileStartWhitespaceTokenizer()
    tokens = tokenizer.tokenize("")

    assert tokens == []


def test_no_leading_whitespace():
    tokenizer = FileStartWhitespaceTokenizer()
    tokens = tokenizer.tokenize("import os\n")

    assert tokens == []


def test_leading_newlines():
    tokenizer = FileStartWhitespaceTokenizer()
    tokens = tokenizer.tokenize("\n\nimport os\n")

    assert len(tokens) == 1
    assert tokens[0]['token'] == "\n\n"


def test_leading_spaces():
    tokenizer = FileStartWhitespaceTokenizer()
    tokens = tokenizer.tokenize("   import os\n")

    assert len(tokens) == 1
    assert tokens[0]['token'] == "   "


def test_leading_tabs():
    tokenizer = FileStartWhitespaceTokenizer()
    tokens = tokenizer.tokenize("\t\timport os\n")

    assert len(tokens) == 1
    assert tokens[0]['token'] == "\t\t"


def test_mixed_leading_whitespace():
    tokenizer = FileStartWhitespaceTokenizer()
    tokens = tokenizer.tokenize("\n \t import os\n")

    assert len(tokens) == 1
    assert tokens[0]['token'] == "\n \t "


def test_token_has_correct_index_and_length():
    tokenizer = FileStartWhitespaceTokenizer()
    tokens = tokenizer.tokenize("\n\n  code\n")

    assert tokens[0]['index'] == 0
    assert tokens[0]['length'] == 4


def test_emits_token_type():
    tokenizer = FileStartWhitespaceTokenizer()

    assert tokenizer.emits_token_type == "file_start_whitespace"
