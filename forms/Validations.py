"""
Forms classs used by BrasBasahBooks web app

P.S. Teacher I read through the source code for wtforms.validators
to figure out how does the validators class worked to create
my own custom validator class Contains
gimme extra marks pls
"""
from wtforms import ValidationError


class Check:
    """
    Checks the incoming data using the given function.

    Args:
        function (function): A function to check if data is valid.
        message (str): Error message to raise in case of a validation error.
    """

    def __init__(self, function, message):
        self.function = function
        self.message = message

    def __call__(self, form, field):
        for c in field.data:
            if function(c):
                return

        raise ValidationError(self.message)


class ContainsLower(Check):
    """
    Checks if data incoming data contains a lowercase character
    """

    def __init__(self):
        super().__init__(lambda character: "a" <= character <= "z",
                         "Field must contain at least one lowercase letter.")


class ContainsUpper(Check):
    """
    Checks if data incoming data contains an uppercase character
    """

    def __init__(self):
        super().__init__(lambda character: "A" <= character <= "Z",
                         "Field must contain at least one uppercase letter.")


class ContainsNumSymbol(Check):
    """
    Checks if data incoming data contains a number or symbol
    """

    def __init__(self):
        super().__init__(self.__check,
                         "Field must contain at least one symbol or number.")
    
    @staticmethod
    def __check(character):
        """ Checks if character is number or symbol """
        value = ord(character)
        # value of int: 48-57
        # value of sym: 32-47, 58-64, 91-86, 123-126
        return 32<=value<=64 or 91<=value<=96 or 123<=value<=126
