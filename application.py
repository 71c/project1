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


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     print(session["username"], session["password"])
#     logged_in_yet = False
#     logged_in = False
#     if request.method == "POST":
#         if "uper_i00d" not in session:
#             print("aaaaaa")
#             session["uper_i00d"] = 0
#             session["username"] = request.form.get("username")
#             session["password"] = request.form.get("password")
#         else:
#             logged_in_yet = True
#             if session["username"] == request.form.get("username") and session["password"] == request.form.get("password"):
#                 logged_in = True
#             else:
#                 logged_in = False
#     if logged_in and logged_in_yet:
#         return render_template("main.html")
#     return render_template("login.html", logged_in_yet=logged_in_yet, logged_in=logged_in)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if request.form.get("log in") != None:
            return render_template("login.html")
        elif request.form.get("sign up") != None:
            return render_template("signup.html")
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if "accounts" not in session:
            session["accounts"] = dict()
        if username in session["accounts"]:
            return render_template("signup.html", alert="Uername exists")
        session["accounts"][username] = {"username": username, "password": password}
        session["current user"] = username
        return render_template("main.html")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if "accounts" not in session:
            session["accounts"] = dict()
        if username in session["accounts"]:
            if password == session["accounts"][username]["password"]:
                session["current user"] = username
                return render_template("main.html")
        return render_template("login.html", alert="account doesn't exist")
    return render_template("login.html")

@app.route("/<string:latitude>,<string:longitude>")
def hello(latitude, longitude):
    weather = requests.get(f"https://api.darksky.net/forecast/c5c0032498bd7f4153671aca4d378dfa/{latitude},{longitude}").json()
    return json.dumps(weather["currently"])

