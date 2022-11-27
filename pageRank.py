from sklearn.feature._extraction import DictVectorizer
import pandas as pd

test = {

    "website1": ["website2", "website3", "website1"],
    "website2": ["website2", "website3"],
    "website3": []

}

dv = DictVectorizer()


print(pd.DataFrame(dv.fit_transform(test).todense(), columns=dv.feature_names_))