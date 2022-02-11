
from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, EmailField, DateField

class Enquiry(Form):
    name = StringField('Name', [validators.Length(min=1, max=100), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    enquiry_type = SelectField('Enquiry Type', [validators.DataRequired()], choices=[('', 'Select'), ('B', 'Question about Books'), ('F', 'Feedback'),('R','Report site vulnerability')], default='')
    comments = TextAreaField('Comments', [validators.Optional()])



class UserEnquiry:
    count = 0
    def __init__(self, name, email, enquiry_type, comments, UserID, UserType):
        # Args: for the self
        #
        #     user_id: the id of the user taken from the account
        #     name: the name of the user
        #     email: email of the user
        #     comments: what is the comments
        #
        # Notes:
        #     realised that i need user class and also guest accounts, therefore it has to obtained from them
        UserEnquiry.count += 1
        self.__count = UserEnquiry.count
        self.__name = name
        self.__email = email
        self.__enquiry_type = enquiry_type
        self.__comments = comments
        self.__UserID = UserID
        self.__UserType = UserType
        self.__reply = None


    # setting mutators and assessor methods
    def get_count(self):
        return self.__count

    def set_count(self, count):
        self.__count = count


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

    def get_UserID(self):
        return self.__UserID
    
    def set_UserID(self, UserID):
        self.__UserID = UserID
    
    def get_UserType(self):
        return self.__UserType
    
    def set_UserType(self, UserType):
        self.__UserType = UserType

    def get_reply(self):
        return self.__reply
    
    def set_reply(self, reply):
        self.__reply = reply

class ReplyEnquiry(Form):
    name = StringField('Name', [validators.Length(min=1, max=100), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    enquiry_type = SelectField('Enquiry Type', [validators.DataRequired()], choices=[('', 'Select'), ('B', 'Question about Books'), ('F', 'Feedback'),('R','Report site vulnerability')], default='')
    comments = TextAreaField('Comments', [validators.Optional()])
    reply = TextAreaField('Reply', [validators.DataRequired()])