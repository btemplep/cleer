from cleer import PyDocstringSpaceTokenizer


def test_empty_document():
    tokenizer = PyDocstringSpaceTokenizer()
    result = tokenizer.tokenize("")

    assert result == []


def test_no_definitions():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "x = 1\ny = 2\n"
    result = tokenizer.tokenize(document)

    assert result == []


def test_def_no_docstring():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo():\n    pass\n"
    result = tokenizer.tokenize(document)

    assert result == []


def test_def_with_docstring_no_extra_space():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo():\n    \"\"\"Doc.\"\"\"\n"
    result = tokenizer.tokenize(document)

    assert result == []


def test_def_with_extra_blank_line():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo():\n\n    \"\"\"Doc.\"\"\"\n"
    result = tokenizer.tokenize(document)

    assert result == [
        {
            "token": "\n\n    ",
            "index": 10,
            "length": 6
        }
    ]


def test_class_with_extra_blank_line():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "class Foo:\n\n    \"\"\"Doc.\"\"\"\n"
    result = tokenizer.tokenize(document)

    assert result == [
        {
            "token": "\n\n    ",
            "index": 10,
            "length": 6
        }
    ]


def test_async_def_with_extra_blank():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "async def foo():\n\n    \"\"\"Doc.\"\"\"\n"
    result = tokenizer.tokenize(document)

    assert result == [
        {
            "token": "\n\n    ",
            "index": 16,
            "length": 6
        }
    ]


def test_multiline_signature():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo(\n    a,\n    b\n):\n\n    \"\"\"Doc.\"\"\"\n"
    result = tokenizer.tokenize(document)

    assert result == [
        {
            "token": "\n\n    ",
            "index": 24,
            "length": 6
        }
    ]


def test_single_quote_docstring():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo():\n\n    '''Doc.'''\n"
    result = tokenizer.tokenize(document)

    assert result == [
        {
            "token": "\n\n    ",
            "index": 10,
            "length": 6
        }
    ]


def test_multiple_definitions():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo():\n    \"\"\"No extra.\"\"\"\n\ndef bar():\n\n    \"\"\"Extra.\"\"\"\n\ndef baz():\n    \"\"\"No extra.\"\"\"\n"
    result = tokenizer.tokenize(document)

    assert len(result) == 1
    assert result[0]['token'] == "\n\n    "


def test_indented_method():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "class Foo:\n    \"\"\"Class doc.\"\"\"\n\n    def bar(self):\n\n        \"\"\"Method doc.\"\"\"\n"
    result = tokenizer.tokenize(document)

    assert len(result) == 1
    assert result[0]['token'] == "\n\n        "


def test_no_token_when_next_content_not_docstring():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo():\n\n    x = 1\n"
    result = tokenizer.tokenize(document)

    assert result == []


def test_next_content_past_end_of_file():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo():\n    pass"
    result = tokenizer.tokenize(document)

    assert result == []


def test_multiline_sig_return_type_on_next_line():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo(\n    a,\n    b\n) -> str:\n\n    \"\"\"Doc.\"\"\"\n"
    result = tokenizer.tokenize(document)

    assert result == [
        {
            "token": "\n\n    ",
            "index": 31,
            "length": 6
        }
    ]


def test_signature_no_colon():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo()\n    \"\"\"Doc.\"\"\"\n"
    result = tokenizer.tokenize(document)

    assert result == []


def test_multiline_sig_with_return_type_colon_on_next_line():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo(\n    a\n)\n-> str:\n\n    \"\"\"Doc.\"\"\"\n"
    result = tokenizer.tokenize(document)

    assert len(result) == 1


def test_multiline_sig_with_blank_then_return_type_colon():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo(\n    a\n)\n\n-> str:\n\n    \"\"\"Doc.\"\"\"\n"
    result = tokenizer.tokenize(document)

    assert len(result) == 1


def test_sig_no_colon_no_arrow_after_paren():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo(\n    a\n)\nx = 1\n"
    result = tokenizer.tokenize(document)

    assert result == []


def test_unmatched_paren_returns_def_line():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo(\n    a\n\n    \"\"\"Doc.\"\"\"\n"
    result = tokenizer.tokenize(document)

    assert result == []


def test_def_at_end_of_file_only_blank_lines():
    tokenizer = PyDocstringSpaceTokenizer()
    document = "def foo():\n\n"
    result = tokenizer.tokenize(document)

    assert result == []
