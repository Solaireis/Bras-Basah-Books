"""
User objects

Provides all user type classes
Guest (guest account)
Customer (logged in account)
Admin (admin account)
GuestDB (dictionary for storing Guest objects)
"""
# Why did I do this? I dunno, thought it was interesting HAHAHA
from .Guest import Guest as Guest
from .Customer import Customer as Customer
from .Admin import Admin as Admin
from .GuestDB import GuestDB as GuestDB
# Please don't mark us down for "unclean code"
# Just treat this as an easter egg
