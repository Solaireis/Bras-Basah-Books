from .User import User

class Admin(User):
    """
    Admin account for administrators

    Attributes:
        __user_id (str): unique ID identifier of admin
        __email (str): email of admin
        __password (str): hashed password of admin
        __username (str): username of admin
        __profile_pic (str): path of profile pic of admin
        __master (bool): flag for master admin account (True when account is master admin)
    """

    def __init__(self, email, password, username="", _master=False):
        super().__init__()
        self.__email = email
        self.__password = self.hash_password(password)
        self.__username = username
        self.__profile_pic = ""
        self.__master = _master
    
    def __repr__(self, ):
        return super().__repr__(email=self.__email, username=self.__username, master=self.__master)

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

    # Checks if account is master admin
    def is_master(self):
        return self.__master

    # Set password, and check password
    def set_password(self, password):
        self.__password = self.hash_password(password)
    def check_password(self, password):
        return self.__password == self.hash_password(password)


    @staticmethod
    def hash_password(password):  # Currently using weird things to just return something
        """ Hash function of the password """
        return "lol"+password.replace("a","b")
