import pytest

from cleer import MultiLineNestedFormatter


def test_format_expands_list_with_2_elements():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("[1, 2]")

    assert result == "[1, 2]"


def test_format_leaves_single_element_list():
    formatter = MultiLineNestedFormatter()
    token = "[1]"
    result = formatter.format(token)

    assert result == token


def test_format_expands_dict_with_2_elements():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("{\"a\": 1, \"b\": 2}")

    assert "{\n" in result
    assert "    \"a\": 1,\n" in result
    assert "    \"b\": 2\n" in result
    assert result.endswith("}")


def test_format_func_call_needs_3_args():
    formatter = MultiLineNestedFormatter()
    token = "func(a, b)"
    result = formatter.format(token)

    assert result == token


def test_format_func_call_expands_with_3_args():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("func(a, b, c)")

    assert result == "func(a, b, c)"


def test_format_nested_list_in_dict_expands_parent():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("{\"key\": [1, 2]}")

    assert result == "{\"key\": [1, 2]}"


def test_format_deeply_nested():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("func([{\"key\": [1, 2]}])")

    assert "func(\n" in result
    assert "[\n" in result
    assert "{\n" in result


def test_format_no_brackets_unchanged():
    formatter = MultiLineNestedFormatter()
    token = "x = 1"
    result = formatter.format(token)

    assert result == token


def test_format_empty_brackets_unchanged():
    formatter = MultiLineNestedFormatter()
    token = "[]"
    result = formatter.format(token)

    assert result == token


def test_format_preserves_strings():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("[\"hello, world\", \"foo\"]")

    assert result == '["hello, world", "foo"]'


def test_format_preserves_single_quote_strings():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("['hello', 'world']")

    assert result == "['hello', 'world']"


def test_format_preserves_base_indent():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("    [1, 2]")

    assert result == "    [1, 2]"


def test_inspect_returns_none_for_correct():
    formatter = MultiLineNestedFormatter()
    result = formatter.inspect("[1, 2]")

    assert result is None


def test_inspect_returns_message_for_needs_expansion():
    formatter = MultiLineNestedFormatter()
    result = formatter.inspect("[{\"key\": \"value\"}]")

    assert result is not None


def test_format_handles_triple_quoted_strings():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("[\"\"\"hello\"\"\", \"world\"]")

    assert result == "[\"\"\"hello\"\"\", \"world\"]"


def test_format_handles_escape_in_strings():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("[\"he\\\"llo\", \"world\"]")

    assert result == "[\"he\\\"llo\", \"world\"]"


def test_format_nested_func_call_in_list():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("[func(a), func(b)]")

    assert result == "[func(a), func(b)]"


def test_format_tuple_with_2_elements():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("(1, 2)")

    assert result == "(1, 2)"


def test_format_single_element_no_expansion():
    formatter = MultiLineNestedFormatter()
    token = "{\"key\": \"value\"}"
    result = formatter.format(token)

    assert result == token


def test_format_nested_needs_expansion_triggers_parent():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("([1, 2])")

    assert result == "([1, 2])"


def test_format_mixed_nested_structures():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("{\"a\": [1, 2], \"b\": [3, 4]}")

    assert "{\n" in result
    assert "\"a\": [1, 2]" in result
    assert "\"b\": [3, 4]" in result


def test_format_triple_single_quote_in_string():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("['''hello''', '''world''']")

    assert result == "['''hello''', '''world''']"


def test_format_single_quote_with_escape():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("['he\\'llo', 'world']")

    assert result == "['he\\'llo', 'world']"


def test_find_matching_close_no_match():
    formatter = MultiLineNestedFormatter()
    result = formatter._find_matching_close(
        "(abc",
        0,
        "(",
        ")"
    )

    assert result == -1


def test_needs_expansion_with_escaped_quotes():
    formatter = MultiLineNestedFormatter()
    result = formatter._needs_expansion("['\\'hello', 'world']")

    assert result is False


def test_format_escaped_single_in_split_elements():
    formatter = MultiLineNestedFormatter()
    elements = formatter._split_elements("'a\\'b', 'c'")

    assert len(elements) == 2


def test_format_nested_with_single_quote_escapes():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("{'key': 'val\\'ue', 'k2': 'v2'}")

    assert "{\n" in result
    assert "'key': 'val\\'ue'," in result


