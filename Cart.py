
class SCart():
    buy_dict = {}
    rent_dict = []

class AddtoBuy(SCart):
    def __init__(self, book_id, book_quantity):
        SCart.__init__(self)
        self.book_id = book_id
        self.book_quantity = book_quantity
        self.buy_dict.update({book_id:book_quantity})
        print(self.buy_dict)

    def get_buy_dict(self):
        return self.buy_dict

    def get_book_id(self):
        return self.book_id

class AddtoRent(SCart):
    def __init__(self, book_id):
        SCart.__init__(self)
        self.rent_dict.append(book_id)
        print(self.rent_dict)

    def get_rent_dict(self):
        return self.rent_dict

    def get_book_id(self):
        return self.book_id


