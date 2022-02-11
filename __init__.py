# Import modules
from flask import Flask, render_template, request, redirect, url_for, session, flash 
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, BadData
from werkzeug.utils import secure_filename
from typing import Union, Dict
import shelve
import os
import stripe

# Import classes
import Book, Cart as c
from users import GuestDB, Guest, Customer, Admin
from forms import SignUpForm, LoginForm, AccountPageForm, ChangePasswordForm, \
                  Enquiry, UserEnquiry, Faq, FaqEntry, AddBookForm, \
                  Coupon, CreateCoupon, OrderForm, RequestCoupon, ReplyEnquiry \


# CONSTANTS
DEBUG = True         # Debug flag (True when debugging)
TOKEN_MAX_AGE = 900  # Max age of token (15 mins)

# For image file upload
BOOK_IMG_UPLOAD_FOLDER = 'static/img/books'
PROFILE_PIC_UPLOAD_FOLDER = "static/img/profile-pic"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


app = Flask(__name__)
app.config.from_pyfile("config/app.cfg")  # Load config file
app.config['UPLOAD_FOLDER'] = BOOK_IMG_UPLOAD_FOLDER  # Set upload folder
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # Set maximum file upload limit (4MB)
app.jinja_env.add_extension("jinja2.ext.do")  # Add do extension to jinja environment
# testing mode
#stripe.api_key = 'sk_test_51KPNSMLcZKZGRW8Qkzf58oSvjzX5LxhHQLBPZkmlCijcfXdhdXtXTTDXf3FqMHd1fd3kWcvxktgp7cj0ka4uSmzS00ilLjWTBX' # Stripe API Key
# live mode
stripe.api_key = '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'


# Serialiser for generating tokens
url_serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

app.config["MAIL_SERVER"] = "smtp.gmail.com" # using gmail
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "noreplybbb02@gmail.com" # using gmail
app.config["MAIL_PASSWORD"] = "Hs!3ck;qnCSyyz^8-p"
mail = Mail(app)

#mail = Mail()  # Mail object for sending emails


"""|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|"""
"""|---------- Jabriel's Codes ----------|"""
"""|_____________________________________|"""


"""    General Funtions    """

# Added type hintings as I needed my editor to recognise the type
def retrieve_db(key, db, value=None) -> Union[
    Dict[str, Customer], Dict[str, Admin], GuestDB[str, Guest], Dict[str, Book.Book]]:
    """ Retrieves object from database using key """
    try:
        value = db[key]  # Retrieve object
        if DEBUG: print(f"retrieved db['{key}'] = {value}")
    except KeyError as err:
        if value is None: value = {}
        db[key] = value  # Assign value to key
        if DEBUG: print(f"retrieve_db(): {repr(err)} | create: db['{key}'] = {value}")
    return value


def get_user() -> Union[Customer, Admin, Guest]:
    """ Returns user by checking session key """

    # If session contains user_id
    if "UserID" in session:

        # Set database key according to user
        key = session["UserType"] + "s"

        # Retrieve user
        try:
            # Doesn't use retrieve_db() as default value is different for different db
            with shelve.open("database") as db:
                user = db[key][session["UserID"]]
        except KeyError as err:  # If unexpected error (might occur when changes are made)
            if DEBUG: print("get_user():", repr(err), "creating guest...")
            # Move on to create guest account
        else:
            if DEBUG: print("get user:", user)
            return user

    # If not UserID in session, create and return guest account
    return create_guest()


def create_guest():
    """ Create and return new guest account """
    guest = Guest()
    user_id = guest.get_user_id()

    # Create sessions
    session["UserType"] = "Guest"
    session["UserID"] = user_id

    with shelve.open("database") as db:
        # Get Guests
        guests_db = retrieve_db("Guests", db, GuestDB())

        # Add guest and clean guest database
        guests_db.add(user_id, guest)
        guests_db.clean()

        # Save changes to database
        db["Guests"] = guests_db
    if DEBUG: print("Guest created:", guest)
    return guest


"""    Before Request    """

# Before first request
@app.before_first_request
def before_first_request():
    # Check if Master admin exists
    with shelve.open("database") as db:
        admins_db = retrieve_db("Admins", db)
        username_to_user_id = retrieve_db("UsernameToUserID", db)
        email_to_user_id = retrieve_db("EmailToUserID", db)

        # Goes through admin accounts
        has_master_account = False
        for admin in admins_db.values():
            if admin.is_master():
                has_master_account = True
                break

        # Create master account
        if not has_master_account:
            # I stored the password in config file cause I didn't want it to appear in python file
            master = Admin("admin", "211973e@mymail.nyp.edu.sg", app.config["MASTER_PASS"], _master=True)
            if DEBUG: print(f"Created: {master}")

            # Store customer into database
            user_id = master.get_user_id()
            admins_db[user_id] = master
            username_to_user_id[master.get_username().lower()] = user_id
            email_to_user_id[master.get_email()] = user_id

            # Save changes to database
            db["UsernameToUserID"] = username_to_user_id
            db["EmailToUserID"] = email_to_user_id
            db["Admins"] = admins_db


# Before request
@app.before_request
def before_request():
    # Make session permanent and set session lifetime
    session.permanent = True
    app.permanent_session_lifetime = Guest.MAX_DAYS

    # Run get user if user_id not in session
    if "UserID" not in session:
        create_guest()


"""    Login/Sign-up Pages    """

# Sign up page
@app.route("/user/sign-up", methods=["GET", "POST"])
def sign_up():
    # Get current (guest) user
    user = get_user()

    # If user is already logged in
    if session["UserType"] != "Guest":
        return redirect(url_for("account"))

    # Get sign up form
    sign_up_form = SignUpForm(request.form)

    # Validate sign up form if request is post
    if request.method == "POST":
        if not sign_up_form.validate():
            if DEBUG: print("Sign-up: form field invalid")
            session["DisplayFieldError"] = True
            return render_template("user/sign_up.html", form=sign_up_form)

        # Extract data from sign up form
        username = sign_up_form.username.data
        email = sign_up_form.email.data.lower()
        password = sign_up_form.password.data

        # Create new user
        with shelve.open("database") as db:

            # Get Customers, UsernameToUserID, EmailToUserID, Guests
            customers_db = retrieve_db("Customers", db)
            username_to_user_id = retrieve_db("UsernameToUserID", db)
            email_to_user_id = retrieve_db("EmailToUserID", db)
            guests_db = retrieve_db("Guests", db)


            # Ensure that email and username are not registered yet
            if username.lower() in username_to_user_id:
                if DEBUG: print("Sign-up: username already exists")
                session["DisplayFieldError"] = session["SignUpUsernameError"] = True
                flash("Username taken", "sign-up-username-error")
                return render_template("user/sign_up.html", form=sign_up_form)
            elif email in email_to_user_id:
                if DEBUG: print("Sign-up: email already exists")
                session["DisplayFieldError"] = session["SignUpEmailError"] = True
                flash("Email already registered", "sign-up-email-error")
                return render_template("user/sign_up.html", form=sign_up_form)

            # Create customer
            customer = Customer(username, email, password)
            if DEBUG: print(f"Created: {customer}")

            # Delete guest account
            guests_db.remove(user.get_user_id())
            if DEBUG: print(f"Deleted: {user}")

            # Store customer into database
            user_id = customer.get_user_id()
            customers_db[user_id] = customer
            username_to_user_id[username.lower()] = user_id
            email_to_user_id[email] = user_id

            # Create session to login
            session["UserID"] = user_id
            session["UserType"] = "Customer"
            if DEBUG: print(f"Logged in: {customer}")

            # Save changes to database
            db["UsernameToUserID"] = username_to_user_id
            db["EmailToUserID"] = email_to_user_id
            db["Customers"] = customers_db
            db["Guests"] = guests_db

        return redirect(url_for("verify_send"))

    # Render page
    return render_template("user/sign_up.html", form=sign_up_form)


