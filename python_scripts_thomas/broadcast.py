#!/usr/bin/env python2.7

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/kernel")
from ipbus import *

IPS = [ "192.168.0.161", "192.168.0.162" ]
icomp = 0
latency = 0

for i in range(0, len(sys.argv)):
    if (sys.argv[i] == '--latency'): latency = int(sys.argv[i + 1])
    if (sys.argv[i] == '--icomp'): icomp = int(sys.argv[i + 1])

for IP in IPS:
    glib = GLIB(IP.strip())

    glib.set2OH(0, "ei2c_reset", 0)
    glib.set2OH(0, "vfat2_all_latency", latency)
    glib.set2OH(0, "vfat2_all_icomp", icomp)
    glib.set2OH(1, "ei2c_reset", 0)
    glib.set2OH(1, "vfat2_all_latency", latency)
    glib.set2OH(1, "vfat2_all_icomp", icomp)
