"""Unit tests for UnaryOperatorTokenizer and UnaryOperatorSpaceFormatter."""

from cleer import UnaryOperatorSpaceFormatter, UnaryOperatorTokenizer


def test_formatter_format_removes_space_minus():
    formatter = UnaryOperatorSpaceFormatter()
    result = formatter.format("- 1")

    assert result == "-1"


def test_formatter_format_removes_space_plus():
    formatter = UnaryOperatorSpaceFormatter()
    result = formatter.format("+ 2")

    assert result == "+2"


def test_formatter_format_removes_space_tilde():
    formatter = UnaryOperatorSpaceFormatter()
    result = formatter.format("~ x")

    assert result == "~x"


def test_formatter_format_leaves_no_space_unchanged():
    formatter = UnaryOperatorSpaceFormatter()
    result = formatter.format("-1")

    assert result == "-1"


def test_formatter_inspect_returns_none_when_no_space():
    formatter = UnaryOperatorSpaceFormatter()
    result = formatter.inspect("-1")

    assert result is None


def test_formatter_inspect_returns_message_when_space_present():
    formatter = UnaryOperatorSpaceFormatter()
    result = formatter.inspect("- 1")

    assert result is not None
    assert "Unary operators" in result


def test_formatter_format_single_char_token():
    formatter = UnaryOperatorSpaceFormatter()
    result = formatter.format("-")

    assert result == "-"


def test_formatter_format_non_operator_token():
    formatter = UnaryOperatorSpaceFormatter()
    result = formatter.format("x")

    assert result == "x"


def test_formatter_inspect_returns_none_for_single_char():
    formatter = UnaryOperatorSpaceFormatter()
    result = formatter.inspect("-")

    assert result is None


def test_tokenizer_finds_unary_after_comma():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = foo(1, - 2)\n")

    assert len(result) == 1
    assert result[0]['token'] == "- "
    assert result[0]['index'] == 11


def test_tokenizer_finds_unary_after_newline():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x =\n    - 1\n")

    assert len(result) == 1
    assert result[0]['token'] == "- "


def test_tokenizer_does_not_tokenize_binary_minus():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = 5 - 1\n")

    assert result == []


def test_tokenizer_skips_operators_in_double_quote_string():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize('x = "- 1"\n')

    assert result == []


def test_tokenizer_skips_operators_in_single_quote_string():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = '- 1'\n")

    assert result == []


def test_tokenizer_skips_operators_in_comments():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("# - 1\n")

    assert result == []


def test_tokenizer_finds_unary_after_return_keyword():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("return - 1\n")

    assert len(result) == 1
    assert result[0]['token'] == "- "


def test_tokenizer_finds_unary_after_yield_keyword():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("yield - x\n")

    assert len(result) == 1
    assert result[0]['token'] == "- "


def test_tokenizer_finds_unary_after_equals():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = - 5\n")

    assert len(result) == 1
    assert result[0]['token'] == "- "
    assert result[0]['index'] == 4
    assert result[0]['length'] == 2


def test_tokenizer_finds_unary_tilde():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = ~ y\n")

    assert len(result) == 1
    assert result[0]['token'] == "~ "


def test_tokenizer_does_not_tokenize_no_space_after_operator():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = -1\n")

    assert result == []


def test_tokenizer_finds_unary_after_open_paren():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = (- 1)\n")

    assert len(result) == 1
    assert result[0]['token'] == "- "


def test_tokenizer_finds_unary_after_open_bracket():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = [- 1]\n")

    assert len(result) == 1
    assert result[0]['token'] == "- "


def test_tokenizer_finds_unary_plus_after_equals():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = + 5\n")

    assert len(result) == 1
    assert result[0]['token'] == "+ "


def test_tokenizer_skips_triple_double_quote_string():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize('x = """- 1"""\n')

    assert result == []


def test_tokenizer_skips_triple_single_quote_string():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = '''- 1'''\n")

    assert result == []


def test_tokenizer_handles_escape_in_double_string():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize('x = "a\\"- 1"\n')

    assert result == []


