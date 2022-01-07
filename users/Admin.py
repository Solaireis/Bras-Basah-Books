from .Customer import Customer

class Admin(Customer):
    """
    Admin account for administrators

    Attributes:
        __user_id (str): unique ID identifier of admin
        __email (str): email of admin
        __password (str): hashed password of admin
        __name (str): name of admin
        __profile_pic (str): path of profile pic of admin
        __gender (str): gender of admin - "M" for male, "F" for female, "O" for other
        __coupons (list): not used by admin
        __orders (list): not used by admin
        shopping_cart (ShoppingCart): not used by admin
    """

    def __init__(self, email, password):
        super().__init__(email, password)
