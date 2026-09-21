'''

'''

#Packages
import sqlite3
import pandas as pd
import nltk
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

cursor.execute('''create table if not exists word_freq(
               contribution_id integer,
               word text,
               date date,
               speaker text,
               frequency integer,
               unique(contribution_id, word))''')

cursor.execute('''create index if not exists index_word_speaker on word_freq(word, speaker);''')

cursor.execute("select rowid, * from contributions where rowid not in (select distinct contribution_id from word_freq)")
contributions = cursor.fetchall()

for contribution in tqdm(contributions, desc="uploading to database"):
    contribution_id = contribution[0]
    text = contribution[6]   # was contribution[5]
    td = contribution[5]     # was contribution[4]
    date = contribution[2]   # was contribution[1]
    tokenised_text = word_tokenize(text.lower())
    tokenised_text_without_stop = [w for w in tokenised_text if w not in stop_words]
    word_counts = Counter(tokenised_text_without_stop).items()
    for word, count in word_counts:
        cursor.execute(
            "insert or ignore into word_freq(contribution_id, word, date, speaker, frequency) values(?, ?, ?, ?, ?)",
            (contribution_id, word, date, td, count)
        )

connection.commit()
connection.close()


    
