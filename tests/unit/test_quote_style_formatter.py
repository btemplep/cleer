import pytest

from cleer import QuoteStyleFormatter


def test_format_converts_single_to_double():
    formatter = QuoteStyleFormatter(style="\"")
    result = formatter.format("'hello'")

    assert result == "\"hello\""


def test_format_leaves_double_quotes_alone():
    formatter = QuoteStyleFormatter(style="\"")
    result = formatter.format("\"hello\"")

    assert result == "\"hello\""


def test_format_no_conversion_when_inner_contains_target():
    formatter = QuoteStyleFormatter(style="\"")
    result = formatter.format("'she said \"hi\"'")

    assert result == "'she said \"hi\"'"


def test_format_converts_double_to_single():
    formatter = QuoteStyleFormatter(style="'")
    result = formatter.format("\"hello\"")

    assert result == "'hello'"


def test_format_no_conversion_when_inner_contains_single():
    formatter = QuoteStyleFormatter(style="'")
    result = formatter.format("\"it's fine\"")

    assert result == "\"it's fine\""


def test_format_converts_triple_single_to_triple_double():
    formatter = QuoteStyleFormatter(style="\"")
    result = formatter.format("'''docstring'''")

    assert result == "\"\"\"docstring\"\"\""


def test_format_leaves_triple_double_alone():
    formatter = QuoteStyleFormatter(style="\"")
    result = formatter.format("\"\"\"docstring\"\"\"")

    assert result == "\"\"\"docstring\"\"\""


def test_format_no_conversion_triple_when_inner_contains_target():
    formatter = QuoteStyleFormatter(style="\"")
    result = formatter.format("'''has \"\"\" inside'''")

    assert result == "'''has \"\"\" inside'''"


def test_format_empty_string():
    formatter = QuoteStyleFormatter(style="\"")
    result = formatter.format("")

    assert result == ""


def test_inspect_returns_none_for_correct_style():
    formatter = QuoteStyleFormatter(style="\"")
    result = formatter.inspect("\"hello\"")

    assert result is None


def test_inspect_returns_message_for_wrong_style():
    formatter = QuoteStyleFormatter(style="\"")
    result = formatter.inspect("'hello'")

    assert result is not None
    assert "\"" in result


def test_inspect_returns_none_for_empty():
    formatter = QuoteStyleFormatter(style="\"")
    result = formatter.inspect("")

    assert result is None


def test_inspect_triple_quote_wrong_style():
    formatter = QuoteStyleFormatter(style="\"")
    result = formatter.inspect("'''docstring'''")

    assert result is not None
    assert "\"\"\"" in result


def test_inspect_triple_quote_correct_style():
    formatter = QuoteStyleFormatter(style="\"")
    result = formatter.inspect("\"\"\"docstring\"\"\"")

    assert result is None


def test_inspect_no_conversion_possible_returns_none():
    formatter = QuoteStyleFormatter(style="\"")
    result = formatter.inspect("'has \" inside'")

    assert result is None


def test_format_triple_double_to_triple_single():
    formatter = QuoteStyleFormatter(style="'")
    result = formatter.format("\"\"\"docstring\"\"\"")

    assert result == "'''docstring'''"


def test_format_triple_no_conversion_when_target_inside():
    formatter = QuoteStyleFormatter(style="'")
    result = formatter.format("\"\"\"has ''' inside\"\"\"")

    assert result == "\"\"\"has ''' inside\"\"\""
