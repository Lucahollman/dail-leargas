'''
Script that conducts sentiment analysis on debate text
'''

#Packages 
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
import sqlite3

from tqdm import tqdm
from textblob import TextBlob

#Fetching data from database 
connection = sqlite3.connect(r"dail-debates.db")
cursor = connection.cursor()

sql_statement = f"select * from debates"
cursor.execute(sql_statement)
debates = cursor.fetchall()

text = debates[20][4]




#Vader sentiment analysis - chunked by sentence
analyser = SentimentIntensityAnalyzer()
sentences = sent_tokenize(text)
scores = [analyser.polarity_scores(sentence)['compound'] for sentence in sentences]
average_score = sum(scores) / len(scores)
print(average_score)


        
