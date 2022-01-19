#   the class for creating an Enquiry
#   sources used in this;
#   1) Unique Id generator:
#   https://docs.python.org/3/library/uuid.html#uuid.uuid5
#   2) is UUID a hash? :
#   https://www.quora.com/Is-UUID-a-hash
import uuid  # imports the module for universally unique identifiers
from users.User import User
from users.Customer import Customer
from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, EmailField, DateField

class Enquiry(Form):
    name = StringField('Username', [validators.Length(min=1, max=100), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    enquiry_type = SelectField('Enquiry Type', [validators.DataRequired()], choices=[('', 'Select'), ('B', 'Question about Books'), ('F', 'Feedback')], default='')
    comments = TextAreaField('Comments', [validators.Optional()])


class UserEnquiry:
    def __init__(self, name, email, enquiry_type, comments):
        # Args: for the self
        #
        #     user_id: the id of the user taken from the account
        #     name: the name of the user
        #     email: email of the user
        #     comments: what is the comments
        #
        # Notes:
        #     realised that i need user class and also guest accounts, therefore it has to obtained from them

        self.__enquiry_id = str(uuid.uuid4())  # enquiry_id: unique id of the enquiry which is needed for matching ids together
        self.__user_id = None  # to link with the user
        self.__name = name
        self.__email = email
        self.__enquiry_type = enquiry_type
        self.__comments = comments


    # setting mutators and assessor methods

    # enquiry id
    def get_enquiry_id(self):
        return self.__enquiry_id

    #def set_enquiry_id(self, enquiry_id):
        #self.__enquiry_id = enquiry_id

    # user id of customer / if guest auto generate one
    def get_user_id(self):  # create the auto generate function if its a guest
        return self.__user_id

    def set_user_id(self, user_id):
        self.__user_id = user_id

    # name of customer / guest
    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    # email of the customer
    def get_email(self):
        return self.__email

    def set_email(self, email):
        self.__email = email

    # enquiry type
    def get_enquiry_type(self):
        return self.__enquiry_type

    def set_enquiry_type(self, enquiry_type):
        self.__enquiry_type = enquiry_type

    # comment
    def get_comments(self):
        return self.__comments

    def set_comments(self, comments):
        self.__comments = comments




