'''
Script that gets metadata for all tds in dail34 and uploads to sql
'''
#Packages
import requests
import pandas as pd 
import sqlite3

#Creating database
connection = sqlite3.connect(r"dail-debates.db")
cursor = connection.cursor()
td_meta_table = '''create table if not exists td_metadata(
            id integer primary key autoincrement,
            name text,
            party text,
            constituency text,
            photo text,
            sentiment integer,
            irish_per integer,
            unique(id, name) 
            )'''
cursor.execute(td_meta_table)

#Accessing API
response = requests.get("https://api.oireachtas.ie/v1/members", params={
    "chamber": "dail",
    "house_no": 34,
    "limit": 300
})

#Grabbing data and putting into dataframe
data = response.json()
tds = []
data = response.json()
for member in data["results"]:
    m = member["member"]
    name = "Deputy " + m["fullName"]
    member_code = m["memberCode"]
    photo_url = f"https://data.oireachtas.ie/ie/oireachtas/member/id/{member_code}/image/large"
    membership = m["memberships"][0]["membership"]
    party = membership["parties"][0]["party"]["showAs"] if membership["parties"] else "Independent"
    constituency = membership["represents"][0]["represent"]["showAs"] if membership["represents"] else ""
    tds.append({"name": name, "photo": photo_url, "party": party, "constituency": constituency})
td_metadata = pd.DataFrame(tds)

#Inserting into Database
for i, row in td_metadata.iterrows():
        cursor.execute(f'''
        insert or ignore into td_metadata (name, photo, party, constituency)
        values("{row["name"]}", "{row["photo"]}", "{row["party"]}", "{row["constituency"]}")              
        ''')

connection.commit()
connection.close()