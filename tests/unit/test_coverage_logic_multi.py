from cleer.formatters.python.py_logic_block_formatter import PyLogicBlockFormatter
from cleer.formatters.multi_line_nested_formatter import MultiLineNestedFormatter


def test_logic_block_inspect_returns_message_for_incorrect():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    after_is_method_or_class = after_stripped.startswith("def ") or after_stripped.startswith("class ")\n'
    )
    result = formatter.inspect(token)

    assert result == "Logic block expressions should follow multiline formatting rules."


def test_logic_block_multiline_if_with_and():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    if something_very_long_variable_name and another_very_long_variable_name_here and third_condition:\n'
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    if (\n"
        "        something_very_long_variable_name\n"
        "        and another_very_long_variable_name_here\n"
        "        and third_condition\n"
        "    ):\n"
    )

    assert result == expected


def test_logic_block_multiline_elif_with_or():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    elif something_very_long_variable_name or another_very_long_variable_name_here or third_condition:\n'
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    elif (\n"
        "        something_very_long_variable_name\n"
        "        or another_very_long_variable_name_here\n"
        "        or third_condition\n"
        "    ):\n"
    )

    assert result == expected


def test_logic_block_multiline_while_with_and():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    while something_very_long_variable_name and another_very_long_variable_name_here and third_cond:\n'
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    while (\n"
        "        something_very_long_variable_name\n"
        "        and another_very_long_variable_name_here\n"
        "        and third_cond\n"
        "    ):\n"
    )

    assert result == expected


def test_logic_block_if_condition_collapses_when_under_80():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    if x == 1 and y == 2:\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    if x == 1 and y == 2:\n"
    )

    assert result == expected


def test_logic_block_if_multiline_paren_stays_when_short():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    if (\n"
        "        x == 1\n"
        "        and y == 2\n"
        "    ):\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    if (\n"
        "        x == 1\n"
        "        and y == 2\n"
        "    ):\n"
    )

    assert result == expected


def test_logic_block_normalize_statement_with_multiline_inner():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    result = (\n"
        "        some_func(\n"
        "            arg1,\n"
        "            arg2,\n"
        "            arg3\n"
        "        )\n"
        "        or other_thing\n"
        "    )\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    result = (\n"
        "        some_func(\n"
        "            arg1,\n"
        "            arg2,\n"
        "            arg3\n"
        "        )\n"
        "        or other_thing\n"
        "    )\n"
    )

    assert result == expected


def test_logic_block_normalize_statement_collapses_single_element_parens():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        a == 1\n"
        "        or func(b)\n"
        "    )\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    x = a == 1 or func(b)\n"
    )

    assert result == expected


def test_logic_block_has_multiple_elements_with_comprehension():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = any(item for item in items) or other_thing\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    x = any(item for item in items) or other_thing\n"
    )

    assert result == expected


def test_logic_block_nested_and_or_expands():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    result = (first_condition and second_condition) or (third_condition and fourth_condition) or another_very_long_thing\n"
    )
    result = formatter.format(token)

    assert "    result = (" in result
    assert "    )\n" in result


def test_logic_block_deeply_nested_indent_uses_100_max():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "                    x = really_long_variable_name_here and another_really_long_variable_name_here\n"
    )
    result = formatter.format(token)

    assert "(\n" in result
    assert "really_long_variable_name_here" in result
    assert "and another_really_long_variable_name_here" in result


def test_logic_block_strip_trailing_colon_multiline():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    if (something_very_long_variable_name_here\n"
        "        and another_very_long_variable_name_exceeds_limit\n"
        "        and third_long_condition_here_too):\n"
    )
    result = formatter.format(token)

    assert result.rstrip().endswith(":")
    assert "if (" in result


def test_logic_block_return_with_logic():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    return something_very_long_variable_name_here and another_very_long_variable_name_exceeds_limit\n'
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    return (\n"
        "        something_very_long_variable_name_here\n"
        "        and another_very_long_variable_name_exceeds_limit\n"
        "    )\n"
    )

    assert result == expected


def test_logic_block_yield_with_logic():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    yield something_very_long_variable_name_here and another_very_long_variable_name_exceeds_limit\n'
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    yield (\n"
        "        something_very_long_variable_name_here\n"
        "        and another_very_long_variable_name_exceeds_limit\n"
        "    )\n"
    )

    assert result == expected


def test_logic_block_assert_with_logic():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    assert something_very_long_variable_name_here and another_very_long_variable_name_exceeds_limit\n'
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    assert (\n"
        "        something_very_long_variable_name_here\n"
        "        and another_very_long_variable_name_exceeds_limit\n"
        "    )\n"
    )

    assert result == expected


def test_logic_block_skips_comments():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    # x = a or b\n"
        "    y = 1\n"
    )
    result = formatter.format(token)

    assert result == token


def test_logic_block_skips_def_lines():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    def inner_func(a_or_b):\n"
        "        pass\n"
    )
    result = formatter.format(token)

    assert result == token


def test_logic_block_skips_async_def():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    async def inner_func(a_or_b):\n"
        "        pass\n"
    )
    result = formatter.format(token)

    assert result == token


def test_logic_block_skips_class_lines():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    class MyClass(BaseA_or_BaseB):\n"
        "        pass\n"
    )
    result = formatter.format(token)

    assert result == token


def test_logic_block_multiline_with_paren_wrapping_has_logic_at_depth_one():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        long_variable_name_here\n"
        "        and another_long_variable_name_that_exceeds_the_line_length_limit\n"
        "        and yet_another_condition\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert result == token


def test_logic_block_unwrap_outer_parens_partial_wrap():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (a == 1) and (b == 2)\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    x = a == 1 and b == 2\n"
    )

    assert result == expected


def test_logic_block_strip_redundant_parens_with_comma_inside():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (a, b) or (c, d)\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    x = (a, b) or (c, d)\n"
    )

    assert result == expected


def test_logic_block_strip_redundant_parens_with_logic_inside():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (a or b) and c\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    x = (a or b) and c\n"
    )

    assert result == expected