# Login page
@app.route("/user/login", methods=["GET", "POST"])
def login():
    # If user is already logged in
    if session["UserType"] != "Guest":
        return redirect(url_for("account"))

    login_form = LoginForm(request.form)
    if request.method == "POST":
        if not login_form.validate():
            # Flash login error message
            flash("Your account and/or password is incorrect, please try again", "form-error")
        else:
            # Extract username/email and password from login form
            username = login_form.username.data.lower()
            password = login_form.password.data

            # Get key for retrieving from database
            key = "EmailToUserID" if "@" in username else "UsernameToUserID"

            # Check username/email
            with shelve.open("database") as db:

                # Retrieve user id
                try:
                    user_id = retrieve_db(key, db)[username]
                except KeyError:
                    # Flash login error message
                    flash("Your account and/or password is incorrect, please try again", "form-error")
                    return render_template("user/login.html", form=login_form)

                # Retrieve user
                try:
                    user = retrieve_db("Customers", db)[user_id]
                    user_type = "Customer"
                except KeyError:  # If user_id not in Customers, try admin
                    try:
                        user = retrieve_db("Admins", db)[user_id]
                        user_type = "Admin"
                    except KeyError:  # Unexpected error
                        if DEBUG: print(f"UserID {user_id} not in database")
                        # Flash login error message
                        flash("Your account and/or password is incorrect, please try again", "form-error")
                        return render_template("user/login.html", form=login_form)

            # Check password
            if user.verify_password(password):
                session["UserID"] = user_id
                session["UserType"] = user_type
                if DEBUG: print("Logged in:", user)
                return redirect(url_for("home"))
            else:
                # Flash login error message
                flash("Your account and/or password is incorrect, please try again", "form-error")

    # Render page
    return render_template("user/login.html", form=login_form)


# Logout
@app.route("/user/logout")
def logout():
    if session["UserType"] != "Guest":
        if DEBUG: print("Logout:", get_user())
        create_guest()
    return redirect(url_for("home"))


"""    Account Pages    """

# Forgot password page
@app.route("/user/forget-password", methods=["GET", "POST"])
def password_forget():
    pass
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Change password page
@app.route("/user/change-password", methods=["GET", "POST"])
def password_change():
    # Get current user
    user = get_user()

    # If user is not logged in
    if session["UserType"] == "Guest":
        return redirect(url_for("login"))

    # Get change password form
    change_password_form = ChangePasswordForm(request.form)

    # Validate sign up form if request is post
    if request.method == "POST":
        if not change_password_form.validate():
            session["DisplayFieldError"] = True
        else:
            # Extract data from sign up form
            current_password = change_password_form.current_password.data
            new_password = change_password_form.new_password.data

            if not user.verify_password(current_password):
                flash("Your password is incorrect, please try again", "form-error")
            else:
                with shelve.open("database") as db:

                    # Retrieve user database
                    key = session["UserType"] + "s"
                    user_db = retrieve_db(key, db)

                    # Get user and set password
                    user = user_db[session["UserID"]]
                    user.set_password(new_password)

                    # Save changes to database
                    db[key] = user_db

                    if DEBUG: print("Password changed for", user)
                    return redirect(url_for("account"))

    return render_template("user/password_change.html", form=change_password_form)


# Send verification link page
@app.route("/user/verify")
def verify_send():

    # Get user
    user = get_user()

    # If not customer or email is verified
    if not isinstance(user, Customer) or user.is_verified():
        return redirect(url_for("home"))

    # Configure noreplybbb02@gmail.com
    # app.config.from_pyfile("config/noreply_email.cfg")
    # mail.init_app(app)

    # Get email
    email = user.get_email()

    # Generate token
    token = url_serialiser.dumps(email, salt=app.config["VERIFY_EMAIL_SALT"])

    # Send message to email entered
    msg = Message(subject="Verify Email",
                  sender=("BrasBasahBooks", "noreplybbb02@gmail.com"),
                  recipients=[email])
    link = url_for("verify", token=token, _external=True)
    msg.html = f"Click <a href='{link}'>here</a> to verify your email.<br />(Link expires after 15 minutes)"
    mail.send(msg)

    flash(f"Verification email sent to {email}")
    return redirect(url_for("account"))


# Verify email page
@app.route("/user/verify/<token>")
def verify(token):
    # Get user
    user = get_user()

    # Get email from token
    try:
        email = url_serialiser.loads(token, salt=app.config["VERIFY_EMAIL_SALT"], max_age=TOKEN_MAX_AGE)
    except BadData as err:  # Token expired or Bad Signature
        if DEBUG: print("Invalid Token:", repr(err))  # print captured error (for debugging)
        return redirect(url_for("verify_fail"))

    with shelve.open("database") as db:
        email_to_user_id = retrieve_db("EmailToUserID", db)
        customers_db = retrieve_db("Customers", db)

        # Get user
        try:
            user = customers_db[email_to_user_id[email]]
        except KeyError:
            if DEBUG: print("No user with email:", email)  # Account was deleted
            return redirect(url_for("verify_fail"))

        # Verify email
        if not user.is_verified():
            user.verify()
        else:  # Email was alreadyt verified
            if DEBUG: print(email, "is already verified")
            return redirect(url_for("verify_fail"))

        # Safe changes to database
        db["Customers"] = customers_db

    return render_template("user/verify/verify.html", email=email)


# Verify fail page
@app.route("/user/verify/fail")
def verify_fail():
    render_template("user/verify/fail.html")


"""    User Pages    """

# View account page
@app.route("/user/account", methods=["GET", "POST"])
def account():
    # Get current user
    user = get_user()

    # If user is not logged in
    if session["UserType"] == "Guest":
        return redirect(url_for("login"))

    # Get account page form
    account_page_form = AccountPageForm(request.form)

    # Validate account page form if request is post
    if request.method == "POST":

        if not account_page_form.validate():
            name = account_page_form.name
            gender = account_page_form.gender
            picture = account_page_form.picture

            # Flash error message (only flash the 1st error)
            error = name.errors[0] if name.errors else picture.errors[0] if picture.errors else gender.errors[0]
            flash(error, "error")
        else:
            # Flash success message
            flash("Account settings updated successfully")

            # Extract email and password from sign up form
            name = " ".join(account_page_form.name.data.split())
            gender = account_page_form.gender.data

            # Check files submitted for profile pic
            if "picture" in request.files:
                file = request.files["picture"]
                if file and allowed_file(file.filename):
                    file.save(os.path.join(PROFILE_PIC_UPLOAD_FOLDER, user.get_user_id()+".png"))
                else:
                    file = None
            else:
                file = None

            with shelve.open("database") as db:
                # Get Customers
                customers_db = retrieve_db("Customers", db)
                user = customers_db[session["UserID"]]

                # Set name and gender
                user.set_name(name)
                user.set_gender(gender)

                # If image uploaded, set profile pic
                if file is not None:
                    user.set_profile_pic()

                # Save changes to database
                db["Customers"] = customers_db

        # Redirect to prevent form resubmission
        return redirect(url_for("account"))

    # Set username and gender to display
    account_page_form.name.data = user.get_name()
    account_page_form.gender.data = user.get_gender()
    return render_template("user/account.html",
                           form=account_page_form,
                           display_name=user.get_display_name(),
                           picture_path=user.get_profile_pic(),
                           username=user.get_username(),
                           email=user.get_email())


