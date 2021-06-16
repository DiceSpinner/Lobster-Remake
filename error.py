class EmptyStackError(Exception):
    """Exception raised when calling pop on an empty stack."""

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Error! Called pop on an empty stack.'


class IllegalConditionalOperatorError(Exception):
    """Exception raised when the input condition operator is illegal."""

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Error! Illegal conditional operator!'