def test_logic_block_triple_quoted_string_in_expression():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    x = a and """some string"""\n'
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        '    x = a and """some string"""\n'
    )

    assert result == expected


def test_logic_block_single_statement_over_80_stays_single():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    if some_very_long_single_condition_without_any_logic_operators_at_all_that_is_over_eighty_characters:\n"
    )
    result = formatter.format(token)

    assert result == token


def test_logic_block_expand_statement_nested_logic():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    result = (a_long_name and b_long_name) or (c_long_name and d_long_name) or (e_long_name and f_long_name)\n"
    )
    result = formatter.format(token)

    assert "    result = (" in result
    assert "    )\n" in result
    assert "or" in result


def test_logic_block_extract_operators_preserves_order():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = really_long_first_condition_name and really_long_second_condition_name or really_long_third_condition\n"
    )
    result = formatter.format(token)

    assert "and" in result
    assert "or" in result


def test_logic_block_dict_key_assignment():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    my_dict['key'] = really_long_first_condition and really_long_second_condition_that_exceeds_limit\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    my_dict['key'] = (\n"
        "        really_long_first_condition\n"
        "        and really_long_second_condition_that_exceeds_limit\n"
        "    )\n"
    )

    assert result == expected


def test_logic_block_dotted_attribute_assignment():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    self.my_attr = really_long_first_condition and really_long_second_condition_that_exceeds_the_limit\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    self.my_attr = (\n"
        "        really_long_first_condition\n"
        "        and really_long_second_condition_that_exceeds_the_limit\n"
        "    )\n"
    )

    assert result == expected


def test_logic_block_normalize_with_tabs_and_spaces():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        a  \t  \n"
        "        or b\n"
        "    )\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    x = a or b\n"
    )

    assert result == expected


def test_logic_block_find_close_in_text_with_strings():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    x = func("(not_a_paren)") or other_thing\n'
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        '    x = func("(not_a_paren)") or other_thing\n'
    )

    assert result == expected


def test_logic_block_escaped_string_chars():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = func(\"it\\'s\") or other_thing\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    x = func(\"it\\'s\") or other_thing\n"
    )

    assert result == expected


def test_logic_block_multiline_unwrapped_single_depth_zero_logic():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = first_thing and second_thing\n"
    )
    result = formatter.format(token)

    assert result == token


def test_logic_block_if_multiline_already_wrapped_in_parens():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    if (\n"
        "        really_long_first_condition\n"
        "        and really_long_second_condition\n"
        "        and really_long_third_condition\n"
        "    ):\n"
    )
    result = formatter.format(token)

    assert result == token


def test_logic_block_two_ops_fits_single_line_no_parens():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    if (\n"
        "        x\n"
        "        and y\n"
        "    ):\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    if (\n"
        "        x\n"
        "        and y\n"
        "    ):\n"
    )

    assert result == expected


def test_multi_nested_inspect_returns_message():
    formatter = MultiLineNestedFormatter()
    token = 'my_func([{"key": [1, 2]}])'
    result = formatter.inspect(token)

    assert result is not None
    assert "Nested punctuation" in result


def test_multi_nested_inspect_returns_none_for_correct():
    formatter = MultiLineNestedFormatter()
    token = "[1]"
    result = formatter.inspect(token)

    assert result is None


def test_multi_nested_generator_expression_not_expanded():
    formatter = MultiLineNestedFormatter()
    token = "func(x for x in items)"
    result = formatter.format(token)

    assert result == token


def test_multi_nested_type_annotation_shallow_not_expanded():
    formatter = MultiLineNestedFormatter()
    token = "dict[str, int]"
    result = formatter.format(token)

    assert result == token


def test_multi_nested_type_annotation_deep_bracket_expanded():
    formatter = MultiLineNestedFormatter()
    token = "dict[str, list[dict[str, list[int]]]]"
    result = formatter.format(token)

    assert "\n" in result


def test_multi_nested_needs_expansion_inner_nested():
    formatter = MultiLineNestedFormatter()
    token = "func([1, 2])"
    result = formatter.format(token)

    assert result == 'func([1, 2])'


def test_multi_nested_exceeds_line_length_expands():
    formatter = MultiLineNestedFormatter()
    long_arg1 = "a" * 50
    long_arg2 = "b" * 50
    token = f"[{long_arg1}, {long_arg2}]"
    result = formatter.format(token)

    assert "\n" in result


def test_multi_nested_single_element_func_call_collapse():
    formatter = MultiLineNestedFormatter()
    token = "func(\n    short\n)"
    result = formatter.format(token)

    assert result == "func(short)"


def test_multi_nested_single_element_func_call_too_long_stays_expanded():
    formatter = MultiLineNestedFormatter()
    long_arg = "a" * 95
    token = f"func(\n    {long_arg}\n)"
    result = formatter.format(token)

    assert "\n" in result


def test_multi_nested_single_item_set_preserves_trailing_comma():
    formatter = MultiLineNestedFormatter()
    token = "{\"item\",}"
    result = formatter.format(token)

    assert "," in result


def test_multi_nested_single_item_tuple_preserves_trailing_comma():
    formatter = MultiLineNestedFormatter()
    token = "(item,)"
    result = formatter.format(token)

    assert result == "(item,)"


def test_multi_nested_adjacent_string_separator():
    formatter = MultiLineNestedFormatter()
    token = '["hello" "world", "other"]'
    result = formatter.format(token)

    assert result == '["hello" "world", "other"]'


def test_multi_nested_collapsed_no_expand_multiple_elements():
    formatter = MultiLineNestedFormatter()
    token = "func(a, b)"
    result = formatter.format(token)

    assert result == "func(a, b)"


def test_multi_nested_has_top_level_colon_dict_not_set():
    formatter = MultiLineNestedFormatter()
    token = '{"key": "value",}'
    result = formatter.format(token)

    assert result == '{"key": "value"}'


def test_multi_nested_deeply_nested_expansion():
    formatter = MultiLineNestedFormatter()
    token = 'func({"key": [1, 2, 3]})'
    result = formatter.format(token)

    assert "\n" in result


