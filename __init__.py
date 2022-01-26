# Import modules
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, BadData
import shelve
import requests
from bs4 import BeautifulSoup
import os
from werkzeug.utils import secure_filename


# Import classes
import Book
import Cart as c
from users import GuestDB, Guest, Customer, Admin
from forms import SignUpForm, LoginForm, AccountPageForm,\
                  Enquiry, UserEnquiry, Faq, FaqEntry, Reply, AddBookForm

# CONSTANTS
DEBUG = True         # Debug flag (True when debugging)
TOKEN_MAX_AGE = 900  # Max age of token (15 mins)

# For image file upload
UPLOAD_FOLDER = 'static/img/books'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


app = Flask(__name__)
app.config.from_pyfile("config/app.cfg")  # Load config file
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Set upload folder
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  #Set maximum file upload limit (4MB)

# Serialiser for generating tokens
url_serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

mail = Mail()  # Mail object for sending emails


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


def get_last_book_id():
    """ Return the ID of the last book """

    books_dict = {}
    db = shelve.open('book.db', 'r')
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

# Home page v2
@app.route("/home2")
def home2():

    try:
        books_dict = {}
        db = shelve.open('book.db', 'r')
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


# Sign up page
@app.route("/account/sign-up", methods=["GET", "POST"])
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
                return render_template("account/sign_up.html", form=sign_up_form)

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

        return redirect(url_for("verify_send"))

    # Render page
    return render_template("account/sign_up.html", form=sign_up_form)


# Login page
@app.route("/account/login", methods=["GET", "POST"])
def login():
    # If user is already logged in
    if session["UserType"] != "Guest":
        return redirect(url_for("account"))

    login_form = LoginForm(request.form)
    if request.method == "POST":
        if not login_form.validate():
            session["FormErrors"] = []
        else:
            # Extract email and password from login form
            email = login_form.email.data.lower()
            password = login_form.password.data

            # Check email
            with shelve.open("database") as db:

                # Retrieve user id
                try:
                    user_id = retrieve_db("EmailToUserID", db)[email]
                except KeyError:
                    # Create loginFailed session
                    session["LoginFailed"] = ""
                    return render_template("account/login.html", form=login_form)

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
                        # Create loginFailed session
                        session["LoginFailed"] = ""
                        return render_template("account/login.html", form=login_form)

            # Check password
            if user.check_password(password):
                session["UserID"] = user_id
                session["UserType"] = user_type
                if DEBUG: print("Logged in:", user)
                return redirect(url_for("home"))
            else:
                # Create loginFailed session
                session["LoginFailed"] = ""
                return render_template("account/login.html", form=login_form)

    # Render page
    return render_template("account/login.html", form=login_form)


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
    return render_template("account/account.html", form=account_page_form, email=user.get_email(), username=user.get_username())


# Logout
@app.route("/account/logout")
def logout():
    if session["UserType"] != "Guest":
        if DEBUG: print("Logout:", get_user())
        create_guest()
    return redirect(url_for("home"))


# Send verification link page
@app.route("/account/verify")
def verify_send():

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

    return render_template("account/verify/send.html", email=email)


# Verify email page
@app.route("/account/verify/<token>")
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

    return render_template("account/verify/verify.html", email=email)


# Verify fail page
@app.route("/account/verify/fail")
def verify_fail():
    render_template("account/verify/fail.html")


# allbooks
@app.route("/allbooks")
def allbooks():
    return render_template("allbooks.html")


# Book Info page
@app.route("/book_info")
def book_info():
    return render_template("book_info.html")


# add to buying cart
@app.route("/addtocart", methods=['GET', 'POST'])
def add_to_cart():
    cart_list = []
    cart_user = []
    user_id = get_user().get_user_id()
    source = requests.get("http://127.0.0.1:5000/book_info").content
    soup = BeautifulSoup(source, 'lxml')
    try:
        book_id = soup.find_all('span')[1].get_text()
        book_id = int(book_id)
        for key, quantity in request.form.items():
            book_quantity = quantity
            book_quantity = int(book_quantity)
        cart_db = shelve.open('cart', 'c')

        try:
            cart_list = cart_db['Cart']
            print(cart_list, "original database")
        except:
            cart_db['Cart'] = []
            print("Error in retrieving Cart Item from cart.db but it is manageable")

        added_book = c.Cart(book_id, book_quantity)
        if len(cart_list) == 0:
            print("New cart created")
            new_cart = [user_id, [added_book.get_book_id(), added_book.get_book_quantity()]]
            cart_list.append(new_cart)
            cart_db['Cart'] = cart_list
            print(cart_db["Cart"])
        else:
            for i in range(len(cart_list)):
                if user_id in cart_list[i]:
                    for j in range(len((cart_list)[i])-1):
                        if j == 0:
                            j += 1
                        if book_id == cart_list[i][j][0]:
                            cart_list[i][j][1] += book_quantity
                            print(cart_list, "before changing database")
                            cart_db['Cart'] = cart_list
                        else:
                            print("Oops book is not in this user's cart")
                            print("Not done yet")
                    break
                elif i == (len(cart_list)-1) and user_id not in cart_user:
                    print("Cannot find user id in cart")
                    new_cart = [user_id, [added_book.get_book_id(), added_book.get_book_quantity()]]
                    cart_list.append(new_cart)
                    cart_db['Cart'] = cart_list
                    print(cart_list)
                # for line in cart_db:
                #     cart_list.append(line)
                #print(cart_list,'current database')

                elif user_id not in cart_list[i]:
                    cart_user.append(cart_list[i][0])
                    print(cart_user)
    except IndexError:
        pass
    cart_db.close()
    return render_template("book_info.html")


