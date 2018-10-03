############################################
# Created by Henri Petrow 2018
# Lappeenranta University of Technology
###########################################

import os
import sys
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *
from DatabaseInterface import *

file = 'hybrids_list.txt'
print "Reading list of hybrids from the file: %s" % file
with open('hybrids_list.txt', 'r') as f:
    hybrids = []
    for line in f:
        line.strip('\n')
        hybrids.append('Hybrid%s' % int(line))

database_browse = DatabaseInterfaceBrowse()
text = "Hybrid Iref CAL_DACm CAL_DACb ADC0M ADC0B ADC1M ADC1B\n"
for hybrid in hybrids:
    print hybrid
    production_data = database_browse.get_production_results(hybrid)
    text += "%s %s %s %s %s %s %s %s\n" % (production_data[0], production_data[11], production_data[9], production_data[10], production_data[5], production_data[6], production_data[7], production_data[8])

print text

outF = open("hybrid_list_calibration_values.txt", "w")
outF.write(text)
outF.close()
