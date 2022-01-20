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
