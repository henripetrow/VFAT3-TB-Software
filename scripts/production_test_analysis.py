############################################
# Created by Henri Petrow 2018
# Lappeenranta University of Technology
###########################################

from DatabaseInterfaceBrowse import *
import matplotlib.pyplot as plt

database = DatabaseInterfaceBrowse(database_name="VFAT3_CERN_TESTSETUP_1")
hybrid_list = database.list_hybrids()
green_hybrids1 = []
yellow_hybrids1 = []
red_hybrids1 = []
none_values1 = []
test_hybrids = ['Hybrid55555']
print "List of tested hybrids:"
for i, hybrid in enumerate(hybrid_list):
    if hybrid not in test_hybrids:
        production_data = database.get_production_results(hybrid)
        hybrid = hybrid[6:]
        if production_data[29] == 'green':
            green_hybrids1.append(hybrid)
        elif production_data[29] == 'yellow':
            yellow_hybrids1.append(hybrid)
        elif production_data[29] == 'red':
            red_hybrids1.append(hybrid)
        else:
            none_values1.append(hybrid)

print "Green Hybrids:"
print green_hybrids1
print "Yellow Hybrids:"
print yellow_hybrids1
print "Red Hybrids:"
print red_hybrids1
print "No status value:"
print none_values1
print ""
print ""
total1 = len(green_hybrids1) + len(yellow_hybrids1) + len(red_hybrids1) + len(none_values1)
all_hybrids_1 = []
all_hybrids_1.extend(green_hybrids1)
all_hybrids_1.extend(yellow_hybrids1)
all_hybrids_1.extend(red_hybrids1)
all_hybrids_1.extend(none_values1)


database = DatabaseInterfaceBrowse(database_name="VFAT3_CERN_TESTSETUP_2")
hybrid_list = database.list_hybrids()
green_hybrids2 = []
yellow_hybrids2 = []
red_hybrids2 = []
none_values2 = []
print "List of tested hybrids:"
for i, hybrid in enumerate(hybrid_list):
    if hybrid not in test_hybrids:
        production_data = database.get_production_results(hybrid)
        hybrid = hybrid[6:]
        if production_data[29] == 'green':
            green_hybrids2.append(hybrid)
        elif production_data[29] == 'yellow':
            yellow_hybrids2.append(hybrid)
        elif production_data[29] == 'red':
            red_hybrids2.append(hybrid)
        else:
            none_values2.append(hybrid)

print "Green Hybrids:"
print green_hybrids2
print "Yellow Hybrids:"
print yellow_hybrids2
print "Red Hybrids:"
print red_hybrids2
print "No status value:"
print none_values2
print ""
print ""
total2 = len(green_hybrids2) + len(yellow_hybrids2) + len(red_hybrids2) + len(none_values2)
all_hybrids_2 = []
all_hybrids_2.extend(green_hybrids2)
all_hybrids_2.extend(yellow_hybrids2)
all_hybrids_2.extend(red_hybrids2)
all_hybrids_2.extend(none_values2)

print "Finding duplicates."
green_hybrids = []
yellow_hybrids = []
red_hybrids = []
none_values = []
for hybrid in green_hybrids2:
    found = 0
    if hybrid in green_hybrids1:
        print "%s, GREEN in setup 2, GREEN in setup 1" % hybrid
        found += 1
    if hybrid in yellow_hybrids1:
        print "%s, GREEN in setup 2, YELLOW in setup 1" % hybrid
        found += 1
    if hybrid in red_hybrids1:
        print "%s, GREEN in setup 2, RED in setup 1" % hybrid
        found += 1
    if hybrid in none_values1:
        print "%s, GREEN in setup 2, None in setup 1" % hybrid
        found += 1
    if found == 0:
        green_hybrids.append(hybrid)


for hybrid in yellow_hybrids2:
    found = 0
    if hybrid in green_hybrids1:
        print "%s, YELLOW in setup 2, GREEN in setup 1" % hybrid
        found += 1
    if hybrid in yellow_hybrids1:
        print "%s, YELLOW in setup 2, YELLOW in setup 1" % hybrid
        found += 1
    if hybrid in red_hybrids1:
        print "%s, YELLOW in setup 2, RED in setup 1" % hybrid
        found += 1
    if hybrid in none_values1:
        print "%s, YELLOW in setup 2, None in setup 1" % hybrid
        found += 1
    if found == 0:
        yellow_hybrids.append(hybrid)

for hybrid in red_hybrids2:
    found = 0
    if hybrid in green_hybrids1:
        print "%s, RED in setup 2, GREEN in setup 1" % hybrid
        found += 1
    if hybrid in yellow_hybrids1:
        print "%s, RED in setup 2, YELLOW in setup 1" % hybrid
        found += 1
    if hybrid in red_hybrids1:
        print "%s, RED in setup 2, RED in setup 1" % hybrid
        found += 1
    if hybrid in none_values1:
        print "%s, RED in setup 2, None in setup 1" % hybrid
        found += 1
    if found == 0:
        red_hybrids.append(hybrid)

for hybrid in none_values2:
    found = 0
    if hybrid in green_hybrids1:
        print "%s, None in setup 2, GREEN in setup 1" % hybrid
        found += 1
    if hybrid in yellow_hybrids1:
        print "%s, None in setup 2, YELLOW in setup 1" % hybrid
        found += 1
    if hybrid in red_hybrids1:
        print "%s, None in setup 2, RED in setup 1" % hybrid
        found += 1
    if hybrid in none_values1:
        print "%s, None in setup 2, None in setup 1" % hybrid
        found += 1
    if found == 0:
        none_values.append(hybrid)

green_hybrids.extend(green_hybrids1)
yellow_hybrids.extend(yellow_hybrids1)
red_hybrids.extend(red_hybrids1)
none_values.extend(none_values1)

total = len(green_hybrids) + len(yellow_hybrids) + len(red_hybrids) + len(none_values)

print ""
print "Setup 1: TOTAL: %s  \nGreen: %s, Yellow: %s, Red: %s \nwith no status information: %s" % (total1, len(green_hybrids1), len(yellow_hybrids1), len(red_hybrids1), len(none_values1))
print ""
print "Setup 2: TOTAL: %s  \nGreen: %s, Yellow: %s, Red: %s \nwith no status information: %s" % (
total2, len(green_hybrids2), len(yellow_hybrids2), len(red_hybrids2), len(none_values2))
print ""
print ""
print "GRAND TOTAL: %s  \nGreen: %s, Yellow: %s, Red: %s \nwith no status information: %s" % (total, len(green_hybrids), len(yellow_hybrids), len(red_hybrids), len(none_values))
print ""
print ""
print "No status:"
print none_values