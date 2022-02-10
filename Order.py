from datetime import date

class User_Order():
    user_order = {}
    ship_info = {}
    order_info = []

class Order_Detail(User_Order):
    def __init__(self, user_id, order_id, ship_address, ship_method, \
                 order_item, total_price):
        User_Order.__init__(self)
        self.user_id = user_id
        self.order_id = order_id
        self.ship_address = ship_address
        self.ship_method = ship_method
        #self.order_date = order_date
        #self.order_status = order_status
        self.order_item = order_item
        self.total_price = total_price
        self.ship_info = {'ship_address': ship_address, 'ship_method': ship_method, \
                          'order_date': str(date.today()), 'order_status': 'Ordered'}
        self.order_info = [order_item, total_price]
        self.user_order = {user_id: self.ship_info, order_id: self.order_info}
        print(self.user_order)

    def get_ship_info(self):
        return self.ship_info

    def get_order_info(self):
        return self.order_info

    def get_user_order(self):
        return self.user_order

