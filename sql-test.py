import sqlite3

# connection - connects to database
#cursor - allows us to interact with database
connection = sqlite3.connect(r"C:\Users\lucah\Documents\manifesto-scraper-prj\dail-debates.db")
cursor = connection.cursor()

# Creating table
#autoincrmenet automatically assigns IDs to items 


debate_table = '''create table if not exists debates(
    ID integer primary key autoincrement,
    name text,
    category text, 
    date DATE,
    text text
)''' 

cursor.execute(debate_table)

# insert statement

insert = "insert into debates(name, category, date) values()"

cursor.execute(insert)
connection.commit() 

connection.close()