def test_multi_nested_newline_in_inner_non_func_call_expands():
    formatter = MultiLineNestedFormatter()
    token = "[\n    item\n]"
    result = formatter.format(token)

    assert result == "[item]"


def test_logic_block_multiline_paren_wrapped_if_with_logic():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    if (first_thing\n"
        "        and second_thing):\n"
    )
    result = formatter.format(token)

    assert "if" in result
    assert result.rstrip().endswith(":")


def test_logic_block_split_statements_leading_and():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        and first_thing\n"
        "        or second_thing\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "first_thing" in result
    assert "second_thing" in result


def test_logic_block_split_statements_leading_or():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        or first_thing\n"
        "        or second_thing\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "first_thing" in result
    assert "second_thing" in result


def test_logic_block_has_logic_operator_with_and_at_end():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = something and\n"
        "        other_thing\n"
    )
    result = formatter.format(token)

    assert "something" in result
    assert "other_thing" in result


def test_logic_block_word_boundary_android():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = android_check or ios_check\n"
    )
    result = formatter.format(token)

    assert result == token


def test_logic_block_single_line_under_80_with_nested_paren():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (a == 1) or (b == 2)\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    x = a == 1 or b == 2\n"
    )

    assert result == expected


def test_multi_nested_format_preserves_non_paired_text():
    formatter = MultiLineNestedFormatter()
    token = "simple_text"
    result = formatter.format(token)

    assert result == "simple_text"


def test_logic_block_multiline_collection_in_logic():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        my_func([\n"
        "            1,\n"
        "            2,\n"
        "            3\n"
        "        ])\n"
        "        or other_thing\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "my_func" in result
    assert "other_thing" in result


def test_logic_block_paren_depth_change_with_strings():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    x = func("(") and other\n'
    )
    result = formatter.format(token)

    assert 'func("(")' in result
    assert "other" in result


def test_logic_block_unwrap_nested_parens_recursively():
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = ((a)) or b\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    x = (a) or b\n"
    )

    assert result == expected


def test_logic_block_unwrapped_paren_multiline_with_logic():
    """Covers lines 181-194: unwrapped parens with logic at depth 0."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (first_very_long_condition_name\n"
        "        or second_very_long_condition_name_exceeds_eighty_characters_total):\n"
    )
    result = formatter.format(token)

    assert "first_very_long_condition_name" in result
    assert "second_very_long_condition_name_exceeds_eighty_characters_total" in result


def test_logic_block_single_statement_over_max_length_if():
    """Covers lines 325-357: single statement exceeds max_length gets wrapped."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    if really_long_method_name_here(arg1, arg2, arg3) and another_really_long_method_call(param1, param2):\n"
    )
    result = formatter.format(token)

    assert "if (" in result
    assert "):" in result


def test_logic_block_format_block_two_statements_over_80_expand():
    """Covers lines 325-357: two statements that don't fit on one line."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    result = really_long_first_condition_name_here and another_really_long_second_condition_name_that_exceeds\n"
    )
    result = formatter.format(token)

    assert "    result = (" in result
    assert "    )\n" in result


def test_logic_block_normalize_statement_preserves_multi_element_parens():
    """Covers lines 435-451: normalize keeps multi-element paren content."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        func(\n"
        "            a,\n"
        "            b,\n"
        "            c\n"
        "        ) or y\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "func(" in result
    assert "a," in result
    assert "b," in result
    assert "c" in result


def test_logic_block_split_statements_word_boundary_android_in_split():
    """Covers lines 948-950: word boundary check for 'and' in _split_statements."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = check_android_version_is_valid_and_current or something_else_that_is_really_long_over_eighty_chars\n"
    )
    result = formatter.format(token)

    assert "check_android_version_is_valid_and_current" in result
    assert "something_else_that_is_really_long_over_eighty_chars" in result


def test_logic_block_split_statements_word_boundary_oracle():
    """Covers lines 959-961: word boundary check for 'or' in _split_statements."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = check_oracle_status and something_else_that_is_really_really_long_to_exceed_the_max_limit\n"
    )
    result = formatter.format(token)

    assert "check_oracle_status" in result


def test_logic_block_extract_operators_word_boundary_and():
    """Covers lines 1054-1055: word boundary in _extract_operators for 'and'."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = check_android or is_valid_and_current or another_really_long_condition_here_to_exceed_max\n"
    )
    result = formatter.format(token)

    assert "check_android" in result
    assert "is_valid_and_current" in result


def test_logic_block_extract_operators_word_boundary_or():
    """Covers lines 1063-1064: word boundary in _extract_operators for 'or'."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = check_oracle and something_else_here and a_really_long_third_condition_to_trigger_expansion\n"
    )
    result = formatter.format(token)

    assert "check_oracle" in result
    assert "something_else_here" in result


def test_logic_block_strip_redundant_parens_with_triple_quote():
    """Covers lines 1103-1130: triple-quoted strings inside _strip_redundant_parens."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    x = ("""some text""") or something_else_long_name_that_exceeds_the_eighty_char_limit\n'
    )
    result = formatter.format(token)

    assert '"""some text"""' in result


def test_logic_block_strip_redundant_parens_preserves_comma_with_strings():
    """Covers lines 1152-1196: comma detection in _strip_redundant_parens with strings."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    x = ("a", "b") or something_else_name_that_is_really_quite_very_long_here_exceeds_limit\n'
    )
    result = formatter.format(token)

    assert '("a", "b")' in result


