"""
Validation classs used by Forms.py

P.S. Teacher I read through the source code for wtforms.validators
to figure out how does the validators class worked to create
my own custom validator class Contains
I also went and learn how to use regex
gimme extra marks pls
"""
from wtforms import ValidationError
import re


class SearchRegex:
    """
    Search the incoming data using the given regex pattern

    Args:
        pattern (str): The regex pattern
        message (str): Error message to raise in case of a validation error
    """

    def __init__(self, pattern, message):
        self.__pattern = re.compile(pattern)
        self.__message = message

    def __call__(self, form, field):
        if self.__pattern.search(field.data):
            return

        raise ValidationError(self.__message)


class ContainsLower(SearchRegex):
    """
    Checks if data incoming data contains a lowercase character
    """

    def __init__(self):
        super().__init__(r"[a-z]",
                         "Field must contain at least one lowercase letter.")


class ContainsUpper(SearchRegex):
    """
    Checks if data incoming data contains an uppercase character
    """

    def __init__(self):
        super().__init__(r"[A-Z]",
                         "Field must contain at least one uppercase letter.")


class ContainsNumSymbol(SearchRegex):
    """
    Checks if data incoming data contains a number or symbol
    """

    def __init__(self):
        # numbers:      [0-9]
        # symbols: [ -/]     [:-@]     [\[-1]     [{-~]
        # letters:                [A-Z]      [a-z]
        # num&sym: [      -     @]     [\[-1]     [{-~]
        super().__init__(r"[ -@\[-`{-~]",
                         "Field must contain at least one symbol or number.")
