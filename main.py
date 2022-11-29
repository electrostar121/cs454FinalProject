from flask import Flask
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer
import os, os.path
from whoosh import index
from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh import qparser
import json

schema = Schema(url = ID(stored=True), content = TEXT(analyzer = StemmingAnalyzer()))
ix = index.open_dir("indexdir")

ranking = "tfidf"
queries = []
comb = []
searchResults = []

with open("prScores.json", "r") as f:
    scores = json.load(f)

def custom_scoring(searcher, fieldname, text, matcher):
    if(ranking == "tfidf"):
        ranked = scoring.TF_IDF().scorer(searcher, fieldname, text).score(matcher)
    elif(ranking == "bm25"):
        ranked = scoring.BM25F().scorer(searcher, fieldname, text).score(matcher)

    if searcher.stored_fields(matcher.id())["url"] in scores:
        ranked += scores[searcher.stored_fields(matcher.id())["url"]]

    return ranked

def whooshSearch():
    customWeighting = scoring.FunctionWeighting(custom_scoring)

    result = []

    with ix.searcher(weighting=customWeighting) as searcher:
        qp = QueryParser("content", schema=ix.schema).parse(queries[0])
        docs = searcher.search(qp, limit=None)

        i = 1

        while i < len(queries):
            if("" == query):
                continue

            qp = QueryParser("content", schema=ix.schema).parse(queries[i])
            nextPart = searcher.search(qp, limit=None)

            if(comb[i - 1] == "and"):
                docs.upgrade(nextPart)
            elif(comb[i - 1] == "or"):
                docs.upgrade_and_extend(nextPart)
            elif(comb[i - 1] == "not"):
                docs.filter(nextPart)

            i += 1

        for hit in docs:#prints out the hits
            result.append(hit["url"])

    return result

app=Flask(__name__)

@app.route('/')
def func():
    return "Hello"

@app.route('/query<num>/<query>')
def query(num, query):
    try:
        queries[int(num)] = query
    except:
        queries.insert(int(num), query)

    return queries

@app.route('/search')
def search():
    results = whooshSearch()

    first10 = {}

    i = 0

    while i < 10 and i < len(results):
        first10[i] = results[i]
        i += 1

    for index, item in enumerate(results):
        try:
            searchResults[index] = item
        except:
            searchResults.insert(index, item)

    return first10

@app.route('/page/<num>')
def switchPage(num):
    num = (int(num) - 1) * 10

    end = num + 10

    next10 = {}

    while num < end and num < len(searchResults):
        next10[num] = searchResults[num]
        num += 1

    return next10

@app.route('/ranking/<ranking>')
def changeRank(ranking):
    return ranking

@app.route('/combine<num>/<whichOne>')
def testing(num, whichOne):
    try:
        comb[int(num)] = whichOne
    except:
        comb.insert(int(num), whichOne)
    return comb

if __name__ == '__main__':
    app.debug=True
    app.run()