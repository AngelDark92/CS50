import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

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

    # group the symbols as per sql command GROUP BY and sums the shares into a variable called total
    history = db.execute(
        "SELECT SUM(shares) as total, symbol, name FROM shares WHERE userid = :userid GROUP BY symbol HAVING total > 0", userid=session["user_id"])
    prices = []
    prices_mult = []
    # collects all the prices in this list
    for items in history:
        price = lookup(items["symbol"])
        prices.append(price["price"])
        # and a multiplication of all the items in the list per the shares
        prices_mult.append((price["price"]) * int(items["total"]))

    cash_dict = db.execute("SELECT cash FROM users WHERE id = :userid", userid=session["user_id"])
    # sending clean data trough flask from python
    cash = cash_dict[0]["cash"]

    # grand total sums the prices in the list and the current cash the user holds
    grand_total = round(cash + sum(prices_mult), 2)

    # decided to zip multiple lists in one file for jinja to iterate over
    # https://stackoverflow.com/questions/17139807/jinja2-multiple-variables-in-same-for-loop
    return render_template("index.html", cash=cash, grand_total=grand_total, lista=zip(prices, prices_mult, history))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        company = lookup(request.form.get("symbol"))

        if company == None:
            return apology("You must enter a company's symbol", 400)

        try:
            shares = int(request.form.get("shares"))

        except:
            return apology("Input must be an integer", 400)

        if shares <= 0:
            return apology('Number of shares was invalid.', 400)

        # price is already float per lookup so operations can be performed with it
        total = shares * company["price"]

        # first check if the user has enough money
        money = db.execute("SELECT cash FROM users WHERE id = :userid", userid=session["user_id"])
        curr_money = money[0]["cash"]

        if total > curr_money:
            return apology("Not enough money to spend in your account.", 400)

        else:
            # else execute the whole db operations
            db.execute("INSERT INTO shares (userid, symbol, price, shares, name) VALUES(:userid, :symbol, :prices, :shares, :name)",
                       userid=session["user_id"], symbol=request.form.get("symbol"), prices=company["price"], shares=shares, name=company["name"])
            db.execute("UPDATE users SET cash = :cash WHERE id = :userid",
                       userid=session["user_id"], cash=curr_money - total)
            flash("Bought!")

            return redirect("/")

    # if request.method is only GET or user reached by clicking on the link
    else:
        return render_template("buy.html")


@app.route("/check/", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    if request.method == "GET":

        result = db.execute("SELECT username FROM users WHERE username = :name",
                            name=request.args.get("username"))
        # check if username already exists
        if not result:
            return jsonify(True)
        else:
            return jsonify(False)

    # in case of post to check
    else:
        return apology("This page does not do anything.", 403)


@app.route("/history/")
@login_required
def history():
    """Show history of transactions"""

    history = db.execute(
        "SELECT date, time, symbol, price, shares, name FROM shares WHERE userid = :userid ORDER BY date ASC", userid=session["user_id"])

    return render_template("history.html", history=history)


@app.route("/login/", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout/")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote/", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        company = lookup(request.form.get("symbol"))

        if company != None:
            return render_template("quoted.html", company=company)
        else:
            return apology('Company\'s "symbol" does not exist')
    # if request.method is GET or user reached by clicking on the link
    else:
        return render_template("quote.html")


@app.route("/register/", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        name = request.form.get("username")

        # getting both passwords to check again if they are equal
        password = request.form.get("password")
        passw2 = request.form.get("confirmation")

        # checking wether the fields are left blank
        if password == "" or passw2 == "" or name == "":
            return apology("Missing username or passwords!", 400)
        elif not password == passw2:
            return apology("Passwords do not match", 400)

        # password protection with hash using the sha256 algorithm
        hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        insert = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hashed)",
                            username=request.form.get("username"), hashed=hashed)

        # check if insert has worked, if not username was already taken
        if not insert:
            return apology("Username already taken", 400)

        # log the user in automatically as per /login/
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=name)
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    # if the request is get renders template register.html
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # if the request method is get just get the data to display in the dropdown menu
    if request.method == "GET":
        symbols = db.execute(
            "SELECT symbol FROM shares WHERE userid = :userid GROUP BY symbol ORDER BY symbol ASC", userid=session["user_id"])
        return render_template("sell.html", symbols=symbols)

    # if it's post verify number of shares and data submitted to be sold
    if request.method == "POST":

        company = lookup(request.form.get("symbol"))

        if company == None:
            return apology("You must select a company's symbol", 400)

        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("Shares must be a number.", 400)

        if shares <= 0:
            return apology("Number od shares must be more than 0.", 400)

        # same as buy
        # getting the current cash
        money = db.execute("SELECT cash FROM users WHERE id = :userid", userid=session["user_id"])
        curr_money = money[0]["cash"]

        # getting the current amount of shares
        database = db.execute("SELECT SUM(shares) as sum FROM shares WHERE userid = :userid AND symbol = :symbol",
                              userid=session["user_id"], symbol=company["symbol"])
        db_shares = database[0]["sum"]

        # checking if requested shares are bigger than owned ones
        if shares > db_shares:
            return apology(f"Number of shares {shares} selected exceeds owned ones. {db_shares}", 400)

        # if shares is bigger then perform operations and submit
        total = shares * company["price"]
        curr_money += total
        try:
            db.execute("UPDATE users SET cash = :cash WHERE id = :userid", cash=curr_money, userid=session["user_id"])
            db.execute("INSERT INTO shares (userid, symbol, price, shares, name) VALUES (:userid, :symbol, :price, :shares, :name)",
                       userid=session["user_id"], symbol=company["symbol"], price=company["price"], shares=-(shares), name=company["name"])
        except:
            return apology("Operation could not be completed, DB error.", 400)

        flash("Sold!")
        return redirect("/")


@app.route("/passw/", methods=["GET", "POST"])
@login_required
def passw():
    """Allows the user to change password"""

    if request.method == "POST":

        # check if all passwords are entered if javascript fails
        if not request.form.get("old_pw") or not request.form.get("password1") or not request.form.get("password2"):
            return apology("All fields must be filled out.", 400)

        # get the passwords
        old_pw = request.form.get("old_pw")
        passw1 = request.form.get("password1")
        passw2 = request.form.get("password2")

        # check if password is same as before
        if old_pw == passw1:
            return apology("The new password needs to be different from the old one.", 403)

        # get the row for current userid
        rows = db.execute("SELECT hash FROM users WHERE id = :userid", userid=session["user_id"])

        # check if old_pw is correct with the hash of the current userid
        if not check_password_hash(rows[0]["hash"], old_pw):
            return apology("Password entered does not match with your current one.", 400)

        # check if passwords are the same
        if passw1 != passw2:
            return apology("New passwords do not match.", 400)

        # update password for userid and flash message. updating with passw gives error for some reason
        new_hash = generate_password_hash(request.form.get("password1"), method='pbkdf2:sha256', salt_length=8)

        db.execute("UPDATE users SET hash = :new_hash WHERE id = :userid", userid=session["user_id"], new_hash=new_hash)
        flash("Password was changed!")

    return render_template("passw.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
