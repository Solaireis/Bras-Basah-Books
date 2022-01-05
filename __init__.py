# Import modules
from flask import Flask, render_template, request, redirect, url_for, session
import shelve

# Import classes
from Users import User, Customer, Admin, Master

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/test")  # To go to test page 127.0.0.1:5000/test
def test():
    return render_template("test.html")

if __name__ == "__main__":
    app.run()
