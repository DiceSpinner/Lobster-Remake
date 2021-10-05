class EmptyStackError(Exception):
    """Exception raised when calling pop on an empty stack."""

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Called pop on an empty stack.'


class CollidedObjectKeyError(Exception):
    """Exception raised when name collision of predefined objects occurs."""

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Cannot construct predefined-objects with the same keys.'


class InvalidConstructorError(Exception):
    """Exception raised when name collision of predefined objects occurs."""

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Cannot construct predefined-objects with the given constructor.'


class EffectSubjectError(Exception):
    """Exception raised when trying to apply an effect on a particle that's
    not its subject.
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'The particle being applied by this effect must be its subject.'


class UnknownShapeError(Exception):
    """Exception raised when receiving unexpected shape of the object.
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Object shape unknown.'


class AttackOnCoolDownError(Exception):
    """Exception raised when the attack is still on cool down.
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Attack still on cool down!'


class InvalidConstructionInfo(Exception):
    """ Exception raised when the provided info to initialize a particle is not valid
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Invalid construction info!'


class UnknownStaminaCostError(Exception):
    """ Exception raised when the stamina required to perform the action is
    unknown
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Stamina cost unknown!'


class UnknownManaCostError(Exception):
    """ Exception raised when the mana required to perform the action is
    unknown
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Mana cost unknown!'


class UnknownCooldownError(Exception):
    """ Exception raised when the cooldown of the spell is unknown
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Spell cooldown unknown!'


class InvalidAttrTypeError(Exception):
    """ Exception raised when the input type of an attribute is invalid
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'Invalid attribute type!'


class UnknownTextureError(Exception):
    """ Exception raised when the input texture name is unknown.
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'The given texture name does not exist!'


class UnknownAttributeError(Exception):
    """ Exception raised when one of the variables of the expression tree used
    for objects evaluation is unknown.
    """

    def __str__(self) -> str:
        """ Return a string representation of this error. """
        return 'All variables must have prefixes for evaluation!'
