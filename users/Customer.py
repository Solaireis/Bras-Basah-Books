from argon2 import PasswordHasher
from .User import User

# Password hasher for hashing
_ph = PasswordHasher()


class Customer(User):
    """
    Customer account for signed up users

    Attributes:
        __user_id (str): unique ID identifier of customer
        __email (str): email of customer
        __password (str): hashed password of customer
        __username (str): username of customer
        __verified (bool): True when customer's email is verified
        __profile_pic (str): path of profile pic of customer
        __gender (str): gender of customer - "M" for male, "F" for female, "O" for other
        __coupons (list): list of the coupons owned by customer
        __orders (list): list of the orders made by customer
    """

    def __init__(self, email, password, username=""):
        super().__init__()
        self.__email = email
        self.set_password(password)
        self.__username = username
        self.__verified = False
        self.__profile_pic = ""
        self.__gender = ""
        self.__coupons = []
        self.__orders = []

    def __repr__(self):
        return super().__repr__(email=self.__email, username=self.__username)


    # Mutator and accessor methods
    def set_email(self, email):
        self.__email = email
    def get_email(self):
        return self.__email

    def set_username(self, username):
        self.__username = username
    def get_username(self):
        return self.__username

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

    # Verify account and return verify
    def verify(self):
        self.__verified = True
    def unverify(self):
        self.__verified = False
    def is_verified(self):
        return self.__verified

    # Set password, and check password
    def set_password(self, password):
        self.__password = _ph.hash(password)
    def check_password(self, password):
        try:     # Try verifying
            _ph.verify(self.__password, password)
        except:  # If verifying fails
            return False
        else:    # If verifying succeeds
            if _ph.check_needs_rehash(self.__password):  # Check if needs rehashing
                self.set_password(password)
            return True
