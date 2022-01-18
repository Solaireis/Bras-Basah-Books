# Import modules
from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature, BadSignature
from datetime import timedelta
import shelve

# Import classes
from users import User, Customer, Admin, Master
from forms import SignUpForm, LoginForm


app = Flask(__name__)
app.config.from_pyfile("config/app.cfg")  # Load config file

# Serialiser for generating tokens
url_serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

mail = Mail()  # Mail object for sending emails 


# Before request
@app.before_request
def before_request():
    # Make session permanent and set session lifetime
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=3)#days=3)

    # If session contains user_id
    if "UserID" in session:

        # Set database key according to user
        if session["Guest"]:
            user_db_key = "Guests"
        else:
            user_db_key = "Customers"

        # Retrieve user
        try:
            with shelve.open("database") as db:
                g.user = db[user_db_key][session["UserID"]]
        except KeyError as err:  # If unexpected error (might occur when changes are made)
            print(repr(err))  # Output error for debugging
        else:
            return  # Terminate before_request()

    # Create new guest user
    guest = User()
    user_id = guest.get_user_id()

    # Create sessions
    session["Guest"] = True
    session["UserID"] = user_id

    # Store guest user object
    with shelve.open("database") as db:
        try:
            user_db = db["Guests"]
        except KeyError:  # Guests not created yet
            user_db = {}
        user_db[user_id] = guest
        db["Guests"] = user_db
    
    # Set g.user variable
    g.user = guest


# Home page
@app.route("/")
def home():
    return render_template("home.html")


# Sign up page
@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    # If user is already logged in
    if not session["Guest"]:
        return redirect(url_for("home"))

    # Get sign up form
    sign_up_form = SignUpForm(request.form)

    # Validate sign up form if request is post
    if request.method == "POST" and sign_up_form.validate():

        # Extract email and password from sign up form
        email = sign_up_form.email.data
        password = sign_up_form.password.data
        username = sign_up_form.username.data

        # Create new user
        with shelve.open("database") as db:

            # Get Customers and EmailToUserID
            try:
                user_db = db["Customers"]
            except KeyError:  # Customers not created yet
                user_db = {}
            try:
                email_to_user_id = db["EmailToUserID"]
            except KeyError:  # EmailToUserID not created yet
                email_to_user_id = {}

            customer = Customer(email, password, username)

            # Store customer into database
            user_id = customer.get_user_id()

            user_db[user_id] = customer
            db["Customers"] = user_db

            email_to_user_id[email] = user_id
            db["EmailToUserID"] = email_to_user_id
        
        return redirect(url_for("home"))

    # Render page
    return render_template("sign_up.html", form=sign_up_form)


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # If user is already logged in
    if not session["Guest"]:
        return redirect(url_for("home"))

    login_form = LoginForm(request.form)
    if request.method == "POST" and login_form.validate():

        # Extract email and password from login form
        email = login_form.email.data
        password = login_form.password.data

        # Check email
        with shelve.open("database") as db:

            # Retrieve user id
            try:
                user_id = db["EmailToUserID"][email]
            except KeyError:
                return "wrong email/password"  # wrong email

            # Retrieve user
            try:
                customer = db["Customers"][user_id]
            except KeyError as err:  # If unexpected error occurs
                # (If code works correctly, this should not happen)
                print("An unexpected error occured:\n" # For debugging
                      f"{err}\nuser_id: {user_id}, email: {email}")
                return "Error: please contact our administrators"

        # Check password
        if customer.check_password(password):
            session["UserID"] = user_id
            session["Guest"] = False
            return redirect(url_for("home"))
        else:
            return "wrong email/password"  # wrong password

    # Render page
    return render_template("login.html", form=login_form)


# Book Info page
@app.route("/book_info")
def book_info():
    return render_template("book_info.html")


