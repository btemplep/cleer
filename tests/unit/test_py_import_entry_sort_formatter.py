import pytest

from cleer import PyImportEntrySortFormatter


def test_format_sorts_import_entries():
    formatter = PyImportEntrySortFormatter()
    result = formatter.format("from thing import c, a, b")

    assert result == "from thing import a, b, c"


def test_format_leaves_sorted_entries_alone():
    formatter = PyImportEntrySortFormatter()
    result = formatter.format("from thing import a, b, c")

    assert result == "from thing import a, b, c"


def test_format_ignores_plain_import():
    formatter = PyImportEntrySortFormatter()
    token = "import os"
    result = formatter.format(token)

    assert result == token


def test_format_single_entry_no_change():
    formatter = PyImportEntrySortFormatter()
    token = "from thing import a"
    result = formatter.format(token)

    assert result == token


def test_format_sorts_parenthesized_import():
    formatter = PyImportEntrySortFormatter()
    token = "from thing import (c, a, b)"
    result = formatter.format(token)

    assert result == "from thing import (a, b, c)"


def test_format_sorts_multiline_parenthesized_import():
    formatter = PyImportEntrySortFormatter()
    token = "from thing import (\n    c,\n    a,\n    b,\n)"
    result = formatter.format(token)

    assert "from thing import (" in result
    assert result.index("a,") < result.index("b,") < result.index("c,")


def test_format_preserves_indent():
    formatter = PyImportEntrySortFormatter()
    token = "    from thing import c, a, b"
    result = formatter.format(token)

    assert result == "    from thing import a, b, c"


def test_inspect_returns_none_for_sorted():
    formatter = PyImportEntrySortFormatter()
    result = formatter.inspect("from thing import a, b, c")

    assert result is None


def test_inspect_returns_message_for_unsorted():
    formatter = PyImportEntrySortFormatter()
    result = formatter.inspect("from thing import c, a, b")

    assert result is not None
    assert "sorted" in result.lower()


def test_inspect_returns_none_for_plain_import():
    formatter = PyImportEntrySortFormatter()
    result = formatter.inspect("import os")

    assert result is None


def test_format_handles_none_module():
    formatter = PyImportEntrySortFormatter()
    token = "from . import something"
    result = formatter.format(token)

    assert result == token


def test_format_handles_single_item_list():
    formatter = PyImportEntrySortFormatter()
    token = "from thing import (a)"
    result = formatter.format(token)

    assert result == token


def test_parse_items_no_match():
    formatter = PyImportEntrySortFormatter()
    module, items, has_parens = formatter._parse_items("import os")

    assert module is None
    assert items is None