"""    Admin Pages    """

# Manage accounts page
@app.route("/admin/manage-accounts", methods=["GET", "POST"])
def manage_accounts():
    user = get_user()

    # If user is not admin
    if not isinstance(user, Admin):
        return redirect(url_for("home"))

    # Get users database
    with shelve.open("database") as db:
        users = tuple(retrieve_db("Customers", db).values())

        # If is master admin
        if user.is_master():
            users += tuple(retrieve_db("Admins", db).values())

    return render_template("admin/manage_accounts.html", users=users, is_master=user.is_master())


"""|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|"""
"""|---------- End of Jabriel's Codes ----------|"""
"""|____________________________________________|"""


#
# Start of Chee Qing's Codes
#

#
# allbooks
#
@app.route("/allbooks")
def allbooks():
    return render_template("allbooks.html")

#
# add to buying cart
#
@app.route("/addtocart/<int:id>", methods=['GET', 'POST'])
def add_to_buy(id):
    user_id = get_user().get_user_id()
    buy_quantity = int(request.form['quantity'])
    cart_dict = {}
    cart_db = shelve.open('database', 'c')
    msg = ""
    try:
        cart_dict = cart_db['Cart']
        print(cart_dict, "original database")
    except:
        print("Error while retrieving data from cart.db")

    book = c.AddtoBuy(id, buy_quantity)
    if user_id in cart_dict:
        book_dict = cart_dict[user_id]
        print(book_dict)
        book_dict = book_dict[0]
        if book_dict == '':
            print("This user does not has anything in buying cart")
            cart_dict[user_id].pop(0)
            cart_dict[user_id].insert(0, {id:buy_quantity})
        else:
            if book.get_book_id() in book_dict:
                book_dict[book.get_book_id()] += buy_quantity
                print("This user has the book in cart")
                cart_dict[user_id][0] = book_dict
                msg = "Added to cart"
            else:
                print('This user does not has this book in cart')
                book_dict[id] = buy_quantity
                cart_dict[user_id][0] = book_dict
    else:
        print("This user has nothing in cart")
        cart_dict[user_id] = [{id:buy_quantity}]
    flash("Book has been added to your cart for you to buy.")
    cart_db['Cart'] = cart_dict
    print(cart_dict, "final database")
    return redirect(request.referrer)

#
# add to renting cart
#
@app.route("/addtorent/<int:id>", methods=['GET', 'POST'])
def add_to_rent(id):
    user_id = get_user().get_user_id()
    cart_dict = {}
    cart_db = shelve.open('database', 'c')
    book_dict = {}
    try:
        cart_dict = cart_db['Cart']
        print(cart_dict, "original database")
    except:
        print("Error while retrieving data from cart.db")

    book = c.AddtoRent(id)
    if user_id in cart_dict:
        book_dict = cart_dict[user_id]
        print(book_dict)
        # user has nothing in his renting cart
        if len(book_dict) == 1:
            print('user has nothing in his renting cart')
            book_dict.append([id])
            print(book_dict)
            cart_dict[user_id] = book_dict
            flash("Book has been added to your cart for rental.")
        else:
            print("user has other books in his renting cart")
            if id in book_dict[1]:
                print("This user already has the book in renting cart")
                flash("Oops... You cannot rent more than 1 same book at a time.", "warning")
            else:
                print("This user does not has the book in renting cart")
                book_dict[1].append(id)
                cart_dict[user_id] = book_dict
                flash("Book has been added to your cart for rental.")
    else:
        print("This user has nothing in both cart")
        cart_dict[user_id] = ['', [id]]
        flash("Book has been added to your cart for rental.")
    cart_db['Cart'] = cart_dict
    print(cart_dict, 'updated database')
    return redirect(request.referrer)

#
# view shopping cart
#
@app.route('/shopping_cart')
def cart():
    user_id = get_user().get_user_id()
    cart_dict = {}
    books_dict = {}
    cart_db = shelve.open('database', 'c')
    book_db = shelve.open('database')
    try:
        books_dict = book_db['Books']
        book_db.close()
    except:
        print("There is no books in the database currently.")
    buy_count = 0
    rent_count = 0
    total_price = 0
    buy_cart = {}
    rent_cart = []
    try:
        cart_dict = cart_db['Cart']
        print(cart_dict)
        books_dict = book_db['Books']
        book_db.close()
    except:
        print("Error while retrieving data from cart.db")

    if user_id in cart_dict:
        user_cart = cart_dict[user_id]
        if user_cart[0] == '':
            print('This user has nothing in the buying cart')
        else:
            buy_cart = user_cart[0]
            # buy_count = len(user_cart[0])
            for key in buy_cart:
                buy_count += buy_cart[key]
                total_price = float(total_price)
                total_price += float(buy_cart[key]*books_dict[key].get_price())
                total_price = float(("%.2f" % round(total_price, 2)))
        if len(user_cart) == 1:
            print('This user has nothing in the renting cart')
        else:
            rent_cart = user_cart[1]
            rent_count = len(user_cart[1])
            for book in rent_cart:
                total_price += float(books_dict[book].get_price()) * 0.1
                total_price = float(("%.2f" % round(total_price, 2)))
    return render_template('cart.html', buy_count=buy_count, rent_count=rent_count, buy_cart=buy_cart, rent_cart=rent_cart, books_dict=books_dict, total_price=total_price)

#
# update quantity in buying cart
#
@app.route('/update_cart/<int:id>', methods=['GET', 'POST'])
def update_cart(id):
    user_id = get_user().get_user_id()
    cart_db = shelve.open('database')
    cart_dict = cart_db['Cart']
    buy_cart = cart_dict[user_id][0]
    book_quantity = int(request.form['quantity'])
    if book_quantity == 0:
        print('Oh no need to delete')
        delete_buying_cart(id)
    else:
        buy_cart[id] = book_quantity
        print(buy_cart)
        cart_dict[user_id][0] = buy_cart
        cart_db['Cart'] = cart_dict
        print(cart_dict, 'updated database')
        cart_db.close()
    return redirect(request.referrer)

#
# delete item in buying cart
#
@app.route("/delete_buying_cart/<int:id>", methods=['GET', 'POST'])
def delete_buying_cart(id):
    user_id = get_user().get_user_id()
    cart_db = shelve.open('database')
    cart_dict = cart_db['Cart']
    buy_cart = cart_dict[user_id][0]
    #only has buying cart
    if len(buy_cart) == 1:
        if len(cart_dict[user_id]) == 1:
            del cart_dict[user_id]
        else:
            cart_dict[user_id][0] = ''
    else:
        del buy_cart[id]
        cart_dict[user_id][0] = buy_cart
    cart_db['Cart'] = cart_dict
    print(cart_dict, 'updated database')
    cart_db.close()
    return redirect(request.referrer)

#
# delete item in renting cart
#
@app.route("/delete_renting_cart/<int:id>", methods=['GET', 'POST'])
def delete_renting_cart(id):
    user_id = get_user().get_user_id()
    cart_db = shelve.open('database')
    cart_dict = cart_db['Cart']
    rent_cart = cart_dict[user_id][1]
    rent_cart.remove(id)
    cart_dict[user_id][1] = rent_cart
    if len(rent_cart) == 0:
        cart_dict[user_id].pop(1)
        if cart_dict[user_id][0] == '':
            del cart_dict[user_id]
    print(cart_dict, 'updated database')
    cart_db['Cart'] = cart_dict
    cart_db.close()
    return redirect(request.referrer)

