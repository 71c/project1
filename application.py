import os

from flask import Flask, render_template, request, session, jsonify
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

    # Make sure location exists.
    location = db.execute("SELECT * FROM locations WHERE zipcode = :zipcode", {"zipcode": zipcode}).fetchone()
    if location is None:
        return render_template('error.html', message="404 error: page not found")

    # I use this a few times for database stuff
    variables = {"user_id": session["user id"], "zipcode": zipcode}

    give_alert = False

    if request.method == "POST":
            # whether the user already logged a visit
            visit_was_logged = db.execute("SELECT * FROM checkins WHERE user_id = :user_id AND zipcode = :zipcode", variables).rowcount > 0

            if not visit_was_logged:
                comment = request.form.get("comment")
                variables["comment"] = comment
                db.execute("INSERT INTO checkins (user_id, zipcode, comment) VALUES (:user_id, :zipcode, :comment)", variables)
                db.commit()
            else:
                give_alert = True


    username = db.execute("SELECT * FROM accounts WHERE id = :user_id", variables).fetchone()["username"]

    loc = db.execute("SELECT * FROM locations WHERE zipcode = :zipcode", variables).fetchone()
    latitude = loc.latitude
    longitude = loc.longitude

    weather = requests.get(f"https://api.darksky.net/forecast/c5c0032498bd7f4153671aca4d378dfa/{latitude},{longitude}").json()["currently"]
    time = datetime.datetime.fromtimestamp(
        weather["time"]
    ).strftime('%Y-%m-%d %H:%M:%S')

    # comments = db.execute("SELECT user_id, comment FROM checkins WHERE zipcode = :zipcode", variables).fetchall()
    comments = db.execute("""SELECT username, comment
    FROM checkins INNER JOIN accounts ON (checkins.user_id = accounts.id AND checkins.zipcode = :zipcode)""", variables)

    return render_template("location.html",
        location=loc,
        username=username,
        weather=weather,
        time=time,
        comments=comments,
        alert="You already submitted a check-in for this location." if give_alert else "",
        alert_class="alert alert-danger" if give_alert else "")


@app.route("/api/<string:zipcode>")
def flight_api(zipcode):
    """Return details about a single location."""

    # Make sure location exists.
    location = db.execute("SELECT * FROM locations WHERE zipcode = :zipcode", {"zipcode": zipcode}).fetchone()
    if location is None:
        return render_template('error.html', message="404 error: page not found")

    # get number of check-ins
    checkin_count = db.execute("""SELECT username, comment
        FROM checkins INNER JOIN accounts ON
        (checkins.user_id = accounts.id AND checkins.zipcode = :zipcode)""", {"zipcode": zipcode}).rowcount

    # return JSON about location
    return jsonify({
            "place_name": location.city.capitalize(),
            "state": location.state,
            "latitude": float(location.latitude),
            "longitude": float(location.longitude),
            "zip": location.zipcode,
            "population": location.population,
            "check_ins": checkin_count
        })

if __name__ == '__main__':
    app.debug = True
    app.run()
