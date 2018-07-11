import os

from flask import Flask, render_template, request, session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests, json
from flask import abort, redirect, url_for
import datetime
# https://stackoverflow.com/questions/3682748/converting-unix-timestamp-string-to-readable-date

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

def print_stuff():
    print("stuff")

@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if len(username) < 1:
            return render_template("signup.html", alert="You need to have a username", alert_class="alert alert-danger")
        if len(password) < 1:
            return render_template("signup.html", alert="You need to have a password", alert_class="alert alert-danger")
        if db.execute("SELECT * FROM accounts WHERE username = :username", {"username": username}).rowcount > 0:
            return render_template("signup.html", alert="Uername already exists", alert_class="alert alert-danger")
        db.execute("INSERT INTO accounts (username, password) VALUES (:username, :password)", {"username": username, "password": password})
        db.commit()
        session["user id"] = db.execute("SELECT id FROM accounts WHERE username = :username", {"username": username}).fetchone()["id"]
        return redirect(url_for('search'))
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
            print(username)
            return redirect(url_for('search'))
        return render_template("login.html", alert="wrong username or password", alert_class="alert alert-danger")
    return render_template("login.html")

@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        search_term = request.form.get("search term")
        if search_term != None:
            return redirect(url_for('results', search_term=search_term))

        if request.form.get("log out") != None:
            session["user id"] = -1
            return render_template("index.html")

    username = db.execute("SELECT * FROM accounts WHERE id = :id", {"id": session["user id"]}).fetchone()["username"]
    return render_template("search.html", username=username)

@app.route("/results/<string:search_term>", methods=["POST", "GET"])
def results(search_term):
    print("HIE")
    results = []
    if search_term.isdigit(): # zip code
        results = db.execute("SELECT * FROM locations WHERE zipcode = :zipcode", {"zipcode": search_term}).fetchall()
    else:
        results = db.execute(f"SELECT * FROM locations WHERE city LIKE :city", {"city": f"%{search_term}%".upper()}).fetchall()

    username = db.execute("SELECT * FROM accounts WHERE id = :id", {"id": session["user id"]}).fetchone()["username"]

    return render_template("results.html", results=results, username=username, message="" if len(results) > 0 else "No results.")

@app.route("/<string:zipcode>", methods=["GET", "POST"])
def location(zipcode):
    if zipcode.isdigit():
        if request.method == "POST":
            if request.form.get("log visit") != None:
                if db.execute("SELECT * FROM checkins WHERE user_id = :user_id AND zipcode = :zipcode", {"user_id": session["user id"], "zipcode": zipcode}).rowcount == 0:
                    db.execute("INSERT INTO checkins (user_id, zipcode) VALUES (:user_id, :zipcode)",
                        {"user_id": session["user id"], "zipcode": zipcode})
                    db.commit()


        username = db.execute("SELECT * FROM accounts WHERE id = :id", {"id": session["user id"]}).fetchone()["username"]

        loc = db.execute("SELECT * FROM locations WHERE zipcode = :zipcode", {"zipcode": zipcode}).fetchone()
        latitude = loc.latitude
        longitude = loc.longitude

        weather = requests.get(f"https://api.darksky.net/forecast/c5c0032498bd7f4153671aca4d378dfa/{latitude},{longitude}").json()["currently"]
        time = datetime.datetime.fromtimestamp(
            weather["time"]
        ).strftime('%Y-%m-%d %H:%M:%S')

        return render_template("location.html", location=loc, username=username, weather=weather, time=time)

@app.route("/<string:latitude>,<string:longitude>")
def hello(latitude, longitude):
    weather = requests.get(f"https://api.darksky.net/forecast/c5c0032498bd7f4153671aca4d378dfa/{latitude},{longitude}").json()
    return json.dumps(weather["currently"])

if __name__ == '__main__':
    app.debug = True
    app.run()