#
# Checkout Form (for shipping address etc)
#
@app.route("/checkout", methods=['GET', 'POST'])
def checkout():
    user_id = get_user().get_user_id()
    cart_dict = {}
    db = shelve.open('database', 'c')
    buy_count = 0
    rent_count = 0
    total_price = 0
    buy_cart = {}
    rent_cart = []
    try:
        books_dict = db['Books']
        db = shelve.open('database', 'c')
        db_pending = db['Pending_Order']
        del db_pending[user_id]
        db['Pending_Order'] = db_pending
        db.close()
    except:
        pass

    try:
        cart_dict = db['Cart']
        print(cart_dict)
    except:
        print("Error while retrieving data from database")

    if user_id in cart_dict:
        user_cart = cart_dict[user_id]
        if user_cart[0] == '':
            print('This user has nothing in the buying cart')
        else:
            buy_cart = user_cart[0]
            for key in buy_cart:
                buy_count += buy_cart[key]
                total_price = float(total_price)
                total_price += float(buy_cart[key]*books_dict[key].get_price())
                total_price = float(("%.2f" % round(total_price, 2)))
        if len(user_cart) == 1:
            print('This user has nothing in the renting cart')
        else:
            rent_cart = user_cart[1]
            rent_count = len(user_cart[1])
            for book in rent_cart:
                total_price += float(books_dict[book].get_price()) * 0.1
                total_price = float(("%.2f" % round(total_price, 2)))
    Orderform = OrderForm.OrderForm(request.form)
    return render_template("checkout.html", form=Orderform, total_price=total_price, buy_count=buy_count, rent_count=rent_count, buy_cart=buy_cart, rent_cart=rent_cart, books_dict=books_dict)

#
# Create Check out session with Stripe
#
@app.route('/create-checkout-session/<total_price>', methods=['POST'])
def create_checkout_session(total_price):
    user_id = get_user().get_user_id()
    order_dict = {}
    print("creating checkout session...")
    total_price = float(total_price)+5
    try:
        db = shelve.open('database')
        cart_dict = db['Cart']
        user_cart = cart_dict[user_id]
        #db = shelve.open('database')
    except:
        user_cart = []
    Orderform = OrderForm.OrderForm(request.form)
    if request.method == 'POST' and Orderform.validate():
        new_order = OrderForm.Order_Detail(user_id, Orderform.name.data, Orderform.email.data, str(Orderform.contact_num.data), \
                   Orderform.address.data, Orderform.ship_method.data, user_cart, total_price)
        order_dict[user_id] = new_order
        db['Pending_Order'] = order_dict
        total_price *= 100
        total_price = int(total_price)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                    'currency': 'sgd',
                    'product_data': {
                      'name': 'Books',
                    },
                    'unit_amount': total_price,
                  },
                  'quantity': 1,
                },
            ],
            payment_method_types=['card'],
            mode='payment',
            success_url='http://127.0.0.1:5000/orderconfirm',
            cancel_url=request.referrer,
        )

        return redirect(checkout_session.url)
    else:
        flash(list(Orderform.errors.values())[0][0], 'warning')
        return redirect(request.referrer)

#
# show confirmation page upon successful payment
#
@app.route("/orderconfirm")
def orderconfirm():
    user_id = get_user().get_user_id()
    db_order= []
    books_dict = {}
    db = shelve.open('database')
    cart_dict = db['Cart']
    db_pending = db['Pending_Order']
    books_dict = db['Books']
    # in case user hand itchy go and reload the page, bring them back to home page
    try:
        new_order = db_pending[user_id]
        cartvalue = cart_dict[user_id]

        try:
            db_order = db['Order']
        except:
            print("Error while loading data from database")
            # return redirect(url_for("home"))

        db_order.append(new_order)

        print("cartvalue:", cartvalue)
        try:
            cartbuy = cartvalue[0]
            print("cartbuy:", cartbuy)
        except:
            pass
        if cartbuy != "":
            for i in books_dict:
                for x, y in zip(list(cartbuy.keys()), list(cartbuy.values())):
                    if i == x:
                        book = books_dict.get(i)
                        print("qty b4", book.get_qty())
                        newqty = int(book.get_qty()) - int(y)
                        book.set_qty(newqty)
                        print("qty aft", book.get_qty())

        try:
            cartrent = cartvalue[1]
            print("cartrent:", cartrent)
            if cartrent != "":
                for i in books_dict:
                    for x in cartrent:
                        if i == x:
                            book = books_dict.get(i)
                            print("rent qty b4:", book.get_rented())
                            newrented = int(book.get_rented()) + int(1)
                            book.set_rented(newrented)
                            print("rent qty aft:", book.get_rented())

        except:
            pass

        del cart_dict[user_id]
        del db_pending[user_id]
        db['Books'] = books_dict
        db['Pending_Order'] = db_pending
        db['Order'] = db_order
        db['Cart'] = cart_dict
        print(db_pending, 'should not have pending order as user already check out')
        print(cart_dict, 'updated database[cart]')
        print(db_order, 'updated databas[order]')
    except KeyError:
        return redirect(url_for("home"))

    db.close()
    return render_template("order_confirmation.html")

#
# Admin manage orders
#
@app.route("/admin/manage_orders")
def manage_orders():
    db_order = []
    new_order = []
    prepare_order = []
    fulfilled_order = []
    books_dict = {}
    try:
        db = shelve.open('database')
        books_dict = db['Books']
        db_order = db['Order']
        print(db_order, "orders in database")
        db.close()
    except:
        print("There might not have any orders as of now.")
    for order in db_order:
        if order.get_order_status() == 'Ordered':
            new_order.append(order)
        elif order.get_order_status() == 'Preparing':
            prepare_order.append(order)
        elif order.get_order_status() == 'Fulfilled':
            fulfilled_order.append(order)
        else:
            print(order, "Wrong order status")

    # display from most recent to the least
    db_order = list(reversed(db_order))
    new_order = list(reversed(new_order))
    prepare_order = list(reversed(prepare_order))
    fulfilled_order = list(reversed(fulfilled_order))

    print('new order', new_order)
    print('prepare order', prepare_order)
    print('fulfilled order',fulfilled_order)

    return render_template('admin/manage_orders.html', all_order=db_order, new_order=new_order, \
                           prepare_order=prepare_order, fulfilled_order=fulfilled_order, books_dict=books_dict)

#
# Admin update order status
#
@app.route("/admin/manage_orders/edit_status/<order_id>", methods=['GET', 'POST'])
def edit_status(order_id):
    db_order = []
    order_status = request.form['order-status']
    print(order_status)
    try:
        db = shelve.open('database')
        db_order = db['Order']
        print(db_order, "orders in database")
    except:
        print("Error while loading data from database")
    print(order_id)
    for order in db_order:
        if order.get_order_id() == order_id:
            order.set_order_status(order_status)
            flash('Order status for ' + order_id + ' has been updated.')
    db['Order'] = db_order
    print(db_order, 'updated database')
    db.close()
    print(order.get_order_status())
    return redirect(request.referrer)

#
# End of Chee Qing's Codes
#


