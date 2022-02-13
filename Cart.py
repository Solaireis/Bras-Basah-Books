
class SCart():
    buy_dict = {}
    rent_dict = []

class AddtoBuy(SCart):
    def __init__(self, book_id, book_quantity):
        SCart.__init__(self)
        self.book_id = book_id
        self.book_quantity = book_quantity
        self.buy_dict.update({book_id:book_quantity})
        
    

    
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

#eden integration, creates discount feature
class Discount(SCart):
    def __init__(self,discount):
        SCart.__init__(self)
        self.__discount = discount


    def get_discount(self):
        return self.__discount
    
    def set_discount(self,discount):
        self.__discount = discount

