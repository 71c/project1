import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests, json

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def login():
    logged_in_yet = False
    login_success_or_failure_message = ""
    if request.method == "POST":
        if "user_id" not in session:
            print("aaaaaa")
            session["user_id"] = 0
            session["username"] = request.form.get("username")
            session["password"] = request.form.get("password")
        else:
            logged_in_yet = True
            if session["username"] == request.form.get("username") and session["password"] == request.form.get("password"):
                login_success_or_failure_message = "you logged in!"
            else:
                login_success_or_failure_message = "wrong username or password"
    if login_success_or_failure_message == "you logged in!":
        return render_template("main.html")
    return render_template("index.html", logged_in_yet=logged_in_yet, login_success_or_failure_message=login_success_or_failure_message)

@app.route("/<string:latitude>,<string:longitude>")
def hello(latitude, longitude):
    weather = requests.get(f"https://api.darksky.net/forecast/c5c0032498bd7f4153671aca4d378dfa/{latitude},{longitude}").json()
    return json.dumps(weather["currently"])

