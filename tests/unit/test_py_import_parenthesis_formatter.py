import pytest

from cleer import PyImportParenthesisFormatter


def test_format_wraps_from_import_with_more_than_3_items():
    formatter = PyImportParenthesisFormatter()
    result = formatter.format("from thing import a, b, c, d")

    assert result == "from thing import (\n    a,\n    b,\n    c,\n    d\n)"


def test_format_leaves_from_import_with_3_items():
    formatter = PyImportParenthesisFormatter()
    token = "from thing import a, b, c"
    result = formatter.format(token)

    assert result == token


def test_format_leaves_from_import_with_2_items():
    formatter = PyImportParenthesisFormatter()
    token = "from thing import a, b"
    result = formatter.format(token)

    assert result == token


def test_format_wraps_plain_import_with_more_than_3_items():
    formatter = PyImportParenthesisFormatter()
    result = formatter.format("import a, b, c, d")

    assert result == "import (\n    a,\n    b,\n    c,\n    d\n)"


def test_format_leaves_plain_import_with_3_items():
    formatter = PyImportParenthesisFormatter()
    token = "import a, b, c"
    result = formatter.format(token)

    assert result == token


def test_format_preserves_indent():
    formatter = PyImportParenthesisFormatter()
    result = formatter.format("    from thing import a, b, c, d")

    assert result.startswith("    from thing import (")
    assert "        a," in result


def test_format_handles_already_parenthesized():
    formatter = PyImportParenthesisFormatter()
    token = "from thing import (a, b, c, d)"
    result = formatter.format(token)

    assert "from thing import (" in result
    assert "    a," in result


def test_format_leaves_non_import_statement():
    formatter = PyImportParenthesisFormatter()
    token = "x = 1"
    result = formatter.format(token)

    assert result == token


def test_inspect_returns_none_for_3_or_fewer():
    formatter = PyImportParenthesisFormatter()
    result = formatter.inspect("from thing import a, b, c")

    assert result is None


def test_inspect_returns_message_for_more_than_3():
    formatter = PyImportParenthesisFormatter()
    result = formatter.inspect("from thing import a, b, c, d")

    assert result is not None
    assert "parenthesized" in result.lower()


def test_format_handles_single_item():
    formatter = PyImportParenthesisFormatter()
    token = "from thing import a"
    result = formatter.format(token)

    assert result == token


def test_format_handles_line_continuation():
    formatter = PyImportParenthesisFormatter()
    token = "from thing import a, b, c, \\\n    d"
    result = formatter.format(token)

    assert "from thing import (" in result


def test_format_returns_token_for_unparseable_from():
    formatter = PyImportParenthesisFormatter()
    token = "from import"
    result = formatter.format(token)

    assert result == token


def test_format_plain_import_single_item():
    formatter = PyImportParenthesisFormatter()
    token = "import os"
    result = formatter.format(token)

    assert result == token


def test_parse_plain_import_no_match():
    formatter = PyImportParenthesisFormatter()
    result = formatter._parse_plain_import("not an import")

    assert result is None


def test_format_plain_import_unparseable():
    formatter = PyImportParenthesisFormatter()
    token = "import "
    result = formatter.format(token)

    assert result == token


def test_format_plain_import_no_module():
    formatter = PyImportParenthesisFormatter()
    token = "import"
    result = formatter.format(token)

    assert result == token


def test_plain_import_parse_returns_none():
    formatter = PyImportParenthesisFormatter()
    result = formatter._parse_plain_import("import")

    assert result is None


def test_plain_import_with_many_items():
    formatter = PyImportParenthesisFormatter()
    token = "import os, sys, re, json"
    result = formatter.format(token)

    assert "import (" in result
    assert "os," in result


def test_plain_import_with_few_items():
    """Cover line 152: plain import with <= 3 items returns unchanged."""
    formatter = PyImportParenthesisFormatter()
    token = "import os, sys, re"
    result = formatter.format(token)

    assert result == token
