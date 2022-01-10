# Import modules
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature, BadSignature
import shelve

# Import classes
from users import User, Customer, Admin, Master
from forms import SignUpForm, SetPasswordForm


app = Flask(__name__)
app.config.from_pyfile("config/app.cfg")  # Load config file

url_serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"]) # Serialiser for generating tokens

mail = Mail()  # Mail object for sending emails 


# Home page
@app.route("/")
def home():
    return render_template("home.html")


# Login page
@app.route("/login")
def login():
    return render_template("login.html")


# Sign up page
@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    sign_up_form = SignUpForm(request.form)
    if request.method == "POST" and sign_up_form.validate():
        
        # Configure noreplybbb02@gmail.com
        app.config.from_pyfile("config/noreply_email.cfg")
        mail.init_app(app)

        # Extract email value from sign up form
        email = request.form["email"]

        # Generate token
        token = url_serialiser.dumps(email, salt=app.config["SIGN_UP_SALT"])

        # Send message to email entered
        msg = Message(subject="Verify Email",
                      sender=("BrasBasahBooks", "noreplybbb02@gmail.com"),
                      recipients=[email])
        link = url_for("sign_up_verify", token=token, _external=True)
        msg.body = f"Your link is {link}"
        mail.send(msg)

        return f"email: {email}, token: {token}"

    # Render page
    return render_template("sign_up.html", form=sign_up_form)


# Sign up verify email page
@app.route("/sign-up/verify/<token>", methods=["GET", "POST"])
def sign_up_verify(token):

    # Get email from token
    try:
        email = url_serialiser.loads(token, salt=app.config["SIGN_UP_SALT"], max_age=900)
    except SignatureExpired:  # Token expired
        return "The token expired!"
    except (BadTimeSignature, BadSignature) as err:  # Invalid token
        print(repr(err))  # print captured error
        return "Oops - This link is invalid or expired."

    # Set password
    set_password_form = SetPasswordForm(request.form)
    if request.method == "POST" and set_password_form.validate():

        # Create new user
        with shelve.open("database") as db:

            # Get Customers and EmailToUserID
            try:
                customers_db = db["Customers"]
            except KeyError:  # Customers not created yet
                customers_db = {}
            try:
                email_to_user_id = db["EmailToUserID"]
            except KeyError:  # EmailToUserID not created yet
                email_to_user_id = {}

            customer = Customer(email, request.form["password"])

            # Store customer into database
            user_id = customer.get_user_id()

            customers_db[user_id] = customer
            db["Customers"] = customers_db

            email_to_user_id[email] = user_id
            db["EmailToUserID"] = email_to_user_id

        return "user created"

    # Render page
    return render_template("sign_up_verify.html", form=set_password_form)

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
    return render_template("test.html")


if __name__ == "__main__":
    app.run()
