import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

# Define a function to render an apology message to the user.
# This function takes a message and an optional HTTP status code (default is 400).
# It escapes special characters in the message to ensure it's safe to display.
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        # Replace special characters with their escaped versions.
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    # Render the apology template with the escaped message and status code.
    return render_template("apology.html", top=code, bottom=escape(message)), code

# Define a decorator to require a user to be logged in to access a route.
# If the user is not logged in, they are redirected to the login page.
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is logged in by looking for a user_id in the session.
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Define a function to look up a stock quote for a given symbol.
# This function uses the IEX Cloud API to fetch the quote.
def lookup(symbol):
    """Look up quote for symbol."""

    # Attempt to contact the IEX Cloud API to get the stock quote.
    try:
        # Retrieve the API key from the environment variables.
        api_key = os.environ.get("API_KEY")
        # Construct the API request URL, including the symbol and API key.
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        # Raise an exception if the request failed.
        response.raise_for_status()
    except requests.RequestException:
        # If there was an error contacting the API, return None.
        return None

    # Attempt to parse the response as JSON.
    try:
        quote = response.json()
        # Extract and return the company name, latest price, and symbol from the quote.
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        # If there was an error parsing the response, return None.
        return None

# Define a function to format a value as USD.
def usd(value):
    """Format value as USD."""
    # Use Python's f-string formatting to format the value as a currency.
    return f"${value:,.2f}"