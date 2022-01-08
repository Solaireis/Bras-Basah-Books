# Import modules
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import shelve

# Import classes
from users import User, Customer, Admin, Master
from forms import SignUpForm


app = Flask(__name__)
app.config.from_pyfile("app.cfg")  # Load config file

# Serialiser for generating tokens
url_serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

mail = Mail()  # Mail object for sending emails 


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    sign_up_form = SignUpForm(request.form)
    if request.method == "POST" and sign_up_form.validate():
        
        # Configure noreplybbb02@gmail.com
        app.config.from_pyfile("noreply_email.cfg")
        mail.init_app(app)

        # Extract email value from sign up form
        email = request.form["email"]

        # Generate token
        token = url_serialiser.dumps(email, salt="sign-up")

        # Send message to email entered
        msg = Message(subject="Verify Email",
                      sender=("BrasBasahBooks", "noreplybbb02@gmail.com"),
                      recipients=[email])
        link = url_for("sign_up_verify", token=token, _external=True)
        msg.body = f"Your link is {link}"
        mail.send(msg)

        return f"email: {email}, token: {token}"

    return render_template("sign_up.html", form=sign_up_form)

@app.route("/sign-up/verify/<token>")
def sign_up_verify(token):
    try:
        email = url_serialiser.loads(token, salt="sign-up", max_age=900)
    except SignatureExpired:
        return "The token expired!"
    return "Token works!"


# with shelve.open("database") as db:
#     try:
#         customers_db = db["customers"]
#     except KeyError:
#         print('No "customers" key in database')
#         customers_db = {}
#     customer = Customer(sign_up_form.email)

# Only during production
# To be removed when published
@app.route("/test")  # To go to test page 127.0.0.1:5000/test
def test():
    return render_template("test.html")

if __name__ == "__main__":
    app.run()
