'''
Script that conducts text anaylsis for debate text in database and reuploads to database
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

#Fetching data from database 
connection = sqlite3.connect(r"dail-debates.db")
cursor = connection.cursor()

sql_statement = f"select * from debates"
cursor.execute(sql_statement)

debates = cursor.fetchall()


#Defining stop words
with open('stop-words.txt', 'r', encoding='utf-8') as f:
    stop_words = set(line.strip() for line in f)

#Tokenising and cleaning text data, building dataframes, and uploading to database
cursor.execute('''create table if not exists debate_frequency_tables(
               id integer,
               words text,
               freq integer,
               prob real)''')

for debate in tqdm(debates, desc="Uploading to database"):
    id = debate[0]
    text = debate[3]
    tokenised_text = word_tokenize(text.lower())
    tokenised_text_without_stop = [w for w in tokenised_text if w not in stop_words]
    fdist = Counter(tokenised_text_without_stop)
    common = fdist.most_common(50)
    labels = [label[0] for label in common]
    if fdist:
         pdist = DictionaryProbDist(fdist, normalize=True)
    else:
         continue
    
    debate_dataframe = pd.DataFrame({
        "id": id,
        "words": labels,
        "freq": [frequency[1] for frequency in common],
        "probability": [pdist.prob(word[0]) for word in common]
    })

    for i, row in debate_dataframe.iterrows():
        cursor.execute(f'''
        insert or ignore into debate_frequency_tables (id, words, freq, prob)
        values("{row["id"]}", "{row["words"]}", "{row["freq"]}", "{row["probability"]}")              
        ''')

#Same for full text
fdist = nltk.FreqDist()
full_text = " ".join([debate[3] for debate in debates])
tokenised_text = word_tokenize(full_text.lower())
tokenised_text_without_stop = [w for w in tokenised_text if w not in stop_words]    
for word in tokenised_text_without_stop:
        fdist[word] += 1

common = fdist.most_common(50)
labels = [label[0] for label in common]
pdist = DictionaryProbDist(fdist, normalize=True)

cursor.execute(f"""drop table if exists full_text """)

debate_table = f'''create table if not exists full_text(
    words text primary key,
    freq integer,
    prob integer
    )''' 

cursor.execute(debate_table)

debate_dataframe = pd.DataFrame({
        "words": labels,
        "freq": [frequency[1] for frequency in common],
        "probability": [pdist.prob(word[0]) for word in common]
    })




for i, row in debate_dataframe.iterrows():
        cursor.execute(f'''
        insert or ignore into full_text (words, freq, prob)
        values("{row["words"]}", "{row["freq"]}", "{row["probability"]}")              
        ''')


connection.commit() 
connection.close()





        
    

    


    


   



