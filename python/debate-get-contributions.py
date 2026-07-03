'''
Script that identifies td contributions + sentiment and uploads to database
'''

#packages 
import sqlite3
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
from tqdm import tqdm

def main():

    #Fetching data from database 
    connection = sqlite3.connect(r"dail-debates.db")
    cursor = connection.cursor()

    sql_statement = f"select * from debates"
    cursor.execute(sql_statement)
    debates = cursor.fetchall()
    analyser = SentimentIntensityAnalyzer()

    #Creating SQL table
    cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS contributions(    
                        debate_id integer,
                        date DATE,
                        td text,
                        contribution text,
                        sentiment real
                        )""")

    for debate in tqdm(debates, desc="Uploading to database"):
        text = debate[4]
        date = debate[3]
        #Creating contribution Dictionary
        speaker_pattern = r"^(Deputy|Deputies|The Tánaiste|The Taoiseach|An Ceann Comhairle|An Leas-Cheann Comhairle)(\s+[A-ZÀ-Ö][a-zA-ZÀ-ÿ']*){0,5}$"
        deputy_list = {}
        current_speaker = None
        for line in text.split("\n"):
                line = line.strip()
                if not line:
                    continue 
                if re.match(speaker_pattern, line) or line.startswith("Minister for") or line.startswith("An Cathaoirleach Gníomhach"):
                    current_speaker = title_remover(line)
                    if current_speaker not in deputy_list:
                        deputy_list[current_speaker] = ""
                    else:
                        deputy_list[current_speaker] += "\n\n"
                else:
                    if current_speaker:
                        deputy_list[current_speaker] += line + " "

        #Vader sentiment analysis - chunked by sentence + inserting into SQL
        deputy_list.pop("Deputies", None)
        average_scores = []
        for td, contribution in deputy_list.items():
            sentences = sent_tokenize(contribution)
            if not sentences:
                sentiment = 0
            else:
                scores = [analyser.polarity_scores(sentence)['compound'] for sentence in sentences]
                sentiment = sum(scores) / len(scores)

            cursor.execute('''
            INSERT INTO contributions (debate_id, date, td, contribution, sentiment)
            VALUES (?, ?, ?, ?, ?)
                        ''', (debate[0], date, td, contribution, sentiment))


    connection.commit() 
    connection.close()


#function that removes titles from deputy names i.e removing a ministerial title 
def title_remover(line): 
    match = re.search(r'\(Deputy ([^)]+)\)', line) 
    if match:
        return f"Deputy {match.group(1)}" 
    return line 

if __name__ == "__main__":
    main()