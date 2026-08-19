"""
Testing tokenising 
"""

#Packages
import sqlite3
import pandas as pd
import nltk
from tqdm import tqdm   
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.probability import DictionaryProbDist
from collections import Counter

def clean_token(token):
    return token.strip("'’‘\"`.,;:!?()[]{}%#&-—")


#Defining stop words
with open('stop-words.txt', 'r', encoding='utf-8') as f:
        stop_words = set(line.strip() for line in f)


text = """The Minister's so-called 'buy-out' scheme, first announced in 2024, was described by Deputy O'Rourke as a 'click-worthy' distraction from the real issue. [54456/26] I put it to the Minister that this isn't a one-off; it's part of a pattern dating back to the '90s. The report (see Ref. no. 12) notes that 90% of applicants — some 7,860 people — were left without a decision, and that the Dept. hasn't clarified whether this constitutes a breach of the '2021 Act. Mr. Hildegarde-Naughton's officials didn't respond, and neither did the NCSE's press office. Isn't it time the Taoiseach's own department practised what it preaches, rather than hiding behind 'ongoing review'?"""



tokenised_text = word_tokenize(text.lower())
cleaned_text = (clean_token(w) for w in tokenised_text)
tokenised_text_without_stop = [w for w in cleaned_text if w and w not in stop_words]
print(tokenised_text_without_stop)