def test_logic_block_strip_redundant_parens_comma_in_nested():
    """More coverage for _strip_redundant_parens comma at depth 0."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (a, b) or (c, d) or something_really_long_to_make_it_go_over_eighty_characters_in_total\n"
    )
    result = formatter.format(token)

    assert "(a, b)" in result
    assert "(c, d)" in result


def test_multi_nested_needs_expansion_bracket_depth_over_2():
    """Covers line 365: _needs_expansion returns True when bracket depth > 2."""
    formatter = MultiLineNestedFormatter()
    token = "func(data[key[nested[deep]]])"
    result = formatter.format(token)

    assert "\n" in result


def test_multi_nested_exceeds_length_triggers_expand():
    """Covers line 592: should_expand = True when collapsed exceeds line length."""
    formatter = MultiLineNestedFormatter()
    long1 = "a" * 45
    long2 = "b" * 45
    token = f"[{long1}, {long2}]"
    result = formatter.format(token)

    assert "\n" in result


def test_multi_nested_single_item_set_trailing_comma_in_expansion():
    """Covers line 623: preserve_trailing suffix = ',' for single-item set."""
    formatter = MultiLineNestedFormatter()
    token = '{"item",}'
    result = formatter.format(token)

    assert "item" in result
    assert "," in result


def test_multi_nested_has_top_level_colon_with_brackets():
    """Covers lines 692-703: _has_top_level_colon with nested brackets."""
    formatter = MultiLineNestedFormatter()
    token = '{"key": [1, 2, 3]}'
    result = formatter.format(token)

    assert "\n" in result


def test_logic_block_format_block_three_plus_statements():
    """Covers lines 267-285: formatting 3+ statements with ops."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = first_condition and second_condition and third_condition and fourth_condition_that_makes_it_long\n"
    )
    result = formatter.format(token)

    assert "    x = (" in result
    assert "        first_condition" in result
    assert "        and second_condition" in result
    assert "        and third_condition" in result
    assert "    )\n" in result


def test_logic_block_unwrap_paren_single_line_with_logic():
    """Covers line 181-184: single-line with paren-wrapped logic."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (first_thing or second_thing)\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    x = first_thing or second_thing\n"
    )

    assert result == expected


def test_logic_block_multiline_unwrapped_paren_with_depth():
    """Covers lines 185-194: multiline paren-wrapped with depth > 0."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (first_long_condition_name_exceeds_limit\n"
        "        or second_long_condition_name_also_exceeds\n"
        "        or third_condition_here)\n"
    )
    result = formatter.format(token)

    assert "first_long_condition_name_exceeds_limit" in result
    assert "second_long_condition_name_also_exceeds" in result
    assert "third_condition_here" in result


def test_logic_block_normalize_collapses_close_not_found():
    """Covers line 436: _find_close_in_text returns -1, fallback append."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (open_paren_not_closed or other\n"
    )
    result = formatter.format(token)

    assert "open_paren_not_closed" in result


def test_multi_nested_single_item_tuple_expanded_trailing():
    """Covers line 623: single-item tuple preserves trailing comma when expanded."""
    formatter = MultiLineNestedFormatter()
    long_item = "x" * 95
    token = f"({long_item},)"
    result = formatter.format(token)

    assert "," in result
    assert "x" in result


def test_multi_nested_format_empty_separator_in_expansion():
    """Covers line 617: suffix = '' for adjacent string separators in expansion."""
    formatter = MultiLineNestedFormatter()
    token = '["hello" "world" "third", "other", "more"]'
    result = formatter.format(token)

    assert result == '["hello" "world" "third", "other", "more"]'


def test_logic_block_format_single_statement_over_80_not_condition():
    """Single statement that exceeds max_length - non-condition (assignment)."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    long_result_variable = really_long_first_thing_condition and really_long_second_thing_condition_here\n"
    )
    result = formatter.format(token)

    assert "long_result_variable = (" in result
    assert "    )\n" in result


def test_logic_block_normalize_multiline_statement_with_newlines():
    """Covers lines 439-451: normalize collapses newlines outside brackets."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        first_long_condition_that_is_really_really_long\n"
        "        and second_also_really_long_condition_here_too\n"
        "        and third_condition\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "first_long_condition_that_is_really_really_long" in result
    assert "second_also_really_long_condition_here_too" in result
    assert "third_condition" in result


def test_logic_block_normalize_statement_with_trailing_whitespace_before_newline():
    """Covers lines 456-470: trailing whitespace before newline in normalize."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        a_condition   \n"
        "        and b_condition\n"
        "        and c_condition\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "a_condition" in result
    assert "b_condition" in result


def test_logic_block_normalize_unmatched_open_paren():
    """Covers lines 435-436: unmatched open paren in _normalize_statement."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        func_call(incomplete\n"
        "        and other_thing\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "func_call" in result
    assert "other_thing" in result


def test_logic_block_has_multiple_elements_for_keyword():
    """Covers lines 548-556: _has_multiple_elements with for keyword (comprehension)."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    result = (\n"
        "        [x for x in items]\n"
        "        or other_thing\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "[x for x in items]" in result
    assert "other_thing" in result


def test_logic_block_paren_wrapped_single_line_rhs_unwraps():
    """Covers line 181: single-line paren-wrapped with depth==0 returns [line], 1."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (thing_one or thing_two or thing_three_that_makes_it_go_over_eighty_characters_total_here)\n"
    )
    result = formatter.format(token)

    assert "thing_one" in result
    assert "thing_two" in result
    assert "thing_three" in result


def test_logic_block_strip_redundant_parens_single_quoted_string():
    """Covers _strip_redundant_parens handling of single-quoted strings."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = ('hello') or something_else_name_that_is_really_long_enough_to_exceed_eighty_char_limit\n"
    )
    result = formatter.format(token)

    assert "'hello'" in result


def test_logic_block_strip_redundant_parens_double_quoted_string():
    """Covers _strip_redundant_parens with double-quoted strings inside."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    x = ("hello") or something_else_name_that_is_really_long_enough_to_exceed_eighty_char_limit\n'
    )
    result = formatter.format(token)

    assert "hello" in result


def test_multi_nested_single_item_set_in_expansion_preserves_trailing_comma():
    """Covers line 623 via expansion with single-item set needing trailing comma."""
    formatter = MultiLineNestedFormatter()
    long_val = "x" * 50
    token = f'func({{"only_{long_val}",}})'
    result = formatter.format(token)

    assert "," in result


def test_multi_nested_has_top_level_colon_returns_false():
    """Covers lines 692-703: when no colon at top level."""
    formatter = MultiLineNestedFormatter()
    token = '{"no_colon_here",}'
    result = formatter.format(token)

    assert "no_colon_here" in result


def test_multi_nested_exceeds_line_length_with_indent():
    """Covers line 592: expansion triggered by exceeds_line_length at higher indent."""
    formatter = MultiLineNestedFormatter()
    long1 = "a" * 40
    long2 = "b" * 40
    token = f"func({long1}, {long2}, c)"
    result = formatter.format(token)

    assert "\n" in result


def test_logic_block_format_block_single_statement_over_80_wraps():
    """Single statement over max_length causes wrap in parens."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = very_long_condition_name_that_contains and operator_inside_of_it_making_it_way_over_eighty_chars\n"
    )
    result = formatter.format(token)

    assert "    x = (" in result
    assert "    )\n" in result


