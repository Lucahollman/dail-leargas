'''
Script that calculates what % of a debate uses the Irish language  

    -Currently has issues relating to Lingua struggling to deal with code-switching 
    -A potential fix may be to detect how many majority Irish sentences there are, but that has less statistical power than a word ratio 


'''

#Packages
from lingua import Language, LanguageDetectorBuilder
import sqlite3

def main():

    

    #Fetching data from database 
    connection = sqlite3.connect(r"dail-debates.db")
    cursor = connection.cursor()

    sql_statement = f"select * from debates"
    cursor.execute(sql_statement)

    debates = cursor.fetchall()
    text = debates[10][4]

    #Language analysis 
    languages = [Language.ENGLISH, Language.IRISH] #Language needs a capital - I cba
    builder = LanguageDetectorBuilder.from_languages(*languages)
    builder = builder.with_minimum_relative_distance(0.95)
    detector = builder.build()

    for result in detector.detect_multiple_languages_of(strip_confoundwords(text)):
       print(f"{result.language}: '{text[result.start_index:result.end_index]}'")


    result = detector.detect_multiple_languages_of(strip_confoundwords(text))
    result_total = detector.detect_multiple_languages_of(text)
    irish = sum(text.word_count for text in result if text.language == Language.IRISH)
    total = sum(text.word_count for text in result_total)
    print(f"Irish: {irish/total*100:.3f}%")
    

confound_words = {"oireachtas", "éireann", "dáil", "taoiseach", "tánaiste", "garda", "síochána", "gardaí", "seán", "ceann", "comhairle", "cathaoirleach", "gníomhach"}
def strip_confoundwords(text):
    return " ".join(w for w in text.split() if w.lower() not in confound_words)

if __name__ == "__main__":
    main()

