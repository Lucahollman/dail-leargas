'''

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
from collections import Counter


#Defining stop words
with open('stop-words.txt', 'r', encoding='utf-8') as f:
        stop_words = set(line.strip() for line in f)


#database connection
connection = sqlite3.connect("dail-debates.db")
cursor = connection.cursor()
cursor.execute("select * from contributions")
contributions = cursor.fetchall()

#Creating SQL table and index
cursor.execute('''create table if not exists word_freq(
               word text,
               date date,
               speaker text,
               frequency integer)''')

cursor.execute('''create index index_word_speaker on word_freq(word, speaker);''')


for contribution in tqdm(contributions, desc= "uploading to database"):
    text = contribution[3]
    td = contribution[2]
    date = contribution[1]
    tokenised_text = word_tokenize(text.lower())
    tokenised_text_without_stop = [w for w in tokenised_text if w not in stop_words]
    word_counts = Counter(tokenised_text_without_stop).items()
    for word, count in word_counts:
        cursor.execute("insert into word_freq(word, date, speaker, frequency)" 
        "values(?, ?, ?, ?)", (word, date, td, count))

connection.commit()
connection.close()


    
