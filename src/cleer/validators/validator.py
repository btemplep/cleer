"""See :class:`Validator`."""

__all__ = [
    "Validator"
]


class Validator:
    """Validator base class.

    Validators are used by cleer to verify that a file has valid syntax.
    This is useful to make sure the files with bad syntax are not attempted to be formatted.

    Validators must implement the `validate` method.
    """


    def validate(self, document: str) -> str | None:
        """Validate a document.

        Validators must implement this method.

        Parameters
        ----------
        document : str
            Document to validate.

        Returns
        -------
        str | None
            Error message. `None` if the document is valid.
        """
        raise NotImplementedError("Validator classes must implement the validator class!")
