import pytest

from cleer import PyImportSectionSpaceTokenizer


def test_empty_document():
    tokenizer = PyImportSectionSpaceTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_no_imports():
    tokenizer = PyImportSectionSpaceTokenizer()
    result = tokenizer.tokenize("x = 1\ny = 2\n")

    assert result == []


def test_single_import_correct_spacing():
    tokenizer = PyImportSectionSpaceTokenizer()
    result = tokenizer.tokenize("import os\n\n\nx = 1\n")

    assert result == []


def test_single_import_missing_blank():
    tokenizer = PyImportSectionSpaceTokenizer()
    result = tokenizer.tokenize("import os\nx = 1\n")

    assert len(result) == 1
    assert result[0]['token'] == "\n"


def test_single_import_one_blank():
    tokenizer = PyImportSectionSpaceTokenizer()
    result = tokenizer.tokenize("import os\n\nx = 1\n")

    assert len(result) == 1
    assert result[0]['token'] == "\n\n"


def test_single_import_too_many_blanks():
    tokenizer = PyImportSectionSpaceTokenizer()
    result = tokenizer.tokenize("import os\n\n\n\nx = 1\n")

    assert len(result) == 1
    assert result[0]['token'] == "\n\n\n\n"


def test_multiple_imports():
    tokenizer = PyImportSectionSpaceTokenizer()
    result = tokenizer.tokenize("import os\nimport sys\n\nx = 1\n")

    assert len(result) == 1
    assert result[0]['token'] == "\n\n"


def test_multiline_import_with_parens():
    tokenizer = PyImportSectionSpaceTokenizer()
    result = tokenizer.tokenize("from foo import (\n    bar\n)\n\nx = 1\n")

    assert len(result) == 1
    assert result[0]['token'] == "\n\n"


def test_import_at_end_of_file():
    tokenizer = PyImportSectionSpaceTokenizer()
    result = tokenizer.tokenize("import os\n")

    assert result == []


def test_indented_import_ignored():
    tokenizer = PyImportSectionSpaceTokenizer()
    result = tokenizer.tokenize("    import os\nx = 1\n")

    assert result == []


def test_from_import():
    tokenizer = PyImportSectionSpaceTokenizer()
    result = tokenizer.tokenize("from os import path\n\nx = 1\n")

    assert len(result) == 1
    assert result[0]['token'] == "\n\n"
