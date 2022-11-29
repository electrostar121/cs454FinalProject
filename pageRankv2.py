from sklearn.feature_extraction import DictVectorizer
import pandas as pd
import numpy as np
import json

#version 2, does a list of list and then converts into a numpy array to do the calculations on, then saves it to a json file
#still used to much ram, but had enough to get it all calculated

def CDtoCM(connectionDict, urlList):
    restructured = []
    keyValues = []
    
    #i = 0

    for key in connectionDict:
        data_dict = []
        for url in urlList:
            if url in connectionDict[key]:
                data_dict.append(1.0)
            else:
                data_dict.append(0.0)
        
        #tmp = sum(data_dict)
        
        restructured.append(data_dict)
        
        #if(tmp == 0.0):
        #    restructured.append(data_dict)
        #else:
        #    for index, data in enumerate(data_dict):
        #        data_dict[index] = data / tmp
        #    restructured.append(data_dict)
        
    #print(len(restructured), len(restructured[0]))
    
    return restructured, keyValues

def pagerank(matrix, numOfUrls, num_iterations = 100, d = 0.85):
    v = np.ones(numOfUrls) / numOfUrls
    M_hat = (d * matrix + (1 - d) / numOfUrls)
    for i in range(num_iterations):
        v = M_hat @ v
        print(i)
    return v

def main():
    with open("optimized.json", 'r') as file:
        data = json.load(file)

    df, keyValues = CDtoCM(data["connections"], data["urlsVisted"])
    
    #del(keyValues)
    
    #with open("save.json", "w") as file:
    #    json.dump({"data": df, "keyValues": keyValues}, file)
        
    #with open("save.json", "r") as file:
    #    loaded = json.load(file)
        
    #df = loaded["data"]
    #keyValues = loaded["keyValues"]
    #print(keyValues)
    #del(loaded)
    
    #print(len(data["urlsVisted"]))
    #print(len(df))
    
    #for key in data["connections"]:
    #    keyValues.append(key)
    
    #endResult = {}
    
    result = pagerank(np.array(df).T, len(df))
    result = result / sum(result)
    
    endResult = list(result)
    
    #for index, key in enumerate(keyValues):
    #    endResult[key] = result[index]
        
    with open("prScores", "w") as f:
        json.dump({"endResult": endResult}, f)
    
    #print(endResult)

if __name__ == "__main__":
    main()