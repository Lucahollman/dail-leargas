# Code that scrapes text from Sinn Fein policy page, tokenises it, and creates a probability distribution for the data

# importing packages
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

# Assigning name and email to html pull request 
headers = {
    "User-Agent": "prj(lucahollman@gmail.com)" 
}

# defining urls we are scraping

url = "https://housing.sinnfein.ie/vision/"

url1 = "https://housing.sinnfein.ie/need/"

# Pulling html

r = requests.get(url, headers=headers)
output = BeautifulSoup(r.text, 'html.parser')

r1 = requests.get(url1, headers=headers)
output1 = BeautifulSoup(r1.text, 'html.parser')

# Singling out data we need - Finds all paragraphs within a certain html class

data = output.find('div', class_ = 'entry-content')
content = data.find_all('p')

data1 = output1.find('div', class_ = 'entry-content')
footer1 = data1.find('div', class_ = 'et_pb_row et_pb_row_5')
if footer1:
    footer1.decompose() #removes contents of footer1 from parsed html
content1 = data1.find_all('p')


# Tokenising data - seperating by word - and cleaning. 
# Strip() first cleans the text by removing html jargon. Join() combines text into single string with a space
# between each string (' ') - This avoids sentences merging into eachother i.e "he went into a bar.It was nice."
# word_tokenize() splits this string into a listt of indivudal words and punctuation. 
 

text_0 = word_tokenize(
    ' '.join(
        [value.text.strip().lower() for value in content]
    ))

idcombine = MWETokenizer([('sinn', 'féin')], separator=' ')
text_0 = idcombine.tokenize(text_0)

text_1 = word_tokenize(
    ' '.join(
        [value.text.strip().lower() for value in content1]
    ))

idcombine1 = MWETokenizer([('sinn', 'féin')], separator=' ')
text_1 = idcombine.tokenize(text_1)

# defining stop words - irrelvant words for our analysis such as "and".

stop = spacy.load("en_core_web_sm")
stop_words = stop.Defaults.stop_words

# Removing stop words from data

textc_0 = [w for w in text_0 if w.lower() not in stop_words]

textc_1 = [w for w in text_1 if w.lower() not in stop_words]
        
# Creating frequency distribution 

fdist = nltk.FreqDist()
for word in textc_0 + textc_1:
    fdist[word] += 1 # increases count by 1 each time a word is seen 

del fdist["."]
del fdist[","]
del fdist["’"]
del fdist["%"]
del fdist["s"]

fdist_w = fdist.most_common(15)
labels = [label[0] for label in fdist_w] # Classifying labels for the dataframe - taken from most common 15 words in freq dist 
# Fdist returns a list of tuples - label[0] takes the first element from each tuple.


# Creating Probability Dist 

pdist_url = DictionaryProbDist(fdist, normalize=True) # Normalize = true: Important

pdist_url_table = pd.DataFrame({
    "words": labels,
    "freq": [frequency[1] for frequency in fdist_w ],
    "probability": [pdist_url.prob(word[0]) for word in fdist_w]
    })

print(pdist_url_table)



