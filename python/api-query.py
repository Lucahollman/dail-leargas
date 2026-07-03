#Packages
import requests
import pandas as pd 
import sqlite3
import json
from tqdm import tqdm

#Connecting to Database
connection = sqlite3.connect(r"dail-debates.db")
cursor = connection.cursor()

cursor.execute('''create table if not exists debates(
               id integer primary key autoincrement,
               title text,
               date text,
               text text,
               category text,
               irish_per integer,
               speaker_list text
               )''')

cursor.execute('''create table if not exists contributions(
               debate_id integer,
               date date,
               td text,
               contribution text,
               sentiment real
               )''')


#Accessing API
response = requests.get("https://api.oireachtas.ie/v1/debates", params={
    "chamber": "dail",
    "date_start": "2026-05-20",   
    "date_end": "2026-07-03",
    "limit": 1000
})
data = response.json()


#Sorting data and uploading to database
for day in tqdm(data["results"], desc = "uploading to database"):
    debate_record = day["debateRecord"]
    date = debate_record["date"]

    for debate_entry in debate_record["debateSections"]:
        debate = debate_entry["debateSection"]
        title = debate["showAs"]

        contributions = []
        for contribution in debate.get("text", []):
            if contribution.get("textType") == "heading":
                continue
            text = contribution.get("text")
            if text and "  " in text:
                clean_text = text.split("  ", 1)[1].strip()
            else:
                continue
            speaker = contribution["speaker"]["showAs"] if contribution.get("speaker") else None
            contributions.append({"speaker": speaker, "text": clean_text, "ot_text": text})
        

        overall_text = []
        for contribution in contributions:
            overall_text.append(contribution["ot_text"])
        overall_text = "\n\n".join(overall_text)

        speaker_list = []
        for c in contributions:
            speaker_list.append(c["speaker"])
        speaker_list = set(speaker_list)
        for value in [None, " A Deputy", " Deputies"]:
            speaker_list.discard(value)

        cursor.execute('''insert or ignore into debates(title, date, text)
                       values(?, ?, ?)''', (title, date, overall_text))
        
        debate_id = cursor.lastrowid

        for contribution in contributions:
            cursor.execute('''insert or ignore into contributions(debate_id, date, td, contribution)
                        values(?, ?, ?, ?)''', (debate_id, date, contribution["speaker"], contribution["text"]))
            

cursor.execute("""
               DELETE FROM debates WHERE title LIKE '%Chuaigh an Cathaoirleach Gníomhach%' 
                OR title LIKE '%Chuaigh an Ceann Comhairle i gceannas%'
                OR title LIKE '%Comhaltaí Nua a Chur in Aithne%'
                OR title LIKE '%Message from Select Committee%'
                OR title LIKE '%Ministerial Rota for Parliamentary Questions%'                
               """)

cursor.execute("""UPDATE debates SET category = CASE
                WHEN title LIKE '%Order of Business%' THEN 'Business of Dáil' 
                WHEN title LIKE '%Business of Dáil%' THEN 'Business of Dáil' 
                WHEN title LIKE '%LEADER%' THEN 'Leaders Questions'
                WHEN title LIKE '%Priority Questions%' THEN 'Priority Questions'
                WHEN title LIKE '%Bill%' THEN 'Bill'
                WHEN title LIKE '%topical%' THEN 'Topical Issue Matter'
                WHEN title LIKE '%motion%' THEN 'Motion'
                WHEN title LIKE '%Questions%' THEN 'Other Questions'
                ELSE 'Other'
               END""")
            
connection.commit()
connection.close()
















# specific_date = data["results"][0]["debateRecord"]
# debate = specific_date["debateSections"][28]["debateSection"]  ###13 as example of blank priority question 

# title = debate["showAs"]


# contributions = []
# for contribution in debate["text"]:
#     if contribution.get("textType") == "heading":
#         continue
#     text = contribution.get("text")
#     speaker = contribution["speaker"]["showAs"] if contribution.get("speaker") else None
#     contributions.append({"speaker": speaker, "text": text})


# overall_text = []
# for contribution in contributions:
#     overall_text.append(contribution["text"])
# overall_text = "\n\n".join(overall_text)

# speaker_list = []
# for c in contributions:
#     speaker_list.append(c["speaker"])
# speaker_list = set(speaker_list)
# speaker_list.discard(None)
# speaker_list.discard(" A Deputy")
# speaker_list.discard(" Deputies")
# print(speaker_list)
