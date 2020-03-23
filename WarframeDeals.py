import requests
import json




def basicSearch(itemName):
    requestString = "http://api.warframe.market/v1/items/{}/orders".format(itemName)
    response = requests.get(requestString, headers={"platform":"pc", "language":"en"})
    response = response.json()

    orders = response["payload"]["orders"]

    orders = [x for x in orders if
        x["order_type"] == "sell" and
        x["visible"] == True]

    orders = sorted(orders, key=lambda x: x["platinum"])

    orders = orders[:5]

    for i in range(len(orders)):
        orders[i] = {k: v for (k, v) in orders[i].items() if
            k == "platinum" or
            k == "user"}
        
        orders[i]["status"] = orders[i]["user"]["status"]
        orders[i]["user"] = orders[i]["user"]["ingame_name"]


    text = itemName.replace('_', ' ').title()
    print(text)

    text = json.dumps(orders, indent=4)
    print(text)

def getSetPieces(setName):
    output = []

    requestString = "http://api.warframe.market/v1/items/{}".format(setName)
    setPieces = requests.get(requestString, headers={"platform":"pc", "language":"en"})
    setPieces = setPieces.json()

    setPieces = setPieces["payload"]["item"]["items_in_set"]
    setPieces = [x for x in setPieces if not x["url_name"].endswith("_set")]
    for i in range(len(setPieces)):
            #setPieces[i] = {k: v for (k, v) in setPieces[i].items() if k == "url_name"}
            output.append(setPieces[i]["url_name"])
    
    return output

def getSetPrice(setName):
    requestString = "http://api.warframe.market/v1/items/{}/orders".format(setName)
    orders = requests.get(requestString, headers={"platform":"pc", "language":"en"})
    orders = orders.json()
    orders = orders["payload"]["orders"]

    outputSetName = setName.replace('_', ' ').title()
    print(outputSetName)

getSetPieces("mesa_prime_set")
getSetPieces("rhino_prime_set")

#uncomment for set prices
"""print()
basicSearch("mesa_prime_set")"""
