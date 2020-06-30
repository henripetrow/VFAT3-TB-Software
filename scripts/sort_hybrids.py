import os
import time
import sys
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *

database = DatabaseInterfaceBrowse()
hybrid_list = database.list_hybrids_modified_by_state('red', greater=6100, smaller=50000)
i = 0
cal_dac_list = [10371, 10393, 9985, 9953, 9827, 8636, 7463, 7460, 7439, 7334, 7330, 7111, 7042, 6820, 6810, 6641, 6632,
                6631, 6560, 6448, 6105] #Vai ADC0 ongelma?
others_list = [7925, 7843, 7731, 7206, 6900, 6555, 6445, 6130] #weird. noise?
old_syc_sc = [7393]
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
    if hybrid in cal_dac_list:
        print_text += ", CAL_DAC problem"
    if hybrid in others_list:
        print_text += ", Other problem"
    i += 1
    print print_text
print i

for hybrid in cal_dac_list_list:
    production_data_int = database.get_production_results(hybrid)
    production_data = []
    for item in production_data_int:
        if item is None or item == "None":
            production_data.append(0)
        else:
            production_data.append(item)
    print_text = "Hybrid: %s, %s, %s, %s, %s" % (hybrid, production_data[5], production_data[6], production_data[7], production_data[8])