def test_logic_block_collapsed_whitespace_in_normalize():
    """Covers _collapse_whitespace usage in _normalize_statement."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        func(  arg  ) or other\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "func(  arg  )" in result
    assert "other" in result


def test_logic_block_find_close_in_text_escaped_quote():
    """Covers lines 494-495: escaped quote inside string in _find_close_in_text."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        func(\"it\\'s \\\"complex\\\"\")\n"
        "        or other_thing\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "other_thing" in result


def test_logic_block_has_multiple_elements_escaped_in_string():
    """Covers lines 528-533: _has_multiple_elements with escaped strings."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        func(\n"
        "            \"it\\'s\",\n"
        "            'other'\n"
        "        )\n"
        "        or something\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "func(" in result
    assert "something" in result


def test_logic_block_unwrap_outer_parens_with_escaped_string():
    """Covers lines 823-824: _unwrap_outer_parens with escaped quotes."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    x = (func("he said \\"hello\\"") or other)\n'
    )
    result = formatter.format(token)

    assert "func(" in result
    assert "other" in result


def test_logic_block_normalize_with_nested_multiline_multi_element():
    """Covers lines 435-436, 425-431: _normalize_statement with multi-element nested content."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        func([\n"
        "            item_one,\n"
        "            item_two\n"
        "        ])\n"
        "        or other_condition_here\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "item_one" in result
    assert "item_two" in result


def test_logic_block_normalize_whitespace_before_newline():
    """Covers lines 456-470: whitespace followed by newline in _normalize_statement."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    long_result_name = (\n"
        "        really_long_condition_check_one  \t\n"
        "        and really_long_condition_check_two\n"
        "        and really_long_condition_check_three\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "really_long_condition_check_one" in result
    assert "really_long_condition_check_two" in result


