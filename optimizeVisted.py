import json

def main():#this just cleans up the visted links in the profile json
    with open("profile.json", 'r') as file:
        data = json.load(file)
        
    newVisted = []
        
    for key in data["connections"]:
        newVisted.append(key)
        
    with open("optimized.json", 'w') as file:
        json.dump({"connections": data["connections"], "urlsVisted": newVisted}, file)

if __name__ == "__main__":
    main()