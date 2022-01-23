"""
Form classes used by BrasBasahBooks web app
"""

# Import WTForms
from wtforms import Form, validators, StringField, RadioField,\
                    TextAreaField, EmailField, PasswordField, FileField,\
                    SelectField, IntegerField, SubmitField, DecimalField

# Import custom validations (for password field)
from .Validations import ContainsLower, ContainsUpper, ContainsNumSymbol

# Import validation for file upload
from flask_wtf.file import FileAllowed, FileRequired


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
    confirm = PasswordField("Confirm Password", [validators.InputRequired(),
                                                 validators.EqualTo("password")])

    # Username
    username = StringField("Username", [validators.Length(max=25)])


class LoginForm(Form):
    """ Login form used for logging in """

    # Email
    email = EmailField("Email", [validators.Email(), validators.DataRequired()])

    # Password
    password = PasswordField("Password", [validators.InputRequired()])


class AccountPageForm(Form):
    """ Account page form used for editing account """

    # Username
    username = StringField("Name", [validators.Length(max=25)])

    # Gender
    gender = RadioField("Gender", choices=[("M", "Male"), ("F", "Female"), ("O", "Others")])


class AddBookForm(Form):
    """ Form used for adding books into inventory """

    language = SelectField('Language', [validators.InputRequired()], choices=[('', 'Select'), ('English', 'English'), ('Chinese', 'Chinese'), ('Malay', 'Malay'), ('Tamil', 'Tamil')], default='')
    category = SelectField('Category', [validators.InputRequired()], choices=[('', 'Select'), ('Action & Adventure', 'Action & Adventure'), ('Classic', 'Classic'), ('Comic', 'Comic'), ('Detective & Mystery', 'Detective & Mystery')], default='')
    age = SelectField('Age', [validators.InputRequired()], choices=[('', 'Select'), ('Children', 'Children'), ('Teenagers', 'Teenagers'), ('Young Adults', 'Young Adults'), ('Adults', 'Adults')], default='')
    action = RadioField('Action', [validators.InputRequired()], choices=[('Buy', 'Buy'), ('Rent', 'Rent'), ('Buy and Rent', 'Buy and Rent')])
    title = StringField('Title', [validators.InputRequired("Title is required")])
    author = StringField('Author', [validators.InputRequired("Author is required")])
    price = DecimalField('Price', [validators.InputRequired("Price is required")], places=2, rounding=None)
    qty = IntegerField('Quantity', [validators.InputRequired("Quantity is required")])
    desc = TextAreaField('Description', [validators.Length(min=1), validators.InputRequired("Description is required")])
    img = FileField('Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
