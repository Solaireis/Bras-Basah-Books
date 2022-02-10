from wtforms import Form, StringField, IntegerField, TextAreaField, MonthField, EmailField, validators

class OrderForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=100), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=100), validators.DataRequired()])
    contact_num = IntegerField("Contact Number", [validators.DataRequired()])
    email = EmailField("Email", [validators.Email(), validators.DataRequired()])
    address = TextAreaField("Address", [validators.DataRequired()])
