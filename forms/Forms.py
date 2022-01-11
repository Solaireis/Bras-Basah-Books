"""
Form classes used by BrasBasahBooks web app
"""

# Import WTForms
from wtforms import Form, validators, StringField, RadioField,\
                    TextAreaField, EmailField, PasswordField, FileField

# Import custom validations (for password field)
from .Validations import ContainsLower, ContainsUpper, ContainsNumSymbol


class SignUpForm(Form):
    """ Sign up form used when signing up """

    # Email
    email = EmailField("Email", [validators.Email(), validators.DataRequired()])

    # Password
    password = PasswordField("Password", [validators.InputRequired(),
                                              validators.Length(min=8, max=80),
                                              ContainsLower(), ContainsUpper(),
                                              ContainsNumSymbol()])

    # Confirm password
    confirm = PasswordField("Confirm Password", [validators.EqualTo("password")])

    # Username
    username = StringField("Username", [validators.Optional()])


class LoginForm(Form):
    """ Login form used for logging in """

    # Email
    email = EmailField("Email", [validators.Email(), validators.DataRequired()])

    # Password
    password = PasswordField("Password", [validators.InputRequired()])
