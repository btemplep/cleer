"""Unit tests for PyImportBlockTokenizer."""

import pytest

from cleer import PyImportBlockTokenizer


def test_single_import():
    tokenizer = PyImportBlockTokenizer()
    result = tokenizer.tokenize("import os\n")

    assert result == [
        {
            "token": "import os",
            "index": 0,
            "length": 9
        }
    ]


def test_multiple_imports_same_block():
    tokenizer = PyImportBlockTokenizer()
    result = tokenizer.tokenize("import os\nimport sys\n")

    assert result == [
        {
            "token": "import os\nimport sys",
            "index": 0,
            "length": 20
        }
    ]


def test_from_import():
    tokenizer = PyImportBlockTokenizer()
    result = tokenizer.tokenize("from os import path\n")

    assert result == [
        {
            "token": "from os import path",
            "index": 0,
            "length": 19
        }
    ]


def test_separate_blocks():
    tokenizer = PyImportBlockTokenizer()
    doc = "import os\nimport sys\n\nimport requests\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 2
    assert result[0]['token'] == "import os\nimport sys"
    assert result[1]['token'] == "import requests"


def test_multiline_import_with_parens():
    tokenizer = PyImportBlockTokenizer()
    doc = "from os import (\n    path,\n    getcwd\n)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "path" in result[0]['token']
    assert "getcwd" in result[0]['token']


def test_multiline_import_followed_by_another():
    tokenizer = PyImportBlockTokenizer()
    doc = "from os import (\n    path,\n    getcwd\n)\nimport sys\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "import sys" in result[0]['token']


def test_no_imports():
    tokenizer = PyImportBlockTokenizer()
    result = tokenizer.tokenize("x = 1\ny = 2\n")

    assert result == []


def test_empty_document():
    tokenizer = PyImportBlockTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_import_after_code():
    tokenizer = PyImportBlockTokenizer()
    doc = "x = 1\nimport os\n"
    result = tokenizer.tokenize(doc)

    assert result == [
        {
            "token": "import os",
            "index": 6,
            "length": 9
        }
    ]


def test_indented_import():
    tokenizer = PyImportBlockTokenizer()
    doc = "if True:\n    import os\n"
    result = tokenizer.tokenize(doc)

    assert result == [
        {
            "token": "    import os",
            "index": 9,
            "length": 13
        }
    ]


def test_mixed_import_and_from():
    tokenizer = PyImportBlockTokenizer()
    doc = "import os\nfrom sys import argv\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "import os" in result[0]['token']
    assert "from sys import argv" in result[0]['token']


def test_non_import_line_breaks_block():
    tokenizer = PyImportBlockTokenizer()
    doc = "import os\nx = 1\nimport sys\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 2
    assert result[0]['token'] == "import os"
    assert result[1]['token'] == "import sys"


def test_subsequent_multiline_import_in_block():
    tokenizer = PyImportBlockTokenizer()
    doc = "import os\nfrom sys import (\n    argv,\n    path\n)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "import os" in result[0]['token']
    assert "argv" in result[0]['token']
