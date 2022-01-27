class GuestDB(dict):
    """
    Guest database for storing guest accounts.
    By utilising pointers, add(), remove(), and renew_active() are all O(1) operations.
    clean() is O(k) where k is number of expired guest accounts.

    Attributes:
        __head (str): UserID of guest account at front of list
        __tail (str): UserID of guest account at end of list
    """

    def __init__(self):
        self.__head = None
        self.__tail = None

    def __repr__(self):
        return f"GuestDB({super().__repr__()})"


    def clean(self):
        """ Clean all expired guests from list and Guests database """
        while self.__head and self[self.__head].is_expired():
            self.remove(self.__head)


    def add(self, user_id, guest=None):
        """ Adds guest to database and/or list """
        if guest:  # If guest account is provided, add it into database
            self[user_id] = guest
        if self.__tail:  # If self.__tail is not None
            self[self.__tail]._next = user_id
            self[user_id]._prev = self.__tail
        else:
            self.__head = user_id
        self.__tail = user_id


    def remove(self, user_id, _pop=True):
        """ Removes guest from database and/or list """

        # Get guest
        guest = self[user_id]

        if guest._prev:  # If guest is not head
            self[guest._prev]._next = guest._next
        else:  # If guest is head
            self.__head = guest._next

        if guest._next:  # If guest is not tail
            self[guest._next]._prev = guest._prev
        else:  # If guest is tail
            self.__tail = guest._prev

        # Remove from database if _pop is True
        if _pop: self.pop(user_id, None)


    def renew_active(self, user_id):
        """ Renews last active date of guest and move guest to end of list """

        # Renew guest's active
        self[user_id].renew_active()

        # Remove guest from database
        self.remove(self, user_id, _pop=False)

        # Adds guest to end of list
        self.add(self, user_id)
