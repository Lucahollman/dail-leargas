'''
Script that conducts text anaylsis for debate text in database
'''

#Packages 
import sqlite3
import pandas as pd 
import nltk
import spacy
from tqdm import tqdm   
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.probability import DictionaryProbDist


#Fetching data from database 
connection = sqlite3.connect(r"dail-debates.db")
cursor = connection.cursor()

sql_statement = f"select * from debates"
cursor.execute(sql_statement)

debates = cursor.fetchall()
connection.close()

#Defining stop words
stop = spacy.load("en_core_web_sm")
stop_words = stop.Defaults.stop_words
stop_words.update([".", ",", "'", "%", "s", "?", "``", "''", "-", "deputy"])



#Tokenising and cleaning text data
fdist = nltk.FreqDist()

for debate in debates:
    text = debate[3]
    tokenised_text = word_tokenize(text.lower())
    tokenised_text_without_stop = [w for w in tokenised_text if w not in stop_words] 
    print(tokenised_text_without_stop)
    1/0
    for word in tokenised_text_without_stop:
        fdist[word] += 1
    fdist
        
    

    


    


   



