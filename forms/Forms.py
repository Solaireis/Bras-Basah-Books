"""
Form classes used by BrasBasahBooks web app
"""

# Import WTForms
from wtforms import Form, validators, StringField, RadioField, SelectField,\
                    TextAreaField, EmailField, PasswordField, DateField, FileField

# Import custom validations (for password field)
from .Validations import ContainsLower, ContainsUpper, ContainsNumSymbol


class SignUpForm(Form):
    """ Sign up form used when signing up """

    # Email for customer
    email = EmailField("Email", [validators.Email(), validators.DataRequired()])


class SetPasswordForm(Form):
    """ Set up password form used after verifying email in sign up process """

    # Password for customer
    password = PasswordField("Set Password", [validators.InputRequired(),
                                              validators.Length(min=8, max=80),
                                              ContainsLower(), ContainsUpper(),
                                              ContainsNumSymbol()])

    # Confirm password for customer
    confirm = PasswordField("Confirm Password", [validators.EqualTo("password")])
