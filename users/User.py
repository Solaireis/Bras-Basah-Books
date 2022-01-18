import uuid

class User:
    """
    User account

    Attributes:
        __user_id (str): unique ID identifier of user
    """

    def __init__(self):
        self.__user_id = str(uuid.uuid4())

    def get_user_id(self):
        return self.__user_id

    def __repr__(self, **kwargs):
        data = (("user_id", self.__user_id),) + tuple(kwargs.items())
        return f"{self.__class__.__name__}({', '.join([f'{i}: {j}' for i, j in data])})"
