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

__version__ = 1

import traceback
import re
import yaml
import requests

INPUTFILENAME = "library.yaml"
OUTPUTFILENAME = "README.md"

# These are used to determine if the by_statement included
# a "by " or "edited by".  If not, a "by " is added
match1 = re.compile(r"^by .*$")
match2 = re.compile(r"edited by .*$")

def isbnlookup(strnum):
    """
    This function performs the RESTful query and returns a
    key value pair with title, authors, and cover image URL
    Input is any valid identifier on OpenLibrary: ISBN10, ISBN13, LCCN, OL
    """
    link = "https://openlibrary.org/api/books?bibkeys={}&format=json&jscmd=data".format(strnum)
    try:
        isbnrequest = requests.get(link)

        content = None
        content = isbnrequest.json()
        if content['{}'.format(strnum)]:
            content = content['{}'.format(strnum)]

        result = dict()
        result['title'] = ""
        if 'title' in content:
            result['title'] = content['title']
        else:
            print("Missing title for {}".format(strnum))

        result['authors'] = ""
        if 'authors' in content:
            if content['authors'][0]:
                result['authors'] = content['authors'][0]['name']
        if 'by_statement' in content:
            result['authors'] = content['by_statement']
        else:
            if len(content['authors']) > 1:
                print("Multiple authors but no by_statement for {}".format(strnum))
        if result['authors'] == "":
            print("Missing authors for {}".format(strnum))

        result['cover'] = ""
        if 'cover' in content:
            if content['cover']['medium']:
                result['cover'] = content['cover']['medium']
        else:
            print("Missing cover for {}".format(strnum))
        return result

    except:
        print("isbnlookup: OpenLibrary need to inspect identifier {}".format(bookisbn))
        print(content)
        print("++++++ converted to")
        print(result)
        print("==== traceback")
        traceback.print_exc()
        print("-------------------------------------")
        pass
    return None

# Load the input file
with open(INPUTFILENAME, 'r') as instream:
    try:
        indata = yaml.load(instream, Loader=yaml.BaseLoader)
    except yaml.YAMLError as exc:
        print(exc)

# Write the output file
with open(OUTPUTFILENAME, 'w') as outstream:
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

                    if not (match1.match(authors) or match2.match(authors)):
                        authors = "by {}".format(authors)
                    print("Found {} - {}".format(bookisbn, title))
                    outstream.write("| ![{}]({}) | **{}** <br/>{} <br/> ISBN: {}| \n".format(title, thumbnail, title, authors, bookisbn))
                else:
                    print("Missing fields {}".format(bookisbn))
            except:
                print("Error on {}".format(bookisbn))

        outstream.write("\n")




