'''
Conducts sentiment analysis on every contribution
'''

# Packages
import sqlite3
from tqdm import tqdm
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize

# Fetching database data
connection = sqlite3.connect(r"dail-debates.db")
cursor = connection.cursor()

cursor.execute("SELECT rowid, td, contribution FROM contributions WHERE sentiment IS NULL")
contributions = cursor.fetchall()

# Sentiment Analysis
analyser = SentimentIntensityAnalyzer()

updates = []

for contribution in tqdm(contributions, desc="Conducting sentiment analysis"):
    row_id = contribution[0]
    td = contribution[1]
    text = contribution[2]

    if not text:
        sentiment = 0
    else:
        sentences = sent_tokenize(text)
        if not sentences:
            sentiment = 0
        else:
            scores = [analyser.polarity_scores(s)['compound'] for s in sentences]
            sentiment = sum(scores) / len(scores)

    updates.append((sentiment, row_id))

cursor.executemany(
    '''UPDATE contributions SET sentiment = ? WHERE rowid = ?''',
    updates
)

connection.commit()
connection.close()