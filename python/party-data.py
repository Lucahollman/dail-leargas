'''
Script that generates overall stats for each party and appends to database
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
from lingua import Language, LanguageDetectorBuilder
import re

def main():

    #Language analysis 
    languages = [Language.ENGLISH, Language.IRISH] #Language needs a capital - I cba
    builder = LanguageDetectorBuilder.from_languages(*languages)
    builder = builder.with_minimum_relative_distance(0.95)
    detector = builder.build()

    #Defining stop words
    stop = spacy.load("en_core_web_sm")
    stop_words = stop.Defaults.stop_words
    stop_words.update([".", ",", "'", "%", "s", "?", "``", "''", "-", "deputy", "--", ":", "(", ")", ";", "—", "[", "]", "’"])

    #Database connection
    connection = sqlite3.connect(r"dail-debates.db")
    cursor=connection.cursor()

    #Accessing database
    cursor.execute(f"select * from contributions")
    contributions = cursor.fetchall()

    cursor.execute(f"select name, party from td_metadata")
    tds = cursor.fetchall()

    #Sorting into party contributions through pandas
    tds_dataframe = pd.DataFrame({
        "name":[td[0] for td in tds],
        "party":[td[1] for td in tds]
    })

    contribution_dataframe = pd.DataFrame({
        "name":[c[1] for c in contributions],
        "contribution": [c[2] for c in contributions],
        "sentiment": [c[3] for c in contributions]
    })

    combined_contribution = (
            contribution_dataframe.groupby("name", as_index=False)
            .agg({
                "contribution": " ".join,
                "sentiment": "mean"
                })
        )

    merged_df = pd.merge(tds_dataframe, combined_contribution, on="name", how="left") 
    merged_df["contribution"] = merged_df["contribution"].fillna("").astype(str)

    party_df = (
        merged_df.groupby("party", as_index=False)
        .agg({
            "contribution": " ".join,
            "sentiment": "mean"
        })
    )

    #Creating SQL Table
    cursor.execute('''create table if not exists parties(
                   id integer primary key autoincrement,
                   party_name text,
                   party_sentiment integer,
                   party_irish_per integer,
                   photo text,
                   link text)
                   ''')

    #Appending info to database
    for i, row in party_df.iterrows():
        sentiment = (row["sentiment"])
        name = (row["party"])
        cursor.execute('''insert or ignore into parties(party_sentiment, party_name)
                    values(?, ?)''', (sentiment, name))

    #Langauge Anaylsis
    for i, row in party_df.iterrows():
        text = (row["contribution"])
        irish_detect = detector.detect_multiple_languages_of(strip_confound_words(text))
        if len(irish_detect) == 0:
            irish_per = 0
        else:
            irish = sum(segment.word_count for segment in irish_detect if segment.language == Language.IRISH)
            total = len(text.split())
            irish_per = (f"{irish/total*100:.2f}")
        cursor.execute('''update parties set party_irish_per = ?
                   where party_name = ?''', (irish_per, row["party"]))
        
    #Creating Probability Distribution Tables
    for i, row in tqdm(party_df.iterrows(), desc ="Creating tables"):
        text = (row["contribution"]) 
        fdist = nltk.FreqDist()
        tokenised_text = word_tokenize(text.lower())
        tokenised_text_without_stop = [w for w in tokenised_text if w not in stop_words] 
        if not tokenised_text_without_stop:
           continue   
        for word in tokenised_text_without_stop:
            fdist[word] += 1
        common = fdist.most_common(50)
        labels = [label[0] for label in common]
        pdist = DictionaryProbDist(fdist, normalize=True)

        party_table = f'''create table if not exists "{row["party"]}"(
            words text primary key,
            freq integer,
            prob integer
            )''' 
    
        cursor.execute(party_table)

        party_dataframe = pd.DataFrame({
        "words": labels,
        "freq": [frequency[1] for frequency in common],
        "probability": [pdist.prob(word[0]) for word in common]
        })

        for j, jrow in party_dataframe.iterrows():
            cursor.execute(f'''
            insert or ignore into "{row["party"]}" (words, freq, prob)
            values("{jrow["words"]}", "{jrow["freq"]}", "{jrow["probability"]}")              
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