# Shopping Cart
@app.route('/go_cart')
def go_cart():
    return render_template('cart.html', book_count=0)
    # if len(cart.cart) > 0:
    #     for i in range(len(cart.cart)):
    #         book_name = list(cart.cart.keys())[i]
    #         book_price = cart.cart[book_name]['book_price']
    #         print(book_name, 'and', book_price)
    #     return render_template('cart.html', cart=cart.cart, book_count=len(cart.cart), book_name=book_name, book_price=book_price)
    # else:
    #     return render_template('cart.html', book_count=len(cart.cart))

#enquiry page
@app.route("/enquiry", methods=['GET', 'POST'])
def enquiry_cust():
    create_enquiry_form = Enquiry(request.form)
    if request.method == 'POST' and create_enquiry_form.validate():
        enquiry_dict = {}
        db = shelve.open('database', 'c')

        try:
            enquiry_dict = db['Enquiry']
        except:
            print("Error in retrieving enquiries from enquiry.db.")

        enquiry = UserEnquiry(create_enquiry_form.name.data, create_enquiry_form.email.data, create_enquiry_form.enquiry_type.data, create_enquiry_form.comments.data)
        enquiry_dict[enquiry.get_enquiry_id()] = enquiry
        db['Enquiry'] = enquiry_dict

        db.close()

        return redirect(url_for('home'))

    return render_template("enquiry_customer.html", form=create_enquiry_form)

#retrieve customers
@app.route("/enquiry-adm")
def enquiry_retrieve_adm():
    enquiry_dict={}
    db = shelve.open('database','r')
    enquiry_dict = db['Enquiry']
    db.close()

    enquiry_list = []
    for key in enquiry_dict:
        enquiry = enquiry_dict.get(key)
        enquiry_list.append(enquiry)
        print(enquiry_list)

    return render_template("enquiry_admin.html", count=len(enquiry_list), enquiry_list=enquiry_list)

@app.route("/faq-adm", methods=['GET', 'POST'])
def faq_adm():
    create_faq_form = Faq(request.form)
    if request.method == 'POST' and create_faq_form.validate():
        faq_dict = {}
        db = shelve.open('faq','c')

        try:
            faq_dict = db['Faq']
        except:
            print("Error in retrieving faq queries from faq.db")

        faq = FaqEntry(create_faq_form.title.data, create_faq_form.desc.data)
        faq_dict[faq.get_faq_id()] = faq
        db['Faq'] = faq_dict

        db.close()

        return redirect(url_for('home'))
    return render_template("faq_adm.html", form=create_faq_form)



# Only during production. To be removed when published.
@app.route("/test")  # To go to test page: http://127.0.0.1:5000/test
def test():
    # If user is already logged in
    if session["Guest"]:
        return "You are a guest"
    else:
        return ("You are logged in<br/>"
                f"Customer({g.user.get_username()}, {g.user.get_email()}, {g.user.get_user_id()}")
    return render_template("test.html")



#the function to allow the app to run
if __name__ == "__main__":
    app.run()




""" Unused by useful code (don't delete) """

# # Configure noreplybbb02@gmail.com
# app.config.from_pyfile("config/noreply_email.cfg")
# mail.init_app(app)

# # Generate token
# token = url_serialiser.dumps(email, salt=app.config["SIGN_UP_SALT"])

# # Send message to email entered
# msg = Message(subject="Verify Email",
#               sender=("BrasBasahBooks", "noreplybbb02@gmail.com"),
#               recipients=[email])
# link = url_for("sign_up_verify", token=token, _external=True)
# msg.body = f"Your link is {link}"
# mail.send(msg)

# return f"email: {email}, token: {token}"

# # Get email from token
# try:
#     email = url_serialiser.loads(token, salt=app.config["SIGN_UP_SALT"], max_age=900)
# except SignatureExpired:  # Token expired
#     return "The token expired!"
# except (BadTimeSignature, BadSignature) as err:  # Invalid token
#     print(repr(err))  # print captured error
#     return "Oops - This link is invalid or expired."
