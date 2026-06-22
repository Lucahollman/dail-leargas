'''
Script that...
    -Issue - Problems with assigning text to TDs - print dataframe to see
'''

#packages 
import sqlite3
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
import pandas as pd 
from tqdm import tqdm



def main():

    #Fetching data from database 
    connection = sqlite3.connect(r"dail-debates.db")
    cursor = connection.cursor()

    sql_statement = f"select * from debates"
    cursor.execute(sql_statement)
    debates = cursor.fetchall()

    
    for debate in tqdm(debates, desc="Uploading to database"):
        text = debate[4]
        #Creating contribution Dictionary
        speaker_pattern = r"^(Deputy|Deputies|The Tánaiste|The Taoiseach|An Ceann Comhairle|An Leas-Cheann Comhairle)(\s+[A-ZÀ-Ö][a-zA-ZÀ-ÿ'-]*){0,5}$"
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
        #Creating SQL table
        cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS "{debate[0]}_contributions"(    
                        td text,
                        contribution text,
                        sentiment integer
                        )""")
    
        #Vader sentiment analysis - chunked by sentence
        deputy_list.pop("Deputies", None)
        average_scores = []
        for td, contribution in deputy_list.items():
            analyser = SentimentIntensityAnalyzer()
            sentences = sent_tokenize(contribution)
            if not sentences:
                average_scores.append(0)
                continue
            scores = [analyser.polarity_scores(sentence)['compound'] for sentence in sentences]
            average_scores.append(sum(scores) / len(scores))

        #Creating Dataframe
        debate_contributions_df = pd.DataFrame({
            "td": list(deputy_list.keys()),
            "contribution": list(deputy_list.values()),
            "sentiment": average_scores
        })

        #Uploading DF to SQL           
        for i, row in debate_contributions_df.iterrows():
            cursor.execute(f'''
            insert or ignore into "{debate[0]}_contributions" (td, contribution, sentiment)
            values(?, ?, ?)            
            ''', (row["td"], row["contribution"], row["sentiment"]))
         
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

