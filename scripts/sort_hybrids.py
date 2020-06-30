import os
import time
import sys
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *

database = DatabaseInterfaceBrowse()
hybrid_list = database.list_hybrids_modified_by_state('red', greater=6100, smaller=50000)
i = 0
cal_dac_list = [8636, 7334, 6820]
buffer_offset_list = [9985, 9953, 9827, 7463]
adc_list = [6105, 6560, 6631, 6632, 6810, 7460, 10371, 10393, 7439, 7042, 6641, 6448, 7330, 7111]

noise_list = [7925, 7843, 7731, 7206, 6900, 6555, 6445, 6130] #weird. noise?

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
    if hybrid in buffer_offset_list:
        print_text += ", Buffer offset problem"
    if hybrid in adc_list:
        print_text += ", ADC problem"
    if hybrid in noise_list:
        print_text += ", Noise problem?"
    i += 1
    print print_text
print i

for hybrid in cal_dac_list:
    production_data_int = database.get_production_results(hybrid)
    production_data = []
    for item in production_data_int:
        if item is None or item == "None":
            production_data.append(0)
        else:
            production_data.append(item)
    print_text = "Hybrid: %s, %s, %s, %s, %s, %s, %s" % (hybrid, production_data[5], production_data[6],
                                                         production_data[7], production_data[8], production_data[9],
                                                         production_data[10])
    print print_text