def test_logic_block_strip_trailing_colon_no_colon():
    """Covers line 380: _strip_trailing_colon returns text unchanged when no colon."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = first_thing or second_thing\n"
    )
    result = formatter.format(token)
    expected = (
        "def func():\n"
        "    x = first_thing or second_thing\n"
    )

    assert result == expected


def test_logic_block_unwrap_outer_parens_triple_quoted_string():
    """Covers _unwrap_outer_parens with triple-quoted string content."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        '    x = ("""text""" == val) or other\n'
    )
    result = formatter.format(token)

    assert '"""text"""' in result
    assert "other" in result


def test_logic_block_has_multiple_elements_single_quoted_content():
    """Covers line 498: single-quote toggling in _find_close_in_text."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        func('hello', 'world', 'test')\n"
        "        or other_thing\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "func(" in result
    assert "other_thing" in result


def test_multi_nested_colon_inside_brackets_not_top_level():
    """Covers lines 692-703: colon inside brackets is not at top level."""
    formatter = MultiLineNestedFormatter()
    token = 'func({"k": "v"}, other, third)'
    result = formatter.format(token)

    assert "\n" in result


def test_multi_nested_escaped_string_in_elements():
    """Covers escaped string handling in split_elements."""
    formatter = MultiLineNestedFormatter()
    token = "func(\"it's\", \"he said hi\", \"third\")"
    result = formatter.format(token)

    assert result == 'func("it\'s", "he said hi", "third")'


def test_logic_block_inspect_returns_none_for_correct_code():
    """Covers line 113: inspect returns None when formatting doesn't change."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = a and b\n"
    )
    result = formatter.inspect(token)

    assert result is None


def test_logic_block_collect_multiline_logic_depth_nonzero():
    """Covers lines 165-174: logic operator at depth 0 but paren depth non-zero."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = first_thing and func(\n"
        "        arg1,\n"
        "        arg2\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "first_thing" in result
    assert "func(" in result
    assert "arg1" in result


def test_logic_block_collect_unwrapped_paren_with_logic_multiline():
    """Covers lines 185-194: unwrapped paren content has logic, depth > 0."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        first_condition or second_condition\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert "first_condition" in result
    assert "second_condition" in result


def test_logic_block_has_nested_logic_directly():
    """Covers lines 325-357: _has_nested_logic method directly."""
    formatter = PyLogicBlockFormatter()

    assert formatter._has_nested_logic("a and b") is True
    assert formatter._has_nested_logic("a or b") is True
    assert formatter._has_nested_logic("func(a and b)") is False
    assert formatter._has_nested_logic("simple") is False
    assert formatter._has_nested_logic("func('and')") is False
    assert formatter._has_nested_logic("func(\"or\")") is False
    assert formatter._has_nested_logic("x[a and b]") is False
    assert formatter._has_nested_logic("x + y") is False


def test_logic_block_has_nested_logic_with_escaped_strings():
    """Covers lines 330-340: _has_nested_logic with escaped quotes."""
    formatter = PyLogicBlockFormatter()

    assert formatter._has_nested_logic("func('it\\'s') and other") is True
    assert formatter._has_nested_logic("func(\"he said \\\"hi\\\"\") and b") is True
    assert formatter._has_nested_logic("func('a\\' and b')") is False


def test_logic_block_strip_trailing_colon_no_colon():
    """Covers line 380: _strip_trailing_colon returns unchanged text."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_trailing_colon("some_expression")

    assert result == "some_expression"


def test_logic_block_normalize_statement_newline_handling():
    """Covers lines 439-451: newline collapsing in _normalize_statement."""
    formatter = PyLogicBlockFormatter()
    result = formatter._normalize_statement("first\n    second\n    third")

    assert result == "first second third"


def test_logic_block_normalize_statement_whitespace_before_newline():
    """Covers lines 464, 467: whitespace handling paths in _normalize_statement."""
    formatter = PyLogicBlockFormatter()
    result = formatter._normalize_statement("first   \nsecond")

    assert result == "first second"


def test_logic_block_normalize_statement_whitespace_not_before_newline():
    """Covers line 467: whitespace followed by non-newline collapses to space."""
    formatter = PyLogicBlockFormatter()
    result = formatter._normalize_statement("first   \n   second\n   third")

    assert "first" in result
    assert "second" in result
    assert "third" in result


def test_logic_block_normalize_unmatched_paren():
    """Covers lines 435-436: _find_close_in_text returns -1, append char."""
    formatter = PyLogicBlockFormatter()
    result = formatter._normalize_statement("(unclosed\n    content")

    assert result == "(unclosed content"


def test_logic_block_find_close_in_text_returns_neg_one():
    """Covers line 511: _find_close_in_text returns -1 for unmatched."""
    formatter = PyLogicBlockFormatter()
    result = formatter._find_close_in_text("(unclosed", 0, "(", ")")

    assert result == -1


def test_logic_block_find_close_in_text_nested_open():
    """Covers line 503: depth += 1 for nested open char."""
    formatter = PyLogicBlockFormatter()
    result = formatter._find_close_in_text("((inner))", 0, "(", ")")

    assert result == 8


def test_logic_block_find_close_in_text_with_escaped_string():
    """Covers _find_close_in_text escape handling in strings."""
    formatter = PyLogicBlockFormatter()
    result = formatter._find_close_in_text("(\"it\\'s\")", 0, "(", ")")

    assert result == 8


def test_logic_block_has_multiple_elements_with_for_keyword():
    """Covers lines 548-553, 556: _has_multiple_elements for keyword detection."""
    formatter = PyLogicBlockFormatter()

    assert formatter._has_multiple_elements("x for x in items") is False
    assert formatter._has_multiple_elements("x for x in items if x > 0") is False


def test_logic_block_has_multiple_elements_for_after_newline():
    """Covers lines 548-553: for keyword preceded by newline."""
    formatter = PyLogicBlockFormatter()

    assert formatter._has_multiple_elements("x\nfor x in items") is False


def test_logic_block_has_multiple_elements_with_comma():
    """Covers _has_multiple_elements with actual comma."""
    formatter = PyLogicBlockFormatter()

    assert formatter._has_multiple_elements("a, b, c") is True
    assert formatter._has_multiple_elements("single") is False


def test_logic_block_split_statements_word_boundary_android_end():
    """Covers lines 948-950: 'and' at end of text with word boundary."""
    formatter = PyLogicBlockFormatter()
    result = formatter._split_statements("check_android")

    assert result == ["check_android"]


def test_logic_block_split_statements_word_boundary_or_end():
    """Covers lines 959-961: 'or' at end of text with word boundary."""
    formatter = PyLogicBlockFormatter()
    result = formatter._split_statements("check_oracle")

    assert result == ["check_oracle"]


def test_logic_block_split_statements_and_followed_by_alnum():
    """Covers lines 948-950: ' and' followed by alphanumeric."""
    formatter = PyLogicBlockFormatter()
    result = formatter._split_statements("check android_thing")

    assert result == ["check android_thing"]


def test_logic_block_split_statements_or_followed_by_alnum():
    """Covers lines 959-961: ' or' followed by alphanumeric."""
    formatter = PyLogicBlockFormatter()
    result = formatter._split_statements("check oracle_thing")

    assert result == ["check oracle_thing"]


def test_logic_block_split_statements_proper_and_split():
    """Verify normal 'and' split works correctly."""
    formatter = PyLogicBlockFormatter()
    result = formatter._split_statements("a and b")

    assert result == ["a", "b"]


def test_logic_block_split_statements_proper_or_split():
    """Verify normal 'or' split works correctly."""
    formatter = PyLogicBlockFormatter()
    result = formatter._split_statements("a or b")

    assert result == ["a", "b"]


def test_logic_block_extract_operators_and_word_boundary():
    """Covers lines 1054-1055: 'and' word boundary in _extract_operators."""
    formatter = PyLogicBlockFormatter()
    result = formatter._extract_operators("check_android or other")

    assert result == ["or"]


def test_logic_block_extract_operators_or_word_boundary():
    """Covers lines 1063-1064: 'or' word boundary in _extract_operators."""
    formatter = PyLogicBlockFormatter()
    result = formatter._extract_operators("check_oracle and other")

    assert result == ["and"]


def test_logic_block_extract_operators_and_at_end_word_boundary():
    """Covers lines 1054-1055: ' and' at end with alnum following."""
    formatter = PyLogicBlockFormatter()
    result = formatter._extract_operators("x and y")

    assert result == ["and"]


def test_logic_block_strip_redundant_parens_escaped_in_string():
    """Covers lines 1104-1105: escape inside string in _strip_redundant_parens."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens("(\"it\\'s\")")

    assert result == "\"it\\'s\""


def test_logic_block_strip_redundant_parens_triple_quote_string():
    """Covers line 1137: triple-quote string detection."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens('("""hello""")')

    assert result == '"""hello"""'


def test_logic_block_strip_redundant_parens_comma_with_escaped():
    """Covers lines 1153-1154, 1158: comma check with string escaping."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens('("a\\",b", other)')

    assert result == '("a\\",b", other)'


def test_logic_block_strip_redundant_parens_comma_at_depth_zero():
    """Covers line 1192: comma at depth 0 returns s unchanged."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens("(a, b)")

    assert result == "(a, b)"


def test_logic_block_strip_redundant_parens_nested_brackets():
    """Covers lines 1173-1174, 1186: brackets/depth in comma check."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens("(func(a, b))")

    assert result == "func(a, b)"


def test_logic_block_strip_redundant_parens_no_comma_no_logic():
    """Covers the path where inner has no comma and no logic → unwrap."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens("(simple_value)")

    assert result == "simple_value"


def test_logic_block_strip_redundant_parens_with_logic():
    """_strip_redundant_parens preserves parens when inner has logic."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens("(a and b)")

    assert result == "(a and b)"


