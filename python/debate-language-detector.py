'''
Script that calculates what % of a debate uses the Irish language  

    -Currently has issues relating to Lingua struggling to deal with code-switching 
    -A potential fix may be to detect how many majority Irish sentences there are, but that has less statistical power than a word ratio 
'''

#Packages
from lingua import Language, LanguageDetectorBuilder
import sqlite3
import re
from tqdm import tqdm   

def main():

    

    #Fetching data from database 
    connection = sqlite3.connect(r"dail-debates.db")
    cursor = connection.cursor()

    sql_statement = f"select * from debates"
    cursor.execute(sql_statement)

    debates = cursor.fetchall()

     #Language analysis 
    languages = [Language.ENGLISH, Language.IRISH] #Language needs a capital - I cba
    builder = LanguageDetectorBuilder.from_languages(*languages)
    builder = builder.with_minimum_relative_distance(0.95)
    detector = builder.build()

    #Iterating through database
    for debate in tqdm(debates, desc="detecting language"):
        text = debate[3]
        irish_detect = detector.detect_multiple_languages_of(strip_confound_words(text))
        irish = sum(text.word_count for text in irish_detect if text.language == Language.IRISH)
        total = len(text.split())
        irish_per = (f"{irish/total*100:.2f}")
        cursor.execute(f'''
        update debates 
        set irish_per = ?
        where id = ?             
        ''', (irish_per, debate[0]))

    #Same for full text
    full_text = " ".join(debate[3] for debate in debates)
    irish_detect = detector.detect_multiple_languages_of(strip_confound_words(full_text))
    irish = sum(full_text.word_count for full_text in irish_detect if full_text.language == Language.IRISH)
    total = len(full_text.split())
    irish_per_full = (f"{irish/total*100:.2f}")

    #Uploading to SQL
    cursor.execute('''create table if not exists fulltext_irishper(
                   irish_per decimal)''')
    cursor.execute('''insert or ignore into fulltext_irishper(irish_per)
                values(?)''', (float(irish_per_full),))
    

    connection.commit() 
    connection.close() 

#Function for cleaning text to faciliate smooth language dectection 
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

