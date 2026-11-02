'''
Script that queries Oireachtas API and populates SQL database
'''

# Packages
import requests
import pandas as pd
import sqlite3
import json
from tqdm import tqdm
from itertools import groupby
from xml_parser import parse_debate_xml
import datetime


# Connecting to Database
connection = sqlite3.connect(r"dail-debates.db")
cursor = connection.cursor()

# Creating tables
cursor.execute('''create table if not exists debates(
               id integer primary key autoincrement,
               title text,
               date text,
               text text,
               category text,
               irish_per integer,
               wordsnum,
               contributionsnum,
               unique(title, date)
               )''')

cursor.execute('''create table if not exists contributions(
               debate_id integer,
               date date,
               section_title,
               text_type text,
               td text,
               contribution text,
               sentiment real,
               contribution_order integer,
               unique(debate_id, contribution_order)
               )''')


# Accessing API
all_debates = []
skip = 0
limit = 50

cursor.execute("select max(date) from debates")
row = cursor.fetchone()
date_start = row[0] if row[0] else "2024-12-18" #Start of 34th Dáil
date_end = datetime.date.today().isoformat()

while True:
    response = requests.get(
        "https://api.oireachtas.ie/v1/debates",
        params={
            "chamber": "dail",
            "date_start": date_start,
            "date_end": date_end,
            "limit": limit,
            "skip": skip,
        }
    )

    data = response.json()
    results = data.get("results", [])

    all_debates.extend(results)

    if len(results) < limit:
        break

    skip += limit

# Sorting data and uploading to database
for day in tqdm(all_debates, desc="uploading to database"):
    debate_record = day["debateRecord"]
    if debate_record["house"]["chamberType"] != "house":
        continue
 
    date = debate_record["date"]
    xml_link = debate_record["formats"]["xml"]["uri"]
 
    xml_response = requests.get(xml_link)
    xml_response.raise_for_status()
 
    debates = parse_debate_xml(xml_response.content)
    for title, contribution_list in debates.items():
        overall_text = []
        for contribution in contribution_list:
            if contribution["text_type"] == "speech":
                overall_text.append(contribution["text"])
 
        overall_text = "\n".join(overall_text)
 
        cursor.execute(
            '''insert or ignore into debates(title, date, text)
               values(?, ?, ?)''',
            (title, date, overall_text)
        )
 
        debate_id = cursor.execute(
            """select id from debates 
               where title = ? and date = ?""",
            (title, date)
        ).fetchone()[0]
 
 
        for i, contribution in enumerate(contribution_list):

            cursor.execute(
                '''insert or ignore into contributions(
                    debate_id,
                    date,
                    section_title,
                    text_type,
                    td,
                    contribution,
                    contribution_order
                )
                values(?, ?, ?, ?, ?, ?, ?)''',
                (
                    debate_id,
                    date,
                    contribution["section_title"],
                    contribution["text_type"],
                    contribution["speaker"],
                    contribution["text"],
                    i
                )
            )
 
 
# Removing unwanted debate sections
cursor.execute("""
DELETE FROM debates 
WHERE title LIKE '%Chuaigh an Cathaoirleach Gníomhach%' 
OR title LIKE '%Chuaigh an Ceann Comhairle i gceannas%'
OR title LIKE '%Comhaltaí Nua a Chur in Aithne%'
OR title LIKE '%Message from Select Committee%'
OR title LIKE '%Ministerial Rota for Parliamentary Questions%'
OR title LIKE '%prelude%'
""")
 
 
# Categorising debates
cursor.execute("""
UPDATE debates 
SET category = CASE
 
WHEN title LIKE '%Order of Business%' 
THEN 'Business of Dáil'
 
WHEN title LIKE '%Business of Dáil%' 
THEN 'Business of Dáil'
 
WHEN title LIKE '%LEADER%' 
THEN 'Leaders Questions'
 
WHEN title LIKE '%Priority Questions%' 
THEN 'Priority Questions'
 
WHEN title LIKE '%Bill%' 
THEN 'Bill'
 
WHEN title LIKE '%topical%' 
THEN 'Topical Issue Matter'
 
WHEN title LIKE '%motion%' 
THEN 'Motion'
 
WHEN title LIKE '%Questions%' 
THEN 'Other Questions'
 
ELSE 'Other'
 
END
""")
 
 
connection.commit()
connection.close()