############################################
# Created by Henri Petrow 2018
# Lappeenranta University of Technology
###########################################

from DatabaseInterfaceBrowse import *
import matplotlib.pyplot as plt
import os
import sys
sys.path.append('../')
from move_hybrid_between_databases import *

database = DatabaseInterfaceBrowse(database_name="VFAT3_CERN_TESTSETUP_1")
hybrid_list = database.list_hybrids()
green_hybrids1 = []
yellow_hybrids1 = []
red_hybrids1 = []
none_values1 = []
test_hybrids = ['Hybrid55555', 'Hybrid5555']
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

green_hybrids2_f = []
yellow_hybrids2_f = []
red_hybrids2_f = []
none_values2_f = []
for hybrid in green_hybrids2:
    found = 0
    if hybrid in green_hybrids1:
        print "%s, GREEN in setup 2, GREEN in setup 1" % hybrid
        green_hybrids2_f.append(hybrid)
        found += 1
    if hybrid in yellow_hybrids1:
        print "%s, GREEN in setup 2, YELLOW in setup 1" % hybrid
        green_hybrids2_f.append(hybrid)
        found += 1
    if hybrid in red_hybrids1:
        print "%s, GREEN in setup 2, RED in setup 1" % hybrid
        green_hybrids2_f.append(hybrid)
        found += 1
    if hybrid in none_values1:
        print "%s, GREEN in setup 2, None in setup 1" % hybrid
        green_hybrids2_f.append(hybrid)
        found += 1
    if found == 0:
        green_hybrids2_f.append(hybrid)


for hybrid in yellow_hybrids2:
    found = 0
    if hybrid in green_hybrids1:
        print "%s, YELLOW in setup 2, GREEN in setup 1" % hybrid
        found += 1
    if hybrid in yellow_hybrids1:
        print "%s, YELLOW in setup 2, YELLOW in setup 1" % hybrid
        yellow_hybrids2_f.append(hybrid)
        found += 1
    if hybrid in red_hybrids1:
        print "%s, YELLOW in setup 2, RED in setup 1" % hybrid
        yellow_hybrids2_f.append(hybrid)
        found += 1
    if hybrid in none_values1:
        print "%s, YELLOW in setup 2, None in setup 1" % hybrid
        yellow_hybrids2_f.append(hybrid)
        found += 1
    if found == 0:
        yellow_hybrids2_f.append(hybrid)

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
        red_hybrids2_f.append(hybrid)
        found += 1
    if hybrid in none_values1:
        print "%s, RED in setup 2, None in setup 1" % hybrid
        red_hybrids2_f.append(hybrid)
        found += 1
    if found == 0:
        red_hybrids2_f.append(hybrid)

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
        none_values2_f.append(hybrid)


green_hybrids1_f = []
yellow_hybrids1_f = []
red_hybrids1_f = []
none_values1_f = []

for hybrid in green_hybrids1:
    found = 0
    if hybrid in green_hybrids2_f:
        found += 1
    if hybrid in yellow_hybrids2_f:
        found += 1
    if hybrid in red_hybrids2_f:
        found += 1
    if found == 0:
        green_hybrids1_f.append(hybrid)

for hybrid in yellow_hybrids1:
    found = 0
    if hybrid in green_hybrids2_f:
        found += 1
    if hybrid in yellow_hybrids2_f:
        found += 1
    if hybrid in red_hybrids2_f:
        found += 1
    if found == 0:
        yellow_hybrids1_f.append(hybrid)

for hybrid in red_hybrids1:
    found = 0
    if hybrid in green_hybrids2_f:
        found += 1
    if hybrid in yellow_hybrids2_f:
        found += 1
    if hybrid in red_hybrids2_f:
        found += 1
    if found == 0:
        red_hybrids1_f.append(hybrid)

none_values1_f = none_values1

total2_f = len(green_hybrids2_f) + len(yellow_hybrids2_f) + len(red_hybrids2_f) + len(none_values2_f)
total1_f = len(green_hybrids1_f) + len(yellow_hybrids1_f) + len(red_hybrids1_f) + len(none_values1_f)

