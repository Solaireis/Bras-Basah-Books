"""
Form classes used by BrasBasahBooks web app
"""

# Import WTForms
from wtforms import Form, validators, StringField, RadioField, SelectField,\
                    TextAreaField, EmailField, PasswordField, DateField

# Import custom validations (for password field)
from .Validations import ContainsLower, ContainsUpper, ContainsNumSymbol


class SignUpForm(Form):
    email = EmailField("Email", [validators.Email(), validators.DataRequired()])


class SetPasswordForm(Form):
    password = PasswordField("Set Password", [validators.InputRequired(),
                                              validators.Length(min=8, max=80),
                                              ContainsLower(), ContainsUpper(),
                                              ContainsNumSymbol()])
    confirm = PasswordField("Confirm Password", [validators.EqualTo("password")])
