import uuid
from .Enquiry import Enquiry

class Reply(Enquiry):
    def __init__(self, reply):
        self.reply_id = uuid.uuid4()  # unique id for the reply
        self.reply = reply

