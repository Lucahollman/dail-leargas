# Code that.... 

# importing packages

from playwright.sync_api import sync_playwright
import re
from bs4 import BeautifulSoup
import requests
import pandas as pd 
import nltk
import spacy
import subprocess
import sys
import matplotlib.pyplot as plt
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


#Creating a scraping function


with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Launching Browser (Headless determines whether browser opens)

        page = browser.new_page() #Creating blank new page
        page.goto("https://www.oireachtas.ie/en/debates/debate/dail/2026-05-14/43/") # Navigating to target url

        title = (f"Page title: {page.title()}") #F string combines two strings - in this case "page title:" and the scraped content 

        page.wait_for_selector(".questions-answers") #Wait until element with class appears 
        text_elements = page.query_selector_all(".questions-answers") # Finds all elements on page with said html class

        full_text = ""
        for text in text_elements: # Loop goes through each element and extracts text
            full_text += (text.inner_text()) + "\n" #\n ensures blocks of text remain seperated 

        browser.close()
        
#Function that filters additonal ministeral titles from speakers names 

def normalise_speaker(line): 
    match = re.search(r'\(Deputy ([^)]+)\)', line) 
    if match:
        return f"Deputy {match.group(1)}" # returns what is inside of the brackets from search 
    return line 

# Creating a dictonary that categorises by speaker  

speaker_pattern = r"^(Deputy|Minister|Tánaiste|Taoiseach|Ceann Comhairle|Senator)[^\n]*$" # Defines pattern we will use to identify speakers
contribution = {} #Empty dictionary that will contain all future contributions 
current_speaker = None #Variable that tracks who is currently speaking 

for line in full_text.split("\n"): #Splits debate into indivdual strings for every line 
    line = line.strip() #Removes whitespace 
    if not line: 
        continue #skips loop - to ignore blank lines 
    
    if re.match(speaker_pattern, line): #Detects if line matches speaker pattern
        current_speaker = normalise_speaker(line) # If yes - current line becomes a speaker name 
        if current_speaker not in contribution:  
            contribution[current_speaker] = "" #Creates new string in the dictonary for this speaker (If this is their first contribution)
        else:
            contribution[current_speaker] += "\n\n" #Adds two new lines to seperate speeches if it is not their 1st contribution 
    else:
        if current_speaker:
            contribution[current_speaker] += line + " " # if the line is not a speaker name, it is appended to current speaker 

# exp print(contribution["Deputy Helen McEntee"])

# Tokenising all debates in database

token_text = word_tokenize(full_text.lower())

# defining stop words - irrelvant words for our analysis such as "and".

stop = spacy.load("en_core_web_sm")
stop_words = stop.Defaults.stop_words

# Removing stop words from data

token_text_c = [w for w in token_text if w.lower() not in stop_words]

# Creating frequency distribution 

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

fdist_text_w = fdist_text.most_common(30)
labels = [label[0] for label in fdist_text_w] # Classifying labels for the dataframe - taken from most common 15 words in freq dist 
# Fdist returns a list of tuples - label[0] takes the first element from each tuple.


# Creating Probability Dist 

pdist_text = DictionaryProbDist(fdist_text, normalize=True) # Normalize = true: Important

pdist_text_table = pd.DataFrame({
    "words": labels,
    "freq": [frequency[1] for frequency in fdist_text_w ],
    "probability": [pdist_text.prob(word[0]) for word in fdist_text_w]
    })

print(pdist_text_table)





    
    
    

