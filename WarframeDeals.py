import requests
import json

def getOrders(itemName):
    requestString = "http://api.warframe.market/v1/items/{}/orders".format(itemName)
    orders = requests.get(requestString, headers={"platform":"pc", "language":"en"}).json()
    orders = orders["payload"]["orders"]
    return orders

def basicSearch(itemName):
    orders = getOrders(itemName)

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

def filterOrders(orders):
    orders = [x for x in orders if
        x["order_type"] == "sell" and
        x["visible"] == True and
        x["region"] == "en" and
        x["platform"] == "pc"]

    return orders

def getSetPieces(setName):
    output = []

    requestString = "http://api.warframe.market/v1/items/{}".format(setName)
    setPieces = requests.get(requestString, headers={"platform":"pc", "language":"en"}).json()
    setPieces = setPieces["payload"]["item"]["items_in_set"]

    setPieces = [x for x in setPieces if not x["url_name"].endswith("_set")]
    for i in range(len(setPieces)):
            output.append(setPieces[i]["url_name"])
    
    return output

def getSetPrice(setName):
    
    output = []

    orders = getOrders(setName)

    orders = filterOrders(orders)
    
    orders = sorted(orders, key=lambda x: x["platinum"])

    cheapestPrice = orders[0]["platinum"]

    orders = [x for x in orders if
        x["user"]["status"] == "ingame"]

    orders = sorted(orders, key=lambda x: x["platinum"])

    cheapestPriceOnline = orders[0]["platinum"]

    output.append(cheapestPrice)
    output.append(cheapestPriceOnline)

    return output

def getPiecemealPrice(setName):
    setPieces = getSetPieces(setName)
    output = {}

    for i in range(len(setPieces)):
        orders = getOrders(setPieces[i])

        orders = filterOrders(orders)
        orders = sorted(orders, key=lambda x: x["platinum"])
        
        output[setPieces[i]] = orders[0]["platinum"]

        orders = [x for x in orders if
            x["user"]["status"] == "ingame"]
        orders = sorted(orders, key=lambda x: x["platinum"])

        output["{}_online".format(setPieces[i])] = orders[0]["platinum"]
    
    return output

def getPrices(setName):
    piecesPrices = getPiecemealPrice(setName)
    pieces = getSetPieces(setName)
    titlePieces = []
    wholeSet = getSetPrice(setName)
    setName = setName.replace('_', ' ').title()

    piecemealTotal = 0
    piecemealOnlineTotal = 0

    for i in range(len(pieces)):
        piecemealTotal += piecesPrices[pieces[i]]
        piecemealOnlineTotal += piecesPrices[pieces[i] + "_online"]
        titlePieces.append(pieces[i].replace('_',' ').title())

    print()
    print(setName)
    print("Cheapest Set: " + str(int(wholeSet[0])))
    print("Cheapest Online Set: " + str(int(wholeSet[1])))
    print("Cheapest Parts:")
    for i in range(len(pieces)):
        print("\t{}: {}".format(titlePieces[i], int(piecesPrices[pieces[i]])))
    print("\tTotal: " + str(int(piecemealTotal)))
    print("Cheapest Online Parts:")
    for i in range(len(pieces)):
        print("\t{}: {}".format(titlePieces[i], int(piecesPrices[pieces[i] + "_online"])))
    print("\tTotal: " + str(int(piecemealOnlineTotal)))