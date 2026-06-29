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


#Fetching data from database 
connection = sqlite3.connect(r"dail-debates.db")
cursor = connection.cursor()

sql_statement = f"select * from debates"
cursor.execute(sql_statement)

debates = cursor.fetchall()


#Defining stop words
stop = spacy.load("en_core_web_sm")
stop_words = stop.Defaults.stop_words
stop_words.update([".", ",", "'", "%", "s", "?", "``", "''", "-", "deputy", "--", ":", "(", ")", ";", "—", "[", "]", "’"])



#Tokenising and cleaning text data, building dataframes, and uploading to database
for debate in tqdm(debates, desc="Uploading to database"):
    fdist = nltk.FreqDist()
    text = debate[4]
    tokenised_text = word_tokenize(text.lower())
    tokenised_text_without_stop = [w for w in tokenised_text if w not in stop_words]    
    for word in tokenised_text_without_stop:
        fdist[word] += 1

    common = fdist.most_common(50)
    labels = [label[0] for label in common]
    pdist = DictionaryProbDist(fdist, normalize=True)

    cursor.execute(f"""drop table if exists "{debate[0]}" """)

    debate_table = f'''create table if not exists "{debate[0]}"(
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
        insert or ignore into "{debate[0]}" (words, freq, prob)
        values("{row["words"]}", "{row["freq"]}", "{row["probability"]}")              
        ''')

#Same for full text
fdist = nltk.FreqDist()
full_text = " ".join([debate[4] for debate in debates])
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





        
    

    


    


   



