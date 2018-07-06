import os

from flask import Flask, render_template, request, session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests, json

app = Flask(__name__)
app.secret_key = "super secret key"
# thing wasn't working. used this: https://stackoverflow.com/questions/26080872/secret-key-not-set-in-flask-session

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["POST", "GET"])
def index():
    # if request.method == "POST":
    #     if request.form.get("log in") != None:
    #         return render_template("login.html")
    #     elif request.form.get("sign up") != None:
    #         return render_template("signup.html")
    return render_template("index.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        if request.form.get("back") != None:
            return render_template("index.html")
        username = request.form.get("username")
        password = request.form.get("password")
        if db.execute("SELECT * FROM accounts WHERE username = :username", {"username": username}).rowcount > 0:
            return render_template("signup.html", alert="Uername already exists")
        db.execute("INSERT INTO accounts (username, password) VALUES (:username, :password)", {"username": username, "password": password})
        db.commit()
        # print(type(db.execute("SELECT id FROM accounts WHERE username = :username", {"username": username}).fetchone()))
        session["user id"] = db.execute("SELECT id FROM accounts WHERE username = :username", {"username": username}).fetchone()["id"]
        return render_template("main.html", username=username)
    return render_template("signup.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        if request.form.get("back") != None:
            return render_template("index.html")
        username = request.form.get("username")
        password = request.form.get("password")
        if db.execute("SELECT * FROM accounts WHERE username = :username and password = :password", {"username": username, "password": password}).rowcount > 0:
            session["user id"] = db.execute("SELECT id FROM accounts WHERE username = :username", {"username": username}).fetchone()["id"]
            return render_template("main.html", username=username)
        return render_template("login.html", alert="wrong username or password")
    return render_template("login.html")

@app.route("/main")
def logout():
    if request.method == "POST":
        if request.form.get("log out") != None:
            session["user id"] = -1
    # username = db.execute("SELECT * FROM accounts WHERE id = :id", {"id": session["user id"]}).fetchone()["username"]
    # print(db.execute("SELECT * FROM accounts WHERE id = :id", {"id": session["user id"]}).fetchone())
    # return render_template("main.html", username=username)

@app.route("/<string:latitude>,<string:longitude>")
def hello(latitude, longitude):
    weather = requests.get(f"https://api.darksky.net/forecast/c5c0032498bd7f4153671aca4d378dfa/{latitude},{longitude}").json()
    return json.dumps(weather["currently"])

if __name__ == '__main__':
    app.debug = True
    app.run()