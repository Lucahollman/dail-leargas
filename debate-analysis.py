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



#Tokenising, cleaning, and building dataframes from text data
fdist = nltk.FreqDist()
debate_dataframes = []

for debate in debates:
    text = debate[3]
    tokenised_text = word_tokenize(text.lower())
    tokenised_text_without_stop = [w for w in tokenised_text if w not in stop_words]    
    for word in tokenised_text_without_stop:
        fdist[word] += 1

    common = fdist.most_common(30)
    labels = [label[0] for label in common]
    pdist = DictionaryProbDist(fdist, normalize=True)
    
    debate_dataframe = pd.DataFrame({
        "words": labels,
        "freq": [frequency[1] for frequency in common],
        "probability": [pdist.prob(word[0]) for word in common]
    })
    debate_dataframes.append((debate[0], debate[1], debate[2], debate_dataframe))

print(debate_dataframes[1])

##### TO DO: Use lingua to detect what % of text is Irish before tokenises the text. Then append to debate_dataframes tuple

        
    

    


    


   



