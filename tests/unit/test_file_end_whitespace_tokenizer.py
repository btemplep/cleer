"""Unit tests for the FileEndWhitespaceTokenizer."""

from cleer import FileEndWhitespaceTokenizer


def test_empty_document():
    tokenizer = FileEndWhitespaceTokenizer()
    tokens = tokenizer.tokenize("")

    assert tokens == []


def test_document_ending_with_exactly_one_newline():
    tokenizer = FileEndWhitespaceTokenizer()
    tokens = tokenizer.tokenize("import os\n")

    assert tokens == []


def test_document_ending_with_multiple_newlines():
    tokenizer = FileEndWhitespaceTokenizer()
    tokens = tokenizer.tokenize("import os\n\n\n")

    assert len(tokens) == 1
    assert tokens[0]['token'] == "\n\n\n"


def test_document_ending_with_no_newline():
    tokenizer = FileEndWhitespaceTokenizer()
    tokens = tokenizer.tokenize("import os")

    assert len(tokens) == 1
    assert tokens[0]['index'] == len("import os")
    assert tokens[0]['length'] == 0
    assert tokens[0]['token'] == ""


def test_document_ending_with_spaces_and_newline():
    tokenizer = FileEndWhitespaceTokenizer()
    tokens = tokenizer.tokenize("import os   \n")

    assert len(tokens) == 1
    assert tokens[0]['token'] == "   \n"


def test_token_has_correct_index_and_length():
    tokenizer = FileEndWhitespaceTokenizer()
    tokens = tokenizer.tokenize("import os\n\n")

    assert tokens[0]['index'] == 9
    assert tokens[0]['length'] == 2
    assert tokens[0]['token'] == "\n\n"


def test_emits_token_type():
    tokenizer = FileEndWhitespaceTokenizer()

    assert tokenizer.emits_token_type == "file_end_whitespace"
