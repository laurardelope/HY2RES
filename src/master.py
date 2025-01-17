from src.data_store import *
from src.historical_data import *
from src.importer import *
from src.inverter import *
from src.PLC import *
from src.battery_diezmado import *
from src.electrolyzer import *
from src.h2_storage_diezmado import *
from src.fuel_cell import *

import datetime
import json

class Master:
    def __init__(self):

        jsonfile=open('./config/config.json')
        json_str=jsonfile.read()
        self.param=json.loads(json_str)
               
        self.dataStore=DataStore()
        self.historicalData=HistoricalData()
        self.importer=Importer(self.param)
        self.inverter=Inverter(self.param)
        self.PLC=Plc(self.param)
        self.battery=BatteryD(self.param)
        self.electrolyzer=Electrolyzer(self.param)
        self.h2Storage=H2StorageD(self.param)
        self.fuelCell=FuelCell(self.param)
        
        self.historicalData.reset(self.dataStore)

        
    def run(self):
        i=0
        self.dataStore.resetReal() #reset(write) all variables
        self.dataStore.resetEst() #reset(write) all variables

        while (i<self.param["n_iter"]):

            index=self.importer.run(self.dataStore)
           
            print(index)
            self.inverter.run(self.dataStore)
            self.battery.run(self.dataStore)
            self.PLC.run(self.dataStore)
            self.electrolyzer.run(self.dataStore)
            self.h2Storage.run(self.dataStore)
            self.fuelCell.run(self.dataStore)

            self.historicalData.write(self.dataStore)


            i=i+1

        self.historicalData.printCsv(self.param)
        self.historicalData.validate(self.param)
