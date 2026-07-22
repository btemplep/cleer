"""Unit tests for PyImportSectionTokenizer."""

import pytest

from cleer import PyImportSectionTokenizer


def test_single_import():
    tokenizer = PyImportSectionTokenizer()
    result = tokenizer.tokenize("import os\n")

    assert result == [
        {
            "token": "import os\n",
            "index": 0,
            "length": 10
        }
    ]


def test_multiple_imports():
    tokenizer = PyImportSectionTokenizer()
    doc = "import os\nimport sys\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == "import os\nimport sys\n"


def test_imports_with_blank_line_between():
    tokenizer = PyImportSectionTokenizer()
    doc = "import os\n\nimport sys\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "import os" in result[0]['token']
    assert "import sys" in result[0]['token']


def test_imports_separated_by_non_import():
    tokenizer = PyImportSectionTokenizer()
    doc = "import os\n\nx = 1\nimport sys\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 2


def test_from_import():
    tokenizer = PyImportSectionTokenizer()
    doc = "from os import path\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "from os import path\n"


def test_multiline_import_with_parens():
    tokenizer = PyImportSectionTokenizer()
    doc = "from os import (\n    path,\n    getcwd\n)\nimport sys\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "path" in result[0]['token']


def test_no_imports():
    tokenizer = PyImportSectionTokenizer()
    result = tokenizer.tokenize("x = 1\ny = 2\n")

    assert result == []


def test_empty_document():
    tokenizer = PyImportSectionTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_import_at_end_of_file():
    tokenizer = PyImportSectionTokenizer()
    doc = "import os"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == "import os"


def test_blank_lines_between_imports_peek_ahead():
    tokenizer = PyImportSectionTokenizer()
    doc = "import os\n\n\nimport sys\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_blank_line_then_non_import():
    tokenizer = PyImportSectionTokenizer()
    doc = "import os\n\nx = 1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == "import os\n"


def test_multiline_import_close_paren():
    tokenizer = PyImportSectionTokenizer()
    doc = "from pkg import (\n    a,\n    b\n)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_import_after_code():
    tokenizer = PyImportSectionTokenizer()
    doc = "x = 1\nimport os\nimport sys\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['index'] == 6


def test_is_import_line_with_close_paren():
    tokenizer = PyImportSectionTokenizer()
    assert tokenizer._is_import_line(")") is True


def test_is_import_line_with_comment():
    tokenizer = PyImportSectionTokenizer()
    assert tokenizer._is_import_line("# comment") is False


def test_is_multiline_continuation():
    tokenizer = PyImportSectionTokenizer()
    assert tokenizer._is_multiline_import_continuation(
        "    x,",
        True
    ) is True
    assert tokenizer._is_multiline_import_continuation(
        "x \\",
        False
    ) is True


def test_subsequent_multiline_import_in_section():
    tokenizer = PyImportSectionTokenizer()
    doc = "import os\nfrom sys import (\n    argv,\n    path\n)\n\nx = 1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "import os" in result[0]['token']
    assert "argv" in result[0]['token']