def test_logic_block_strip_redundant_parens_close_before_end():
    """Covers line 1135: depth reaches 0 before end of string → return s."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens("(a) + (b)")

    assert result == "(a) + (b)"


def test_logic_block_strip_redundant_parens_single_quote_in_comma():
    """Covers lines 1153-1154: single-quote string in comma detection."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens("('a,b')")

    assert result == "'a,b'"


def test_logic_block_strip_redundant_parens_triple_single_quote():
    """Covers line 1137: triple single-quote handling."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens("('''hello''')")

    assert result == "'''hello'''"


def test_logic_block_strip_redundant_parens_comma_in_string():
    """Covers lines 1158: comma inside string doesn't trigger return."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens('("hello, world")')

    assert result == '"hello, world"'


def test_logic_block_strip_redundant_parens_escape_in_comma_check():
    """Covers lines 1153-1154: escape inside string during comma check."""
    formatter = PyLogicBlockFormatter()
    input_str = '("it\\\'s fine")'
    result = formatter._strip_redundant_parens(input_str)

    assert result == '"it\\\'s fine"'


def test_logic_block_normalize_multiline_with_open_bracket():
    """Covers _normalize_statement with brackets that have multiple elements."""
    formatter = PyLogicBlockFormatter()
    result = formatter._normalize_statement("func([\n    1,\n    2,\n    3\n]) or other")

    assert "func([" in result
    assert "1," in result
    assert "other" in result


def test_logic_block_normalize_bracket_single_element():
    """Covers _normalize_statement bracket collapsing with single element."""
    formatter = PyLogicBlockFormatter()
    result = formatter._normalize_statement("func(\n    arg\n)")

    assert result == "func(arg)"


def test_multi_nested_exceeds_length_triggers_expand_direct():
    """Covers line 592: collapsed form exceeds line length so should_expand is set."""
    formatter = MultiLineNestedFormatter()
    long1 = "argument_one_" + "x" * 30
    long2 = "argument_two_" + "y" * 30
    long3 = "argument_three_" + "z" * 30
    token = f"function_call({long1}, {long2}, {long3})"
    result = formatter.format(token)

    assert "\n" in result


def test_multi_nested_single_item_set_expanded_preserve_trailing():
    """Covers line 623: single-item set expanded preserves trailing comma."""
    formatter = MultiLineNestedFormatter()
    token = "func({\"only_item\",}, other_arg, third_arg)"
    result = formatter.format(token)

    assert result == 'func({"only_item",}, other_arg, third_arg)'


def test_multi_nested_single_item_tuple_expanded_preserve_trailing():
    """Covers line 623: single-item tuple expanded preserves trailing comma."""
    formatter = MultiLineNestedFormatter()
    token = "func((only_item,), other_arg, third_arg)"
    result = formatter.format(token)

    assert result == 'func((only_item,), other_arg, third_arg)'


def test_multi_nested_has_top_level_colon_escaped_string():
    """Covers lines 692-693: escape inside string in _has_top_level_colon."""
    formatter = MultiLineNestedFormatter()
    result = formatter._has_top_level_colon("func('it\\'s: not')")

    assert result is False


def test_multi_nested_has_top_level_colon_single_quote():
    """Covers line 696: single quote toggling in _has_top_level_colon."""
    formatter = MultiLineNestedFormatter()
    result = formatter._has_top_level_colon("'key: value'")

    assert result is False


def test_multi_nested_has_top_level_colon_with_brackets():
    """Covers lines 701, 703: brackets affect depth in _has_top_level_colon."""
    formatter = MultiLineNestedFormatter()
    result = formatter._has_top_level_colon("[a:b]")

    assert result is False


def test_multi_nested_has_top_level_colon_actual_colon():
    """Covers _has_top_level_colon returns True for actual top-level colon."""
    formatter = MultiLineNestedFormatter()
    result = formatter._has_top_level_colon("key: value")

    assert result is True


def test_multi_nested_has_top_level_colon_double_quote():
    """Covers line 696 variant: double quote toggling."""
    formatter = MultiLineNestedFormatter()
    result = formatter._has_top_level_colon('"key: value"')

    assert result is False


def test_multi_nested_collapsed_with_empty_separator():
    """Covers line 635: empty separator in collapsed mode."""
    formatter = MultiLineNestedFormatter()
    token = '("hello" "world")'
    result = formatter.format(token)

    assert "hello" in result
    assert "world" in result


def test_logic_block_format_block_prefix_none_direct():
    """Covers line 232: _format_logic_block when prefix is None."""
    formatter = PyLogicBlockFormatter()
    result = formatter._format_logic_block(["# this is a comment"])

    assert result == ["# this is a comment"]


def test_logic_block_collect_with_open_paren_multiline_no_logic():
    """Covers the case where open_depth > 0 but no logic at depth one."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    x = (\n"
        "        simple_value\n"
        "    )\n"
    )
    result = formatter.format(token)

    assert result == token


def test_logic_block_normalize_statement_tab_whitespace_collapse():
    """Covers lines 456-470: tab followed by non-newline text."""
    formatter = PyLogicBlockFormatter()
    result = formatter._normalize_statement("a\t\tb\n    c")

    assert "a" in result
    assert "b" in result
    assert "c" in result


def test_logic_block_normalize_tabs_before_newline():
    """Covers line 464: tabs followed by newline get skipped."""
    formatter = PyLogicBlockFormatter()
    result = formatter._normalize_statement("a\t\t\n  b")

    assert result == "a b"


def test_logic_block_expand_statement_with_nested_logic():
    """Covers _expand_statement with nested logic operators."""
    formatter = PyLogicBlockFormatter()
    token = (
        "def func():\n"
        "    result = (first_cond and second_cond) or (third_cond and fourth_cond) or fifth_really_long_cond_name\n"
    )
    result = formatter.format(token)

    assert "    result = (" in result
    assert "    )\n" in result
    assert "or" in result


def test_multi_nested_format_line_580():
    """Covers line 580: the collapsed check before should_expand."""
    formatter = MultiLineNestedFormatter()
    token = "func(short_a, short_b)"
    result = formatter.format(token)

    assert result == "func(short_a, short_b)"


def test_logic_block_has_nested_logic_bracket_depth():
    """Covers _has_nested_logic with bracket depth changes."""
    formatter = PyLogicBlockFormatter()

    assert formatter._has_nested_logic("{a and b}") is False
    assert formatter._has_nested_logic("[a or b]") is False
    assert formatter._has_nested_logic("x + y and z") is True


def test_logic_block_strip_redundant_parens_escaped_backslash():
    """Covers 1104-1105: double backslash (escaped backslash) inside string."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens('("path\\\\to\\\\file")')

    assert result == '"path\\\\to\\\\file"'


