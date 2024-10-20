import os
from flask import Flask, render_template
import requests
import sqlite3
from transformers import T5ForConditionalGeneration, T5Tokenizer

app = Flask(__name__)

# Initialize model and tokenizer
model = T5ForConditionalGeneration.from_pretrained('t5-small')
tokenizer = T5Tokenizer.from_pretrained('t5-small')

def fetch_articles(api_key):
    url = (
        'https://newsapi.org/v2/everything?'
        'q=politics&'  # Adjust keyword here if needed
        'from=2024-10-10&'
        'sortBy=popularity&'
        'apiKey=' + api_key
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        print(f"Fetched articles: {articles}")  # Debug statement
        return articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching articles: {e}")
        return []

def setup_database():
    try:
        conn = sqlite3.connect('news.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                title TEXT NOT NULL,
                summary TEXT NOT NULL
            )
        ''')
        conn.commit()
        print("Summaries table created or already exists.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """Escape special characters."""
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

def summarize(text):
    if text is None or text.strip() == "":
        return "No content available to summarize."
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def store_summaries(summaries):
    if not summaries:
        print("No summaries to store.")
        return
    with sqlite3.connect('news.db') as conn:
        c = conn.cursor()
        c.executemany('INSERT INTO summaries (title, summary) VALUES (?, ?)', summaries)
        conn.commit()
        print(f"Stored summaries: {summaries}")  # Debug statement

def get_summaries():
    with sqlite3.connect('news.db') as conn:
        c = conn.cursor()
        c.execute('SELECT title, summary FROM summaries')
        return c.fetchall()

@app.route("/")
def weekly():
    print("Weekly route accessed")  # Debug statement
    summaries = get_summaries()  # Fetch the summaries from the database
    if not summaries:
        return apology("No summaries available", 404)
    return render_template("index.html", summaries=summaries)


@app.route("/daily")
def daily():
    return apology("This page is not complete", 400)

@app.route("/monthly")
def monthly():
    return apology("This page is not complete", 400)

@app.route("/past")
def past():
    return apology("This page is not complete", 400)

if __name__ == '__main__':
    api_key = 'c3379e1e7c3b49db8ea3f8971ba0c2f2'  # Your API key directly used here

    # Setup the database
    setup_database()  # This should create the summaries table if it doesn't exist

    # Fetch articles and summarize them
    articles = fetch_articles(api_key)
    if articles:
        summaries = []
        for article in articles:
            title = article.get('title')
            content = article.get('content')
            if title and content:
                summary = summarize(content)
                summaries.append((title, summary))
                print(f"Summary generated for: {title}")  # Debug statement
        
        store_summaries(summaries)  # Store summaries in the database
        
        # Check if summaries have been stored
        stored_summaries = get_summaries()
        print(f"Stored summaries: {stored_summaries}")  # Debug statement
    else:
        print("No articles fetched.")

    # Start the Flask app
    app.run(debug=True)
