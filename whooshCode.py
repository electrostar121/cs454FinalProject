from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer
import os, os.path
from whoosh import index
from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh import qparser
import json


def indexAdd(ix, location):#this function adds to the index from the file location
    writer = ix.writer()

    files = os.listdir(location)
    files = [f for f in files if os.path.isfile(location+'/'+f)]#we get all the files in that directory given

    for x in files:
        if x.endswith(".json"):#we make sure it ends with .txt
            try:
                with open(location + x, 'r') as file:
                    data = json.load(file)
            except:
                data = {"url": x, "contents": ""}
            writer.add_document(url=data["url"], content=data["contents"])#add the doc to the index

    writer.commit()


def indexSearch(ix, numResults):#this is where the searching is done
    while 1:

        raw = input("Input: ")#get the input from the user
        parts = raw.split()

        if(parts[0] == "-d"):#see if the user put in -d then parse the rest of the input

            print("Doing it disjunctive")

            qp = QueryParser("content", schema=ix.schema, group=qparser.OrGroup)
            q = qp.parse(" ".join(parts[1:]))

        else:

            print("Doing it conjunctive")

            qp = QueryParser("content", schema=ix.schema)
            q = qp.parse(" ".join(parts))

        print("Results:")

        with ix.searcher() as searcher:
            results = searcher.search(q, limit=numResults)#get the results, and limit it to the number that is set

            for hit in results[:numResults]:#prints out the hits
                print("\t" + hit["url"])

        print("\n\n")

if __name__ == "__main__":

    #this is how we can change the location of where we generate our index from and how many results we want

    location = "pages/"
    numResults = 10

    #this is our schema
    schema = Schema(url = ID(stored=True),
                    content = TEXT(analyzer = StemmingAnalyzer()))

    #checks if the index already exists, if it doesn't then create an index based off of the directory we pass it
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
        ix = index.create_in("indexdir", schema)
        indexAdd(ix, location)
    else:
        ix = index.open_dir("indexdir")

    print("Size of database:", ix.doc_count(), "\n")#we print out the size of the database

    #indexSearch(ix, numResults)#and this is where our searching is done