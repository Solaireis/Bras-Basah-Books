class Book:

    """
    Create book object

    Attributes:
        __book_id (str): unique ID identifier of book
        __language (str): book language
        __category (str): book category
        __age (str): book age group
        __action (str): whether book is available for buy/rent - "B" for only buy, "R" for only rent, "BR" for buy and rent
        __title (str): book title
        __author (str): book author
        __price (int): book price
        __qty (int): book quantity
        __desc (str): book description
        __img (str): path of book cover image
    """

    count_id = 0

    def __init__(self, language, category, age, action, title, author, price, qty, desc, img, rented):
        Book.count_id += 1
        self.__book_id = Book.count_id
        self.__language = language
        self.__category = category
        self.__age = age
        self.__action = action
        self.__title = title
        self.__author = author
        self.__price = price
        self.__qty = qty
        self.__desc = desc
        self.__img = img
        self.__rented = rented

    # Mutator methods

    def set_book_id(self, book_id):
        self.__book_id = book_id

    def set_language(self, language):
        self.__language = language

    def set_category(self, category):
        self.__category = category

    def set_age(self, age):
        self.__age = age

    def set_action(self, action):
        self.__action = action

    def set_title(self, title):
        self.__title = title

    def set_author(self, author):
        self.__author = author

    def set_price(self, price):
        self.__price = price

    def set_qty(self, qty):
        self.__qty = qty

    def set_desc(self, desc):
        self.__desc = desc

    def set_img(self, img):
        self.__img = img

    def set_rented(self, rented):
        self.__rented = rented

    # Accessor methods
    def get_book_id(self):
        return self.__book_id

    def get_language(self):
        return self.__language

    def get_category(self):
        return self.__category

    def get_age(self):
        return self.__age

    def get_action(self):
        return self.__action

    def get_title(self):
        return self.__title

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price

    def get_qty(self):
        return self.__qty

    def get_desc(self):
        return self.__desc

    def get_img(self):
        return self.__img

    def get_rented(self):
        return self.__rented
