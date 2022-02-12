from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, EmailField, DateField, \
    IntegerField, \
    ValidationError, DateTimeField, HiddenField

import datetime



class CreateCoupon(Form):
    
    name = StringField('Name', [validators.DataRequired()])

    def validate_name(self, field):
        if len(field.data) > 20:
            raise ValidationError("Name of coupon must be less than 20 Characters!")

    discount = IntegerField('Discount Applied', [validators.data_required()])

    def validate_discount(self, field):
        if field.data > 100:
            raise ValidationError("Discount input have to be less than 100!")


    coupon_code = StringField('Coupon Code', [validators.data_required()])  # please validate if there is a overwrite code
   
    def validate_coupon_code(self, field):
        if len(field.data) > 20:
            raise ValidationError("Coupon code must be less than 20 Characters!")

            
    startdate = StringField('Start Date' , [validators.data_required()])
    enddate = StringField('End Date' , [validators.data_required()])

class UpdateCoupon(Form):
    
    name = StringField('Name', [validators.DataRequired()])

    def validate_name(self, field):
        if len(field.data) > 20:
            raise ValidationError("Name of coupon must be less than 20 Characters!")

    discount = IntegerField('Discount Applied', [validators.data_required()])

    def validate_discount(self, field):
        if field.data > 100:
            raise ValidationError("Discount input have to be less than 100!")

            
    startdate = StringField('Start Date' , [validators.data_required()])
    enddate = StringField('End Date' , [validators.data_required()])

class Coupon:
    today = datetime.datetime.now()
    count = 0
    expired = ['Expired', 'Active']
    def __init__(self, name, discount, coupon_code_id, start_date, end_date):
        self.__count = Coupon.count + 1
        self.__name = name
        self.__discount = discount
        #self.__valid_date = valid_date
        self.__coupon_code_id = coupon_code_id
        self.__start_date = start_date
        self.__end_date = end_date
        self.__created_date = Coupon.today.strftime("%Y-%m-%d ")
        self.__expired = Coupon.expired[1]

    def get_count(self):
        return self.__count

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def get_discount(self):
        return self.__discount

    def set_discount(self, discount):
        self.__discount = discount

   # def get_valid_date(self):
        #return self.__valid_date

    #def set_valid_date(self, date):
        #self.__valid_date = date

    def get_coupon_code_id(self):
        return self.__coupon_code_id

    def set_coupon_code_id(self, coupon):
        self.__coupon_code_id = coupon

    def get_created_date(self):
        return self.__created_date

    def set_created_date(self, date):
        self.__created_date = date

    def get_start_date(self):
        return self.__start_date

    def set_start_date(self, date):
        self.__start_date = date
    
    def get_end_date(self):
        return self.__end_date
    
    def set_end_date(self, date):
        self.__end_date = date
    
    def get_expired(self):
        return self.__expired
    
    def set_expired(self, expired):
        self.__expired = Coupon.expired[expired]

class RequestCoupon(Form):
    coupon_code = StringField('Coupon Code', [validators.data_required()])


