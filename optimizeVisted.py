import json

def main():
    with open("profile.json", 'r') as file:
        data = json.load(file)
        
    newVisted = []
        
    for key in data["connections"]:
        newVisted.append(key)
        
    with open("optimized.json", 'w') as file:
        json.dump({"connections": data["connections"], "urlsVisted": newVisted}, file)

if __name__ == "__main__":
    main()