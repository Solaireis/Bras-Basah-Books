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
from flask_wtf.file import FileAllowed


class SignUpForm(Form):
    """ Sign up form used when signing up """

    # Username
    username = StringField("Username", [validators.InputRequired(message=""),
                                        validators.Length(min=3, max=20, message=""),
                                        ValidUsername(message="Username can only contain letters, numbers, and underscores")])

    # Email
    email = EmailField("Email", [validators.InputRequired(message=""),
                                 validators.Email(message=""),
                                 validators.Length(max=320, message="")])

    # Password
    password = PasswordField("Password", [validators.InputRequired(message=""),
                                          validators.Length(min=8, max=80, message=""),
                                          ContainsLower(message="Password must contain at least one lowercase letter"),
                                          ContainsUpper(message="Password must contain at least one uppercase letter"),
                                          ContainsNumSymbol(message="Password must contain at least one symbol or number")])

    # Confirm password
    confirm = PasswordField("Confirm Password", [validators.InputRequired(message=""),
                                                 validators.Length(min=8, max=80, message=""),
                                                 validators.EqualTo("password", message="Password entered is different")])


class LoginForm(Form):
    """ Login form used for logging in """

    # Username / Email
    username = StringField("Username / Email", [validators.InputRequired(message="")])

    # Password
    password = PasswordField("Password", [validators.InputRequired(message="")])


class AccountPageForm(Form):
    """ Account page form used for editing account """

    # Picture
    picture = FileField("Picture", [validators.Optional(),
                                    FileAllowed(["jpg", "jpeg", "png"], message="File uploaded is not in an accepted format")])

    # Name
    name = StringField("Name", [validators.Optional(),
                                validators.Regexp("^[a-zA-Z ]*$", message="Name should only contain letters and spaces"),
                                validators.Length(min=2, max=26, message="Name should be 2-26 characters long")])

    # Gender
    gender = RadioField("Gender", [validators.Optional()], choices=[("M", "Male"), ("F", "Female"), ("O", "Others")])


class ChangePasswordForm(Form):
    """ Changing password form used for changing password """

    # Current password
    current_password = PasswordField("Current Password", [validators.InputRequired(message="")])

    # New password
    new_password = PasswordField("New Password", [validators.InputRequired(message=""),
                                                  validators.Length(min=8, max=80, message=""),
                                                  ContainsLower(message="Password must contain at least one lowercase letter"),
                                                  ContainsUpper(message="Password must contain at least one uppercase letter"),
                                                  ContainsNumSymbol(message="Password must contain at least one symbol or number")])

    # Confirm password
    confirm_password = PasswordField("Confirm Password", [validators.InputRequired(message=""),
                                                          validators.Length(min=8, max=80, message=""),
                                                          validators.EqualTo("new_password", message="Password entered is different")])


class ForgetPasswordForm(Form):
    """ Forget password form used when setting new password """

    # New password
    new_password = PasswordField("New Password", [validators.InputRequired(message=""),
                                                  validators.Length(min=8, max=80, message=""),
                                                  ContainsLower(message="Password must contain at least one lowercase letter"),
                                                  ContainsUpper(message="Password must contain at least one uppercase letter"),
                                                  ContainsNumSymbol(message="Password must contain at least one symbol or number")])

    # Confirm password
    confirm_password = PasswordField("Confirm Password", [validators.InputRequired(message=""),
                                                          validators.Length(min=8, max=80, message=""),
                                                          validators.EqualTo("new_password", message="Password entered is different")])


class CreateUserForm(SignUpForm):
    """ Create user form used when creating new users """

    # User Type
    user_type = SelectField("User Type", [validators.InputRequired(message="")],
                            choices=[("", "Select User Type"), ("C", "Customer"), ("A", "Admin")],
                            default="")

class DeleteUserForm(Form):
    """ Delete user form used when deleting new users """

    # User ID
    user_id = StringField(validators=[validators.InputRequired(message="")])



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
