#!/usr/bin/env python2.7

import sys, os, random, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/kernel")
from ipbus import *

####################################################

print

####################################################

Passed = '\033[92m   > Passed... \033[0m'
Failed = '\033[91m   > Failed... \033[0m' 

def txtTitle(str):
    print '\033[1m' + str + '\033[0m'

glibIP = raw_input("> Enter the GLIB's IP address: ")
glib = GLIB(glibIP.strip())

print

####################################################

txtTitle("A. Testing the GLIB's presence")
print "   Trying to read the GLIB board ID... If this test fails, the script will stop."

if (glib.get("board_id") != 0): print Passed
else:
    print Failed
    sys.exit()

testA = True

print

###################################################

for i in range(0, 24):
    print "-------------------", str(i), "-------------------"

    s = glib.get('vfat2_' + str(i) + '_ctrl0')
    glib.set('vfat2_' + str(i) + '_ctrl0', 55)
    glib.set('scan_reset', 1)
    glib.set('scan_mode', 0)
    glib.set('scan_vfat2', i)
    glib.set('scan_min', 0)
    glib.set('scan_max', 20)
    glib.set('scan_step', 1)
    glib.set('scan_n', 10000)
    glib.set('scan_toggle', 1)
    time.sleep(1)
    data = glib.fifoRead('scan_data', 20)
    for d in data:
        print hex((d & 0xff000000) >> 24), " = ", (d & 0xffffff) / 10000. * 100
    glib.set('vfat2_' + str(i) + '_ctrl0', s)
