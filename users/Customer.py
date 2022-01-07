import uuid
from .User import User
# from ShoppingCart import ShoppingCart

class Customer(User):
    """
    Customer account for signed up users

    Attributes:
        __user_id (str): unique ID identifier of customer
        __email (str): email of customer
        __password (str): hashed password of customer
        __name (str): name of customer
        __profile_pic (str): path of profile pic of customer
        __gender (str): gender of customer - "M" for male, "F" for female, "O" for other
        __coupons (list): list of the coupons owned by customer
        __orders (list): list of the orders made by customer
        shopping_cart (ShoppingCart): shopping cart of customer
    """

    def __init__(self, email, password, shopping_cart=None,
                 name=None, profile_pic=None, gender=None):
        self.__user_id = uuid.uuid4()
        self.__email = email
        self.__password = self.hash_password(password)
        self.__name = name
        self.__profile_pic = profile_pic
        self.__gender = gender
        self.__coupons = []
        self.__orders = []
        if shopping_cart is None:
            self.shopping_cart = None  # ShoppingCart()
        else:
            self.shopping_cart = shopping_cart


    # Mutator and accessor methods
    def set_email(self, email):
        self.__email = email
    def get_email(self):
        return self.__email
        
    def set_name(self, name):
        self.__name = name
    def get_name(self):
        return self.__name
        
    def set_profile_pic(self, profile_pic):
        self.__profile_pic = profile_pic
    def get_profile_pic(self):
        return self.__profile_pic
        
    def set_gender(self, gender):
        self.__gender = gender
    def get_gender(self):
        return self.__gender
        
    def set_coupons(self, coupons):
        self.__coupons = coupons
    def get_coupons(self):
        return self.__coupons
        
    def set_orders(self, orders):
        self.__orders = orders
    def get_orders(self):
        return self.__orders

    def get_user_id(self):
        return self.__user_id

    def set_password(self, password):
        self.__password = self.hash_password(password)

    def check_password(self, password):
        return self.__password == self.hash_password(password)


    @staticmethod
    def hash_password(password):  # Currently using hash() to just return something
        """ Hash function of the password """
        return hash(password)
