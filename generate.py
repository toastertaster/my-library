#!/usr/bin/env python

# generate.py
# Generate a markdown list of books
# Run by executing python generate.py

# load the YAML file library.yaml with entries like
# Section name:
#   - "<ISBN>"
#   - "<ISBN>"
#   - "<OpenLibrary identifier>"
# The quotemarks are useful to prevent the interpretation of 
# the ISBNs that begin with 0's as another base.
# Using ISBN13 identifiers also prevents this issue, so the quotes
# are unnecessary.
# The OpenLibrary API allows for any type of identifier:
# ISBN10, ISBN13, OL, etc.

# For each ISBN number, do a look up on openlibrary.org
# Title, Authors, and Cover are extracted to create the
# Markdown list.

# The output file is README.md

# The console output is used to troubleshoot any entries and determine
# what fields are missing from the openlibrary.org entry.
# For working results, need a title, by_statement (in librarian edit mode), 
# and a cover. Sometimes covers are shown but need to have a new 
# version uploaded if the entry is very old. 

import yaml
import requests
import json

inputfilename = "library.yaml"
outputfilename = "README.md"

# This function performs the RESTful query and returns a 
# key value pair with title, authors, and cover image URL
def isbnlookup(strnum):
    link = "https://openlibrary.org/api/books?bibkeys={}&format=json&jscmd=data".format(strnum)
    try:
        isbninfo = requests.get(link)

        content = None
        content = isbninfo.json()
        if content['{}'.format(strnum)]:
            content = content['{}'.format(strnum)]

        result = dict()
        result['title'] = ""
        if content['title']:
            result['title'] = content['title']

        result['authors'] = ""
        if content['authors']:
            if content['authors'][0]:
                result['authors'] = content['authors'][0]['name']
        if content['by_statement']:
            result['authors'] = content['by_statement']

        result['cover'] = ""
        if content['cover']:
            if content['cover']['medium']:
                result['cover'] = content['cover']['medium'] 
        return result

    except:
        print("isbnlookup: OpenLibrary need to inspect identifier {}".format(bookisbn))
        print(content)
        print(result)
        print("---------------")
        pass
    return None

# Load the input file
with open(inputfilename, 'r') as instream:
    try:
        indata = yaml.load(instream)
    except yaml.YAMLError as exc:
        print(exc)

# Write the output file
with open(outputfilename, 'w') as outstream:
    for entry in indata:
        print(entry) # prints the Section name:
        outstream.write("# {}\n\n".format(entry))
        outstream.write("| | Book |\n")
        outstream.write("| :-----: | :----- |\n")
        for listentry in indata[entry]:

            bookisbn = "{}".format(listentry) # string of the list entry in the YAML

            try:
                isbninfo = isbnlookup(bookisbn) # key value pair
                if isbninfo:
                    title = isbninfo['title']
                    authors = isbninfo['authors']
                    thumbnail = isbninfo['cover']
                    print("Found {} - {}".format(bookisbn, title))
                    outstream.write("| ![{}]({}) | **{}** <br/>by {} <br/> ISBN: {}| \n".format(title, thumbnail, title, authors, bookisbn))
                else:
                    print("Missing fields {}".format(bookisbn))
            except:
                print("Error on {}".format(bookisbn))
            
        outstream.write("\n")




