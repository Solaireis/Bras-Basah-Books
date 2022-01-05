# Import modules
from flask import Flask, render_template, request, redirect, url_for, session
import shelve

# Import classes
from Users import User, Customer, Admin, Master

app = Flask(__name__)

@app.route("/")
def home():
    # return render_template("home.html")
    return "We really need another meeting this week"

# @app.route("/test")
# def test():
#     return render_template("navbar&footer.html")

if __name__ == "__main__":
    app.run()
