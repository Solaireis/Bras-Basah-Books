import uuid  # imports the module for universally unique identifiers
from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, EmailField, DateField

class Faq(Form):
    title = StringField('Title', [validators.Length(min=1, max=120), validators.DataRequired()])
    desc = TextAreaField('Description', [validators.Length(min=1, max=2000), validators.DataRequired()])


class FaqEntry():
    def __init__(self, title, desc):
        self.__faq_id = str(uuid.uuid4())  # faq_id: unique id of the enquiry which is needed for matching ids together
        self.__title = title
        self.__desc = desc

    def get_faq_id(self):
        return self.__faq_id
