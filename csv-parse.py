import csv

urls = []

with open("debate-metadata.csv", "r") as debate_metadata: # opening and reading (the r is for reading) csv file - as debate_csv (naming the variable)
    debate_csv = csv.reader(debate_metadata) # returns object - need to iterate over

    next(debate_csv) # skips first line (as these are our labels)

    for line in debate_csv:
        urls.append(line[0]) # prints only first line

print(urls)