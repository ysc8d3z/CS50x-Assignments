import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
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
    rows = db.execute("""
        SELECT symbol, name, SUM(shares) as total_shares
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol
        HAVING total_shares > 0""",
        session["user_id"])
    holdings = []
    grand_total = 0
    for row in rows:
        stock = lookup(row["symbol"])
        holdings.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "shares": row["total_shares"],
            "price": usd(stock["price"]),
            "total": usd(stock["price"] * row["total_shares"])
        })
        grand_total += stock["price"] * row["total_shares"]

    rows = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = rows[0]["cash"]
    grand_total += cash

    return render_template("index.html", holdings=holdings, cash=usd(cash), grand_total=usd(grand_total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        stock = lookup(symbol)
        shares = int(request.form.get("shares"))
        user_id = session["user_id"]
        stock_name = stock["name"]
        stock_price = stock["price"]

        if stock == None:
            return apology("Invalid Symbol")
        if shares < 1:
            return apology("Invalid number of shares")

        # Get the amount of cash current user has
        rows = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        cash = rows[0]["cash"]

        updated_cash = cash - (stock_price * shares)
        # Check if user can afford the stock
        if updated_cash < 0:
            return apology("Insufficient buying power")
        # Purchase stock
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)
        db.execute("""
            INSERT INTO transactions
            (user_id, name, symbol, shares, price, type)
            VALUES (?, ?, ?, ?, ?, ?)""",
            user_id, stock_name, symbol, shares, stock_price, "buy")
        if shares > 1:
            flash(f"Bought {shares} shares of {symbol}!")
        else:
            flash(f"Bought {shares} share of {symbol}!")
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    transactions = db.execute("""
        SELECT symbol, shares, price, time
        FROM transactions
        WHERE user_id = ?
    """, session['user_id'])
    for i in range(len(transactions)):
        transactions[i]['price'] = usd(transactions[i]['price'])
    return render_template("history.html", transactions=transactions)


@app.route("/watchlist", methods=["GET", "POST"])
@login_required
def watchlist():
    flag = True
    """Show users list of stocks on watch"""
    if request.method == "POST":
        symbol_to_lookup = request.form.get("symbol")
        symbol = request.form.get("symbol").upper()
        stock = lookup(symbol_to_lookup)

        if stock == None:
            return apology("Invalid Symbol")
        else:
            stock_price = stock["price"]
            stock_name = stock["name"]
            watched = db.execute("""
                SELECT symbol
                FROM watchlist
                WHERE user_id = ?
            """, session['user_id'])

            if watched == False:
                db.execute("""
                    INSERT INTO watchlist
                    (user_id, name, symbol, price)
                    VALUES (?, ?, ?, ?)""",
                    session['user_id'], stock_name, symbol, stock_price)
                flash(f"{symbol} was added to your watchlist!")
                return render_template("watchlist.html")

            for i in range(len(watched)):
                if symbol == watched[i]['symbol']:
                    flag = False
            if flag == True:
                db.execute("""
                    INSERT INTO watchlist
                    (user_id, name, symbol, price)
                    VALUES (?, ?, ?, ?)""",
                    session['user_id'], stock_name, symbol, stock_price)
                flash(f"{symbol} was added to your watchlist!")
                return render_template("watchlist.html")
            else:
                flash(f"{symbol} is already in your watchlist!")
                return render_template("watchlist.html")

    watching = db.execute("""
        SELECT symbol, price
        FROM watchlist
        WHERE user_id = ?
    """, session['user_id'])
    for i in range(len(watching)):
        watching[i]['price'] = usd(watching[i]['price'])
    return render_template("watchlist.html", watching=watching)


@app.route("/login", methods=["GET", "POST"])
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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # if request method "POST" look up the stock price
    if request.method == "POST":
        symbol_to_lookup = request.form.get("symbol")
        stock = lookup(symbol_to_lookup)
        if stock != None:
            return render_template("quoted.html", stock={'name': stock['name'], 'symbol': stock['symbol'], 'price': usd(stock['price'])})
        else:
            return apology("Invalid Symbol")
    # if request method "GET" display form to look stock quote (quote.html)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # When form is submitted via POST, insert the new user into users table.
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # Ensure username was submitted
        if not username:
            return apology("must provide username")

        # Ensure username isn't taken
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return apology("that username is already taken, please enter another")

        # Ensure password was submitted
        elif not password:
            return apology("must provide password")

        # Ensure password confirmation was submitted
        elif not confirmation:
            return apology("must provide password confirmation")

        # Ensure passwords match
        if confirmation != password:
            return apology("passwords do not match")

        # Hash the password
        pass_hash = generate_password_hash(password)#, method='pbkdf2:sha256', salt_length=8)
        # Insert user into databse
        rows = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, pass_hash)

        return redirect("/")

    # When requested via GET, should display registration form.
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        stock = lookup(symbol)
        shares = int(request.form.get("shares"))
        user_id = session["user_id"]
        stock_name = stock["name"]
        stock_price = stock["price"]

        if shares < 1:
            return apology("Invalid number of shares")

        rows = db.execute("""
            SELECT symbol, SUM(shares) as totalShares
            FROM transactions
            WHERE user_id = ?
            GROUP BY symbol
            HAVING totalShares > 0;
        """, user_id)
        for row in rows:
            if row["symbol"] == symbol:
                if shares > row['totalShares']:
                    return apology("Too Many Shares")

        # Get the amount of cash current user has
        rows = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        cash = rows[0]["cash"]

        updated_cash = cash + (stock_price * shares)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)
        db.execute("""
            INSERT INTO transactions
            (user_id, name, symbol, shares, price, type)
            VALUES (?, ?, ?, ?, ?, ?)""",
            user_id, stock_name, symbol, -1 * shares, stock_price, "buy")
        if shares > 1:
            flash(f"Sold {shares} shares of {symbol}!")
        else:
            flash(f"Sold {shares} share of {symbol}!")
        return redirect("/")

    else:
        rows = db.execute("""
            SELECT symbol
            FROM transactions
            WHERE user_id = ?
            GROUP BY symbol
            HAVING SUM(shares) > 0;
        """, session["user_id"])
        return render_template("sell.html", symbols = [row["symbol"] for row in rows])


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
