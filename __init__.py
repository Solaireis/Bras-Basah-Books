# Import modules
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, BadData
import shelve

# Import classes
from users import GuestDB, Guest, Customer, Admin
from forms import SignUpForm, LoginForm, AccountPageForm, AddBookForm

# Debug flag (constant) (True when debuggin)
DEBUG = True

app = Flask(__name__)
app.config.from_pyfile("config/app.cfg")  # Load config file

# Serialiser for generating tokens
url_serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

mail = Mail()  # Mail object for sending emails 

with shelve.open("database") as db:
    for key in ("EmailToUserID", "Customers", "Admins", "Orders"):
        if key not in db:
            db[key] = {}
    if "Guests" not in db:
        db["Guests"] = GuestDB()


def retrieve_db(key, db, value={}):
    """ Retrieves object from database using key """
    try:
        value = db[key]  # Retrieve object
        if DEBUG: print(f'retrieved db["{key}"] = {value}')
    except KeyError as err:
        if DEBUG: print("retrieve_db():", repr(err), f'db["{key}"] = {value}')
        db[key] = value  # Assign value to key
    return value


def get_user():
    """ Returns user by checking session key """

    # If session contains user_id
    if "UserID" in session:

        # Set database key according to user
        key = session["UserType"] + "s"

        # Retrieve user
        try:
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


# Before request
@app.before_request
def before_request():
    # Make session permanent and set session lifetime
    session.permanent = True
    app.permanent_session_lifetime = Guest.MAX_DAYS

    # Run get user if user_id not in session
    if "UserID" not in session:
        create_guest()


# Home page
@app.route("/")
def home():
    return render_template("home.html")


# Sign up page
@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    # Get current (guest) user
    user = get_user()

    # If user is already logged in
    if session["UserType"] != "Guest":
        return redirect(url_for("account"))

    # Get sign up form
    sign_up_form = SignUpForm(request.form)

    # Validate sign up form if request is post
    if request.method == "POST" and sign_up_form.validate():

        # Extract email and password from sign up form
        email = sign_up_form.email.data.lower()
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
            customer = Customer(email, password, username)
            if DEBUG: print(f"Created: {customer}")

            # Delete guest account
            if DEBUG: print(f"Deleted: {user}")
            guests_db.remove(user.get_user_id())

            # Store customer into database
            user_id = customer.get_user_id()
            customers_db[user_id] = customer
            email_to_user_id[email] = user_id

            # Create session to login
            session["UserID"] = user_id
            session["UserType"] = "Customer"
            if DEBUG: print(f"Logged in: {customer}")

            # Save changes to database
            db["EmailToUserID"] = email_to_user_id
            db["Customers"] = customers_db
            db["Guests"] = guests_db

        return redirect(url_for("verify_link"))

    # Render page
    return render_template("sign_up.html", form=sign_up_form)


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # If user is already logged in
    if session["UserType"] != "Guest":
        return redirect(url_for("account"))

    login_form = LoginForm(request.form)
    if request.method == "POST" and login_form.validate():

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
                session["LoginFailed"] = ""
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
            if DEBUG: print("Logged in:", user)
            return redirect(url_for("home"))
        else:
            # Create loginFailed session
            session["LoginFailed"] = ""
            return render_template("login.html", form=login_form)

    # Render page
    return render_template("login.html", form=login_form)


# View account page
@app.route("/account", methods=["GET", "POST"])
def account():
    # Get current user
    user = get_user()

    # If user is not logged in
    if session["UserType"] == "Guest":
        return redirect(url_for("login"))

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
    if session["UserType"] != "Guest":
        create_guest()
    return redirect(url_for("home"))


# Send verification link page
@app.route("/verify")
def verify_link():

    # Get user
    user = get_user()

    # If not customer or email is verified
    if not isinstance(user, Customer) or user.is_verified():
        return redirect(url_for("home"))

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
    msg.html = f"Click <a href='{link}'>here</a> to verify your email.<br />(Link expires after 15 minutes)"
    mail.send(msg)

    return render_template("sent_verify.html", email=email)


