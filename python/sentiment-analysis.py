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

cursor.execute("SELECT td, contribution FROM contributions")
contributions = cursor.fetchall()

# Sentiment Analysis
analyser = SentimentIntensityAnalyzer()

updates = []

for contribution in tqdm(contributions, desc="Conducting sentiment analysis"):
    td = contribution[0]
    text = contribution[1]

    if not text:
        sentiment = 0
    else:
        sentences = sent_tokenize(text)

        if not sentences:
            sentiment = 0
        else:
            scores = [
                analyser.polarity_scores(sentence)['compound']
                for sentence in sentences
            ]
            sentiment = sum(scores) / len(scores)

    
    updates.append((sentiment, text))


cursor.executemany(
    '''
    UPDATE contributions
    SET sentiment = ?
    WHERE contribution = ?
    ''',
    updates
)

connection.commit()
connection.close()