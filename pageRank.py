from sklearn.feature_extraction import DictVectorizer
import pandas as pd

test = {

    "website3": ["website2", "website3", "website1"],
    "website1": ["website2", "website3"],
    "website2": []

}

listOfUrls = ["website1", "website2", "website3"]

restructured = []
keyValues = []

flag = True
i = 0

for key in test:
    data_dict = {}
    for url in listOfUrls:
        if url in test[key]:
            data_dict[url] = 1
        else:
            data_dict[url] = 0
            
    restructured.append(data_dict)
    keyValues.append(key)
    
dv = DictVectorizer()
df = pd.DataFrame(dv.fit_transform(restructured).todense(), columns=dv.feature_names_, index=dict(enumerate(keyValues))).rename(index=dict(enumerate(keyValues)))
    
#print(df)

#print(df.loc["website3", :])

for item in keyValues:
    for item2 in listOfUrls:
        print(df.loc[item, item2])
        