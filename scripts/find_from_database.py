import os
import time
import sys
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *


red_list = []
yellow_list = []
green_list = []

database = DatabaseInterfaceBrowse()
hybrid_list = database.list_hybrids_by_lot(1)
for hybrid in hybrid_list:
    production_data_int = database.get_production_results(hybrid)
    production_data = []
    for item in production_data_int:
        if item is None or item == "None":
            production_data.append("")
        else:
            production_data.append(item)
    if production_data[29] == 'red':
        red_list.append(hybrid[6:])
    elif production_data[29] == 'yellow':
        yellow_list.append(hybrid[6:])
    elif production_data[29] == 'green':
        yellow_list.append(hybrid[6:])
    else:
        print "Problematic hybrid: %s" % hybrid[6:]