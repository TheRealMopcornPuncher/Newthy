from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/daily")
def daily():
    return apology("This page is not complete", 400)

@app.route("/monthly")
def monthly():
    return apology("This page is not complete", 400)

@app.route("/past")
def past():
    return apology("This page is not complete", 400)