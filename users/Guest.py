from datetime import datetime, timedelta
from .User import User

class Guest(User):
    """
    Guest account for guests (anonymous users)

    Attributes:
        MAX_DAYS (timedelta): maximum days that an inactive guest account will be store
        __user_id (str): unique ID identifier of guest
        __last_active (datetime): time that guest account was last active
        _prev (str): UserID of previous guest account created
        _next (str): UserID of next guest account to be created
    """

    MAX_DAYS = timedelta(days=3)

    def __init__(self):
        super().__init__()
        self.__last_active = datetime.now()
        self._prev = None
        self._next = None

    def renew_active(self):
        """ Renews last active date """
        self.__last_active = datetime.now()

    def is_expired(self):
        """ Checks if guest account is expired """
        return datetime.now() - self.__last_active >= self.__class__.MAX_DAYS
