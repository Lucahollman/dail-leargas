'''
Script that queries Oireachtas api and populates SQL database with 
'''

#Packages
import requests
import pandas as pd 
import sqlite3
import json
from tqdm import tqdm
from itertools import groupby

#Connecting to Database
connection = sqlite3.connect(r"dail-debates.db")
cursor = connection.cursor()

#Creating tables
cursor.execute('''create table if not exists debates(
               id integer primary key autoincrement,
               title text,
               date text,
               text text,
               category text,
               irish_per integer
               )''')

cursor.execute('''create table if not exists contributions(
               debate_id integer,
               date date,
               section_title,
               text_type text,
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

    debates = {}
    for debate_entry in debate_record["debateSections"]:
        debate = debate_entry["debateSection"]
        if debate.get("containsDebate") == False:
            continue
        if debate["parentDebateSection"] is not None:
            title = debate["parentDebateSection"]["showAs"]
        else:
            title = debate["showAs"]
        section_title = debate["showAs"]

        contributions_list = debates.setdefault(title, [])
        
        for contribution in debate.get("text", []):
            if contribution.get("textType") != "heading":
                type = contribution.get("textType")
            else:
                continue
            text = contribution.get("text")
            if text and "  " in text:
                prefix, text = text.split("  ", 1)
                if len(prefix) > 100:  
                    text = text.strip()
            else:
                text = text.strip() if text else text
            if contribution["speaker"] != None:
                speaker = contribution["speaker"]["showAs"]
            else:
                speaker = None
            contributions_list.append({ "text_type": type, "speaker": speaker, "text": text, "section_title": section_title})
            
   
    for title, contribution_list in debates.items():
        overall_text = []
        for contribution in contribution_list:
            if contribution["text_type"] == "speech":
                overall_text.append(contribution["text"])
            else:
                continue
        overall_text = "\n".join(overall_text)

        cursor.execute('''insert or ignore into debates(title, date, text)
                    values(?, ?, ?)''', (title, date, overall_text))
    
        debate_id = cursor.execute("""select id from debates where title = ? and date = ?""", (title, date)).fetchone()[0]

        for contribution in contribution_list:
            cursor.execute('''insert or ignore into contributions(debate_id, date, section_title, text_type, td, contribution)
                        values(?, ?, ?, ?, ?, ?)''', (debate_id, date, contribution["section_title"], contribution["text_type"], contribution["speaker"], contribution["text"]))

        

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
