import os
import time
import sys
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *

database = DatabaseInterfaceBrowse()
hybrid_list = database.list_hybrids_modified_by_state('red', greater=6100, smaller=50000)
i = 0
for hybrid in hybrid_list:
    production_data_int = database.get_production_results(hybrid)
    production_data = []
    for item in production_data_int:
        if item is None or item == "None":
            production_data.append(0)
        else:
            production_data.append(item)
    print_text = "Hybrid: %s" % hybrid
    if production_data[1] is None or production_data[1] == "None":
        print_text += ", short circuit"
    if int(production_data[40]) == 1:
        print_text += ", short circuit"
    if int(production_data[41]) == 1:
        print_text += ", sync problem"
    i += 1
    print print_text
print i
