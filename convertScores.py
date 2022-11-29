import json

def main():
    with open("optimized.json", 'r') as file:
        data = json.load(file)

    with open("prScores", 'r') as file:
        scores = json.load(file)

    keyValues = []

    for key in data["connections"]:
        keyValues.append(key)

    endResult = {}

    for index, key in enumerate(keyValues):
        endResult[key] = scores["endResult"][index]

    with open("prScores.json", 'w') as file:
        json.dump(endResult, file)

if __name__ == "__main__":
    main()