#
# Eden Pages
#
# Start of enquiry pages
#
#
# Create Enquiry/Contact Us (customer/guest)
#
@app.route("/enquiry", methods=['GET', 'POST'])
def enquiry_cust():
    create_enquiry_form = Enquiry(request.form) #create enquiry form
    if request.method == 'POST' and create_enquiry_form.validate(): #if form is submitted and validated
        enquiry_dict = {} #empty dictionary to store enquiry details
        db = shelve.open('database', 'c')

        try:
            enquiry_dict = db['Enquiry'] #load enquiry details from database
        except:
            print("Error in retrieving enquiries ") #if no enquiries found in database

        try: # check if user already has an enquiry id
            UserEnquiry.count = count_id('Enquiry') #get the count of enquiry id
            
        except:
            print("No database found") #flags out for debugging
        
        try:
            user_id = session["UserID"] #get user id from session
            user_type = session["UserType"] #get user type from session
            
            if session["UserType"] == "Customer": #session for user
                customer_dict = retrieve_db('Customers',db) #load customer details from database
                customer = customer_dict.get(session["UserID"]) #get customer details from database
                print(customer)
                count = count_id('Enquiry') + 1 #get the count of enquiry id
                customer.add_enquiry(count) #add enquiry id to customer
                customer_dict[session["UserID"]] = customer #update customer details in database
                db['Customers'] = customer_dict #update customer details in database
        except:
            print("No database found for session") 


        enquiry = UserEnquiry(create_enquiry_form.name.data, create_enquiry_form.email.data,\
             create_enquiry_form.enquiry_type.data, create_enquiry_form.comments.data, user_id, user_type) # submit form details
        enquiry_dict[enquiry.get_count()] = enquiry #add enquiry details to dictionary
        db['Enquiry'] = enquiry_dict #save to database

        db.close() #close database

        return redirect(url_for('home')) #redirect to home page

    return render_template("enquiry/create_enquiry.html", form=create_enquiry_form) #render template

#
# retrieve customers(admin)
#

@app.route("/enquiry-adm") #admin dashboard
def enquiry_retrieve_adm():
    db = shelve.open('database','c') #open database
    enquiry_dict = retrieve_db('Enquiry', db )  # refer to the retrieve_db function
    db.close()

    enquiry_list = [] #empty list to store enquiry details
    for key in enquiry_dict: #loop through the dictionary
        enquiry = enquiry_dict.get(key) #get the enquiry details
        enquiry_list.append(enquiry) #add to list
        print(enquiry_list) #print for debugging

    return render_template("enquiry/enquiry_admin.html", count=len(enquiry_list), enquiry_list=enquiry_list) #render template

#
# faq Admin create
#
@app.route("/create-faq", methods=['GET', 'POST']) 
def create_faq():
    create_faq_form = Faq(request.form) #create faq form
    if request.method == 'POST' and create_faq_form.validate(): #if form is submitted and validated
        faq_dict = {}
        db = shelve.open('database','c') #open database

        try:
            faq_dict = db['Faq'] #load faq details from database
        except:
            print("Error in retrieving faq queries from faq.db") #if no faq queries found in database


        try:
            FaqEntry.count = count_id('Faq') #retrieve counter
        except:
            print("No Database found") #flags out for debugging

        faq = FaqEntry(create_faq_form.title.data, create_faq_form.desc.data) #submit form details
        faq_dict[faq.get_count()] = faq #add faq details to dictionary
        db['Faq'] = faq_dict # save to database

        db.close()  #close database

        return redirect(url_for('home')) #redirect to home page
    return render_template("faq/create_faq.html", form=create_faq_form) #render template

#
# counter for generating id
#
def count_id(Table): 
    the_dict = {} #empty dictionary
    db = shelve.open('database','c') #open database
    the_dict = db[Table] #load table details from database
    db.close() #close database

    count = [0] #test
    for key in the_dict: #loop through the dictionary
        count.append(key) #add to list
    
    highest_id = max(count) #gets the highest id


    return int(highest_id) #return highest id

#
# Update the enquiry, Reply to Customer enquiry
#
@app.route('/update-enq/<int:id>/', methods=['GET', 'POST'])
def update_enq(id):
    update_enquiry = ReplyEnquiry(request.form) #create update enquiry form

    if request.method == 'POST' and update_enquiry.validate(): #if form is submitted and validated
        users_dict={} #empty dictionary to store user details
        db = shelve.open('database','w') #open database
        enquiry_dict = db['Enquiry'] #load enquiry details from database

        # replying to  customer enquiry
        enquiry_id = enquiry_dict.get(id) #retrieve enquiry details from database
        enquiry_id.set_name(update_enquiry.name.data)
        enquiry_id.set_email(update_enquiry.email.data)
        enquiry_id.set_enquiry_type(update_enquiry.enquiry_type.data)
        enquiry_id.set_comments(update_enquiry.comments.data)
        enquiry_id.set_reply(update_enquiry.reply.data)#allows for reply to be updated

        db['Enquiry'] = enquiry_dict #saves to db
        db.close() #close database
        return redirect(url_for('enquiry_retrieve_adm'))

    else:
        enquiry_dict = {} #empty dictionary to store enquiry details
        db = shelve.open('database','w') #open database
        enquiry_dict = db['Enquiry'] #load enquiry details from database
        db.close() #close database

        #places the customer enquiries into the update form, which will be rendered
        enquiry_id = enquiry_dict.get(id)
        update_enquiry.name.data = enquiry_id.get_name()
        update_enquiry.email.data = enquiry_id.get_email()
        update_enquiry.enquiry_type.data = enquiry_id.get_enquiry_type()
        update_enquiry.comments.data = enquiry_id.get_comments()
        update_enquiry.reply.data = enquiry_id.get_reply()

        return render_template('enquiry/enquiry_adm_upd.html', form= update_enquiry)

#
# to mail to guest enquiry, alternative reply to enquiry based on UserType
#
@app.route('/mail-enq/<int:id>/', methods=['GET', 'POST'])
def mail_enq(id):
    mail_enquiry = ReplyEnquiry(request.form) #create mail enquiry form

    if request.method == 'POST' and mail_enquiry.validate(): #if form is submitted and validated
        users_dict={}
        db = shelve.open('database','w')
        enquiry_dict = db['Enquiry']

        #updates the database for admins to see
        enquiry_id = enquiry_dict.get(id)
        enquiry_id.set_name(mail_enquiry.name.data)
        enquiry_id.set_email(mail_enquiry.email.data)
        enquiry_id.set_enquiry_type(mail_enquiry.enquiry_type.data)
        enquiry_id.set_comments(mail_enquiry.comments.data)
        enquiry_id.set_reply(mail_enquiry.reply.data)
        db['Enquiry'] = enquiry_dict
        db.close()

        #sends the mail to the guest
        # app.config.from_pyfile("config/noreply_email.cfg")
        # mail.init_app(app)

        # crafting of mail
        # message subj, sender, recipient
        msg = Message(subject="Enquiry Ticket No:" + enquiry_id.get_count(),
                    sender=("BrasBasahBooks", "noreplybbb02@gmail.com"), 
                    recipients=[enquiry_id.get_email()])

        #message contents
        msg.body = "Dear " + enquiry_id.get_name() + ",\n\n" \
                    + "here are your enquiry details: " + "\n\n" \
                    + "Enquiry Type: " + enquiry_id.get_enquiry_type() + "\n\n" \
                    + "Comments: " + "\n\n" + enquiry_id.get_comments() + "\n\n" \
                    + "Reply: " + "\n\n" + enquiry_id.get_reply() \
                    + "Regards,\n" + "BrasBasahBooks"

        # send the mail
        mail.send(msg)

        flash(f"Verification email sent to {enquiry_id.get_email()}") #flash message
        return redirect(url_for('enquiry_retrieve_adm'))

    else:
        enquiry_dict = {} #empty dictionary to store enquiry details
        db = shelve.open('database','w') #open database
        enquiry_dict = db['Enquiry'] #load enquiry details from database
        db.close() #close database

        #places the guest enquiries into the update form, which will be rendered and be able to be updated
        enquiry_id = enquiry_dict.get(id)
        mail_enquiry.name.data = enquiry_id.get_name()
        mail_enquiry.email.data = enquiry_id.get_email()
        mail_enquiry.enquiry_type.data = enquiry_id.get_enquiry_type()
        mail_enquiry.comments.data = enquiry_id.get_comments()
        mail_enquiry.reply.data = enquiry_id.get_reply()

        return render_template('enquiry/enq_adm_mail.html', form= mail_enquiry)

