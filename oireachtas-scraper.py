# Code that scrapes text from list of Dáil debates in urls.txt, then creates probability distribution tables for combined text 
# of all the debates and the combined contributions of each TD included in the debates. 

# importing packages

from playwright.sync_api import sync_playwright
import re
import requests
import pandas as pd 
import nltk
import spacy
import subprocess
import sys
import csv
from nltk.tokenize import word_tokenize
from nltk.tokenize import MWETokenizer
from nltk.probability import DictionaryProbDist
from nltk.corpus import stopwords
from collections import Counter

# Downloads
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('maxent_ne_chunker_tab')
nltk.download('words')
subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

#Urls we want to scrape - Opens text file containing urls and appends lines to urls variable

urls = []

with open("debate-metadata.csv", "r") as debate_metadata: # opening and reading (the r is for reading) csv file - as debate_csv (naming the variable)
    debate_csv = csv.reader(debate_metadata) # returns object - need to iterate over

    next(debate_csv) # skips first line (as these are our labels)

    for line in debate_csv:
        urls.append(line[0]) # prints only first line




#Scrape code 

full_text = []


with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Launching Browser (Headless determines whether browser opens)
        page = browser.new_page() #Creating blank new page

        for url in urls:
            page.goto(url) # Navigating to target url
            page.wait_for_selector(".questions-answers") #Wait until element with class appears 
            text_elements = page.query_selector_all(".questions-answers") # Finds all elements on page with said html class

            for text in text_elements: # Loop goes through each element and extracts text
                full_text.extend(text.inner_text())

        browser.close()

full_text = ''.join(full_text) 



#Function that filters additonal ministeral titles from speakers names 

def normalise_speaker(line): 
    match = re.search(r'\(Deputy ([^)]+)\)', line) #regex searches for pattern (returns only characters after Deputy), line shows where to search 
    if match:
        return f"Deputy {match.group(1)}" # returns what is inside of the brackets from search 
    return line # if no match was found, function returns original line unchanged 

# Creating a dictonary that categorises by speaker  

speaker_pattern = r"^(Deputy|Minister|Tánaiste|Taoiseach|Ceann Comhairle|Senator)[^\n]*$" # Defines pattern we will use to identify speakers
deputy_dictonary = {} #Empty dictionary that will contain all future contributions 
current_speaker = None #Variable that tracks who is currently speaking 

for line in full_text.split("\n"): #Splits debate into indivdual strings for every line 
    line = line.strip() #Removes whitespace 
    if not line: 
        continue #skips loop - to ignore blank lines 
    
    if re.match(speaker_pattern, line): #Detects if line matches speaker pattern
        current_speaker = normalise_speaker(line) # If yes - current line becomes a speaker name - running function to remove additional titles 
        if current_speaker not in deputy_dictonary:  
            deputy_dictonary[current_speaker] = "" #Creates new string in the dictonary for this speaker (If this is their first contribution)
        else:
            deputy_dictonary[current_speaker] += "\n\n" #Adds two new lines to seperate speeches if it is not their 1st contribution 
    else:
        if current_speaker:
            deputy_dictonary[current_speaker] += line + " " # if the line is not a speaker name, it is appended to current speaker 

# defining stop words - irrelvant words for our analysis such as "and".

stop = spacy.load("en_core_web_sm")
stop_words = stop.Defaults.stop_words

# TD analysis for loop -> Creates a dictonary that holds a probability dist table for each TD for all their contributions in the database. 

td_analysis = {}

for speaker, text in deputy_dictonary.items():
    token_td_text = word_tokenize(text.lower())
    token_td_text_c = [w for w in token_td_text if w.lower() not in stop_words]
    fdist_td_text = nltk.FreqDist()
    for word in token_td_text_c:
        fdist_td_text[word] += 1

    for punct in [".", ",", "'", "%", "s", "?", "``", "''", "-", "deputy"]:
        if punct in fdist_td_text:
            del fdist_td_text[punct]

    fdist_td_text_w = fdist_td_text.most_common(30)
    labels = [label[0] for label in fdist_td_text_w]
    if not fdist_td_text:  # check that skips TD's with small contributions to avoid prob dist error
        continue
    pdist_td_text = DictionaryProbDist(fdist_td_text, normalize=True)

    td_analysis[speaker] = pd.DataFrame({
        "words": labels,
        "freq": [frequency[1] for frequency in fdist_td_text_w],
        "probability": [pdist_td_text.prob(word[0]) for word in fdist_td_text_w]
    })

#Full text analysis 

token_text = word_tokenize(full_text.lower())
token_text_c = [w for w in token_text if w.lower() not in stop_words] 

fdist_text = nltk.FreqDist()
for word in token_text_c:
    fdist_text[word] += 1 # increases count by 1 each time a word is seen 

del fdist_text["."]
del fdist_text[","]
del fdist_text["’"]
del fdist_text["%"]
del fdist_text["s"]
del fdist_text["?"]
del fdist_text["``"]
del fdist_text["''"]
del fdist_text["-"]
del fdist_text["deputy"]

fdist_text_w = fdist_text.most_common(30)
labels = [label[0] for label in fdist_text_w] # Classifying labels for the dataframe - taken from most common 15 words in freq dist 
# Fdist returns a list of tuples - label[0] takes the first element from each tuple.

pdist_text = DictionaryProbDist(fdist_text, normalize=True) # Normalize = true: Important

pdist_text_table = pd.DataFrame({
    "words": labels,
    "freq": [frequency[1] for frequency in fdist_text_w ],
    "probability": [pdist_text.prob(word[0]) for word in fdist_text_w]
    })

# Output - Full text analysis and specific td analysis 


## print(deputy_dictonary["Deputy Paul Murphy"])




    
    
    

