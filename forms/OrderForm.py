import uuid
from datetime import date
from wtforms import Form, StringField, IntegerField, TextAreaField, EmailField, RadioField, validators

def contact_num_check(form, field):
    if len(str(field.data)) != 8:
        raise validators.ValidationError('Please enter a valid mobile number!')
    elif str((field.data))[0] != '9':
        if str((field.data))[0] != '8':
            num = str(field.data)
            print(num[0])
            print(type(str((field.data))[0]))
            raise validators.ValidationError('Please make sure your phone number starts with 8 or 9!')

class OrderForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=100), validators.DataRequired()])
    contact_num = IntegerField("Contact Number", [contact_num_check, validators.DataRequired()])
    email = EmailField("Email", [validators.Email(), validators.DataRequired()])
    address = TextAreaField("Address", [validators.DataRequired()])
    ship_method = RadioField('Shipping Method', choices=[('Standard Delivery', 'Standard Delivery (3 - 5 business days)'), \
                                                         ('Self-collection', 'Self-collect (Pick up at our store)')], \
                             default='Standard Delivery')

class User_Order():
    user_order = {}
    ship_info = {}
    order_info = []

class Order_Detail(User_Order):
    def __init__(self, user_id, name, email, contact_num, ship_address, ship_method, \
                 order_item, total_price):
        User_Order.__init__(self)
        self.user_id = user_id
        self.ship_address = ship_address
        self.ship_method = ship_method
        self.name = name
        self.email = email
        self.contact_num = contact_num
        #self.order_date = order_date
        #self.order_status = order_status
        self.order_item = order_item
        self.total_price = total_price
        self.order_id = str(uuid.uuid4())
        self.ship_info = {'name': name, 'email': email, 'contact_num': contact_num,\
                          'ship_address': ship_address, 'ship_method': ship_method, \
                          'order_date': str(date.today()), 'order_status': 'Ordered'}
        self.order_info = [order_item, total_price]
        self.user_order = {user_id: self.ship_info, self.order_id: self.order_info}
        #print(self.user_order)

    def get_ship_info(self):
        return self.ship_info

    def get_order_info(self):
        return self.order_info

    def get_user_order(self):
        return self.user_order

    def get_user_id(self):
        return self.user_id

user_id = 2

order_item = [{1:2}, [2,3]]
total_price = 100
ship_address = '123B AMK Road'
ship_method = "Delivery"
name = 'Chiobu'
email = 'chiobu@email.com'
contact_num = 12341234
#order = Order_Detail(user_id, name, email, contact_num, ship_address, ship_method, order_item, total_price)
