# Import modules
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, BadData
import shelve

# Import classes
from users import GuestDB, Guest, Customer, Admin, Master
from forms import SignUpForm, LoginForm, AccountPageForm


app = Flask(__name__)
app.config.from_pyfile("config/app.cfg")  # Load config file

# Serialiser for generating tokens
url_serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

mail = Mail()  # Mail object for sending emails 


def retrieve_db(key, db, value={}):
    """ Retrieves object from database using key """
    try:
        value = db[key]  # Retrieve object
    except KeyError:     # If key not created yet
        db[key] = value  # Assign value to key
    return value


def get_user():
    """ Returns user by checking session key """

    # If session contains user_id
    if "UserID" in session:

        # Set database key according to user
        user_db_key = session["UserType"] + "s"

        # Retrieve user
        try:
            with shelve.open("database") as db:
                user_db = retrieve_db(user_db_key, db)
                user = user_db[session["UserID"]]
        except KeyError as err:  # If unexpected error (might occur when changes are made)
            print(repr(err))  # Output error for debugging
            # Move on to create guest account
        else:
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
    return guest


# Before request
@app.before_request
def before_request():
    # Make session permanent and set session lifetime
    session.permanent = True
    app.permanent_session_lifetime = Guest.MAX_DAYS

    # Run get user if user_id not in session
    if "UserId" not in session:
        create_guest()


# Home page
@app.route("/")
def home():
    return render_template("home.html")


# Sign up page
@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    # If user is already logged in
    if session["UserType"] != "Guest":
        return redirect(url_for("home"))

    # Get sign up form
    sign_up_form = SignUpForm(request.form)

    # Validate sign up form if request is post
    if request.method == "POST" and sign_up_form.validate():

        # Get current (guest) user
        user = get_user()

        # Extract email and password from sign up form
        email = sign_up_form.email.data
        password = sign_up_form.password.data
        username = sign_up_form.username.data

        # Create new user
        with shelve.open("database") as db:

            # Get Customers, EmailToUserID, Guests
            customers_db = retrieve_db("Customers", db)
            email_to_user_id = retrieve_db("EmailToUserID", db)
            guests_db = retrieve_db("Guests", db)


            # Ensure that email is not registered yet
            if email in email_to_user_id:
                return render_template("sign_up.html", form=sign_up_form)

            # Create customer
            customer = Customer(email, password, username, user.shopping_cart)

            # Delete guest account
            guests_db.remove(user.get_user_id())

            # Store customer into database
            user_id = customer.get_user_id()
            customers_db[user_id] = customer
            email_to_user_id[email] = user_id

            # Create session to login
            session["UserID"] = user_id
            session["UserType"] = "Customer"

            # Save changes to database
            db["EmailToUserID"] = email_to_user_id
            db["Customers"] = customers_db
            db["Guests"] = guests_db

        return redirect(url_for("home"))

    # Render page
    return render_template("sign_up.html", form=sign_up_form)


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # If user is already logged in
    if session["UserType"] != "Guest":
        return redirect(url_for("home"))

    login_form = LoginForm(request.form)
    if request.method == "POST" and login_form.validate():

        # Remove LoginFailed session
        session.pop("LoginFailed", None)

        # Extract email and password from login form
        email = login_form.email.data
        password = login_form.password.data

        # Check email
        with shelve.open("database") as db:

            # Retrieve user id
            try:
                user_id = retrieve_db("EmailToUserID", db)[email]
            except KeyError:
                # Create loginFailed session
                session["LoginFailed"] = True
                return render_template("login.html", form=login_form)

            # Retrieve user
            try:
                user = retrieve_db("Customers", db)[user_id]
                user_type = "Customer"
            except KeyError:
                user = retrieve_db("Admins", db)[user_id]
                user_type = "Admin"

        # Check password
        if user.check_password(password):
            session["UserID"] = user_id
            session["UserType"] = user_type
            return redirect(url_for("home"))
        else:
            # Create loginFailed session
            session["LoginFailed"] = True
            return render_template("login.html", form=login_form)

    # Render page
    return render_template("login.html", form=login_form)


# View account page
@app.route("/account", methods=["GET", "POST"])
def account():
    # If user is not logged in
    if session["UserType"] == "Guest":
        return redirect(url_for("login"))

    # Get current (customer) user
    user = get_user()

    # Get account page form
    account_page_form = AccountPageForm(request.form)

    # Validate account page form if request is post
    if request.method == "POST" and account_page_form.validate():

        # Extract email and password from sign up form
        username = account_page_form.username.data
        gender = account_page_form.gender.data

        with shelve.open("database") as db:
            # Get Customers
            customers_db = retrieve_db("Customers", db)
            user.set_username(username)
            user.set_gender(gender)
            customers_db[session["UserID"]] = user

            # Save changes to database
            db["Customers"] = customers_db

    # Set username and gender to display
    account_page_form.username.data = user.get_username()
    account_page_form.gender.data = user.get_gender()
    return render_template("account.html", form=account_page_form, email=user.get_email())


# Logout
@app.route("/logout")
def logout():
    if "UserType" != "Guest":
        create_guest()
    return redirect(url_for("home"))


# Send verification link page
@app.route("/verify")
def verify_link():

    # Get user
    user = get_user()

    # Configure noreplybbb02@gmail.com
    app.config.from_pyfile("config/noreply_email.cfg")
    mail.init_app(app)

    # Get email
    email = user.get_email()

    # Generate token
    token = url_serialiser.dumps(email, salt=app.config["VERIFY_EMAIL_SALT"])

    # Send message to email entered
    msg = Message(subject="Verify Email",
                sender=("BrasBasahBooks", "noreplybbb02@gmail.com"),
                recipients=[email])
    link = url_for("verify", token=token, _external=True)
    msg.html = f"Your link is {link}<br />(Link expires after 15 minutes)"
    mail.send(msg)

    return render_template("sent_verify.html", email=email)


# Verify email page
@app.route("/verify/<token>")
def verify(token):
    # Get email from token
    try:
        email = url_serialiser.loads(token, salt=app.config["VERIFY_EMAIL_SALT"], max_age=900)
    except BadData as err:  # Token expired or Bad Signature
        print(repr(err))  # print captured error (for debugging)
        return redirect(url_for("verify_fail"))
    
    with shelve.open("database") as db:
        email_to_user_id = retrieve_db("EmailToUserID", db)
        customers_db = retrieve_db("Customers", db)

        # Get user and verify email
        user = customers_db[email_to_user_id[email]]
        user.set_verified(True)

        db["Customers"] = customers_db

    return render_template("verify_email.html", email=email)


# Verify failed page
@app.route("/verify/fail")
def verify_fail():
    return render_template("verify_fail.html")



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


# Only during production. To be removed when published.
@app.route("/test")  # To go to test page: http://127.0.0.1:5000/test
def test():

    # Get user
    user = get_user()

    # If user is already logged in
    if session["UserType"] == "Guest":
        return ("You are a guest<br/>"
                f"Guest({user.get_user_id()})")
    else:
        return (f"You are logged in<br/>{session['UserType']}"
                f"({user.get_username()}, {user.get_email()}, {user.get_user_id()})")
    return render_template("test.html")


if __name__ == "__main__":
    app.run(debug=True)
