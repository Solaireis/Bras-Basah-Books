import uuid  # imports the module for universally unique identifiers
from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, EmailField, DateField

class Faq(Form):
    title = StringField('Title', [validators.Length(min=1, max=120), validators.DataRequired()])
    desc = TextAreaField('Description', [validators.Length(min=1, max=2000), validators.DataRequired()])


class FaqEntry():
    count = 0
    def __init__(self, title, desc):
        self.__count = FaqEntry.count + 1
        self.__faq_id = str(uuid.uuid4())  # faq_id: unique id of the enquiry which is needed for matching ids together
        self.__title = title
        self.__desc = desc
        self.__helpful = 0

    def get_count(self):
        return self.__count

    def set_count(self,count):
        self.__count = count

    def get_faq_id(self):
        return self.__faq_id

    def set_faq_id(self, faq_id):
        self.__faq_id = faq_id

    def get_title(self):
        return self.__title

    def set_title(self,title):
        self.__title = title

    def get_desc(self):
        return self.__desc

    def set_desc(self,desc):
        self.__desc = desc

    def get_helpful(self):
        return self.__helpful
    
    def set_helpful(self,helpful):
        self.__helpful = helpful

