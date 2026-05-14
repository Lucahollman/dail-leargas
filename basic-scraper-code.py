# Code that will extract a table from a website and convert into a csv file.

# importing packages
from bs4 import BeautifulSoup
import requests
import pandas as pd 

# defining website we are scraping

url = "https://en.wikipedia.org/wiki/List_of_largest_companies_in_the_United_States_by_revenue"

# Assigning name and email to project to address website restrictions 

headers = {
    "User-Agent": "prj(lucahollman@gmail.com)" 
}

# Pulling html

r = requests.get(url, headers=headers)
output = BeautifulSoup(r.text, 'html.parser')

# Singling out data we need 

table = output.find_all('table')[0]
titles = table.find_all('th')
data = table.find_all('tr')


titles_c = [title.text.strip() for title in titles]
df = pd.DataFrame(columns = titles_c) # Defining dataframe

for row in data[1:]:
    data_i = row.find_all('td')
    data_c = [value.text.strip() for value in data_i]

    length = len(df)
    df.loc[length] = data_c

# Exporting to csv

df.to_csv(r'C:\Users\lucah\Documents\folder-for-output\scrapedata.csv', index = False)