#
# delete Enquiry
#
@app.route('/delete-enq/<int:id>',methods=['POST']) 
def delete_enq(id):
    enquiry_dict = {} #empty dictionary to store enquiry details
    db = shelve.open('database','w') #open database
    enquiry_dict = db['Enquiry'] #load enquiry details from database

    enquiry_dict.pop(id) #delete enquiry from database
    db['Enquiry'] = enquiry_dict #save to db
    db.close() #close database
    return redirect(url_for('enquiry_retrieve_adm'))

#
#view faq , customer to view enquiries
#
@app.route('/view-enq',methods=['GET', 'POST'])
def view_enq():#allows the viewing of faq
    db = shelve.open('database','w') #open database
    customer_dict = retrieve_db('Customers',db) #retrieve customer details from database
    db.close() #close database

    customer = customer_dict.get(session["UserID"]) #retrieve customer id from database
    enquiry_list = customer.get_enquiry() #retrieve enquiry details from database
    print(enquiry_list) #print enquiry details

    db = shelve.open('database','w') #open database
    enquiry_dict = retrieve_db('Enquiry',db) #retrieve enquiry details from database
    db.close() #close database

    #retrieve enquiry details from database, to match with customer enquiry
    enquiry_list_final = []
    for enquiry in enquiry_list: #for each enquiry in the customer enquiry list
        print(enquiry) #print enquiry list from customer database  - debugging purposes
        for key in enquiry_dict: #for each enquiry in the enquiry dictionary
            print(key) #print enquiry key  - debugging purposes
            if enquiry == key: #if the enquiry id from the customer list matches the enquiry id from the enquiry dictionary
                enquiry_list_final.append(enquiry_dict.get(key)) #append the enquiry details to the final list
                print('enquiry',enquiry_list_final) #print enquiry final list - debugging purposes
    
    return render_template('enquiry/view_enq.html', count=len(enquiry_list_final), enquiry_list=enquiry_list_final)

#
# retrieve enquiry from admin side
#
@app.route('/faq-dashboard')#retrieve faq
def faq_dashboard(): #allows the viewing of faq adm
    db = shelve.open('database','c')
    faq_dict = retrieve_db('Faq',db)
    db.close()

    faq_list = []
    for key in faq_dict:
        faq = faq_dict.get(key)
        faq_list.append(faq)
        print(faq_list)

    return render_template("faq/faq_dashboard.html", count=len(faq_list), faq_list=faq_list)

#
# update faq from the admin side
#
@app.route('/update-faq/<int:id>/',methods=['GET','POST'])
def update_faq(id):
    update_faq = Faq(request.form)
    if request.method == 'POST' and update_faq.validate():
        faq_dict = {}
        db = shelve.open('database','w')
        faq_dict = db['Faq']

        faq = faq_dict.get(id)
        faq.set_title(update_faq.title.data)
        faq.set_desc(update_faq.desc.data)

        db['Faq'] = faq_dict
        db.close()
        return redirect(url_for('faq_dashboard'))

    else:
        faq_dict = {}
        db = shelve.open('database','r')
        faq_dict = db['Faq']
        db.close()

        faq = faq_dict.get(id)
        update_faq.title.data = faq.get_title()
        update_faq.desc.data = faq.get_desc()
        return render_template('faq/update_faq.html', form=update_faq)

#
# delete enquiry
#
@app.route('/delete-faq/<int:id>', methods=['POST'])
def delete_faq(id):
    faq_dict={}
    db = shelve.open('database','w')
    faq_dict = db['Faq']
    faq_dict.pop(id)
    db['Faq'] = faq_dict
    db.close()
    return redirect(url_for('faq_dashboard'))

#view faq
@app.route('/faq', methods=['GET', 'POST'])
def faq():
    db = shelve.open('database','c')
    faq_dict = retrieve_db('Faq',db)
    db.close()

    faq_list = []
    for key in faq_dict:
        faq = faq_dict.get(key)
        faq_list.append(faq)
        print(faq_list)

    return render_template("faq/faq.html", count=len(faq_list), faq_list=faq_list)

# is this helpful function for FAQ
@app.route('/helpful-faq/<int:id>', methods=['GET', 'POST'])
def helpful_faq(id):
    db = shelve.open('database','c')
    faq_dict = retrieve_db('Faq',db)


    faq = faq_dict.get(id)
    faq.set_helpful(faq.get_helpful() + 1)

    db['Faq'] = faq_dict
    db.close()

    return redirect(url_for('faq'))

# Create coupon
@app.route('/coupon', methods =['GET','POST'])
def coupon_adm():
    create_coupon = CreateCoupon(request.form)   # import the coupon class first
    if request.method == 'POST' and create_coupon.validate():
        db = shelve.open('database', 'c')
        coupon_dict = retrieve_db('Coupon',db)


        coupon = Coupon(create_coupon.name.data,create_coupon.discount.data,create_coupon.coupon_code.data,create_coupon.startdate.data,create_coupon.enddate.data)
        coupon_dict[coupon.get_coupon_code_id] = coupon
        db['Coupon'] = coupon_dict
        db.close()


    return render_template("coupon/create_coupons.html", form=create_coupon)

# retrieve coupons as an admin
@app.route('/retrieve-coupons')
def retrieve_coupons():
    coupon_dict = {}
    db = shelve.open('database','w')
    coupon_dict = retrieve_db('Coupon',db)
    db.close()

    coupon_list=[]
    for key in coupon_dict:
        coupon = coupon_dict.get(key)
        coupon_list.append(coupon)

    return render_template('coupon/retrieve_coupons.html', count=len(coupon_list), coupon_list=coupon_list)

# update coupons
@app.route('/update-coupon/<int:id>/',methods=['GET','POST'])
def update_coupons(id):
    coupon_form = CreateCoupon(request.form)
    if request.method == 'POST' and coupon_form.validate():
        coupon_dict = {}
        db = shelve.open('database','w')
        coupon_dict = db['Coupon']

        coupon = coupon_dict.get(id)
        coupon.set_name(coupon_form.name.data)
        coupon.set_discount(coupon_form.discount.data)
        coupon.set_valid_date(coupon_form.valid_date.data)
        coupon.set_coupon_code_id(coupon_form.coupon_code.data)

        db['Coupon'] = coupon_dict
        db.close()

        return redirect(url_for('retrieve_coupons'))

    else:
        coupon_dict={}
        db =shelve.open('database','w')
        coupon_dict = db['Coupon']
        db.close()

        coupon = coupon_dict.get(id)
        coupon_form.name.data = coupon.get_name()
        coupon_form.discount.data = coupon.get_discount()
        coupon_form.valid_date.data = coupon.get_valid_date()
        coupon_form.coupon_code.data = coupon.get_coupon_code_id()

        return render_template('coupon/update_coupons.html', form=coupon_form)

