'''
Conducts sentiment anaylsis on every contribution
'''

#Packages
import sqlite3
from tqdm import tqdm
import nltk 
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize

#Fetching database data
connection = sqlite3.connect(r"dail-debates.db")
cursor = connection.cursor()

cursor.execute("select td, contribution from contributions")
contributions = cursor.fetchall()

#Sentiment Analysis
analyser = SentimentIntensityAnalyzer()
average_scores = []
for contribution in tqdm(contributions, desc = "conducting sentiment analysis"):
    td = contribution[0]
    text = contribution[1]
    if not text:
        sentiment = 0
    else:
        sentences = sent_tokenize(text)
    if not sentences:
        sentiment = 0
    else:
        scores = [analyser.polarity_scores(sentence)['compound'] for sentence in sentences]
        sentiment = sum(scores) / len(scores)

    cursor.execute('''update contributions 
                   set sentiment = ? 
                   where contribution = ?''', (sentiment, contribution[1]))
    

connection.commit()
connection.close()
