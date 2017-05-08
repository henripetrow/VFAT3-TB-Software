#!/usr/bin/env python2.7

import sys, os, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/kernel")
from ipbus import *

####################################################

print "Dumping the VFAT2 registers to disk"

glib = GLIB()

filename = time.strftime("vfat2_%Y_%m_%d_%H_%M_%S.txt", time.gmtime())
f = open(filename, "w")

for i in range(0, 24):
    values = glib.blockRead("vfat2_" + str(i) + "_ctrl0", 0x96)
    f.write(str(i) + "\t")
    for val in values: f.write(str(val & 0xff) + "\t")
    f.write("\n")

f.close()
