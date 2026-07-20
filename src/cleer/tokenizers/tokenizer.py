__all__ = ["Tokenizer"]


from typing import List

from cleer.exceptions import NotImplementedError


class Tokenizer:
    """Tokenizer base class.

    Tokenizers are used by cleer to take a document string and return tokens.

    Tokenizers must implement the `tokenize` method.

    Tokens from the same tokenizer **cannot** overlap.
    """
    emits_token_type: str = ""


    def tokenize(self, document: str) -> List[dict]:
        """Tokenize a document.

        Tokens from a single call of tokenize cannot overlap.

        Tokenizers must implement this method.

        Parameters
        ----------
        document : str
            Document to tokenize.

        Returns
        -------
        List[TokenResult]
            List of token results.
        """
        raise NotImplementedError("Tokenizer classes must implement the tokenize method!")
