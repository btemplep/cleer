from cleer import (
    PyAllSpacingFormatter,
    PyClassVarWhitespaceFormatter,
    PyCodeBlockNewLinesFormatter,
    PyTypeHintSpacingFormatter,
)


def test_code_block_exit_stmt_adds_blank_line_before_dedent():
    formatter = PyCodeBlockNewLinesFormatter()
    token = (
        "def func():\n"
        "    if inner:\n"
        "        return x\n"
        "\n"
        "    elif other:\n"
        "\n"
        "        raise Error()\n"
        "    z = 2\n"
    )
    result = formatter.format(token)

    assert "\n\n    z = 2\n" in result


def test_code_block_exit_stmt_break_adds_blank_line():
    formatter = PyCodeBlockNewLinesFormatter()
    token = (
        "def func():\n"
        "    for item in items:\n"
        "        if done:\n"
        "            break\n"
        "\n"
        "        process(item)\n"
        "    finish()\n"
    )
    result = formatter.format(token)

    assert "\n\n    finish()\n" in result


def test_code_block_exit_stmt_continue_adds_blank_line():
    formatter = PyCodeBlockNewLinesFormatter()
    token = (
        "def func():\n"
        "    for item in items:\n"
        "        if skip:\n"
        "            continue\n"
        "\n"
        "        process(item)\n"
        "    finish()\n"
    )
    result = formatter.format(token)

    assert "\n\n    finish()\n" in result


def test_code_block_exit_stmt_raise_adds_blank_line():
    formatter = PyCodeBlockNewLinesFormatter()
    token = (
        "def func():\n"
        "    for item in items:\n"
        "        if bad:\n"
        "            raise ValueError()\n"
        "\n"
        "        process(item)\n"
        "    finish()\n"
    )
    result = formatter.format(token)

    assert "\n\n    finish()\n" in result


def test_code_block_blank_lines_skipped_during_scan():
    formatter = PyCodeBlockNewLinesFormatter()
    token = (
        "def func():\n"
        "    if outer:\n"
        "        if inner:\n"
        "\n"
        "            x = 1\n"
        "        y = 2\n"
    )
    result = formatter.format(token)

    assert "        y = 2\n" in result


def test_code_block_exit_stmt_after_blank_line_in_nested_block():
    formatter = PyCodeBlockNewLinesFormatter()
    token = (
        "def func():\n"
        "    if outer:\n"
        "        if inner:\n"
        "\n"
        "            return x\n"
        "        y = 2\n"
    )
    result = formatter.format(token)

    assert "\n        y = 2\n" in result


def test_code_block_single_line_docstring_in_body():
    formatter = PyCodeBlockNewLinesFormatter()
    token = (
        "def func():\n"
        '    """Start.\n'
        '    Some """text""" here.\n'
        '    """\n'
        "    if x:\n"
        "        pass\n"
        "    y = 1\n"
    )
    result = formatter.format(token)

    assert '    """Start.\n' in result


def test_code_block_single_line_docstring_single_quotes():
    formatter = PyCodeBlockNewLinesFormatter()
    token = (
        "def func():\n"
        "    '''Start.\n"
        "    Some '''text''' here.\n"
        "    '''\n"
        "    if x:\n"
        "        pass\n"
        "    y = 1\n"
    )
    result = formatter.format(token)

    assert "    '''Start.\n" in result


def test_all_spacing_inspect_no_all_returns_none():
    formatter = PyAllSpacingFormatter()
    result = formatter.inspect("import os\n\nx = 1\n")

    assert result is None


def test_all_spacing_inspect_bad_spacing_returns_message():
    formatter = PyAllSpacingFormatter()
    token = '__all__ = ["Thing"]\nimport os\n'
    result = formatter.inspect(token)

    assert result is not None
    assert "__all__" in result


def test_all_spacing_format_no_newline_after_all():
    formatter = PyAllSpacingFormatter()
    token = '__all__ = ["Thing"]'
    result = formatter.format(token)

    assert result.endswith("\n")


def test_all_spacing_format_multiline_bracket():
    formatter = PyAllSpacingFormatter()
    token = '__all__ = [\n    "Thing",\n    "Other"\n]\nimport os\n'
    result = formatter.format(token)

    assert "]\n\n\nimport os\n" in result


def test_all_spacing_format_no_newline_between_all_and_code():
    formatter = PyAllSpacingFormatter()
    token = '__all__ = [\n    "Thing"\n]import os\n'
    result = formatter.format(token)

    assert "\n\n\nimport os\n" in result


def test_all_spacing_format_docstring_wrong_spacing_before_all():
    formatter = PyAllSpacingFormatter()
    token = '"""Module doc."""\n\n\n__all__ = ["Thing"]\n\n\nimport os\n'
    result = formatter.format(token)

    assert '"""Module doc."""\n\n__all__' in result


def test_all_spacing_format_empty_after_all():
    formatter = PyAllSpacingFormatter()
    token = '__all__ = ["Thing"]'
    result = formatter.format(token)

    assert result == '__all__ = ["Thing"]\n'


def test_class_var_whitespace_inspect_violation():
    formatter = PyClassVarWhitespaceFormatter()
    result = formatter.inspect("\n\n")

    assert result is not None
    assert "no blank lines" in result


def test_class_var_whitespace_inspect_no_violation():
    formatter = PyClassVarWhitespaceFormatter()
    result = formatter.inspect("\n")

    assert result is None


def test_type_hint_spacing_inspect_violation_space_before():
    formatter = PyTypeHintSpacingFormatter()
    result = formatter.inspect(" : ")

    assert result is not None
    assert "colon" in result.lower()


def test_type_hint_spacing_inspect_violation_no_space_after():
    formatter = PyTypeHintSpacingFormatter()
    result = formatter.inspect(":")

    assert result is not None
    assert "colon" in result.lower()


def test_type_hint_spacing_inspect_no_violation():
    formatter = PyTypeHintSpacingFormatter()
    result = formatter.inspect(": ")

    assert result is None