# add to renting cart
@app.route("/add_to_rent", methods=['GET', 'POST'])
def add_to_rent():
    cart_list = []
    cart_user = []
    user_id = get_user().get_user_id()
    source = requests.get("http://127.0.0.1:5000/book_info").content
    soup = BeautifulSoup(source, 'lxml')
    try:
        book_id = soup.find_all('span')[1].get_text()
        book_id = int(book_id)
        cart_db = shelve.open('renting_cart', 'c')

        try:
            cart_list = cart_db['Cart']
            print(cart_list, "original database")
        except:
            cart_db['Cart'] = []
            print("Error in retrieving Cart Item from renting_cart.db but it is manageable")

        added_book = c.RentCart(book_id)
        if len(cart_list) == 0:
            print("New cart created")
            new_cart = [user_id, [added_book.get_book_id()]]
            cart_list.append(new_cart)
            cart_db['Cart'] = cart_list
            print(cart_db["Cart"])
        else:
            for i in range(len(cart_list)):
                if user_id in cart_list[i]:
                    for j in range(len((cart_list)[i])-1):
                        if j == 0:
                            j += 1
                        if book_id == cart_list[i][j][0]:
                            print("Book already in renting cart. Cannot rent more than 1.")
                        else:
                            print("Oops book is not in this user's cart")
                            print("Not done yet")
                    break
                elif i == (len(cart_list)-1) and user_id not in cart_user:
                    print("Cannot find user id in cart")
                    new_cart = [user_id, [added_book.get_book_id()]]
                    cart_list.append(new_cart)
                    cart_db['Cart'] = cart_list
                    print(cart_list)
                # for line in cart_db:
                #     cart_list.append(line)
                #print(cart_list,'current database')

                elif user_id not in cart_list[i]:
                    cart_user.append(cart_list[i][0])
                    print(cart_user)
    except IndexError:
        pass
    cart_db.close()
    return render_template("book_info.html")


# Shopping Cart
@app.route('/go_cart')
def go_cart():
    user_id = get_user().get_user_id()
    # retrieve buying cart
    try:
        cart_db = shelve.open('cart')
        cart_list = cart_db['Cart']
        cart_db.close()
    except:
        cart_list = []
        print("Cart is empty now.")
    # retrieve renting cart
    try:
        rentingcart_db = shelve.open('renting_cart')
        renting_cart_list = rentingcart_db['Cart']
        rentingcart_db.close()
    except:
        renting_cart_list = []
        print("Renting cart is empty now.")
    book_db = shelve.open('book.db', 'r')
    books_dict = book_db['Books']
    book_db.close()
    book_cart = []
    user_rent_cart = []
    book_info = []
    book_id = 0
    rent_bookid = 0
    book_name = ""
    rent_bookname = ""
    book_price = 0
    rent_bookprice = 0
    book_quantity = 0
    total_price = 0
    if len(cart_list) != 0:
        for i in range(len(cart_list)):
            if user_id in cart_list[i]:
                user_cart = cart_list[i]
                for j in range(1, len(user_cart)):
                    book_cart = [user_cart[j]]
                    for a in range(0,len(book_cart),2):
                        book_id = book_cart[a][a]
                        book_name = books_dict[book_id].get_title()
                        book_price = books_dict[book_id].get_price()
                        book_quantity = book_cart[a][a+1]
                        book = book_id, book_name, float(book_price), book_quantity
                        book_info.append(book)
                        total_price += float(book_quantity)*float(book_price)

        if len(renting_cart_list) != 0:
            for b in range(len(renting_cart_list)):
                user_rent_cart = renting_cart_list[b]
                if user_id in user_rent_cart:
                    user_rent_cart.pop(0)
                for c in range(len(user_rent_cart)):
                    rent_bookid = user_rent_cart[c][0]
                    rent_bookname = books_dict[rent_bookid].get_title()
                    rent_bookprice = float(books_dict[rent_bookid].get_price()) * 0.1
                    total_price += rent_bookprice
        total_price = ("%.2f" % round(total_price, 2))
        return render_template('cart.html', book_cart=book_cart, user_rent_cart=user_rent_cart, book_count=len(book_cart), rent_book_count=len(user_rent_cart), book_name=book_name, book_price=book_price, book_quantity=book_quantity, book_id=book_id, rent_bookid=rent_bookid, rent_bookname=rent_bookname, rent_bookprice=rent_bookprice, total_price=total_price)
    else:
        return render_template('cart.html', book_count=0, rent_book_count=0)


