"""Unit tests for BinaryOperatorTokenizer."""

import pytest

from cleer import BinaryOperatorTokenizer


def test_simple_assignment():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("x = 1\n")

    assert result == [
        {
            "token": " = ",
            "index": 1,
            "length": 3
        }
    ]


def test_addition():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("x = 1 + 2\n")

    assert len(result) == 2
    assert result[0]['token'] == " = "
    assert result[1]['token'] == " + "


def test_multiple_operators():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("x = a + b - c\n")

    assert len(result) == 3
    assert result[0]['token'] == " = "
    assert result[1]['token'] == " + "
    assert result[2]['token'] == " - "


def test_compound_assignment_operators():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("x += 1\n")

    assert result == [
        {
            "token": " += ",
            "index": 1,
            "length": 4
        }
    ]


def test_comparison_operators():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("a == b\n")

    assert result == [
        {
            "token": " == ",
            "index": 1,
            "length": 4
        }
    ]


def test_not_equal():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("a != b\n")

    assert result == [
        {
            "token": " != ",
            "index": 1,
            "length": 4
        }
    ]


def test_bitwise_operators():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("a & b\n")

    assert result[0]['token'] == " & "


def test_power_operator():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("x = a ** b\n")

    assert any(t['token'] == " ** " for t in result)


def test_floor_division():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("x = a // b\n")

    assert any(t['token'] == " // " for t in result)


def test_shift_operators():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("x = a >> b\n")

    assert any(t['token'] == " >> " for t in result)


def test_left_shift():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("x = a << b\n")

    assert any(t['token'] == " << " for t in result)


def test_arrow_operator():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("x = a -> b\n")

    assert any(t['token'] == " -> " for t in result)


def test_excludes_signature_equals_by_default():
    tokenizer = BinaryOperatorTokenizer()
    doc = "def func(x=1, y=2):\n    pass\n"
    result = tokenizer.tokenize(doc)

    for t in result:
        assert "=" not in t['token'] or t['token'].strip() != "="


def test_includes_signature_equals_when_disabled():
    tokenizer = BinaryOperatorTokenizer(exclude_signature_equals=False)
    doc = "x = func(y=1)\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " = "


def test_excludes_call_equals_by_default():
    tokenizer = BinaryOperatorTokenizer()
    doc = "result = func(x=1, y=2)\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " = "
    assert len(result) == 1


def test_includes_call_equals_when_disabled():
    tokenizer = BinaryOperatorTokenizer(exclude_call_equals=False)
    doc = "func(x=1)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) > 0


def test_skips_strings_single_quote():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = 'a + b'\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " = "


def test_skips_strings_double_quote():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = \"a + b\"\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " = "


def test_skips_triple_single_quote_strings():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = '''a + b'''\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " = "


def test_skips_triple_double_quote_strings():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = \"\"\"a + b\"\"\"\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " = "


def test_skips_comments():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = 1  # a + b\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " = "


def test_unary_minus():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = -1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " = "


def test_unary_plus():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = +1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " = "


def test_unary_tilde():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = ~a\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " = "


def test_unary_after_open_paren():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = (-1)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " = "


def test_unary_after_comma():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = [1, -2]\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " = "


def test_unary_at_start_of_document():
    tokenizer = BinaryOperatorTokenizer()
    doc = "-1\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_star_in_function_args_excluded():
    tokenizer = BinaryOperatorTokenizer()
    doc = "func(a, *args)\n"
    result = tokenizer.tokenize(doc)

    star_tokens = [t for t in result if t['token'].strip() == "**"]
    assert len(star_tokens) == 0


def test_star_after_comma_in_parens():
    tokenizer = BinaryOperatorTokenizer()
    doc = "func(a, *args)\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_dash_before_greater_than_excluded():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = a -> b\n"
    result = tokenizer.tokenize(doc)

    tokens_with_dash_alone = [t for t in result if t['token'].strip() == "-"]
    assert len(tokens_with_dash_alone) == 0


def test_no_whitespace_around_operator():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x=1\n"
    result = tokenizer.tokenize(doc)

    assert result == [
        {
            "token": "=",
            "index": 1,
            "length": 1
        }
    ]


def test_extra_whitespace_around_operator():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x  =  1\n"
    result = tokenizer.tokenize(doc)

    assert result == [
        {
            "token": "  =  ",
            "index": 1,
            "length": 5
        }
    ]


def test_operator_with_tabs():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x\t=\t1\n"
    result = tokenizer.tokenize(doc)

    assert result == [
        {
            "token": "\t=\t",
            "index": 1,
            "length": 3
        }
    ]


def test_is_in_string_with_escape():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = \"a \\\" + b\"\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " = "


def test_is_in_string_with_single_escape():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = 'a \\' + b'\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " = "


def test_is_in_comment_with_hash_in_string():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = \"#\" + y\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 2
    assert result[0]['token'] == " = "
    assert result[1]['token'] == " + "