#delete the coupons
@app.route('/delete-coupon/<int:id>',methods=['GET', 'POST'])
def delete_coupons(id):
    coupon_dict = {}
    db = shelve.open('database','w')
    coupon_dict = db['Coupon']
    coupon_dict.pop(id)
    db['Coupon'] = coupon_dict
    db.close()
    return redirect(url_for('retrieve_coupons'))

#customer retrieve coupons
@app.route('/request-coupon', methods=['GET', 'POST'])
def request_coupons():
    request_coupons = RequestCoupon(request.form)
    if request.method == 'POST' and request_coupons.validate():
        db = shelve.open('database','c')
        coupon_dict = retrieve_db('Coupon',db)

        coupon_list = []
        for key in coupon_dict:
            coupon = coupon_dict.get(key)
            print('coupon_code',coupon.get_coupon_code_id())
            if coupon.get_coupon_code_id() == request_coupons.coupon_code.data:
                coupon_list.append(coupon.get_coupon_code_id())
                print('coupon_list',coupon_list)
                print('Found coupon')
                if session["UserType"] == "Customer":
                    customer_dict = retrieve_db('Customers',db)
                    customer = customer_dict.get(session["UserID"])
                    customer.add_coupons(coupon.get_coupon_code_id())
                    customer_dict[session["UserID"]] = customer
                    db['Customers'] = customer_dict
                    db.close()
                    return redirect(url_for('retrieve_cu_coupons'))
            else:
                print('no match for coupon')

    return render_template('coupon/customer_coupons.html', form=request_coupons)

# retrieve coupons as a customer
@app.route('/retrieve-customer-coupons', methods=['GET', 'POST'])
def retrieve_cu_coupons():
    customer_dict = {}
    db = shelve.open('database','w')
    customer_dict = retrieve_db('Customers',db)
    db.close()


    customer = customer_dict.get(session["UserID"])
    coupon_list = customer.get_coupons()

    coupon_dict = {}
    db = shelve.open('database','w')
    coupon_dict = retrieve_db('Coupon',db)
    db.close()

    coupon_list_final = []
    for coupon in coupon_list:
        for key in coupon_dict:
            if coupon == coupon_dict.get(key).get_coupon_code_id():
                coupon_list_final.append(coupon_dict.get(key))

    return render_template('coupon/retrieve_cust_coupons.html', count=len(coupon_list_final), coupon_list=coupon_list_final)

#
# about page static
#
@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html")

#
# Error handling page
#
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error/404.html")

@app.route('/sitemap',methods=["GET", "POST"])
def sitemap():
    return render_template("sitemap.html")

#
#End of eden codes
#


#
# luqman's codes
#

# Function to return id of last book to set ID for newly added books
def get_last_book_id():
    """ Return the ID of the last book """

    books_dict = {}
    db = shelve.open('database', 'r')
    books_dict = db['Books']
    db.close()

    id_list = list(books_dict.keys())
    last_id = max(id_list)
    return int(last_id)

    # count_dict = {}
    # db = shelve.open('database.db', 'c')
    #
    # try:
    #     count_dict = db['Count']
    # except:
    #     print("Error in retrieving count from database.db")
    #
    # count_dict[last_id] = last_id
    # db['Count'] = count_dict


# Check if file extension is valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Home page
@app.route("/")
def home():

    try:
        books_dict = {}
        db = shelve.open('database', 'r')
        books_dict = db['Books']
        db.close()

    except:
        print("There are no books")


    english = []
    chinese = []
    for key in books_dict:
        book = books_dict.get(key)
        if book.get_language() == "English":
            english.append(book)
        elif book.get_language() == "Chinese":
            chinese.append(book)

    # books_list = []
    # for key in books_dict:
    #     book = books_dict.get(key)
    #     books_list.append(book)

    return render_template("home2.html", english=english, chinese=chinese)  # optional: books_list=books_list


# Add Book
lang_list = [('', 'Select'), ('English', 'English'), ('Chinese', 'Chinese'), ('Malay', 'Malay'), ('Tamil', 'Tamil')]
cat_list = [('', 'Select'), ('Action & Adventure', 'Action & Adventure'), ('Classic', 'Classic'), ('Comic', 'Comic'), ('Detective & Mystery', 'Detective & Mystery')]


@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    add_book_form = AddBookForm(request.form)
    add_book_form.language.choices = lang_list
    add_book_form.category.choices = cat_list
    if request.method == "POST" and add_book_form.validate():
        books_dict = {}
        db = shelve.open('database', 'c')

        try:
            books_dict = db['Books']
        except:
            print("Error in retrieving Books from database")

        try:
            Book.Book.count_id = get_last_book_id()
        except:
            print("First time adding book so last book id not needed")

        book = Book.Book(add_book_form.language.data, add_book_form.category.data, add_book_form.age.data, add_book_form.action.data, add_book_form.title.data, add_book_form.author.data, add_book_form.price.data, add_book_form.qty.data, add_book_form.desc.data, add_book_form.img.data, rented=0)

        if add_book_form.language2.data != "":
            book.set_language(add_book_form.language2.data)
            lang_list.append(tuple([add_book_form.language2.data, add_book_form.language2.data]))

        if add_book_form.category2.data != "":
            book.set_category(add_book_form.category2.data)
            cat_list.append(tuple([add_book_form.category2.data, add_book_form.category2.data]))


        # check if post request has image file part
        if 'bookimg' not in request.files:
            flash('There is no image uploaded!')
            return redirect(request.url)
        bookimg = request.files['bookimg']
        if bookimg == '':
            flash("No image selected for uploading")
            return redirect(request.url)
        if bookimg and allowed_file(bookimg.filename):
            filename = str(secure_filename(bookimg.filename))
            currentbookid = book.get_book_id()
            extension=filename.split(".")
            extension=str(extension[1])
            bookimg.filename = str(currentbookid) + "." + extension

            path = os.path.join(app.config['UPLOAD_FOLDER'], bookimg.filename)
            bookimg.save(path)
            print("upload_image filename: " + filename)

        else:
            print('Allowed image types are -> png, jpg, jpeg')
            return render_template('add_book.html', form=add_book_form)

        print("Book image uploaded under " + str(path))

        book.set_img(str("/" + path))
        books_dict[book.get_book_id()] = book
        db['Books'] = books_dict

        # Test codes
        books_dict = db['Books']
        book = books_dict[book.get_book_id()]
        print(book.get_title(), book.get_price(), "was stored in database successfully with book_id==", book.get_book_id())
        db.close()
        flash("Book successfully added!")
        # return redirect(url_for('inventory'))

    return render_template('add_book.html', form=add_book_form)


# Inventory system for admin
@app.route('/inventory')
def inventory():

    try:
        books_dict = {}
        db = shelve.open('database', 'r')
        books_dict = db['Books']
        db.close()

    except:
        print("There are no books")

    books_list = []
    for key in books_dict:
        book = books_dict.get(key)
        books_list.append(book)

    return render_template('inventory.html', count=len(books_list), books_list=books_list)


