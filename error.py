class EmptyStackError(Exception):
    """Exception raised when calling pop on an empty stack."""

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Called pop on an empty stack.'


class IllegalConditionalOperatorError(Exception):
    """Exception raised when the input condition operator is illegal."""

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Illegal conditional operator!'


class NoneConditionError(Exception):
    """Exception raised when the input condition is None while root
    is not an operator.
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'The input condition must not be None when the root is' \
               'not an operator!'


class EffectSubjectError(Exception):
    """Exception raised when trying to apply an effect on a particle that's
    not its subject.
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'The particle being applied by this effect must be its subject.'


class UnknownTypeError:
    """Exception raised when receiving unexpected input data type.
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Unknown datatype.'


class UnknownShapeError:
    """Exception raised when receiving unexpected shape of the object.
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Object shape unknown.'
