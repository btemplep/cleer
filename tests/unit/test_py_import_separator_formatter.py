import pytest

from cleer import PyImportSeparatorFormatter


def test_format_separates_stdlib_and_third_party():
    formatter = PyImportSeparatorFormatter()
    token = "import os\nimport requests\n"
    result = formatter.format(token)

    assert "import os" in result
    assert "import requests" in result
    assert "\n\n" in result


def test_format_separates_three_blocks():
    formatter = PyImportSeparatorFormatter(internal_packages=["my_lib"])
    token = "import os\nimport requests\nimport my_lib\n"
    result = formatter.format(token)

    parts = result.strip().split("\n\n")
    assert len(parts) == 3
    assert "import os" in parts[0]
    assert "import requests" in parts[1]
    assert "import my_lib" in parts[2]


def test_format_handles_relative_imports():
    formatter = PyImportSeparatorFormatter()
    token = "import os\nfrom . import thing\n"
    result = formatter.format(token)

    assert "\n\n" in result
    assert "import os" in result
    assert "from . import thing" in result


def test_format_handles_from_imports():
    formatter = PyImportSeparatorFormatter()
    token = "from os.path import join\nimport requests\n"
    result = formatter.format(token)

    parts = result.strip().split("\n\n")
    assert len(parts) == 2


def test_format_empty_statements():
    formatter = PyImportSeparatorFormatter()
    token = "\n\n"
    result = formatter.format(token)

    assert result == token


def test_format_single_block():
    formatter = PyImportSeparatorFormatter()
    token = "import os\nimport sys\n"
    result = formatter.format(token)

    assert "import os\nimport sys\n" in result


def test_format_ensures_trailing_newlines():
    formatter = PyImportSeparatorFormatter()
    token = "import os\nimport requests"
    result = formatter.format(token)

    assert result.endswith("\n")


def test_format_multiline_import_statement():
    formatter = PyImportSeparatorFormatter()
    token = "from os.path import (\n    join,\n    exists\n)\nimport requests\n"
    result = formatter.format(token)

    assert "from os.path import (" in result
    assert "import requests" in result
    assert "\n\n" in result


def test_format_backslash_continuation():
    formatter = PyImportSeparatorFormatter()
    token = "from os.path import join, \\\n    exists\nimport requests\n"
    result = formatter.format(token)

    assert "from os.path import join" in result
    assert "import requests" in result


def test_inspect_returns_none_for_correct():
    formatter = PyImportSeparatorFormatter()
    token = "import os\n\nimport requests\n"
    result = formatter.inspect(token)

    assert result is None


def test_inspect_returns_message_for_unseparated():
    formatter = PyImportSeparatorFormatter()
    token = "import os\nimport requests\n"
    result = formatter.inspect(token)

    assert result is not None
    assert "separated" in result.lower()


def test_format_all_four_blocks():
    formatter = PyImportSeparatorFormatter(internal_packages=["internal_pkg"])
    token = "import os\nimport requests\nimport internal_pkg\nfrom . import local\n"
    result = formatter.format(token)

    parts = result.strip().split("\n\n")
    assert len(parts) == 4


def test_classify_current_package():
    formatter = PyImportSeparatorFormatter(current_packages=["my_package"])
    result = formatter._classify_import("import my_package")

    assert result == 3


def test_classify_stdlib():
    formatter = PyImportSeparatorFormatter()
    result = formatter._classify_import("import os")

    assert result == 0


def test_classify_third_party():
    formatter = PyImportSeparatorFormatter()
    result = formatter._classify_import("import requests")

    assert result == 1


def test_classify_internal():
    formatter = PyImportSeparatorFormatter(internal_packages=["my_internal"])
    result = formatter._classify_import("import my_internal")

    assert result == 2


def test_classify_relative():
    formatter = PyImportSeparatorFormatter()
    result = formatter._classify_import("from . import thing")

    assert result == 3


def test_get_module_name_from_import():
    formatter = PyImportSeparatorFormatter()
    result = formatter._get_module_name("from os.path import join")

    assert result == "os"


def test_get_module_name_plain_import():
    formatter = PyImportSeparatorFormatter()
    result = formatter._get_module_name("import sys")

    assert result == "sys"


def test_get_module_name_no_match():
    formatter = PyImportSeparatorFormatter()
    result = formatter._get_module_name("x = 1")

    assert result == ""


def test_is_relative_import():
    formatter = PyImportSeparatorFormatter()

    assert formatter._is_relative_import("from . import thing") is True
    assert formatter._is_relative_import("from .sub import thing") is True
    assert formatter._is_relative_import("from os import path") is False


def test_get_full_import_statement_backslash_multi_line():
    formatter = PyImportSeparatorFormatter()
    lines = [
        "from os import join, \\",
        "    exists, \\",
        "    dirname"
    ]
    statement, end_idx = formatter._get_full_import_statement(
        lines,
        0
    )

    assert "join" in statement
    assert "dirname" in statement
    assert end_idx == 2
