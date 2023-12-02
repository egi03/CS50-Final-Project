import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
import random
import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finalproject.db")

# Global variable
randomlist = []

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        return render_template("index.html")
    return render_template("play.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username")

        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    if username == "" or len(db.execute('SELECT username FROM users WHERE username = ?', username)) > 0:
        return apology("Invalid Username")
    if password == "":
        return apology("Invalid password")
    elif password != confirmation:
        return apology("Passwords don't match")

    db.execute('INSERT INTO users (username, hash) VALUES(?, ?)', username, generate_password_hash(password))
    rows = db.execute("SELECT * FROM users WHERE username = ?", username)
    session["user_id"] = rows[0]["id"]
    # Redirect user to home page
    return redirect("/")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/play", methods=["GET", "POST"])
@login_required
def play():
    global randomlist
    if request.method == 'GET':
        randomlist = random.sample(range(1,36), 5)
        # Getting 5 random numbers to see which cars will be promped
        q1 = db.execute("SELECT name FROM cars WHERE id = ?", randomlist[0])[0]['name']
        q2 = db.execute("SELECT name FROM cars WHERE id = ?", randomlist[1])[0]['name']
        q3 = db.execute("SELECT name FROM cars WHERE id = ?", randomlist[2])[0]['name']
        q4 = db.execute("SELECT name FROM cars WHERE id = ?", randomlist[3])[0]['name']
        q5 = db.execute("SELECT name FROM cars WHERE id = ?", randomlist[4])[0]['name']
        return render_template("play.html", q1=q1, q2=q2, q3=q3, q4=q4, q5=q5)

    correct = 0
    a1 = request.form.get("first")
    a2 = request.form.get("second")
    a3 = request.form.get("third")
    a4 = request.form.get("forth")
    a5 = request.form.get("fifth")

    if a1 == db.execute("SELECT body_styles FROM cars WHERE id = ?", randomlist[0])[0]['body_styles']:
        correct += 1
    if a2 == db.execute("SELECT body_styles FROM cars WHERE id = ?", randomlist[1])[0]['body_styles']:
        correct += 1
    if a3 == db.execute("SELECT body_styles FROM cars WHERE id = ?", randomlist[2])[0]['body_styles']:
        correct += 1
    if a4 == db.execute("SELECT body_styles FROM cars WHERE id = ?", randomlist[3])[0]['body_styles']:
        correct += 1
    if a5 == db.execute("SELECT body_styles FROM cars WHERE id = ?", randomlist[4])[0]['body_styles']:
        correct += 1

    user_id = session["user_id"]
    time = datetime.datetime.now()
    db.execute("INSERT INTO results (user_id, result, date) VALUES(?, ?, ?)", user_id, correct, time)

    return render_template("end.html", result=correct)


@app.route("/results")
@login_required
def results():
    user_id = session["user_id"]
    user = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]['username']
    result = db.execute("SELECT result, date FROM results WHERE user_id = ?", user_id)
    return render_template("results.html", result=result, user=user)

