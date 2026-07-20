from cleer.formatters.max_newlines_formatter import MaxNewlinesFormatter
from cleer.formatters.max_space_formatter import MaxSpaceFormatter
from cleer.tokenizers.max_newlines_tokenizer import MaxNewlinesTokenizer


def test_max_newlines_formatter_inspect_returns_violation_message():
    formatter = MaxNewlinesFormatter()
    result = formatter.inspect("\n\n\n\n")

    assert result == "There should be no more than 2 consecutive blank lines."


def test_max_newlines_formatter_inspect_returns_none_for_acceptable():
    formatter = MaxNewlinesFormatter()
    result = formatter.inspect("\n\n\n")

    assert result is None


def test_max_newlines_formatter_format_reduces_to_three_newlines():
    formatter = MaxNewlinesFormatter()
    result = formatter.format("\n\n\n\n\n")

    assert result == "\n\n\n"


def test_max_newlines_formatter_format_five_newlines():
    formatter = MaxNewlinesFormatter()
    result = formatter.format("\n\n\n\n\n\n\n")

    assert result == "\n\n\n"


def test_max_space_formatter_format_rb_string_prefix():
    formatter = MaxSpaceFormatter()
    result = formatter.format('x = rb"hello  world"')

    assert result == 'x = rb"hello  world"'


def test_max_space_formatter_format_br_string_prefix():
    formatter = MaxSpaceFormatter()
    result = formatter.format('x = br"hello  world"')

    assert result == 'x = br"hello  world"'


def test_max_space_formatter_format_only_whitespace_returns_unchanged():
    formatter = MaxSpaceFormatter()
    result = formatter.format("    ")

    assert result == "    "


def test_max_space_formatter_format_empty_string_returns_unchanged():
    formatter = MaxSpaceFormatter()
    result = formatter.format("")

    assert result == ""


def test_max_newlines_tokenizer_document_ends_without_trailing_newline():
    tokenizer = MaxNewlinesTokenizer()
    document = "hello\n\n\n\nworld"
    tokens = tokenizer.tokenize(document)

    assert len(tokens) == 1
    assert tokens[0]["token"] == "\n\n\n\n"
    assert tokens[0]["index"] == 5
    assert tokens[0]["length"] == 4


def test_max_newlines_tokenizer_multiple_sequences_no_trailing_newline():
    tokenizer = MaxNewlinesTokenizer()
    document = "start\n\n\n\nmiddle\n\n\n\n\nend"
    tokens = tokenizer.tokenize(document)

    assert len(tokens) == 2
    assert tokens[0]["token"] == "\n\n\n\n"
    assert tokens[0]["index"] == 5
    assert tokens[0]["length"] == 4
    assert tokens[1]["token"] == "\n\n\n\n\n"
    assert tokens[1]["index"] == 15
    assert tokens[1]["length"] == 5


def test_max_newlines_tokenizer_newlines_at_end_no_content_after():
    tokenizer = MaxNewlinesTokenizer()
    document = "hello\n\n\n\n"
    tokens = tokenizer.tokenize(document)

    assert len(tokens) == 1
    assert tokens[0]["token"] == "\n\n\n\n"
    assert tokens[0]["index"] == 5
    assert tokens[0]["length"] == 4
