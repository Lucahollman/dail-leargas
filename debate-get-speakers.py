'''
Script that identifies all speakers that contributed to debate and uploads list of said speakers to sql 
'''

#packages 
import sqlite3
import re
import json
from tqdm import tqdm

def main():

    #Fetching data from database 
    connection = sqlite3.connect(r"dail-debates.db")
    cursor = connection.cursor()

    sql_statement = f"select * from debates"
    cursor.execute(sql_statement)
    debates = cursor.fetchall()

    #Iterating through database - Identifying Speakers
    for debate in tqdm(debates, desc="detecting speakers"):
        speaker_pattern = r"^(Deputy|The Tánaiste|The Taoiseach|An Ceann Comhairle|An Leas-Cheann Comhairle)(\s+\S+){0,2}$"
        speaker_list = []
        text = debate[4]
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue 
            if re.match(speaker_pattern, line) or line.startswith("Minister for") or line.startswith("An Cathaoirleach Gníomhach"):
                line_without_title = title_remover(line)
                if line_without_title not in speaker_list:
                    speaker_list.append(line_without_title)
        cursor.execute(f'''
        update debates 
        set speaker_list = ?
        where id = ?             
        ''', (json.dumps(speaker_list), debate[0]))

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

        

    