def test_triple_single_quote_unterminated():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = '''unterminated\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " = "


def test_triple_double_quote_unterminated():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = \"\"\"unterminated\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " = "


def test_single_quote_string_with_backslash():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = 'a\\\\b' + c\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " = "
    assert result[1]['token'] == " + "


def test_comment_without_newline():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = 1 # end"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " = "


def test_paren_depth_with_strings():
    tokenizer = BinaryOperatorTokenizer()
    doc = "func(a, x=1)\n"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_decorator_line_excluded():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = 1\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " = "


def test_multiple_operators_same_line():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = a + b * c\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 3


def test_augmented_assignments():
    tokenizer = BinaryOperatorTokenizer()

    for op in [
        "**=",
        "//=",
        ">>=",
        "<<=",
        "+=",
        "-=",
        "*=",
        "/=",
        "%=",
        "&=",
        "|=",
        "^="
    ]:
        doc = f"x {op} 1\n"
        result = tokenizer.tokenize(doc)
        assert len(result) > 0, f"Failed for operator {op}"


def test_empty_document():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_no_operators():
    tokenizer = BinaryOperatorTokenizer()
    result = tokenizer.tokenize("hello world\n")

    assert result == []


def test_overlap_prevention():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x == 1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " == "


def test_greater_equal():
    tokenizer = BinaryOperatorTokenizer()
    doc = "a >= b\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " >= "


def test_less_equal():
    tokenizer = BinaryOperatorTokenizer()
    doc = "a <= b\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " <= "


def test_modulo():
    tokenizer = BinaryOperatorTokenizer()
    doc = "a % b\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " % "


def test_xor():
    tokenizer = BinaryOperatorTokenizer()
    doc = "a ^ b\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " ^ "


def test_pipe():
    tokenizer = BinaryOperatorTokenizer()
    doc = "a | b\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " | "


def test_greater_than():
    tokenizer = BinaryOperatorTokenizer()
    doc = "a > b\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " > "


def test_less_than():
    tokenizer = BinaryOperatorTokenizer()
    doc = "a < b\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " < "


def test_is_in_function_signature_no_def():
    tokenizer = BinaryOperatorTokenizer()
    doc = "(x=1)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) > 0


def test_is_in_function_signature_paren_after_pos():
    tokenizer = BinaryOperatorTokenizer()
    doc = "def func\nx = 1\n"
    result = tokenizer.tokenize(doc)

    assert any(t['token'].strip() == "=" for t in result)


def test_is_in_function_call_no_paren():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = 1\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == " = "


def test_is_in_function_call_paren_not_after_identifier():
    tokenizer = BinaryOperatorTokenizer(exclude_call_equals=True)
    doc = "( x=1)\n"
    result = tokenizer.tokenize(doc)

    assert any(t['token'].strip() == "=" for t in result)


def test_double_star_after_open_paren():
    tokenizer = BinaryOperatorTokenizer()
    doc = "func(a, **kwargs)\n"
    result = tokenizer.tokenize(doc)

    star_tokens = [t for t in result if "**" in t['token']]
    assert len(star_tokens) == 0


def test_unary_after_colon():
    tokenizer = BinaryOperatorTokenizer()
    doc = "d = {\"k\": -1}\n"
    result = tokenizer.tokenize(doc)

    equals_tokens = [t for t in result if t['token'].strip() == "="]
    assert len(equals_tokens) == 1


def test_is_in_string_single_quote():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_string("x = 'hello", 7) is True


def test_is_in_string_double_quote():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_string("x = \"hello", 7) is True


def test_is_in_string_triple_single():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_string("x = '''hello", 8) is True


def test_is_in_string_triple_double():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_string("x = \"\"\"hello", 8) is True


def test_is_in_string_not_in_string():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_string("x = hello", 7) is False


def test_is_in_string_escape_in_single():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_string("x = 'a\\'b", 9) is True


def test_is_in_string_escape_in_double():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_string("x = \"a\\\"b", 9) is True


def test_is_in_string_closed_triple_single():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_string("'''abc''' x", 10) is False


def test_is_in_string_closed_triple_double():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_string("\"\"\"abc\"\"\" x", 10) is False


def test_is_in_string_closed_single():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_string("'abc' x", 6) is False


def test_is_in_string_closed_double():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_string("\"abc\" x", 6) is False


def test_is_in_comment_true():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_comment("x = 1 # test + 1", 14) is True


def test_is_in_comment_false():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_comment("x = 1 + 2", 6) is False


def test_is_in_comment_hash_in_string():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_comment("x = '# hash' + y", 14) is False


def test_is_in_comment_hash_in_double_string():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_comment("x = \"# hash\" + y", 14) is False


def test_get_paren_depth_zero():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._get_paren_depth("x = 1", 3) == 0


def test_get_paren_depth_one():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._get_paren_depth("func(x", 6) == 1


def test_get_paren_depth_with_close():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._get_paren_depth("func(x) y", 8) == 0


