import os
import time
import sys
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *

lot_nr = input("Give the lot number:")
database = DatabaseInterfaceBrowse()
hybrid_list = database.list_hybrids(greater=6100)
for hybrid in hybrid_list:
    production_data_int = database.get_production_results(hybrid)
    production_data = []
    for item in production_data_int:
        if item is None or item == "None":
            production_data.append(0)
        else:
            production_data.append(item)
    if production_data[29] == 'red':
        print "Hybrid: %s, Dead Channels: %s, Color: %s" % (hybrid, production_data[20], production_data[29])