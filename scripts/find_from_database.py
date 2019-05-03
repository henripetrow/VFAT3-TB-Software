import os
import time
import sys
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *

lot_nr = input("Give the lot number:")
database = DatabaseInterfaceBrowse()
hybrid_list = database.list_hybrids_by_lot(lot_nr)
for hybrid in hybrid_list:
    production_data_int = database.get_production_results(hybrid)
    production_data = []
    for item in production_data_int:
        if item is None or item == "None":
            production_data.append(0)
        else:
            production_data.append(item)
    if production_data[20] > 0:
        print "Hybrid: %s, Dead Channels: %s, Color: %s" % (hybrid, production_data[20], production_data[29])





# red_list = []
# yellow_list = []
# green_list = []
#
# lot_nr = input("Give the lot number:")
#
# database = DatabaseInterfaceBrowse()
# hybrid_list = database.list_hybrids_by_lot(lot_nr)
# for hybrid in hybrid_list:
#     production_data_int = database.get_production_results(hybrid)
#     production_data = []
#     for item in production_data_int:
#         if item is None or item == "None":
#             production_data.append("")
#         else:
#             production_data.append(item)
#     if production_data[29] == 'red':
#         red_list.append(hybrid[6:])
#     elif production_data[29] == 'yellow':
#         yellow_list.append(hybrid[6:])
#     elif production_data[29] == 'green':
#         green_list.append(hybrid[6:])
#     else:
#         print "Problematic hybrid: %s" % hybrid[6:]
#
#
# print "\nGreen hybrids: %s" % len(green_list)
# print green_list
#
# print "\nYellow hybrids: %s" % len(yellow_list)
# print yellow_list
#
# print "\nRed hybrids: %s" % len(red_list)
# print red_list
#
# print "\n\n*****************"
# print "Found hybrids for lot %s:" % lot_nr
# print "Green hybrids: %s" % len(green_list)
# print "Yellow hybrids: %s" % len(yellow_list)
# print "Red hybrids: %s" % len(red_list)
# print "*****************\n"