def test_needs_expansion_with_escape_in_double_quote():
    formatter = MultiLineNestedFormatter()
    result = formatter._needs_expansion("[\"he\\\\llo\", \"world\"]")

    assert result is False


def test_needs_expansion_with_single_quote_string():
    formatter = MultiLineNestedFormatter()
    result = formatter._needs_expansion("['hello', 'world']")

    assert result is False


def test_needs_expansion_with_escape_in_single_quote_string():
    formatter = MultiLineNestedFormatter()
    result = formatter._needs_expansion("['he\\'llo', 'world']")

    assert result is False


def test_needs_expansion_escape_inside_string_at_top_level():
    formatter = MultiLineNestedFormatter()
    result = formatter._needs_expansion("'he\\'llo', [1, 2]")

    assert result is False


def test_needs_expansion_single_quote_toggle_at_top_level():
    formatter = MultiLineNestedFormatter()
    result = formatter._needs_expansion("'hello', [1, 2]")

    assert result is False


def test_format_adjacent_strings_with_r_prefix():
    formatter = MultiLineNestedFormatter()
    result = formatter._split_elements('"hello" r"world"')

    assert len(result[0]) == 2
    assert result[0][0] == '"hello"'
    assert result[0][1] == 'r"world"'
    assert result[1][0] == ""


def test_format_adjacent_strings_with_b_prefix():
    formatter = MultiLineNestedFormatter()
    result = formatter._split_elements('"hello" b"world"')

    assert len(result[0]) == 2
    assert result[0][0] == '"hello"'
    assert result[0][1] == 'b"world"'
    assert result[1][0] == ""


def test_format_adjacent_strings_with_f_prefix():
    formatter = MultiLineNestedFormatter()
    result = formatter._split_elements('"hello" f"world"')

    assert len(result[0]) == 2
    assert result[0][0] == '"hello"'
    assert result[0][1] == 'f"world"'
    assert result[1][0] == ""


def test_format_func_call_with_adjacent_strings_collapsed():
    formatter = MultiLineNestedFormatter()
    result = formatter.format('func("hello" r"world")')

    assert result == 'func("hello" r"world")'


def test_format_adjacent_r_prefix_in_list_expands():
    formatter = MultiLineNestedFormatter()
    result = formatter.format('["hello" r"world"]')

    assert result == '["hello" r"world"]'


def test_format_adjacent_strings_in_list_with_comma_elements():
    formatter = MultiLineNestedFormatter()
    result = formatter.format('["hello" r"world", "other"]')

    assert result == '["hello" r"world", "other"]'


def test_split_elements_r_prefix_no_adjacent():
    formatter = MultiLineNestedFormatter()
    result = formatter._split_elements('x, r"hello"')

    assert len(result[0]) == 2
    assert result[0][0] == "x"
    assert result[0][1] == 'r"hello"'
    assert result[1][0] == ","


def test_format_func_call_adjacent_b_prefix_collapsed():
    formatter = MultiLineNestedFormatter()
    result = formatter.format('func(b"hello" b"world")')

    assert result == 'func(b"hello" b"world")'


def test_split_elements_adjacent_plain_double_quote_strings():
    formatter = MultiLineNestedFormatter()
    result = formatter._split_elements('"hello" "world"')

    assert len(result[0]) == 2
    assert result[0][0] == '"hello"'
    assert result[0][1] == '"world"'
    assert result[1][0] == ""


def test_split_elements_adjacent_plain_single_quote_strings():
    formatter = MultiLineNestedFormatter()
    result = formatter._split_elements("'hello' 'world'")

    assert len(result[0]) == 2
    assert result[0][0] == "'hello'"
    assert result[0][1] == "'world'"
    assert result[1][0] == ""


def test_format_adjacent_plain_strings_in_list_expands():
    formatter = MultiLineNestedFormatter()
    result = formatter.format('["hello" "world"]')

    assert result == '["hello" "world"]'


def test_format_adjacent_single_quote_strings_in_list_expands():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("['hello' 'world']")

    assert result == "['hello' 'world']"


def test_format_func_call_adjacent_plain_strings_collapsed():
    formatter = MultiLineNestedFormatter()
    result = formatter.format('func("hello" "world")')

    assert result == 'func("hello" "world")'


def test_format_func_call_adjacent_single_quote_collapsed():
    formatter = MultiLineNestedFormatter()
    result = formatter.format("func('hello' 'world')")

    assert result == "func('hello' 'world')"
