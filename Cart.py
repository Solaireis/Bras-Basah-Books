
class SCart():
    buy_dict = {}
    rent_dict = {}



class AddtoBuy(SCart):
    def __init__(self, book_id, book_quantity):
        Cart.__init__(self, book_id, book_quantity)
        self.buy_dict.update({book_id:book_quantity})
        print(self.buy_dict)

    def get_buy_dict(self):
        return self.buy_dict

    def get_book_id(self):
        return self.book_id

class AddtoRent(SCart):
    def __init__(self, book_id, book_quantity):
        Cart.__init__(self)
        self.rent_dict.update({book_id:book_quantity})
        print(self.rent_dict)

class Cart():
    def __init__(self, book_id, book_quantity):
        self.book_id = book_id
        self.book_quantity = book_quantity

    def get_book_id(self):
        return self.book_id
    def set_book_id(self, book_id):
        self.book_id = book_id

    def get_book_quantity(self):
        return self.book_quantity
    def set_book_id(self, book_quantity):
        self.book_quantity = book_quantity

class RentCart():
    def __init__(self, book_id):
        self.book_id = book_id

    def get_book_id(self):
        return self.book_id
    def set_book_id(self, book_id):
        self.book_id = book_id

    testing = {'s':{'a':'c'}}
    testing['s'].update({'c':'c'})
    print(testing)
