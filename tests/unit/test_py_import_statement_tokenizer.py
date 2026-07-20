import pytest

from cleer import PyImportStatementTokenizer


def test_finds_simple_import():
    tokenizer = PyImportStatementTokenizer()
    doc = "import os\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 1
    assert tokens[0]['token'] == "import os"


def test_finds_from_import():
    tokenizer = PyImportStatementTokenizer()
    doc = "from sys import path\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 1
    assert tokens[0]['token'] == "from sys import path"


def test_handles_multi_line_import_with_parens():
    tokenizer = PyImportStatementTokenizer()
    doc = "from thing import (\n    a,\n    b\n)\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 1
    assert "from thing import (" in tokens[0]['token']
    assert ")" in tokens[0]['token']


def test_multiple_imports_found():
    tokenizer = PyImportStatementTokenizer()
    doc = "import os\nimport sys\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 2
    assert tokens[0]['token'] == "import os"
    assert tokens[1]['token'] == "import sys"


def test_backslash_line_continuation():
    tokenizer = PyImportStatementTokenizer()
    doc = "from package import \\\n    module_one, \\\n    module_two\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 1
    assert "module_one" in tokens[0]['token']
    assert "module_two" in tokens[0]['token']
    assert "\\" in tokens[0]['token']


def test_backslash_continuation():
    """Cover lines 86-90: import with backslash line continuation."""
    tokenizer = PyImportStatementTokenizer()
    doc = "from package import \\\n    module_one, \\\n    module_two\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 1
    assert "module_one" in tokens[0]['token']
    assert "module_two" in tokens[0]['token']


def test_backslash_continuation_single():
    """Cover backslash continuation with single continuation line."""
    tokenizer = PyImportStatementTokenizer()
    doc = "import \\\n    os\n"
    tokens = tokenizer.tokenize(doc)

    assert len(tokens) == 1
