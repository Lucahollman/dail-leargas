'''
'''

#Packages
import sqlite3
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.probability import DictionaryProbDist
import nltk
import spacy
from tqdm import tqdm  
from collections import Counter
from lingua import Language, LanguageDetectorBuilder
import re

def main():

    #Language analysis 
    languages = [Language.ENGLISH, Language.IRISH] #Language needs a capital - I cba
    builder = LanguageDetectorBuilder.from_languages(*languages)
    builder = builder.with_minimum_relative_distance(0.95)
    detector = builder.build()

    #Defining stop words
    with open('stop-words.txt', 'r', encoding='utf-8') as f:
        stop_words = set(line.strip() for line in f)

    #Fetching data from database and organising
    connection = sqlite3.connect(r"dail-debates.db")
    cursor = connection.cursor()

    sql_statement = f"select td, contribution, sentiment from contributions"
    cursor.execute(sql_statement)
    tds = cursor.fetchall()

    cursor.execute("SELECT id, name FROM td_metadata")
    metadata = cursor.fetchall()

    contribution_dataframe = pd.DataFrame({
            "name": [td[0] for td in tds],
            "contribution": [td[1] for td in tds],
            "sentiment": [td[2] for td in tds]
        })
    

    combined_contribution = (
        contribution_dataframe.groupby("name", as_index=False)
        .agg({
            "contribution": " ".join,
            "sentiment": "mean"
            })
    )

    #Iterating through data -> conducting language analysis 
    for index, row in combined_contribution.iterrows():
        text = (row["contribution"])
        irish_detect = detector.detect_multiple_languages_of(strip_confound_words(text))
        if len(irish_detect) == 0:
            irish_per = 0
        else:
            irish = sum(segment.word_count for segment in irish_detect if segment.language == Language.IRISH)
            total = len(text.split())
            irish_per = (f"{irish/total*100:.2f}")
        cursor.execute(f'''
        update td_metadata 
        set irish_per = ?
        where name = ?             
        ''', (irish_per, row["name"]))
        
    #Uploading sentiment scores to database
    for i, row in combined_contribution.iterrows():
        cursor.execute('''
            update td_metadata 
            set sentiment = ?
            where name = ?
        ''', (row["sentiment"], row["name"]))
    #Creating Probability Distribution Tables
    cursor.execute('''create table if not exists td_frequency_tables(
                   name integer,
                   words text,
                   freq integer,
                   prob real)''')
    
    for i, row in tqdm(combined_contribution.iterrows(), desc ="Creating tables"):
        text = (row["contribution"]) 
        name = (row["name"])
        fdist = nltk.FreqDist()
        tokenised_text = word_tokenize(text.lower())
        tokenised_text_without_stop = [w for w in tokenised_text if w not in stop_words] 
        if not tokenised_text_without_stop:
           continue   
        fdist = Counter(tokenised_text_without_stop)
        common = fdist.most_common(50)
        labels = [label[0] for label in common]
        if fdist:
            pdist = DictionaryProbDist(fdist, normalize=True)
        else:
            continue

        td_dataframe = pd.DataFrame({
        "name": name,
        "words": labels,
        "freq": [frequency[1] for frequency in common],
        "probability": [pdist.prob(word[0]) for word in common]
        })

        for j, jrow in td_dataframe.iterrows():
            cursor.execute(f'''
            insert or ignore into td_frequency_tables (name, words, freq, prob)
            values("{jrow["name"]}", "{jrow["words"]}", "{jrow["freq"]}", "{jrow["probability"]}")              
            ''')

    connection.commit()
    connection.close()


def strip_confound_words(text):
    confound_words = {
        "oireachtas", "eireann", "dail", "taoiseach", "tánaiste", "garda", "síochána", "gardaí", "seán", "ceann", "comhairle", "cathaoirleach", "gníomhach", "sinn", "fein", "fine", "gael", "fianna", "fail", "deputy", "minister",
        #deputy names
        "bennett", "cathy", "boyd", "barrett", "richard", "brady", "john",
        "buckley", "pat", "byrne", "joanna", "clarke", "sorca", "collins",
        "michael", "coppinger", "ruth", "cronin", "reada", "crowe", "sean",
        "cummins", "jen", "daly", "pa", "devine", "maire", "donnelly", "paul",
        "ellis", "dessie", "fitzmaurice", "gannon", "gary", "gibney", "sinead",
        "gogarty", "nicholas", "gould", "thomas", "graves", "ann", "guirke",
        "johnny", "hayes", "eoin", "healy-rae", "healy", "danny", "seamus",
        "hearne", "rory", "kelly", "alan", "kenny", "eoghan", "kerrane",
        "claire", "lawless", "lawlor", "george", "mac", "lochlainn", "padraig",
        "mcgettigan", "donna", "mcguinness", "conor", "mitchell", "denise",
        "murphy", "mythen", "newsome", "drennan", "natasha", "ni", "raghallaigh",
        "shonagh", "nolan", "carol", "ocallaghan", "cian", "odonoghue",
        "robert", "oflynn", "ken", "ogorman", "roderic", "oreilly", "louise",
        "orourke", "darren", "o", "laoghaire", "donnchadh", "murchu", "ruairi",
        "snodaigh", "aengus", "suilleabhain", "fiontann", "quaide", "liam",
        "quinlivan", "maurice", "rice", "sheehan", "smith", "duncan", "stanley",
        "brian", "toibin", "peadar", "wall", "mark", "ward", "charles",
        "whitmore", "jennifer", "aird", "william", "ardagh", "catherine",
        "boland", "grace", "brabazon", "tom", "brennan", "shay", "browne",
        "james", "burke", "colm", "butler", "mary", "butterly", "paula",
        "malcolm", "cahill", "callaghan", "calleary", "dara", "carrigy",
        "micheal", "carroll", "macneill", "cleere", "peter", "chap", "clendennen",
        "cooney", "joe", "cathal", "currie", "emer", "martin", "dempsey",
        "aisling", "devlin", "cormac", "dillon", "dooley", "timmy", "feighan",
        "frankie", "fleming", "sean", "foley", "norma", "gallagher", "cope",
        "geoghegan", "grealish", "noel", "heydon", "higgins", "keogh", "keira",
        "lahart", "lowry", "maxwell", "david", "mcauliffe", "mccarthy",
        "mcconalogue", "charlie", "mccormack", "tony", "mcentee", "helen",
        "mcgrath", "seamus", "mcgreehan", "erin", "moran", "kevin", "boxer",
        "moynihan", "aindrias", "shane", "murnane", "oconnor", "neville",
        "obrien", "darragh", "jim", "oconnell", "maeve", "odonnell",
        "kieran", "odonovan", "patrick", "omeara", "ryan", "oshea",
        "osullivan", "christopher", "cearuil", "naoise", "fearghaíl", "muiri",
        "richmond", "neale", "roche", "smyth", "niamh", "timmins", "edward",
        "toole", "gillian", "troy", "barry", "nash", "ged"
    }
    def normalise(word):
        fada_translation_list = str.maketrans("áéíóú",
                                      "aeiou")
        return re.sub(r"[^a-z-]", "", word.lower().translate(fada_translation_list))

    text = " ".join(
        word for word in text.split()
        if normalise(word) not in confound_words
    )
    return text



if __name__ == "__main__":
    main()
