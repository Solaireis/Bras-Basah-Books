"""
User objects

Provides all user type classes
User (general user class) (parent class)
Guest (guest account)
Customer (logged in account)
Admin (admin account)
Master (master admin account) (child class of Admin)
"""
# Why did I do this? I dunno, thought it was funny HAHAHA
from .User import User as User
from .Guest import Guest as Guest
from .Customer import Customer as Customer
from .Admin import Admin as Admin
from .Master import Master as Master
from .GuestDB import GuestDB as GuestDB
# Please don't mark us down for "unclean code"
# Just treat this as an easter egg
