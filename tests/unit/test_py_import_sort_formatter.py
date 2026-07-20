import pytest

from cleer import PyImportSortFormatter


def test_format_sorts_plain_imports():
    formatter = PyImportSortFormatter()
    result = formatter.format("import sys\nimport os")

    assert result == "import os\nimport sys"


def test_format_sorts_from_imports():
    formatter = PyImportSortFormatter()
    result = formatter.format("from sys import path\nfrom os import getcwd")

    assert result == "from os import getcwd\nfrom sys import path"


def test_format_leaves_sorted_alone():
    formatter = PyImportSortFormatter()
    token = "import os\nimport sys"
    result = formatter.format(token)

    assert result == token


def test_format_single_import_no_change():
    formatter = PyImportSortFormatter()
    token = "import os"
    result = formatter.format(token)

    assert result == token


def test_format_multiline_import_kept_together():
    formatter = PyImportSortFormatter()
    token = "from z import (\n    a,\n    b\n)\nimport os"
    result = formatter.format(token)

    assert result.index("import os") < result.index("from z import")


def test_format_backslash_continuation_kept_together():
    formatter = PyImportSortFormatter()
    token = "from z import a, \\\n    b\nimport os"
    result = formatter.format(token)

    assert result.index("import os") < result.index("from z import")


def test_inspect_returns_none_for_sorted():
    formatter = PyImportSortFormatter()
    result = formatter.inspect("import os\nimport sys")

    assert result is None


def test_inspect_returns_message_for_unsorted():
    formatter = PyImportSortFormatter()
    result = formatter.inspect("import sys\nimport os")

    assert result is not None
    assert "sorted" in result.lower()


def test_format_mixed_imports():
    formatter = PyImportSortFormatter()
    token = "import sys\nfrom os import path\nimport abc"
    result = formatter.format(token)

    lines = result.split("\n")
    assert lines[0] == "import abc"
    assert lines[1] == "from os import path"
    assert lines[2] == "import sys"


def test_get_sort_key_from_import():
    formatter = PyImportSortFormatter()
    result = formatter._get_sort_key("from os.path import join")

    assert result == "os.path"


def test_get_sort_key_plain_import():
    formatter = PyImportSortFormatter()
    result = formatter._get_sort_key("import sys")

    assert result == "sys"


def test_get_sort_key_fallback():
    formatter = PyImportSortFormatter()
    result = formatter._get_sort_key("something weird")

    assert result == "something weird"


def test_format_backslash_continuation_multi_line():
    formatter = PyImportSortFormatter()
    token = "from z import a, \\\n    b, \\\n    c\nimport os"
    result = formatter.format(token)

    assert result.index("import os") < result.index("from z import")
