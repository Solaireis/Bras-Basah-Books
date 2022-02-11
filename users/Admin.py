from argon2 import PasswordHasher
from .User import User

# Profile pic path
_UPLOAD_FOLDER = r"/static/img/profile-pic/"
_DEFAULT_PIC_NAME = r"default.png"

# Password hasher for hashing
_ph = PasswordHasher()


class Admin(User):
    """
    Admin account for administrators

    Attributes:
        __user_id (str): unique ID identifier of admin
        __email (str): email of admin
        __password (str): hashed password of admin
        __username (str): username of admin
        __profile_pic (str): path to profile pic of admin
        __master (bool): flag for master admin account (True when account is master admin)
    """

    def __init__(self, username, email, password, _master=False):
        super().__init__()
        self.__username = username
        self.__email = email
        self.set_password(password)
        self.__profile_pic = _UPLOAD_FOLDER + _DEFAULT_PIC_NAME
        self.__master = _master

    def __repr__(self):
        return super().__repr__(username=self.__username, email=self.__email, master=self.__master)

    # Mutator and accessor methods
    def set_email(self, email):
        self.__email = email
    def get_email(self):
        return self.__email

    def set_username(self, username):
        self.__username = username
    def get_username(self):
        return self.__username

    def set_profile_pic(self):
        self.__profile_pic = f"{_UPLOAD_FOLDER}{self.get_user_id()}.png"
    def get_profile_pic(self):
        return self.__profile_pic

    # Checks if account is master admin
    def is_master(self):
        return self.__master

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