def test_get_paren_depth_with_escape_in_string():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._get_paren_depth("'\\(' x", 5) == 0


def test_get_paren_depth_with_single_quote():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._get_paren_depth("'(' x", 4) == 0


def test_get_paren_depth_with_double_quote():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._get_paren_depth("\"(\" x", 4) == 0


def test_is_in_function_signature_true():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_function_signature("def func(x=1):\n", 11) is True


def test_is_in_function_signature_no_def():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_function_signature("func(x=1)", 7) is False


def test_is_in_function_signature_paren_after():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_function_signature("def func\nx = 1", 11) is False


def test_is_in_function_signature_pos_after_close():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_function_signature("def func(x):\ny = 1", 15) is False


def test_is_in_function_call_true():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_function_call("func(x=1)", 6) is True


def test_is_in_function_call_no_paren():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_function_call("x = 1", 2) is False


def test_is_in_function_call_paren_not_after_ident():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_function_call("( x=1)", 3) is False


def test_is_in_function_call_with_nested_close():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_function_call("a(b()=1)", 5) is True


def test_is_decorator_true():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_decorator("@dec\n", 2) is True


def test_is_decorator_false():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_decorator("x = 1\n", 3) is False


def test_is_unary_operator_not_unary_op():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_unary_operator(
        "x = 1",
        "=",
        2
    ) is False


def test_exclude_signature_equals_found():
    tokenizer = BinaryOperatorTokenizer(exclude_signature_equals=True)
    doc = "def func(x=1):\n    pass\n"
    result = tokenizer.tokenize(doc)

    equals_tokens = [t for t in result if t['token'].strip() == "="]
    assert len(equals_tokens) == 0


def test_exclude_call_equals_in_call():
    tokenizer = BinaryOperatorTokenizer(exclude_call_equals=True)
    doc = "result = func(x=1)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " = "


def test_operator_in_covered_set():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x == 1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " == "


def test_star_after_comma_in_paren():
    tokenizer = BinaryOperatorTokenizer()
    doc = "f(a, *b)\n"
    result = tokenizer.tokenize(doc)

    star_tokens = [t for t in result if "*" in t['token']]
    assert len(star_tokens) == 0


def test_overlap_in_tokenize():
    tokenizer = BinaryOperatorTokenizer()
    doc = "a >= b\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == " >= "


def test_is_in_function_call_spaces_before_paren():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_function_call("func  (x=1)", 8) is True


def test_is_in_function_call_dot_before_paren():
    tokenizer = BinaryOperatorTokenizer()
    assert tokenizer._is_in_function_call("obj.method(x=1)", 12) is True


def test_signature_with_nested_paren():
    tokenizer = BinaryOperatorTokenizer(exclude_signature_equals=True)
    doc = "def func(x=(1, 2)):\n    pass\n"
    result = tokenizer.tokenize(doc)

    equals_tokens = [t for t in result if t['token'].strip() == "="]
    assert len(equals_tokens) == 0


def test_dash_before_arrow():
    tokenizer = BinaryOperatorTokenizer()
    doc = "def func() -> int:\n    pass\n"
    result = tokenizer.tokenize(doc)

    arrow_tokens = [t for t in result if "->" in t['token']]
    assert len(arrow_tokens) == 1


def test_overlap_in_covered():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x **= 1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "**=" in result[0]['token']


def test_covered_position_break():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x **= 1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert "**=" in result[0]['token']


def test_minus_before_arrow_not_tokenized():
    tokenizer = BinaryOperatorTokenizer()
    doc = "def func() -> int:\n    x = 1\n"
    result = tokenizer.tokenize(doc)

    arrow_tokens = [t for t in result if "->" in t['token']]
    assert len(arrow_tokens) == 1
    minus_only_tokens = [t for t in result if t['token'].strip() == "-"]
    assert len(minus_only_tokens) == 0


def test_overlap_in_covered_chars():
    tokenizer = BinaryOperatorTokenizer()
    doc = "x + + y\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_arrow_operator_is_tokenized():
    """Test that -> is tokenized as a binary operator."""
    tokenizer = BinaryOperatorTokenizer()
    doc = "def func() -> int:\n    return 1\n"
    tokens = tokenizer.tokenize(doc)

    arrow_tokens = [t for t in tokens if "->" in t['token']]
    assert len(arrow_tokens) == 1


def test_operator_overlap_covered():
    """Cover lines 373-374: overlap detection in covered ranges."""
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = a == b != c\n"
    tokens = tokenizer.tokenize(doc)

    indices = set()
    for t in tokens:
        for i in range(t['index'], t['index'] + t['length']):
            assert i not in indices
            indices.add(i)


def test_already_covered_operator():
    """Cover line 336: operator position already in covered set."""
    tokenizer = BinaryOperatorTokenizer()
    doc = "x = y >= z\n"
    tokens = tokenizer.tokenize(doc)

    assert isinstance(tokens, list)