# Verify email page
@app.route("/verify/<token>")
def verify(token):
    # Get user
    user = get_user()

    # Get email from token
    try:
        email = url_serialiser.loads(token, salt=app.config["VERIFY_EMAIL_SALT"], max_age=900)
    except BadData as err:  # Token expired or Bad Signature
        if DEBUG: print("Invalid Token:", repr(err))  # print captured error (for debugging)
        return render_template("verify_fail.html")

    with shelve.open("database") as db:
        email_to_user_id = retrieve_db("EmailToUserID", db)
        customers_db = retrieve_db("Customers", db)

        # Get user
        try:
            user = customers_db[email_to_user_id[email]]
        except KeyError:
            if DEBUG: print("No user with email:", email)  # Account was deleted
            return render_template("verify_fail.html")
        
        # Verify email
        if not user.is_verified():
            user.verify()
        else:  # Email was alreadyt verified
            if DEBUG: print(email, "is already verified")
            return render_template("verify_fail.html")

        # Safe changes to database
        db["Customers"] = customers_db

    return render_template("verify_email.html", email=email)


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
        return f"You are a guest<br/>{user}"
    else:
        return f"You are logged in<br/>{user}"
    return render_template("test.html")


@app.route('/addBook', methods=['GET', 'POST'])
def add_book():
    add_book_form = AddBookForm(request.form)
    if request.method == "POST" and add_book_form.validate():
        books_dict = {}
        db = shelve.open('book.db', 'c')

        try:
            books_dict = db['Books']
        except:
            print("Error in retrieving Books from book.db")

        book = Book.Book(add_book_form.language.data, add_book_form.category.data, add_book_form.age.data, add_book_form.action.data, add_book_form.title.data, add_book_form.author.data, add_book_form.price.data, add_book_form.qty.data, add_book_form.desc.data, add_book_form.img.data)
        books_dict[book.get_book_id()] = book
        db['Books'] = books_dict

        # Test codes
        books_dict = db['Books']
        book = books_dict[book.get_book_id()]
        print(book.get_title(), book.get_price(), "was stored in book.db successfully with book_id==", book.get_book_id())
        db.close()
        return "Book successfully added"
    return render_template('add_book.html', form=add_book_form)


@app.route('/inventory')
def inventory():
    books_dict = {}
    db = shelve.open('book.db', 'r')
    books_dict = db['Books']
    db.close()

    books_list = []
    for key in books_dict:
        book = books_dict.get(key)
        books_list.append(book)

    return render_template('inventory.html', count=len(books_list), books_list=books_list)


@app.route('/updateBook/<int:id>/', methods=['GET', 'POST'])
def update_book(id):
    update_book_form = AddBookForm(request.form)
    if request.method == 'POST' and update_book_form.validate():
        books_dict = {}
        db = shelve.open('book.db', 'w')
        books_dict = db['Books']

        book = books_dict.get(id)
        book.set_language(update_book_form.language.data)
        book.set_category(update_book_form.category.data)
        book.set_age(update_book_form.age.data)
        book.set_action(update_book_form.action.data)
        book.set_title(update_book_form.title.data)
        book.set_author(update_book_form.author.data)
        book.set_price(update_book_form.price.data)
        book.set_qty(update_book_form.qty.data)
        book.set_desc(update_book_form.desc.data)
        book.set_img(update_book_form.img.data)

        db['Books'] = books_dict
        db.close()

        return redirect(url_for('inventory'))

    else:
        books_dict = {}
        db = shelve.open('book.db', 'r')
        books_dict = db['Books']
        db.close()

        book = books_dict.get(id)
        update_book_form.language.data = book.get_language()
        update_book_form.category.data = book.get_category()
        update_book_form.age.data = book.get_age()
        update_book_form.action.data = book.get_action()
        update_book_form.title.data = book.get_title()
        update_book_form.author.data = book.get_author()
        update_book_form.price.data = book.get_price()
        update_book_form.qty.data = book.get_qty()
        update_book_form.desc.data = book.get_desc()
        update_book_form.img.data = book.get_img()

        return render_template('update_book.html', form=update_book_form)


if __name__ == "__main__":
    app.run(debug=DEBUG)
