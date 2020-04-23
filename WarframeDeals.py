import requests
import json
import concurrent.futures
from tkinter import *
from tkinter import scrolledtext
from tkinter.ttk import *


class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('Warframe Deals')
        self.master.geometry('400x250')
        self.master.resizable(0,0)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.cbSelection = Combobox(self, values=['Prime Set', 'Profile', 'Cephalon Simaris', 'Red Veil'], state='readonly')
        self.cbSelection.current(0)
        self.cbSelection.grid(row=0, column=0)
        self.cbSelection.bind('<<ComboboxSelected>>', self.onComboChange)

        self.txtInput = Entry(self)
        self.txtInput.grid(row=1, column=0)

        self.btnVendors = Button(self, text='Submit', command=self.submitSearch)
        self.btnVendors.grid(row=2,column=0)

    def submitSearch(self):
        self.outputBox = scrolledtext.ScrolledText(self, width=40, height=10)

        choice = self.cbSelection.get()
        itemList = ''
        output = ''
        if (choice == 'Prime Set'):
            output = getPrices(self.txtInput.get())
            for i in output:
                self.outputBox.insert(END, i + '\n')
        elif (choice == 'Profile'):
            output = getProfilePrices(self.txtInput.get())
            self.outputUndercuts(output)
        else:
            itemList = getVendorItems(choice)
            output = ''

            for i in itemList:
                output += ('{}: {}\n'.format(i[0], i[1]))
            self.outputBox.insert(END, output)

        self.outputBox.config(state='disabled')
        self.outputBox.grid(row=3, column=0)
        
    def onComboChange(self, eventObject):
        if (self.cbSelection.get() != 'Prime Set' and self.cbSelection.get() != 'Profile'):
            self.txtInput.grid_forget()
        else:
            self.txtInput.grid(row=1, column=0)

    def outputUndercuts(self, items):
        for i in items:
            line = ''
            line += i.name + ':\n'
            if (i.modRank != -1):
                line += '\tRank: {}\n'.format(i.modRank)
            line += '\tYour Price: {}\n'.format(i.yourPrice)
            line += '\tLowest Online Price: {}\n'.format(i.cheapestOnlinePrice)
            self.outputBox.insert(END, line)
        
class Item:
    def __init__(self, name = '', cheapestPrice = -1, cheapestOnlinePrice = -1, yourPrice = -1, modRank = -1):
        super().__init__()
        self.name = name
        self.cheapestPrice = cheapestPrice
        self.cheapestOnlinePrice = cheapestOnlinePrice
        self.yourPrice = yourPrice
        self.modRank = modRank

def getOrders(itemName):
    requestString = "http://api.warframe.market/v1/items/{}/orders".format(itemName)
    orders = requests.get(requestString).json()
    orders = orders["payload"]["orders"]
    return orders

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
    setPieces = requests.get(requestString).json()
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

def getPiecemealPrices(setName):
    setPieces = getSetPieces(setName)
    output = {}

    for i in range(len(setPieces)):
        orders = getOrders(setPieces[i])

        orders = filterOrders(orders)
        orders = sorted(orders, key=lambda x: x["platinum"])
        
        output[setPieces[i]] = orders[0]["platinum"]

        for j in orders:
                if (j["user"]["status"] == "ingame"):
                    output["{}_online".format(setPieces[i])] = j["platinum"]
                    break

        
    
    return output

def getPrices(setName):
    setName = '{}_prime_set'.format(setName.lower())
    piecemealTotal = 0
    piecemealOnlineTotal = 0
    titlePieces = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:

        piecesPrices = executor.submit(getPiecemealPrices, setName)
        pieces = executor.submit(getSetPieces, setName)
        wholeSet = executor.submit(getSetPrice, setName)
        
        piecesPrices = piecesPrices.result()
        pieces = pieces.result()
        wholeSet = wholeSet.result()

    for i in range(len(pieces)):
        piecemealTotal += piecesPrices[pieces[i]]
        piecemealOnlineTotal += piecesPrices[pieces[i] + "_online"]
        titlePieces.append(pieces[i].replace('_',' ').title())

    setName = setName.replace('_', ' ').title()

    output = []

    
    output.append(setName)
    output.append("Cheapest Set: " + str(int(wholeSet[0])))
    output.append("Cheapest Online Set: " + str(int(wholeSet[1])))
    output.append("Cheapest Parts:")
    for i in range(len(pieces)):
        output.append("\t{}: {}".format(titlePieces[i], int(piecesPrices[pieces[i]])))
    output.append("\tTotal: " + str(int(piecemealTotal)))
    output.append("Cheapest Online Parts:")
    for i in range(len(pieces)):
        output.append("\t{}: {}".format(titlePieces[i], int(piecesPrices[pieces[i] + "_online"])))
    output.append("\tTotal: " + str(int(piecemealOnlineTotal)))

    return output

