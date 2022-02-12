import uuid
import datetime
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
    address = TextAreaField("Address")

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
        self.order_item = order_item
        self.total_price = total_price
        self.order_id = str(uuid.uuid4())
        self.ship_info = {'name': name, 'email': email, 'contact_num': contact_num,\
                          'ship_address': ship_address, 'ship_method': ship_method, \
                          'order_date': str(datetime.date.today()), 'order_status': 'Ordered'}
        self.order_info = [order_item, total_price]
        self.user_order = {user_id: self.ship_info, self.order_id: self.order_info}
        #print(self.user_order)

    # overall dictionary & list
    def get_ship_info(self):
        return self.ship_info
    def get_order_info(self):
        return self.order_info
    def get_user_order(self):
        return self.user_order

    # get user id and order id
    def get_user_id(self):
        return self.user_id
    def get_order_id(self):
        user_order = self.get_user_order()
        order_id = list(user_order)[1]
        return order_id

    # get data from ship_info
    def get_name(self):
        return self.name
    def get_email(self):
        return self.email
    def get_contact_num(self):
        return self.contact_num
    def get_ship_address(self):
        return self.ship_address
    def get_ship_method(self):
        return self.ship_method

    def get_order_date(self):
        ship_info = self.get_ship_info()
        order_date = ship_info['order_date']
        return order_date
    def get_order_status(self):
        ship_info = self.get_ship_info()
        order_status = ship_info['order_status']
        return order_status

    # get data from order_info
    def get_order_item(self):
        return self.order_item
    def get_buy_item(self):
        order_item = self.get_order_item()
        if order_item[0] != '':
            buy_item = order_item[0]
        else:
            buy_item = ''
        return buy_item
    def get_rent_item(self):
        order_item = self.get_order_item()
        if len(order_item) == 1:
            rent_item = ''
        else:
            rent_item = order_item[1]
        return rent_item
    def get_total_price(self):
        return self.total_price
    def get_buy_count(self):
        buy_count = 0
        buy_item = self.get_buy_item()
        if buy_item == '':
            buy_count = 0
        else:
            for quantity in buy_item:
                buy_count += buy_item[quantity]
        return buy_count
    def get_rent_count(self):
        rent_item = self.get_rent_item()
        if rent_item == '':
            rent_count = 0
        else:
            if rent_item[-1] == 'Returned':
                rent_count = (len(rent_item)-1)
            else:
                rent_count = len(rent_item)
        return rent_count
    def get_item_count(self):
        buy_count = self.get_buy_count()
        rent_count = self.get_rent_count()
        item_count = buy_count + rent_count
        return item_count

    # update order status as an admin
    def set_order_status(self, order_status):
        ship_info = self.get_ship_info()
        ship_info['order_status'] =  order_status
        return order_status

    # for returning of rented book
    def get_return_date(self):
        order_date = self.get_order_date()
        order_date = datetime.datetime.strptime(order_date, '%Y-%m-%d').date()
        return_date = order_date + datetime.timedelta(days=14)
        return return_date
    def get_today_date(self):
        today = datetime.date.today()
        return today
    def set_returned_status(self, returned):
        returned = returned.upper()
        rent_item = self.get_rent_item()
        if returned == "YES":
            return_status = 'Returned'
            rent_item.append(return_status)
            print(rent_item)
        else:
            return_status = 'Not Returned'
            rent_item.pop(-1)
            print(rent_item)
        return return_status
    def get_returned_status(self):
        rent_item = self.get_rent_item()
        if rent_item != '':
            if rent_item[-1] == 'Returned':
                return_status = 'Returned'
            else:
                return_status = 'Not Returned'
        else:
            return_status = "No rented books"
        return return_status

# user_id = 1
# name = 'chiobu'
# email = "testing@gmail.com"
# contact_num = '12341234'
# ship_address = ""
# ship_method = 'Standard Delivery'
#
# order_item = ['', [1,2]]
# total_price = 300
#
# order = Order_Detail(user_id, name, email, contact_num, ship_address, ship_method, order_item, total_price)
# print(order.get_user_order())
# print(order.get_order_item())
# print(order.get_ship_address())

