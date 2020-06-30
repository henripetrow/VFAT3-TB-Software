import os
import time
import sys
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *

database = DatabaseInterfaceBrowse()
hybrid_list = database.list_hybrids_modified_by_state('red', greater=6100, smaller=50000)
i = 0
others_list = [10371, 10393, 9985, 9953, 9827, 8636, 7925, 7731, 7463]
# 7925 7731weird.
for hybrid in hybrid_list:
    production_data_int = database.get_production_results(hybrid)
    production_data = []
    for item in production_data_int:
        if item is None or item == "None":
            production_data.append(0)
        else:
            production_data.append(item)
    print_text = "Hybrid: %s" % hybrid
    if int(production_data[1]) == 0:
        print_text += ", short circuit1"
    if int(production_data[40]) == 1:
        print_text += ", short circuit"
    if int(production_data[41]) == 1:
        print_text += ", sync problem"
    if int(production_data[36]) > 0:
        print_text += ", S-bit problem"
    if hybrid in others_list:
        print_text += ", Other problem"
    i += 1
    print print_text
print i
