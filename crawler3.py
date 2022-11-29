from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib.robotparser
import requests
import time
import json
import socket

def crawler3(profile):
    queue = profile["queue"]
    urlsVisted = profile["urlsVisted"]
    bannedDomains = profile["bannedDomains"]
    connections = profile["connections"]
    saveLocation = profile["saveLocation"]
    defaultDelay = profile["defaultDelay"]

    keyWords = profile["keyWords"]

    pagesMax = profile["pagesMax"]
    pagesRead = profile["pagesRead"]

    urlparse("scheme://netloc/path;parameters?query#fragment")
    socket.setdefaulttimeout(None)

    urlCurrent = ''
    urlParsed = ''

    domainCurrent = ''
    domainPrevious = ''

    crawlDelay = defaultDelay

    canRead = True

    while pagesRead < pagesMax:
        print("Queue size:", len(queue))
        print("Total pages read so far:", pagesRead)

        if queue:
            urlCurrent = queue.pop(0)
            print("Pulling from the queue:", urlCurrent)
        else:
            print("Queue emptied before reaching the limit")
            break

        urlParsed = urlparse(urlCurrent)
        domainPrevious = domainCurrent
        domainCurrent = urlParsed.scheme + "://" + urlParsed.netloc

        if(domainCurrent != domainPrevious) and (domainCurrent not in bannedDomains):
            print("Entered a different domain")

            rp = urllib.robotparser.RobotFileParser()

            try:
                f = urllib.request.urlopen(domainCurrent + "/robots.txt", timeout=10)
                raw = f.read()
                rp.parse(raw.decode("utf-8").splitlines())
            except:
                bannedDomains.append(domainCurrent)
                print("Cannot read the robots.txt file, banning domain")
            else:
                crawlDelay = rp.crawl_delay("*")
                if crawlDelay is None:
                    crawlDelay = defaultDelay

                print("Read the robots.txt and set crawl delay")

        if (urlCurrent not in urlsVisted) and (domainCurrent not in bannedDomains):
            if(rp.can_fetch("*", urlCurrent)):
                time.sleep(crawlDelay)

                try:
                    result = requests.get(urlCurrent)
                    canRead = True
                except:
                    print("Skipping URL: Had issue getting webpage")
                    canRead = False

                if canRead:
                    rawPage = result.text
                    bs = BeautifulSoup(rawPage, 'lxml')
                    content = bs.get_text("\n", strip=True)

                    searchable = content.lower()

                    for word in keyWords:
                        if word in searchable:

                            fileName = urlCurrent.replace('/', '').replace(':', '').replace('\n', '').replace('?', '').replace('=', '')#creates the url file name
                            fileName = fileName[:128]

                            endResult = {

                                "url": urlCurrent,

                                "contents": content

                            }

                            with open(saveLocation + f"/pages/{fileName}.json", "w") as file:
                                json.dump(endResult, file, indent=4)

                            urlsVisted.append(urlCurrent)

                            pagesRead += 1

                            links = []
                            for link in bs('a'):#grabs all the links from the page
                                tmp = link.get("href")
                                if tmp is not None:
                                    if ('http' in tmp) and ('.pdf' not in tmp) and ('.mp4' not in tmp) and ('.mp3' not in tmp)and ('.jpg' not in tmp) and ('.png' not in tmp):#searches for only the links that have the http substring in it
                                        try:                                        
                                            tmpParse = urlparse(tmp)
                                        except:
                                            print("Cannot parse potential link")
                                        else:
                                            if tmpParse.path == '':
                                                tmp += '/'
                                            if tmp not in links:
                                                links.append(tmp)

                            
                            connections[urlCurrent] = links

                            print("Found", len(links), "unique connections")

                            linksAdded = 0

                            for link in links:#adds the links to the queue if we havent already visted them or are already in the queue
                                if (link not in urlsVisted) and (link not in queue):
                                    queue.append(link)

                                    linksAdded += 1

                            print("Added", linksAdded, "to the queue")


                            print("Page has finished reading")


                            if(pagesRead % profile["saveInterval"] == 0):
                                print("Saving...")
                                profile["queue"] = queue
                                profile["urlsVisted"] = urlsVisted
                                profile["bannedDomains"] = bannedDomains
                                profile["connections"] = connections
                                profile["saveLocation"] = saveLocation
                                profile["defaultDelay"] = defaultDelay

                                profile["pagesMax"] = pagesMax
                                profile["pagesRead"] = pagesRead


                                with open(saveLocation + "/profile.json", "w") as file:
                                    json.dump(profile, file, indent=4)


                            break

            else:
                print("Disallowed from reading page")
        
        else:
            print("Page could not be read")

        print("Finished, moving to next in queue")
        urlsVisted.append(urlCurrent)

        print("\n\n")

    

if __name__ == '__main__':

    profile = {

        "queue": ["https://en.wikipedia.org/wiki/Portal:Water", "https://en.wikipedia.org/wiki/Category:Drinking_water", " https://www.cdc.gov/healthywater/drinking/index.html", "https://www.who.int/news-room/fact-sheets/detail/drinking-water", "https://www.healthdirect.gov.au/drinking-water-and-your-health", "https://www.epa.gov/ground-water-and-drinking-water/basic-information-about-your-drinking-water"],

        "urlsVisted": [],
        
        "bannedDomains": [],

        "connections": {},

        "saveLocation": "/run/media/pwanner/Ghost Drive/",

        "defaultDelay": 0,

        "pagesRead": 0,

        "pagesMax": 50000,

        "keyWords": ["water", "drinking", "drink", "h2o", "glacier", "ground", "spring", "ice", "river", "creek", "ocean", "sea", "snow"],

        "saveInterval": 50

    }

    with open("/run/media/pwanner/Ghost Drive/profile.json", "r") as f:
        profile = json.load(f)

    crawler3(profile)
