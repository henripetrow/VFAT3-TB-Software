#!/usr/bin/env python2.7

import sys, os, time, struct, signal
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/kernel")
from ipbus import *

####################################################

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

####################################################

print "Dumping the VFAT2 registers to disk"

glib = GLIB()

filename = time.strftime("tkdata_%Y_%m_%d_%H_%M_%S.txt", time.gmtime())
f = open(filename, "wb", 0)

signal.signal(signal.SIGINT, signal_handler)

while (True):
    depth = glib.get("tk_data_cnt")
    if (depth > 0):
        fmt = ">" + "I" * depth
        raw_data = glib.fifoRead("tk_data_rd", depth)
        str_data = struct.pack(fmt, *raw_data)
        for d in str_data: f.write(d)

f.close()
