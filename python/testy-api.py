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
               contributionsnum
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


# Accessing API
all_debates = []
skip = 0
limit = 50

while True:
    response = requests.get(
        "https://api.oireachtas.ie/v1/debates",
        params={
            "chamber": "dail",
            "date_start": "2024-12-18",
            "date_end": "2026-08-03",
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

    debates = {}
    for debate_entry in debate_record["debateSections"]:
        debate = debate_entry["debateSection"]
        if debate.get("containsDebate") == False:
            continue

        if debate["parentDebateSection"] is not None:
            title = debate["parentDebateSection"]["showAs"]
        else:
            title = debate["showAs"]