# Update Book
@app.route('/update-book/<int:id>/', methods=['GET', 'POST'])
def update_book(id):
    update_book_form = AddBookForm(request.form)
    update_book_form.language.choices = lang_list
    update_book_form.category.choices = cat_list
    if request.method == 'POST' and update_book_form.validate():
        books_dict = {}
        db = shelve.open('database', 'w')
        books_dict = db['Books']

        book = books_dict.get(id)
        if update_book_form.language.data != "":
            book.set_language(update_book_form.language.data)
        else:
            book.set_language(update_book_form.language2.data)
        if update_book_form.category.data != "":
            book.set_category(update_book_form.category.data)
        else:
            book.set_category(update_book_form.category2.data)
        book.set_age(update_book_form.age.data)
        book.set_action(update_book_form.action.data)
        book.set_title(update_book_form.title.data)
        book.set_author(update_book_form.author.data)
        book.set_price(update_book_form.price.data)
        book.set_qty(update_book_form.qty.data)
        book.set_desc(update_book_form.desc.data)
        book.set_img(book.get_img())

        # check if post request has image file part
        if 'bookimg' not in request.files:
            flash('There is no image uploaded!')
            return redirect(request.url)
        bookimg = request.files['bookimg']
        if bookimg == '':
            flash("No image selected for uploading")
            return redirect(request.url)
        if bookimg and allowed_file(bookimg.filename):
            filename = str(secure_filename(bookimg.filename))
            currentbookid = book.get_book_id()
            extension=filename.split(".")
            extension=str(extension[1])
            bookimg.filename = str(currentbookid) + "." + extension

            path = os.path.join(app.config['UPLOAD_FOLDER'], bookimg.filename)
            bookimg.save(path)
            book.set_img(str("/" + path))
            print("upload_image filename: " + filename)

        db['Books'] = books_dict
        db.close()

        flash("Book successfully updated!")
        return redirect(url_for('inventory'))


    else:
        books_dict = {}
        db = shelve.open('database', 'r')
        books_dict = db['Books']
        db.close()

        book = books_dict.get(id)
        update_book_form.language.data = book.get_language()
        update_book_form.language2.data = book.get_language()
        update_book_form.category.data = book.get_category()
        update_book_form.category2.data = book.get_category()
        update_book_form.age.data = book.get_age()
        update_book_form.action.data = book.get_action()
        update_book_form.title.data = book.get_title()
        update_book_form.author.data = book.get_author()
        update_book_form.price.data = book.get_price()
        update_book_form.qty.data = book.get_qty()
        update_book_form.desc.data = book.get_desc()
        update_book_form.img.data = book.get_img()

        return render_template('update_book.html', form=update_book_form)


# Delete Book
@app.route('/delete-book/<int:id>', methods=['POST'])
def delete_book(id):
    books_dict = {}
    db = shelve.open('database', 'w')
    books_dict = db['Books']

    book = books_dict.get(id)
    deletethisbook = str(book.get_img())
    deletethisbook = deletethisbook[1:]
    books_dict.pop(id)
    if os.path.isfile(deletethisbook):
        os.remove(deletethisbook)
        print(deletethisbook + ' is deleted')
    else:
        print(deletethisbook)
        print("This book cover image does not exist")

    db['Books'] = books_dict
    db.close()

    return redirect(url_for('inventory'))


# Book info page v2
@app.route('/book/<int:id>', methods=['GET', 'POST'])
def book_info2(id):
    book_db = shelve.open('database', 'r')
    books_dict = book_db['Books']
    book_db.close()

    currentbook = []
    book = books_dict.get(id)



    book.set_book_id(book.get_book_id())
    book.set_language(book.get_language())
    book.set_category(book.get_category())
    book.set_age(book.get_age())
    book.set_action(book.get_action())
    book.set_title(book.get_title())
    book.set_author(book.get_author())
    book.set_price(book.get_price())
    book.set_qty(book.get_qty())
    book.set_desc(book.get_desc())
    book.set_img(book.get_img())

    currentbook.append(book)
    print(currentbook, book.get_title())

    return render_template('book_info2.html', currentbook=currentbook)


# My Orders for customer
@app.route('/my-orders')
def my_orders():

    try:
        orders_list = []
        db = shelve.open('database', 'r')
        orders_list = db['Order']
        db.close()

    except:
        print("There are no orders")

    print("orders_list:", orders_list)
    for i in orders_list:
        print(i.get_name())

    return render_template('my_orders.html', count=len(orders_list), books_list=orders_list)

#
# end of luqman's codes
#


# Only during production. To be removed when published.
# temp home page
@app.route("/temp-home")
def temp_home():
    return render_template("home.html")
@app.route("/test", methods=["GET", "POST"])  # To go to test page: http://127.0.0.1:5000/test
def test():
    # Get current (guest) user
    user = get_user()

    sign_up_form = SignUpForm(request.form)

    # Validate sign up form if request is post
    if request.method == "POST":
        if not sign_up_form.validate():
            if DEBUG: print("Sign-up: form field invalid")
            session["DisplayFieldError"] = True
            flash("WARNING: TESTING PAGE FOR CREATING ADMINS", "warning")
            flash(f"Currently logged in as: {user}")
            return render_template("user/sign_up.html", form=sign_up_form)

        # Extract data from sign up form
        username = sign_up_form.username.data
        email = sign_up_form.email.data.lower()
        password = sign_up_form.password.data

        # Create new user
        with shelve.open("database") as db:

            # Get Admins, UsernameToUserID, EmailToUserID, Guests
            admins_db = retrieve_db("Admins", db)
            username_to_user_id = retrieve_db("UsernameToUserID", db)
            email_to_user_id = retrieve_db("EmailToUserID", db)
            guests_db = retrieve_db("Guests", db)


            # Ensure that email and username are not registered yet
            if username.lower() in username_to_user_id:
                if DEBUG: print("Sign-up: username already exists")
                session["DisplayFieldError"] = True
                flash("WARNING: TESTING PAGE FOR CREATING ADMINS", "warning")
                flash(f"Currently logged in as: {user}")
                return render_template("user/sign_up.html", form=sign_up_form)
            elif email in email_to_user_id:
                if DEBUG: print("Sign-up: email already exists")
                session["DisplayFieldError"] = True
                flash("WARNING: TESTING PAGE FOR CREATING ADMINS", "warning")
                flash(f"Currently logged in as: {user}")
                return render_template("user/sign_up.html", form=sign_up_form)

            # Create customer
            admin = Admin(username, email, password)
            if DEBUG: print(f"Created: {admin}")

            # Delete guest account
            guests_db.remove(user.get_user_id())
            if DEBUG: print(f"Deleted: {user}")

            # Store customer into database
            user_id = admin.get_user_id()
            admins_db[user_id] = admin
            username_to_user_id[username.lower()] = user_id
            email_to_user_id[email] = user_id

            # Create session to login
            session["UserID"] = user_id
            session["UserType"] = "Admin"
            if DEBUG: print(f"Logged in: {admin}")

            # Save changes to database
            db["UsernameToUserID"] = username_to_user_id
            db["EmailToUserID"] = email_to_user_id
            db["Admins"] = admins_db
            db["Guests"] = guests_db

        flash(f"Currently logged in as: {user}")
        return redirect(url_for("home"))

    # Render page
    flash("WARNING: TESTING PAGE FOR CREATING ADMINS", "warning")
    flash(f"Currently logged in as: {user}")
    return render_template("user/sign_up.html", form=sign_up_form)


if __name__ == "__main__":
    app.run(debug=DEBUG)  # Run app