def test_tokenizer_handles_escape_in_single_string():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = 'a\\'- 1'\n")

    assert result == []


def test_tokenizer_empty_document():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_tokenizer_no_operators():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("hello world\n")

    assert result == []


def test_tokenizer_unary_at_start_of_document():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("- 1\n")

    assert len(result) == 1
    assert result[0]['token'] == "- "
    assert result[0]['index'] == 0


def test_tokenizer_comment_without_newline():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("# - 1")

    assert result == []


def test_tokenizer_unary_after_not_keyword():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = not - 1\n")

    assert len(result) == 1
    assert result[0]['token'] == "- "


def test_tokenizer_unary_after_colon():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("d = {\"k\": - 1}\n")

    assert len(result) == 1
    assert result[0]['token'] == "- "


def test_tokenizer_multiple_unary_operators():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = [- 1, + 2, ~ y]\n")

    assert len(result) == 3
    assert result[0]['token'] == "- "
    assert result[1]['token'] == "+ "
    assert result[2]['token'] == "~ "


def test_tokenizer_unterminated_triple_double_string():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize('x = """- 1\n')

    assert result == []


def test_tokenizer_unterminated_triple_single_string():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = '''- 1\n")

    assert result == []


def test_tokenizer_token_index_and_length():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = - 5\n")

    assert result[0]['index'] == 4
    assert result[0]['length'] == 2


def test_tokenizer_finds_unary_after_lambda():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("f = lambda: - x\n")

    assert len(result) == 1
    assert result[0]['token'] == "- "


def test_tokenizer_multiple_spaces_between_operator_and_operand():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = -   5\n")

    assert len(result) == 1
    assert result[0]['token'] == "-   "
    assert result[0]['length'] == 4


def test_tokenizer_tabs_between_operator_and_operand():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = -\t5\n")

    assert len(result) == 1
    assert result[0]['token'] == "-\t"
    assert result[0]['length'] == 2


def test_tokenizer_is_in_string_single_quote():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_string("x = 'hello", 7) is True


def test_tokenizer_is_in_string_double_quote():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_string('x = "hello', 7) is True


def test_tokenizer_is_in_string_triple_single():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_string("x = '''hello", 8) is True


def test_tokenizer_is_in_string_triple_double():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_string('x = """hello', 8) is True


def test_tokenizer_is_in_string_not_in_string():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_string("x = hello", 7) is False


def test_tokenizer_is_in_string_escape_in_single():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_string("x = 'a\\'b", 9) is True


def test_tokenizer_is_in_string_escape_in_double():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_string('x = "a\\"b', 9) is True


def test_tokenizer_is_in_string_closed_triple_single():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_string("'''abc''' x", 10) is False


def test_tokenizer_is_in_string_closed_triple_double():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_string('"""abc""" x', 10) is False


def test_tokenizer_is_in_string_closed_single():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_string("'abc' x", 6) is False


def test_tokenizer_is_in_string_closed_double():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_string('"abc" x', 6) is False


def test_tokenizer_is_in_comment_true():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_comment("x = 1 # test + 1", 14) is True


def test_tokenizer_is_in_comment_false():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_comment("x = 1 + 2", 6) is False


def test_tokenizer_is_in_comment_hash_in_single_string():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_comment("x = '# hash' + y", 14) is False


def test_tokenizer_is_in_comment_hash_in_double_string():
    tokenizer = UnaryOperatorTokenizer()

    assert tokenizer._is_in_comment('x = "# hash" + y', 14) is False


def test_tokenizer_finds_unary_after_open_brace():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = {- 1}\n")

    assert len(result) == 1
    assert result[0]['token'] == "- "


def test_tokenizer_does_not_tokenize_binary_plus():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = 5 + 1\n")

    assert result == []


def test_tokenizer_inline_comment_after_code():
    tokenizer = UnaryOperatorTokenizer()
    result = tokenizer.tokenize("x = - 5 # - 1\n")

    assert len(result) == 1
    assert result[0]['token'] == "- "
    assert result[0]['index'] == 4
