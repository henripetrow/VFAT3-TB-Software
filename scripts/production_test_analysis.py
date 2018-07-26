############################################
# Created by Henri Petrow 2018
# Lappeenranta University of Technology
###########################################

from DatabaseInterfaceBrowse import *
import matplotlib.pyplot as plt

database = DatabaseInterfaceBrowse(database_name="VFAT3_Production")
hybrid_list = database.list_hybrids()
green_hybrids = []
yellow_hybrids = []
red_hybrids = []
test_hybrids = ['Hybrid55555']
print "List of tested hybrids:"
for i, hybrid in enumerate(hybrid_list):
    if hybrid not in test_hybrids:
        production_data = database.get_production_results(hybrid)
        hybrid = hybrid[6:]
        if production_data[29] == 'green':
            green_hybrids.append(hybrid)
        if production_data[29] == 'yellow':
            yellow_hybrids.append(hybrid)
        if production_data[29] == 'red':
            red_hybrids.append(hybrid)

print "Green Hybrids:"
print green_hybrids
print "Yellow Hybrids:"
print yellow_hybrids
print "Red Hybrids:"
print red_hybrids

total = len(green_hybrids) + len(yellow_hybrids) + len(red_hybrids)

print "TOTAL: %s  \nGreen: %s, Yellow: %s, Red: %s" % (total, len(green_hybrids), len(yellow_hybrids), len(red_hybrids))




# hybrid_nr = raw_input("Choose hybrid:")
# hybrid = hybrid_list[int(hybrid_nr)]
# show_data = [1, 1, 1, 1]
#
# production_data = database.get_production_results(hybrid)
# adc0m = production_data[5]
# adc0b = production_data[6]
# adc1m = production_data[7]
# adc1b = production_data[8]
# cal_dacm = production_data[9]
# cal_dacb = production_data[10]
# print ""
# print "------------------------"
# print hybrid
# print "------------------------"
# print "HV_ID_VER:\t %s" % production_data[1]
# print "BUFFER_OFFSET:\t %s" % production_data[2]
# print "VREF_ADC:\t %s" % production_data[3]
# print "V_BGR:\t\t %s" % production_data[4]
# print "Iref:\t\t %s" % production_data[11]
# print "ADC0:\t\t %s %s" % (adc0m, adc0b)
# print "ADC1:\t\t %s %s" % (adc1m, adc1b)
# print "CAL_DAC:\t %s + %s" % (cal_dacm, cal_dacb)
# print "Register Test:\t %s" % production_data[14]
# print "EC errors:\t %s" % production_data[15]
# print "BC errors:\t %s" % production_data[16]
# print "CRC errors:\t %s" % production_data[17]
# print "Hit errors:\t %s" % production_data[18]
# print "Noisy Channels:\t %s" % production_data[19]
# print "Dead Channels:\t %s" % production_data[20]
# print "BIST:\t\t %s" % production_data[21]
# print "Scan Chain:\t %s" % production_data[22]
# print "SLEEP POWER:\t A: %s D: %s" % (production_data[23], production_data[24])
# print "RUN POWER:\t A: %s D: %s" % (production_data[25], production_data[26])
# print "Location:\t %s" % production_data[27]
# print "Temperature:\t %s" % production_data[28]
# print "State:\t %s" % production_data[29]
# print "------------------------"

