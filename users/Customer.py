from argon2 import PasswordHasher
from .User import User

# Profile pic path
_UPLOAD_FOLDER = r"/static/img/profile-pic/"
_DEFAULT_PIC_NAME = r"default.png"

# Password hasher for hashing
_ph = PasswordHasher()


class Customer(User):
    """
    Customer account for signed up users

    Attributes:
        __user_id (str): unique ID identifier of customer
        __username (str): username of customer
        __email (str): email of customer
        __password (str): hashed password of customer
        __name (str): name of customers
        __verified (bool): True when customer's email is verified
        __profile_pic (str): path to profile pic of customer
        __gender (str): gender of customer - "M" for male, "F" for female, "O" for other
        __coupons (list): list of the coupons owned by customer
        __orders (list): list of the orders made by customer
        __enquiry (list): list of enquiry made by the customer
    """

    def __init__(self, username, email, password):
        super().__init__()
        self.__username = username
        self.__email = email
        self.set_password(password)
        self.__name = ""
        self.__verified = False
        self.__profile_pic = _UPLOAD_FOLDER + _DEFAULT_PIC_NAME
        self.__gender = ""
        self.__coupons = []
        self.__orders = []
        self.__enquiry = []

    def __repr__(self):
        return super().__repr__(username=self.__username, email=self.__email)


    # Mutator and accessor methods
    def set_username(self, username):
        self.__username = username
    def get_username(self):
        return self.__username

    def set_name(self, name):
        self.__name = name
    def get_name(self):
        return self.__name
    
    def get_display_name(self):
        """ Returns name for displaying, displays username if name not provided """
        return self.__name or self.__username

    def set_email(self, email):
        self.__email = email
    def get_email(self):
        return self.__email

    def set_profile_pic(self):
        self.__profile_pic = f"{_UPLOAD_FOLDER}{self.get_user_id()}.png"
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
    def verify_password(self, password):
        try:     # Try verifying
            _ph.verify(self.__password, password)
        except:  # If verifying fails
            return False

        # Check if needs rehashing
        if _ph.check_needs_rehash(self.__password):
            self.set_password(password)

        return True

    # Eden integration
    def add_coupons(self,coupon_code):
        self.__coupons.append(coupon_code)

    def add_enquiry(self,enquiry):
        self.__enquiry.append(enquiry)
    
    def get_enquiry(self):
        return self.__enquiry
    
    def set_enquiry(self,enquiry):
        self.__enquiry = enquiry