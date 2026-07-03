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

    debate_list = {}
    q_headers = []

    for debate_entry in debate_record["debateSections"]:
        debate = debate_entry["debateSection"]
        if debate.get("containsDebate") == False:
            continue
        if debate["parentDebateSection"] is not None:
            title = debate["parentDebateSection"]["showAs"]
        else:
            title = debate["showAs"]

        if title not in debate_list:
            debate_list[title] = []
        
        section_title = debate["showAs"]
        
        for contribution in debate.get("text", []):
            if contribution.get("textType") == "heading":
                continue
            text = contribution.get("text")
            if text and "  " in text:
                clean_text = text.split("  ", 1)[1].strip()
            else:
                continue
            speaker = contribution["speaker"]["showAs"] if contribution.get("speaker") else None
            debate_list[title].append({"speaker": speaker, "text": clean_text, "ot_text": text, "section_title": section_title})
            
    for title, contributions in debate_list.items():
        text_blocks = []
        last_section_title = None

        for c in contributions:
            if c["section_title"] != last_section_title:
                text_blocks.append(f"{c['section_title']}")
                last_section_title = c["section_title"]
            text_blocks.append(c["ot_text"])
        overall_text = "\n\n".join(text_blocks)

        
        # speaker_list = []
        # for c in contributions:
        #     speaker_list.append(c["speaker"])
        # speaker_list = set(speaker_list)
        # for value in [None, " A Deputy", " Deputies"]:
        #     speaker_list.discard(value)

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
