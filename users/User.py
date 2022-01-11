import uuid
# from ShoppingCart import ShoppingCart

class User:
    """
    User account for guests (anonymous users)

    Attributes:
        __user_id (str): unique ID identifier of user
        shopping_cart (ShoppingCart): shopping cart of user
    """

    def __init__(self):
        self.__user_id = str(uuid.uuid4())
        self.shopping_cart = None  # ShoppingCart()

    def get_user_id(self):
        return self.__user_id
