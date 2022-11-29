from flask import Flask, redirect, url_for, request, render_template
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer
import os, os.path
from whoosh import index
from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh import qparser
from urllib.parse import urlparse
import json

#this is what runs the entire website

schema = Schema(url = ID(stored=True), content = TEXT(analyzer = StemmingAnalyzer(), stored=True))
ix = index.open_dir("indexdir")

ranking = "tfidf"
queries = []
comb = []
searchResults = []
restrictDomain = []

with open("prScores.json", "r") as f:#preloads the page rank scores
    scores = json.load(f)

def custom_scoring(searcher, fieldname, text, matcher):
    ranked = 0
    if(ranking == "tfidf"):
        ranked += scoring.TF_IDF().scorer(searcher, fieldname, text).score(matcher)
    
    if(ranking == "bm25"):
        ranked += scoring.BM25F().scorer(searcher, fieldname, text).score(matcher)

    if searcher.stored_fields(matcher.id())["url"] in scores:
        ranked += scores[searcher.stored_fields(matcher.id())["url"]]

    return ranked

def whooshSearch():#this is where all the searching gets done
    customWeighting = scoring.FunctionWeighting(custom_scoring)

    urls = []
    content = []

    with ix.searcher(weighting=customWeighting) as searcher:
        qp = QueryParser("content", schema=ix.schema).parse(queries[0])
        docs = searcher.search(qp, limit=None)

        i = 1

        while i < len(queries):#does all the queries
            if("" == query):
                continue

            qp = QueryParser("content", schema=ix.schema).parse(queries[i])
            nextPart = searcher.search(qp, limit=None)

            if(comb[i - 1] == "and"):#this is where the combination of the queries happens
                docs.upgrade(nextPart)
            elif(comb[i - 1] == "or"):
                docs.upgrade_and_extend(nextPart)
            elif(comb[i - 1] == "not"):
                docs.filter(nextPart)

            i += 1
            
        if restrictDomain:#checks to see if we restrict what domain ending we can search
            for hit in docs:
                for domain in restrictDomain:
                    if domain in hit["url"]:
                        urls.append(hit["url"])
                        content.append(hit["content"][:200])              
        else:
            for hit in docs:#prints out the hits
                urls.append(hit["url"])
                content.append(hit["content"][:200])

    return urls, content#returns the urls and content

app=Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")#gets the home page

@app.route('/results/', methods=['GET', 'POST'])#results page
def results():
    if request.method == 'POST':
        data = request.form
    else:
        data = request.args
    
    global queries 
    queries = list(data.getlist("searchbar"))
    global comb 
    comb = data.getlist("select")
    global restrictDomain
    restrictDomain = data.getlist("domain")

    global ranking
    ranking = data.get("ranking")
    print(data.get("ranking"))
 
    urls, content = whooshSearch()
    
    sudoTitles = []
    
    urlparse("scheme://netloc/path;parameters?query#fragment")
    
    for url in urls:#generates the titles from the urls, was dumb and forgot to save titles while crawling
        urlParsed = urlparse(url)
        title = urlParsed.path.replace("/", " ") + " " + urlParsed.netloc
        sudoTitles.append(title)
 
    return render_template('results.html', results = zip(urls, content, sudoTitles))#sends it to be placed on page


#everything below can be used as an api sort of thing, otherwise its never used
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
def combine(num, whichOne):
    try:
        comb[int(num)] = whichOne
    except:
        comb.insert(int(num), whichOne)
    return comb

@app.route('/getStuff', methods = ['POST', 'GET'])
def getStuff():
    if request.method == "POST":
        print("Hello")
    else:
        print("Hi")

if __name__ == '__main__':
    app.debug=True
    app.run()