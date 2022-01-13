from .Admin import Admin

class Master(Admin):
    """
    Master administrative account to manage admin accounts

    Attributes:
        __user_id (str): unique ID identifier of master admin
        __email (str): email of master admin
        __password (str): hashed password of master admin
        __username (str): username of master admin
        __verified (bool): True when master admin's email is verified
        __profile_pic (str): path of profile pic of master admin
        __gender (str): not used by master admin
        __coupons (list): not used by master admin
        __orders (list): not used by master admin
        shopping_cart (ShoppingCart): not used by master admin
    """

    def __init__(self):
        super().__init__("helpbbb01@gmail.com", "3wy-bkJFG!v4pcu;8B", "Master Admin")
        self.set_profile_pic("") #Path to profile pic of master admin