green_hybrids = green_hybrids1_f + green_hybrids2_f
print "TOTAL green:"
print green_hybrids
yellow_hybrids = yellow_hybrids1_f + yellow_hybrids2_f
print "TOTAL yellow:"
print yellow_hybrids
red_hybrids = red_hybrids1_f + red_hybrids2_f
print "TOTAL red:"
print red_hybrids
none_values = none_values1_f + none_values2_f
print "TOTAL None-value:"
print none_values


total = len(green_hybrids) + len(yellow_hybrids) + len(red_hybrids) + len(none_values)

print ""
print "Setup 1: TOTAL: %s  \nGreen: %s, Yellow: %s, Red: %s \nwith no status information: %s" % (total1_f, len(green_hybrids1_f), len(yellow_hybrids1_f), len(red_hybrids1_f), len(none_values1_f))
print ""
print "Setup 2: TOTAL: %s  \nGreen: %s, Yellow: %s, Red: %s \nwith no status information: %s" % (total2_f, len(green_hybrids2_f), len(yellow_hybrids2_f), len(red_hybrids2_f), len(none_values2_f))
print ""
print ""
print "GRAND TOTAL: %s  \nGreen: %s, Yellow: %s, Red: %s \nwith no status information: %s" % (total, len(green_hybrids), len(yellow_hybrids), len(red_hybrids), len(none_values))
print ""
print ""
print "No status:"
print none_values

hybrids_with_short =['3568', '4393', '3704', '2870', '4366', '5895', '4285', '3891', '2824', '2583', '4234', '4911']

with open('hybrid_sa_good_hybrids.txt') as f:
    green_inventory = f.read().splitlines()
print "Checking green inventory:"
for hybrid_i in green_inventory:
    if hybrid_i not in green_hybrids:
        print "Hybrid %s not found in database of greens." % hybrid_i
    if hybrid_i in yellow_hybrids:
        print "Hybrid %s found in database of yellows." % hybrid_i
    if hybrid_i in red_hybrids:
        print "Hybrid %s found in database of reds." % hybrid_i
print ""

with open('hybrid_sa_yellow_hybrids.txt') as f:
    yellow_inventory = f.read().splitlines()
print "Checking yellow inventory:"
for hybrid_i in yellow_inventory:
    if hybrid_i not in yellow_hybrids:
        print "Hybrid %s not found in database of yellows." % hybrid_i
    if hybrid_i in green_hybrids:
        print "Hybrid %s found in database of greens." % hybrid_i
    if hybrid_i in red_hybrids:
        print "Hybrid %s found in database of reds." % hybrid_i
print ""

with open('hybrid_sa_red_hybrids.txt') as f:
    red_inventory = f.read().splitlines()
print "Checking red inventory:"
for hybrid_i in red_inventory:
    if hybrid_i not in red_hybrids:
        print "Hybrid %s not found in database of reds." % hybrid_i
        if hybrid_i in hybrids_with_short:
            print "But in the list of shorts"
    if hybrid_i in green_hybrids:
        print "Hybrid %s found in database of greens." % hybrid_i
    if hybrid_i in yellow_hybrids:
        print "Hybrid %s found in database of yellows." % hybrid_i
print ""
#
# for g_hybrid in green_hybrids:
#     if g_hybrid not in lines:
#         print "Hybrid %s not found in green inventory." % g_hybrid

testsetup1_hybrids = green_hybrids1_f + yellow_hybrids1_f + red_hybrids1_f
testsetup2_hybrids = green_hybrids2_f + yellow_hybrids2_f + red_hybrids2_f

print len(testsetup1_hybrids)
print len(testsetup2_hybrids)
amount = len(testsetup2_hybrids)
for i, hybrid in enumerate(testsetup2_hybrids):
    print hybrid
    print "%s/%s" % (i+1, amount)
    move_hybrid_between_databases(hybrid, "VFAT3_CERN_TESTSETUP_2", "VFAT3_Production_final")