# Import modules
from flask import Flask, render_template, request, redirect, url_for, session
import shelve

# Import classes
from users import User, Customer, Admin, Master
from forms import SignUpForm

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    sign_up_form = SignUpForm(request.form)
    if request.method == 'POST' and sign_up_form.validate():
        return redirect(url_for('home'))
    return render_template('sign_up.html', form=sign_up_form)

# Only during production
# To be removed when published
@app.route("/test")  # To go to test page 127.0.0.1:5000/test
def test():
    return render_template("test.html")

if __name__ == "__main__":
    app.run()
