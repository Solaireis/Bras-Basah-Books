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

user_id = 2
order_id = 3
order_item = [{1:2}, [2,3]]
total_price = 100
ship_address = '123B AMK Road'
ship_method = "Delivery"
order = Order_Detail(user_id, order_id, ship_address, ship_method, order_item, total_price)
print(order.get_order_info())
print(order.get_ship_info())


#
# class OrderItem():
#     order_dict = {}
#
# class OrderInfo(OrderItem):
#     def __init__(self, book_id, book_quantity, user_id, order_id, ship_address, ship_method, order_date, order_status, total_price):
#         OrderItem.__init__(self)
#         self.order_dict.update({book_id:book_quantity})
#         self.user_id = user_id
#         self.order_id = order_id
#         self.ship_address = ship_address
#         self.ship_method = ship_method
#         self.order_date = order_date
#         self.order_status = order_status
#         self.total_price = total_price
#
#     def get_user_id(self):
#         return self.order_id
#
#     def get_order_id(self):
#         return self.order_id
#
#     def get_ship_address(self):
#         return self.ship_address
#
#     def get_ship_method(self):
#         return self.ship_method
#
#     def get_order_date(self):
#         return self.order_date
#
#     def get_order_status(self):
#         return self.order_status
#
#     def get_total_price(self):
#         return self.total_price
#
#     def set_user_id(self, user_id):
#         self.user_id = user_id
#
#     def set_order_id(self, order_id):
#         self.order_id = order_id
#
#     def set_ship_address(self, ship_address):
#         self.ship_address = ship_address
#
#     def set_ship_method(self, ship_method):
#         self.ship_method = ship_method
#
#     def set_order_date(self, order_date):
#         self.order_date = order_date
#
#     def set_order_status(self, order_status):
#         self.order_status = order_status
#
#     def set_total_price(self, total_price):
#         self.total_price = total_price
#
# class BookOrder():
#     def __init__(self, book_name, book_price, book_quantity, book_img):
#         self.book_name = book_name
#         self.book_price = book_price
#         self.book_quantity = book_quantity
#         self.book_img = book_img
#
#     def get_book_name(self):
#         return self.book_name
#
#     def get_book_price(self):
#         return self.book_price
#
#     def get_book_quantity(self):
#         return self.book_quantity
#
#     def get_book_img(self):
#         return self.book_img
#
#     def set_book_name(self, book_name):
#         self.book_name = book_name
#
#     def set_book_price(self, book_price):
#         self.book_price = book_price
#
#     def set_book_quantity(self, book_quantity):
#         self.book_quantity = book_quantity
#
#     def set_book_img(self, book_img):
#         self.book_img = book_img
#
# #
# # class OrderPerson():
# #     def __init__(self, user_id, order_id, card_digit, ship_address, ship_method, order_date, order_status, total_amount):
# #         self.user_id = user_id
# #         self.order_id = order_id
# #         self.card_digit = card_digit
# #         self.ship_address = ship_address
# #         self.ship_method = ship_method
# #         self.order_date = order_date
# #         self.order_status = order_status
# #         self.total_amount = total_amount
# #
# #     def get_user_id(self):
# #         return self.order_id
# #
# #     def get_order_id(self):
# #         return self.order_id
# #
# #     def get_card_digit(self):
# #         return self.book_card_digit
# #
# #     def get_ship_address(self):
# #         return self.ship_address
# #
# #     def get_ship_method(self):
# #         return self.ship_method
# #
# #     def get_order_date(self):
# #         return self.order_date
# #
# #     def get_order_status(self):
# #         return self.order_status
# #
# #     def get_total_amount(self):
# #         return self.total_amount
# #
# #     def set_user_id(self, user_id):
# #         self.user_id = user_id
# #
# #     def set_order_id(self, order_id):
# #         self.order_id = order_id
# #
# #     def set_card_digit(self, card_digit):
# #         self.card_digit = card_digit
# #
# #     def set_ship_address(self, ship_address):
# #         self.ship_address = ship_address
# #
# #     def set_ship_method(self, ship_method):
# #         self.ship_method = ship_method
# #
# #     def set_order_date(self, order_date):
# #         self.order_date = order_date
# #
# #     def set_order_status(self, order_status):
# #         self.order_status = order_status
# #
# #     def set_total_amount(self, total_amount):
# #         self.total_amount = total_amount
# #
# # class BookOrder():
# #     def __init__(self, book_name, book_price, book_quantity, book_img):
# #         self.book_name = book_name
# #         self.book_price = book_price
# #         self.book_quantity = book_quantity
# #         self.book_img = book_img
# #
# #     def get_book_name(self):
# #         return self.book_name
# #
# #     def get_book_price(self):
# #         return self.book_price
# #
# #     def get_book_quantity(self):
# #         return self.book_quantity
# #
# #     def get_book_img(self):
# #         return self.book_img
# #
# #     def set_book_name(self, book_name):
# #         self.book_name = book_name
# #
# #     def set_book_price(self, book_price):
# #         self.book_price = book_price
# #
# #     def set_book_quantity(self, book_quantity):
# #         self.book_quantity = book_quantity
# #
# #     def set_book_img(self, book_img):
# #         self.book_img = book_img
