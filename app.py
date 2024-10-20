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
    url = ('https://newsapi.org/v2/everything?'
           'q=keyword&'
           'from=2023-10-01&'
           'sortBy=popularity&'
           'apiKey=' + api_key)
    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        return articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching articles: {e}")
        return []

def setup_database():
    with sqlite3.connect('news.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS summaries
                     (title TEXT, summary TEXT)''')
        conn.commit()

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
    if text is None:
        return "No content available to summarize."
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def store_summaries(summaries):
    with sqlite3.connect('news.db') as conn:
        c = conn.cursor()
        c.executemany('INSERT INTO summaries (title, summary) VALUES (?, ?)', summaries)
        conn.commit()

def get_summaries():
    with sqlite3.connect('news.db') as conn:
        c = conn.cursor()
        c.execute('SELECT title, summary FROM summaries')
        return c.fetchall()

@app.route("/")
def weekly():
    summaries = get_summaries()  # Fetch the summaries from the database
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
    api_key = 'c3379e1e7c3b49db8ea3f8971ba0c2f2'
    
    # Setup the database and fetch articles
    setup_database()
    articles = fetch_articles(api_key)
    
    # Summarize articles and store them in the database
    summaries = [(article['title'], summarize(article.get('content'))) for article in articles]
    store_summaries(summaries)
    
    # Start the Flask app
    app.run(debug=True)
