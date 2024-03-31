import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from flask_bcrypt import Bcrypt
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_dvRELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    rows = db.execute("SELECT * FROM stock WHERE user_id = :user_id", user_id=user_id)
    cashs = db.execute("SELECT cash FROM users WHERE user_id = :user_id", user_id=user_id)
    return render_template("index.html", rows=rows, cashs=cashs)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        user_id = session["user_id"]
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        price = lookup(symbol)
        total = price * shares
        cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=user_id)[0]["cash"]
        if total > cash:
            return apology("You don't have enough cash", 403)
        else:
            db.execute("INSERT INTO stock (items, shares, value, user_id, price) VALUES (?, ?, ?, ?, ?)",
                       (symbol, shares, total, user_id, price))
            db.execute("INSERT INTO history (user_id, name, shares, price) VALUES (?, ?, ?, ?)",
                       (user_id, symbol, shares, price))
            db.execute("UPDATE users SET cash = ? WHERE id = ?", (cash - total, user_id))
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    rows = db.execute("SELECT * FROM history WHERE user_id = :user_id", user_id=user_id)
    return render_template("index.html", rows=rows)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return apology("must provide username and password", 403)
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        result = lookup(symbol)
        if result is None:
            return apology("This symbol does not exist", 403)
        else:
            return result
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if not username or not password or not confirm_password:
            return apology("must provide username, password, and confirm password", 403)
        if password != confirm_password:
            return apology("passwords do not match", 403)
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if len(rows) != 0:
            return apology("this username is already exists", 403)
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed_password))
        user_id = db.execute("SELECT id FROM users WHERE username = :username", username=username)[0]["id"]
        session["user_id"] = user_id
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        user_id = session["user_id"]
        symbol = request.form.get("item")
        shares = int(request.form.get("shares"))
        price = lookup(symbol)
        total = price * shares
        num = db.execute("SELECT shares FROM stock WHERE user_id = :user_id AND items = :symbol",
                         user_id=user_id, symbol=symbol)[0]["shares"]
        cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=user_id)[0]["cash"]
        if num < shares:
            return apology("You don't have enough shares", 403)
        else:
            diff = num - shares
            real = cash + total
            db.execute("UPDATE stock SET shares = ? WHERE user_id = ? AND items = ?", (diff, user_id, symbol))
            db.execute("UPDATE users SET cash = ? WHERE id = ?", (real, user_id))
            db.execute("INSERT INTO history (user_id, name, shares, price) VALUES (?, ?, ?, ?)",
                       (user_id, symbol, shares, price))
    else:
        user_id = session["user_id"]
        rows = db.execute("SELECT items FROM stock WHERE user_id = :user_id", user_id=user_id)
        return render_template("sell.html", rows=rows)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)