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
        self.cbVendors = Combobox(self, values=['Prime Set', 'Cephalon Simaris', 'Red Veil'], state='readonly')
        self.cbVendors.current(0)
        self.cbVendors.grid(row=0, column=0)
        self.cbVendors.bind('<<ComboboxSelected>>', self.onComboChange)

        self.input = Entry(self)
        self.input.grid(row=1, column=0)

        self.btnVendors = Button(self, text='Submit', command=self.getVendorPrices)
        self.btnVendors.grid(row=2,column=0)

    def getVendorPrices(self):
        self.outputBox = scrolledtext.ScrolledText(self, width=40, height=10)

        choice = self.cbVendors.get()
        modList = ''
        output = ''
        if (choice == 'Prime Set'):
            output = getPrices(self.input.get())
        else:
            modList = getVendorItems(choice)

        if (modList != ''):
            output = ''
            for i in modList:
                output += ('{}: {}\n'.format(i[0], i[1]))
            self.outputBox.insert(INSERT, output)
        else:
            for i in output:
                self.outputBox.insert(INSERT, i + '\n')


        self.outputBox.config(state='disabled')
        self.outputBox.grid(row=3, column=0)
        
    def onComboChange(self, eventObject):
        if (self.cbVendors.get() != 'Prime Set'):
            self.input.grid_forget()
        else:
            self.input.grid(row=1, column=0)
        


def getOrders(itemName):
    requestString = "http://api.warframe.market/v1/items/{}/orders".format(itemName)
    orders = requests.get(requestString, headers={"platform":"pc", "language":"en"}).json()
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
    setName = '{}_prime_set'.format(setName.lower())
    piecemealTotal = 0
    piecemealOnlineTotal = 0
    titlePieces = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:

        piecesPrices = executor.submit(getPiecemealPrice, setName)
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
            ]}

    prices = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
        prices.update(executor.map(getItem, items[vendor]))

    prices = sorted(prices.items(), key=lambda x: x[1], reverse=True)

    return prices

def getItem(item):
    requestString = "http://api.warframe.market/v1/items/{}/orders".format(item)
    orders = requests.get(requestString).json()
    orders = orders["payload"]["orders"]
    orders = [x for x in orders if
    x["user"]["status"] == "ingame"]
    
    orders = sorted(orders, key=lambda x: x["platinum"])
    cheapestPriceOnline = orders[0]["platinum"]

    return (item, cheapestPriceOnline)

root = Tk()
app = Application(master = root)
app.mainloop()