# Update Cart
@app.route('/update_cart', methods=['GET', 'POST'])
def update_cart():
    user_id = get_user().get_user_id()
    cart_db = shelve.open('cart')
    cart_list = cart_db['Cart']
    book_quantity = request.form['quantity']
    book_id = request.form['book_id']
    print(book_id, 'is book id', book_quantity, 'is quantity')
    for i in range(len(cart_list)):
            print(cart_list[i])
            if user_id in cart_list[i]:
                for j in range(1, len(cart_list[i])):
                    print('j =', j)
                    book_cart = [cart_list[i][j]]
                    if int(book_id) == cart_list[i][j][0]:
                        if int(book_quantity) == 0:
                            delete_buying_cart()
                        else:
                            cart_list[i][j][1] = int(book_quantity)
                            print(cart_list[i][j][1])
                            cart_db['Cart'] = cart_list
                    else:
                        print(cart_list[i][j], 'cannot find leh')
                    # for a in range(0,len(book_cart),2):
                    #     if book_id == book_cart[a][a]
            else:
                print(cart_list, "cannot find user")
    cart_db.close()
    return go_cart()

# Delete cart
@app.route("/delete_buying_cart", methods=['GET', 'POST'])
def delete_buying_cart():
    user_id = get_user().get_user_id()
    cart_db = shelve.open('cart')
    cart_list = cart_db['Cart']
    book_id = request.form['book_id']
    for i in range(len(cart_list)):
        if user_id in cart_list[i]:
            for j in range(1, len(cart_list[i])):
                if int(book_id) == cart_list[i][j][0]:
                    del cart_list[i][j]
                    print(cart_list[i], 'deleted some item')
                    cart_db['Cart'] = cart_list
                    if len(cart_list[i]) == 1:
                        del cart_list[i]
                        print(cart_list)
                        cart_db['Cart'] = cart_list
    cart_db.close()
    return go_cart()


# Delete renting cart
@app.route("/delete_renting_cart", methods=['GET', 'POST'])
def delete_renting_cart():
    print('renting')
    user_id = get_user().get_user_id()
    cart_db = shelve.open('renting_cart')
    cart_list = cart_db['Cart']
    book_id = request.form['book_id']
    for i in range(len(cart_list)):
        if user_id in cart_list[i]:
            for j in range(1, len(cart_list[i])):
                if int(book_id) == cart_list[i][j][0]:
                    del cart_list[i][j]
                    print(cart_list[i], 'deleted some item')
                    cart_db['Cart'] = cart_list
                    if len(cart_list[i]) == 1:
                        del cart_list[i]
                        print(cart_list)
                        cart_db['Cart'] = cart_list
    cart_db.close()
    return go_cart()


# Checkout
@app.route("/checkout")
def checkout():
    return render_template("checkout.html")


#
# enquiry page
#
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

#
# retrieve customers
#

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

#
# faq Admin create
#
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


# Add Book
@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    add_book_form = AddBookForm(request.form)
    if request.method == "POST" and add_book_form.validate():
        books_dict = {}
        db = shelve.open('book.db', 'c')

        try:
            books_dict = db['Books']
        except:
            print("Error in retrieving Books from book.db")

        try:
            Book.Book.count_id = get_last_book_id()
        except:
            print("First time adding book so last book id not needed")

        book = Book.Book(add_book_form.language.data, add_book_form.category.data, add_book_form.age.data, add_book_form.action.data, add_book_form.title.data, add_book_form.author.data, add_book_form.price.data, add_book_form.qty.data, add_book_form.desc.data, add_book_form.img.data)

        if add_book_form.language2.data != "":
            book.set_language(add_book_form.language2.data)

        if add_book_form.category2.data != "":
            book.set_category(add_book_form.category2.data)

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
        print(book.get_title(), book.get_price(), "was stored in book.db successfully with book_id==", book.get_book_id())
        db.close()
        return redirect(url_for('inventory'))

    return render_template('add_book.html', form=add_book_form)


# Inventory system for admin
@app.route('/inventory')
def inventory():

    try:
        books_dict = {}
        db = shelve.open('book.db', 'r')
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
    if request.method == 'POST' and update_book_form.validate():
        books_dict = {}
        db = shelve.open('book.db', 'w')
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

        return redirect(url_for('inventory'))

    else:
        books_dict = {}
        db = shelve.open('book.db', 'r')
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
    db = shelve.open('book.db', 'w')
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
    book_db = shelve.open('book.db', 'r')
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



# Only during production. To be removed when published.
@app.route("/test")  # To go to test page: http://127.0.0.1:5000/test
def test():
    # # Get user
    # user = get_user()
    # # If user is already logged in
    # if session["UserType"] == "Guest":
    #     return f"You are a guest<br/>{user}"
    # else:
    #     return f"You are logged in<br/>{user}"
    return render_template("test.html")


if __name__ == "__main__":
    app.run(debug=DEBUG)
