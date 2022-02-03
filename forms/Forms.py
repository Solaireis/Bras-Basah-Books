"""
Form classes used by BrasBasahBooks web app
"""

# Import WTForms
from wtforms import Form, validators, StringField, RadioField,\
                    TextAreaField, EmailField, PasswordField, FileField,\
                    SelectField, IntegerField, SubmitField, DecimalField

# Import custom validations (for password field)
from .Validations import ContainsLower, ContainsUpper, ContainsNumSymbol, ValidUsername

# Import validation for file upload
from flask_wtf.file import FileAllowed, FileRequired


class SignUpForm(Form):
    """ Sign up form used when signing up """

    # Username
    username = StringField("Username", [validators.InputRequired(),
                                        validators.Length(min=3, max=20),
                                        ValidUsername()])

    # Email
    email = EmailField("Email", [validators.InputRequired(), validators.Email()])

    # Password
    password = PasswordField("Password", [validators.InputRequired(),
                                          validators.Length(min=8, max=80),
                                          ContainsLower(), ContainsUpper(),
                                          ContainsNumSymbol()])

    # Confirm password
    confirm = PasswordField("Confirm Password", [validators.InputRequired(),
                                                 validators.EqualTo("password")])


class LoginForm(Form):
    """ Login form used for logging in """

    # Username / Email
    username = StringField("Username / Email", [validators.InputRequired()])

    # Password
    password = PasswordField("Password", [validators.InputRequired()])


class AccountPageForm(Form):
    """ Account page form used for editing account """

    # Name
    name = StringField("Name", [validators.Optional(), validators.Length(min=1)])

    # Gender
    gender = RadioField("Gender", [validators.Optional()], choices=[("M", "Male"), ("F", "Female"), ("O", "Others")])


class ChangePasswordForm(Form):
    """ Changing password form used for changing password """

    # Current password
    current_password = PasswordField("Current Password", [validators.InputRequired()])

    # New password
    new_password = PasswordField("New Password", [validators.InputRequired(),
                                                  validators.Length(min=8, max=80),
                                                  ContainsLower(), ContainsUpper(),
                                                  ContainsNumSymbol()])

    # Confirm password
    confirm_password = PasswordField("Confirm Password", [validators.InputRequired(),
                                                          validators.EqualTo("new_password")])



class AddBookForm(Form):
    """ Form used for adding books into inventory """

    language = SelectField('Language', [validators.Optional()], default='')
    language2 = StringField('Language', [validators.Optional()])
    category = SelectField('Category', [validators.Optional()], default='')
    category2 = StringField('Category', [validators.Optional()])
    age = SelectField('Age', [validators.InputRequired()], choices=[('', 'Select'), ('Children', 'Children'), ('Teenagers', 'Teenagers'), ('Young Adults', 'Young Adults'), ('Adults', 'Adults')], default='')
    action = RadioField('Action', [validators.InputRequired()], choices=[('Buy', 'Buy'), ('Rent', 'Rent'), ('Buy and Rent', 'Buy and Rent')])
    title = StringField('Title', [validators.InputRequired("Title is required")])
    author = StringField('Author', [validators.InputRequired("Author is required")])
    price = DecimalField('Price', [validators.InputRequired("Price is required")], places=2, rounding=None)
    qty = IntegerField('Quantity', [validators.InputRequired("Quantity is required")])
    desc = TextAreaField('Description', [validators.Length(min=1), validators.InputRequired("Description is required")])
    img = FileField('Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])

    def validate(self, extra_validators=None):
        if not super(AddBookForm, self).validate():
            return False

        if not self.language.data and not self.language2.data:
            msg = 'Choose a language'
            self.language.errors.append(msg)
            self.language2.errors.append(msg)
            return False

        if not self.category.data and not self.category2.data:
            msg = 'Choose a category'
            self.category.errors.append(msg)
            self.category2.errors.append(msg)
            return False

        return True

