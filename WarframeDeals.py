import requests
import json
from tkinter import *
from tkinter import scrolledtext
from tkinter.ttk import *


class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('Warframe Deals')
        self.master.geometry('400x250')
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.cbVendors = Combobox(self, values=['Cephalon Simaris', 'Red Veil'], state='readonly')
        self.cbVendors.current(0)
        self.cbVendors.grid(row=0, column=0)
        
        self.input = Entry(self)
        self.input.grid(row=1, column=0)

        self.btnVendors = Button(self, text='Submit', command=self.getVendorItems)
        self.btnVendors.grid(row=2,column=0)

    def getVendorItems(self):
        if (self.cbVendors.get() == 'Cephalon Simaris'):
            modList = getSimarisItems()
        elif (self.cbVendors.get() == 'Red Veil'):
            modList = getRedVeilItems()

        output = ''

        for i in modList:
            output += ('{}: {}\n'.format(i[0], i[1]))


        self.outputBox = scrolledtext.ScrolledText(self, width=40, height=10)
        self.outputBox.insert(INSERT, output)
        self.outputBox.config(state='disabled')
        self.outputBox.grid(row = 3, column=0)
        


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
    setName = '{}_prime_set'.format(setName)
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

def getVendorPrices(items):
    final_items = {}

    for i in range(len(items)):
        requestString = "http://api.warframe.market/v1/items/{}/orders".format(items[i])
        orders = requests.get(requestString).json()
        orders = orders["payload"]["orders"]
        orders = [x for x in orders if
        x["user"]["status"] == "ingame"]
        
        orders = sorted(orders, key=lambda x: x["platinum"])
        cheapestPriceOnline = orders[0]["platinum"]

        final_items[items[i]] = cheapestPriceOnline

    final_items = sorted(final_items.items(), key=lambda x: x[1], reverse=True)

    return final_items

def getSimarisItems():
    items = ['looter',
            'detect_vulnerability',
            'reawaken',
            'negate',
            'ambush',
            'energy_generator',
            'energy_conversion',
            'health_conversion',
            'astral_autopsy',
            'companion_weapon_riven_mod_(veiled)']
    
    

    return getVendorPrices(items)

def getRedVeilItems():
    items = ['accumulating_whipclaw',
            'anchored_glide',
            'ballistic_bullseye',
            'beguiling_lantern',
            'blood_forge',
            'capacitance',
            # this mod is not yet on warframe.market 'catapult',
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
            # this mod is not yet on warframe.market 'spellbound_harvest',
            'staggering_shield',
            'stockpiled_blight',
            'target_fixation',
            'tectonic_fracture',
            'titanic_rumbler',
            'toxic_blight',
            'transistor_shield',
            # this mod is not yet on warframe.market 'tribunal',
            'venari_bodyguard',
            'venom_dose',
            'warding_thurible'
            ]
    
    return getVendorPrices(items)

root = Tk()
app = Application(master = root)
app.mainloop()