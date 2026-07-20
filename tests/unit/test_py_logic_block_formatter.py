from cleer.formatters.python.py_logic_block_formatter import PyLogicBlockFormatter


def test_multiline_over_80_chars_with_two_statements():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "        is_next_func = (start, end, indent) != func_ranges[-1] and any(\n"
        "                s == next_line for s, _, _ in func_ranges\n"
        "            )\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "        is_next_func = (\n"
        "            (start, end, indent) != func_ranges[-1]\n"
        "            and any(s == next_line for s, _, _ in func_ranges)\n"
        "        )\n"
    )

    assert result == expected


def test_two_statements_under_80_collapse_to_single_line():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "        is_net_func = (\n"
        '            "this" == "that"\n'
        '            or "thing" != "that"\n'
        "        )\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        '        is_net_func = "this" == "that" or "thing" != "that"\n'
    )

    assert result == expected


def test_single_line_over_80_expands_to_multiline():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '        after_is_method_or_class = after_stripped.startswith("def ") or after_stripped.startswith("class ")\n'
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "        after_is_method_or_class = (\n"
        '            after_stripped.startswith("def ")\n'
        '            or after_stripped.startswith("class ")\n'
        "        )\n"
    )

    assert result == expected


def test_two_statements_under_80_in_parens_stay_multiline_when_over_80():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "        is_docstring = (\n"
        "            first_stripped.startswith('\"\"\"')\n"
        "            or first_stripped.startswith(\"'''\")\n"
        "        )\n"
    )
    result = formatter.format(token)
    # collapsed single line would be 91 chars, so stays multiline
    assert result == token


def test_two_statements_under_80_collapse_to_single_line_short():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    is_ok = (\n"
        "        x == 1\n"
        "        or y == 2\n"
        "    )\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    is_ok = x == 1 or y == 2\n"
    )

    assert result == expected


def test_extra_inner_parens_removed():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '        one_more = (stripped.startswith("import ")\n'
        '            or stripped.startswith("from ")\n'
        '            or stripped.startswith(")")\n'
        '            or (stripped.startswith("#")))\n'
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "        one_more = (\n"
        '            stripped.startswith("import ")\n'
        '            or stripped.startswith("from ")\n'
        '            or stripped.startswith(")")\n'
        '            or stripped.startswith("#")\n'
        "        )\n"
    )

    assert result == expected


def test_single_statement_in_parens_no_logic_not_touched():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "        x = (\n"
        "            something\n"
        "        )\n"
    )
    result = formatter.format(token)
    # No and/or operator = not a logic block, so formatter does not touch it

    assert result == token


def test_single_statement_with_or_in_parens_collapses():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        a or b\n"
        "    )\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    x = a or b\n"
    )

    assert result == expected


def test_no_change_when_already_correct_single_line():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = a or b\n"
    )
    result = formatter.format(token)

    assert result == token


def test_no_change_when_already_correct_multiline():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    long_var = (\n"
        "        something_very_long_here\n"
        "        and another_very_long_thing_here\n"
        "        and yet_another_thing\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert result == token


def test_inspect_returns_none_for_correct():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = a or b\n"
    )
    result = formatter.inspect(token)

    assert result is None


def test_inspect_returns_message_for_violation():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '        after_is_method_or_class = after_stripped.startswith("def ") or after_stripped.startswith("class ")\n'
    )
    result = formatter.inspect(token)

    assert result is not None


def test_three_statements_go_multiline_even_if_short():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = a or b or c\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    x = (\n"
        "        a\n"
        "        or b\n"
        "        or c\n"
        "    )\n"
    )

    assert result == expected


def test_condition_with_if():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    if something_really_long_variable_name.startswith("prefix") or another_really_long_check.endswith("suffix"):\n'
        "        pass\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    if (\n"
        '        something_really_long_variable_name.startswith("prefix")\n'
        '        or another_really_long_check.endswith("suffix")\n'
        "    ):\n"
        "        pass\n"
    )

    assert result == expected


def test_preserves_and_operator():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    result = first_condition and second_condition and third_condition\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    result = (\n"
        "        first_condition\n"
        "        and second_condition\n"
        "        and third_condition\n"
        "    )\n"
    )

    assert result == expected


def test_mixed_operators():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    result = first_condition and second_condition or third_condition\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    result = (\n"
        "        first_condition\n"
        "        and second_condition\n"
        "        or third_condition\n"
        "    )\n"
    )

    assert result == expected


def test_does_not_touch_non_logic_lines():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = 1\n"
        "    y = 2\n"
        "    return x + y\n"
    )
    result = formatter.format(token)

    assert result == token
