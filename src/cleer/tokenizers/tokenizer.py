__all__ = [
    "TokenResult",
    "Tokenizer"
]


from typing import TypedDict

from cleer.exceptions import NotImplementedError


class TokenResult(TypedDict):
    """Token and location from a tokenizer.

    Attributes
    ----------
    token : str
        Token from a tokenizer.
    index : int
        Index where the token starts in the source document string, inclusive.
    length : int
        Character length of the token.
    """
    token: str
    index: int
    length: int


class Tokenizer:
    """Tokenizer base class.

    Tokenizers are used by cleer to take a document string and return tokens.

    Tokenizers must implement the `tokenize` method.

    Tokens from the same tokenizer **cannot** overlap.
    """
    emits_token_type: str = ""


    def tokenize(self, document: str) -> list[TokenResult]:
        """Tokenize a document.

        Tokens from a single call of tokenize cannot overlap.

        Tokenizers must implement this method.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Returns
        -------
        list[TokenResult]
            List of token results.
        """
        raise NotImplementedError("Tokenizer classes must implement the tokenize method!")