def getVendorItems(vendor):
    items = {'Cephalon Simaris': ['looter',
            'detect_vulnerability',
            'reawaken',
            'negate',
            'ambush',
            'energy_generator',
            'energy_conversion',
            'health_conversion',
            'astral_autopsy',
            'companion_weapon_riven_mod_(veiled)'],
            
            'Red Veil': ['accumulating_whipclaw',
            'anchored_glide',
            'ballistic_bullseye',
            'beguiling_lantern',
            'blood_forge',
            'capacitance',
            'catapult',
            'contagion_cloud',
            'creeping_terrify',
            'despoil',
            'dread_ward',
            'eroding_blight',
            'exothermic',
            'fatal_teleport',
            'fireball_frenzy',
            'funnel_clouds',
            'gleaming_blight',
            'healing_flame',
            'hushed_invisibility',
            'immolated_radiance',
            'ironclad_flight',
            'irradiating_disarm',
            'jet_stream',
            'lasting_covenant',
            'mesa’s_waltz',
            'muzzle_flash',
            'ore_gaze',
            'path_of_statues',
            'pilfering_strangledome',
            'razorwing_blitz',
            'regenerative_molt',
            'rising_storm',
            'safeguard_switch',
            'savior_decoy',
            'seeking_shuriken',
            'shield_of_shadows',
            'shock_trooper',
            'shocking_speed',
            'smoke_shadow',
            'soul_survivor',
            'spellbound_harvest',
            'staggering_shield',
            'stockpiled_blight',
            'target_fixation',
            'tectonic_fracture',
            'titanic_rumbler',
            'toxic_blight',
            'transistor_shield',
            'tribunal',
            'venari_bodyguard',
            'venom_dose',
            'warding_thurible'
            ]}

    prices = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
        prices.update(executor.map(getItem, items[vendor]))

    prices = sorted(prices.items(), key=lambda x: x[1], reverse=True)

    return prices

def getItem(item):
    orders = getOrders(item)
    orders = filterOrders(orders)
    orders = sorted(orders, key=lambda x: x["platinum"])
    
    cheapestPriceOnline = -1

    for i in orders:
        if (i["user"]["status"] == "ingame"):
            cheapestPriceOnline = orders[0]["platinum"] = i["platinum"]
            break
    
    if (cheapestPriceOnline == -1):
        return (item, -1)

    return (item, cheapestPriceOnline)

def getProfilePrices(username):
    requestString = "https://api.warframe.market/v1/profile/{}/orders".format(username)
    orders = requests.get(requestString).json()
    orders = orders['payload']['sell_orders']
    items = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
        for i in executor.map(checkUndercut, orders):
            items.append(i)
    
    return items

def checkUndercut(saleOrder):
    item = Item()
    item.name = saleOrder['item']['en']['item_name']
    item.yourPrice = saleOrder['platinum']

    itemOrders = getOrders(saleOrder['item']['url_name'])
    itemOrders = filterOrders(itemOrders)
    itemOrders = sorted(itemOrders, key=lambda x: x["platinum"])
    if ('mod_rank' in saleOrder.keys()):
        
        item.modRank = saleOrder['mod_rank']
        

        filteredOrders = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            args = ((order, item.modRank) for order in itemOrders)
            for i in executor.map(lambda a: rankFilter(*a), args):
                if (i != None):
                    filteredOrders.append(i)

        item.cheapestPrice = filteredOrders[0]['platinum']
        for i in filteredOrders:
            if (i['user']['status'] == 'ingame'):
                item.cheapestOnlinePrice = i['platinum']
                break
        
    else:
        item.cheapestPrice = itemOrders[0]['platinum']
        
        for i in itemOrders:
            if (i['user']['status'] == 'ingame'):
                item.cheapestOnlinePrice = i['platinum']
                break

    return item

def rankFilter(order, modRank):
    if ('mod_rank' in order.keys()):
        if (order['mod_rank'] == modRank):
            return order


root = Tk()
app = Application(master = root)
app.mainloop()