import uuid
from .Enquiry import UserEnquiry

class Reply(UserEnquiry):
    def __init__(self, reply):
        self.__reply_id = uuid.uuid4()  # unique id for the reply
        self.__reply = reply

    def get_reply_id(self):
        return self.__reply_id

    def get_reply(self):
        return self.__reply

    def set_reply(self,reply):
        self.__reply = reply
