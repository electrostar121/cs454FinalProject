from sklearn.feature_extraction import DictVectorizer
import pandas as pd
import numpy as np
import json
import gc

#version 1 of page rank, used up too much ram had to redo

def CDtoCM(connectionDict, urlList):
    restructured = []
    keyValues = []

    for key in connectionDict:
        data_dict = {}
        for url in urlList:
            if url in connectionDict[key]:
                data_dict[url] = 1
            else:
                data_dict[url] = 0
        
        gc.collect()
                        
        restructured.append(data_dict)
        keyValues.append(key)
        
    dv = DictVectorizer()
    df = pd.DataFrame(dv.fit_transform(restructured).todense(), columns=dv.feature_names_, index=dict(enumerate(keyValues))).rename(index=dict(enumerate(keyValues)))
    
    rowTotals = df.sum(axis = 1)
    
    for key in keyValues:
        df = df.apply(lambda x: (x / rowTotals[key]) if (x.name == key and rowTotals[key] != 0.0) else x, axis = 1)
    
    return df, keyValues

def pagerank(matrix, numOfUrls, num_iterations = 100, d = 0.85):
    v = np.ones(numOfUrls) / numOfUrls
    print(v)
    M_hat = (d * matrix + (1 - d) / numOfUrls)
    for i in range(num_iterations):
        v = M_hat @ v
    return v

def main():
    with open("optimized.json", 'r') as file:
        data = json.load(file)

    df, keyValues = CDtoCM(data["connections"], data["urlsVisted"])
    
    result = pagerank(df.to_numpy().T, len(data["urlsVisted"]))
    result = result / sum(result)
    
    endResult = {}
    
    for index, key in enumerate(keyValues):
        endResult[key] = result[index]
        
    with open("prScores.json", "w") as f:
        json.dump(endResult, f)
    
    print(endResult)

if __name__ == "__main__":
    main()