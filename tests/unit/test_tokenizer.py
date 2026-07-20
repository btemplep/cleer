"""Unit tests for base Tokenizer class."""

import pytest

from cleer import Tokenizer
from cleer.exceptions import NotImplementedError


def test_tokenize_raises_not_implemented():
    tokenizer = Tokenizer()
    with pytest.raises(
        NotImplementedError,
        match="Tokenizer classes must implement the tokenize method!"
    ):
        tokenizer.tokenize("some document")