def test_logic_block_strip_redundant_parens_triple_quote_comma():
    """Covers line 1137 with triple-quote containing comma."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens('("""a,b""")')

    assert result == '"""a,b"""'


def test_logic_block_strip_redundant_parens_closing_bracket_in_comma():
    """Covers line 1186: closing bracket decrements comma_depth."""
    formatter = PyLogicBlockFormatter()
    result = formatter._strip_redundant_parens("([1, 2, 3])")

    assert result == "[1, 2, 3]"


def test_multi_nested_has_top_level_colon_nested_bracket_colon():
    """Covers lines 701, 703: depth increase/decrease around colon."""
    formatter = MultiLineNestedFormatter()

    assert formatter._has_top_level_colon("({a: b})") is False
    assert formatter._has_top_level_colon("x: y") is True
    assert formatter._has_top_level_colon("(x): y") is True


def test_multi_nested_func_call_two_long_args_exceeds_length():
    """Covers line 592: func call with 2 args that exceed max length when collapsed."""
    formatter = MultiLineNestedFormatter()
    long1 = "argument_one_" + "x" * 40
    long2 = "argument_two_" + "y" * 40
    token = f"my_function({long1}, {long2})"
    result = formatter.format(token)

    assert "\n" in result
    assert long1 in result
    assert long2 in result


def test_multi_nested_func_call_two_adjacent_strings_exceeds_length():
    """Covers line 580: adjacent string separator in collapse path exceeding length."""
    formatter = MultiLineNestedFormatter()
    long1 = '"' + "h" * 48 + '"'
    long2 = '"' + "w" * 48 + '"'
    token = f"my_function({long1} {long2})"
    result = formatter.format(token)

    assert "\n" in result


def test_multi_nested_func_call_two_adjacent_strings_short():
    """Covers line 635: adjacent string separator in collapsed path (under length)."""
    formatter = MultiLineNestedFormatter()
    token = 'my_func("hello" "world")'
    result = formatter.format(token)

    assert result == 'my_func("hello" "world")'


def test_multi_nested_single_item_set_with_nested_expansion():
    """Covers line 623: single-item set with inner content that triggers expansion."""
    formatter = MultiLineNestedFormatter()
    token = "{[1, 2],}"
    result = formatter.format(token)

    assert result == '{[1, 2],}'


def test_multi_nested_single_item_tuple_with_nested_expansion():
    """Covers line 623: single-item tuple with inner content that triggers expansion."""
    formatter = MultiLineNestedFormatter()
    token = "([1, 2],)"
    result = formatter.format(token)

    assert result == '([1, 2],)'


def test_logic_block_multiline_assignment_with_logic_in_parens():
    """Cover lines 185-194: multiline assignment with paren-wrapped logic expression."""
    from cleer import PyLogicBlockFormatter

    formatter = PyLogicBlockFormatter()
    token = (
        "x = (a_thing\n"
        "    and b_thing\n"
        "    and c_thing)\n"
    )
    result = formatter.format(token)
    assert "and" in result


def test_logic_block_variable_name_contains_and():
    """Cover lines 948-950, 1054-1055: variable name containing 'and' substring."""
    from cleer import PyLogicBlockFormatter

    formatter = PyLogicBlockFormatter()
    # Multiline if with 'android' which contains 'and' as substring
    token = (
        "if (\n"
        "    something\n"
        "    and android\n"
        "    and other_thing\n"
        "):\n"
        "    pass\n"
    )
    result = formatter.format(token)
    assert "android" in result


def test_logic_block_variable_name_contains_or():
    """Cover lines 959-961, 1063-1064: variable name containing 'or' substring."""
    from cleer import PyLogicBlockFormatter

    formatter = PyLogicBlockFormatter()
    # Multiline if with 'oracle' which contains 'or' as substring
    token = (
        "if (\n"
        "    something\n"
        "    or oracle\n"
        "    or other_thing\n"
        "):\n"
        "    pass\n"
    )
    result = formatter.format(token)
    assert "oracle" in result


def test_logic_block_and_at_end_with_identifier():
    """Cover word boundary check when 'and' is followed by identifier char."""
    from cleer import PyLogicBlockFormatter

    formatter = PyLogicBlockFormatter()
    # Expression where 'anderson' contains ' and' but followed by identifier
    token = (
        "if (\n"
        "    anderson\n"
        "    and thing\n"
        "):\n"
        "    pass\n"
    )
    result = formatter.format(token)
    assert "anderson" in result
    assert "thing" in result


def test_multi_nested_needs_expansion_set_two_elements():
    formatter = MultiLineNestedFormatter()
    result = formatter._needs_expansion("{1, 2}")

    assert result is True


def test_multi_nested_single_elem_becomes_multiline_after_format():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("[PyImportSeparatorFormatter(internal_packages=internal_packages, current_packages=current_packages)]")

    assert "\n" in result
    assert "[\n" in result
    assert "    PyImportSeparatorFormatter(\n" in result


def test_multi_nested_single_item_tuple_trailing_comma_preserved():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("(PyImportSeparatorFormatter(internal_packages=internal_packages, current_packages=current_packages),)")

    assert "(\n" in result
    assert "),\n" in result


def test_multi_nested_empty_list_with_newline():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("[\n]")

    assert result == "[\n]"
