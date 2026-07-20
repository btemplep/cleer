"""Unit tests for PairedPunctuationTokenizer."""

import pytest

from cleer import PairedPunctuationTokenizer


def test_simple_list():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("x = [1, 2, 3]\n")

    assert len(result) == 1
    assert result[0]['token'] == "x = [1, 2, 3]"


def test_simple_function_call():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("func(a, b)\n")

    assert len(result) == 1
    assert result[0]['token'] == "func(a, b)"


def test_simple_dict():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("x = {\"a\": 1}\n")

    assert len(result) == 1
    assert result[0]['token'] == "x = {\"a\": 1}"


def test_nested_brackets():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("x = [[1, 2], [3, 4]]\n")

    assert len(result) == 1
    assert result[0]['token'] == "x = [[1, 2], [3, 4]]"


def test_multiline_list():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = [\n    1,\n    2\n]\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == "x = [\n    1,\n    2\n]"


def test_def_excluded():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("def func(a, b):\n    pass\n")

    assert result == []


def test_async_def_excluded():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("async def func(a, b):\n    pass\n")

    assert result == []


def test_decorator_excluded():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("@decorator(arg)\ndef func():\n    pass\n")

    assert result == []


def test_multiple_statements():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = [1, 2]\ny = (3, 4)\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 2


def test_overlapping_prevented():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = [func(1)]\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == "x = [func(1)]"


def test_skip_string_single_quote():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("x = 'hello [world]'\n")

    assert result == []


def test_skip_string_double_quote():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("x = \"hello [world]\"\n")

    assert result == []


def test_skip_triple_single_quote():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("x = '''hello [world]'''\n")

    assert result == []


def test_skip_triple_double_quote():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("x = \"\"\"hello [world]\"\"\"\n")

    assert result == []


def test_skip_comment():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("# x = [1, 2]\ny = 1\n")

    assert result == []


def test_comment_without_newline():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("# x = [1, 2]")

    assert result == []


def test_unmatched_bracket():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("x = [1, 2\n")

    assert result == []


def test_empty_document():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_no_punctuation():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("x = 1\n")

    assert result == []


def test_string_with_escape():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("x = 'a\\'s [test]'\n")

    assert result == []


def test_triple_quote_unterminated():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("'''[1, 2]\n")

    assert len(result) == 1


def test_string_in_brackets():
    tokenizer = PairedPunctuationTokenizer()
    result = tokenizer.tokenize("x = [\"hello\"]\n")

    assert len(result) == 1
    assert result[0]['token'] == "x = [\"hello\"]"


def test_comment_in_matching_close():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = [\n    1, # comment\n    2\n]\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_triple_single_in_matching_close():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = ['''text''']\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_triple_double_in_matching_close():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = [\"\"\"text\"\"\"]\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_single_quote_in_matching_close():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = ['text']\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_double_quote_in_matching_close():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = [\"text\"]\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_escape_in_matching_close():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = ['te\\'xt']\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_escape_in_double_matching_close():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = [\"te\\\"xt\"]\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1


def test_already_covered_skipped():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = [func(1, 2)]\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == "x = [func(1, 2)]"


def test_tokens_sorted():
    tokenizer = PairedPunctuationTokenizer()
    doc = "a = [1]\nb = (2)\n"
    result = tokenizer.tokenize(doc)

    for i in range(len(result) - 1):
        assert result[i]['index'] <= result[i + 1]['index']


def test_statement_start_at_beginning():
    tokenizer = PairedPunctuationTokenizer()
    doc = "[1, 2, 3]\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['index'] == 0


def test_curly_braces():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = {1, 2, 3}\n"
    result = tokenizer.tokenize(doc)

    assert result[0]['token'] == "x = {1, 2, 3}"


def test_comment_without_newline_in_matching():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = [1, # comment"
    result = tokenizer.tokenize(doc)

    assert result == []


def test_bracket_with_spaces_after_close():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = [1, 2]  \ny = 1\n"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_bracket_no_newline_after():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = [1, 2] + y"
    result = tokenizer.tokenize(doc)

    assert len(result) >= 1


def test_overlap_in_covered_ranges():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = [func(1, 2), other(3)]\n"
    result = tokenizer.tokenize(doc)

    assert len(result) == 1
    assert result[0]['token'] == "x = [func(1, 2), other(3)]"


def test_overlap_in_nested_paired_punctuation():
    tokenizer = PairedPunctuationTokenizer()
    doc = "x = foo([1, 2])\n"
    result = tokenizer.tokenize(doc)

    assert isinstance(result, list)
    indices = [t['index'] for t in result]
    assert len(indices) == len(set(indices))


def test_statement_in_covered_range():
    """Cover lines 228-229: overlap detection for covered ranges."""
    tokenizer = PairedPunctuationTokenizer()
    doc = "def func():\n    result = my_func([1, 2, 3], other_func([4, 5]))\n    return result\n"
    tokens = tokenizer.tokenize(doc)

    indices = [
        (
            t['index'],
            t['index'] + t['length']
        ) for t in tokens
    ]
    for i, (
        s1,
        e1
    ) in enumerate(indices):
        for j, (
            s2,
            e2
        ) in enumerate(indices):
            if i != j:
                assert not (s1 < e2 and s2 < e1)
