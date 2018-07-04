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

# r
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if "user_id" not in session:
            # new_id = len(user_ids)
            # user_ids += [new_id]
            session["username"] = request.form.get("username")
            session["password"] = request.form.get("password")
    return render_template("index.html", notes=[session["username"], session["password"]])
# dd
@app.route("/<string:latitude>,<string:longitude>")
def hello(latitude, longitude):
    weather = requests.get(f"https://api.darksky.net/forecast/c5c0032498bd7f4153671aca4d378dfa/{latitude},{longitude}").json()
    return json.dumps(weather["currently"])

