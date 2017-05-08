#!/usr/bin/env python

import sys, os, random, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/kernel")
from ipbus import *


N_SBIT_EVENTS = 10000.
N_TK_EVENTS = 100.
VFAT2 = 0

glib = GLIB()

glib.set("oh_trigger_source", 1)

glib.set("vfat2_"+str(VFAT2)+"_ctrl0", 55)
glib.set("vfat2_"+str(VFAT2)+"_ctrl1", 0)
glib.set("vfat2_"+str(VFAT2)+"_ctrl2", 48)
glib.set("vfat2_"+str(VFAT2)+"_ctrl3", 0)
glib.set("vfat2_"+str(VFAT2)+"_ipreampin", 168)
glib.set("vfat2_"+str(VFAT2)+"_ipreampfeed", 80)
glib.set("vfat2_"+str(VFAT2)+"_ipreampout", 150)
glib.set("vfat2_"+str(VFAT2)+"_ishaper", 150)
glib.set("vfat2_"+str(VFAT2)+"_ishaperfeed", 100)
glib.set("vfat2_"+str(VFAT2)+"_icomp", 75)
glib.set("vfat2_"+str(VFAT2)+"_vthreshold1", 15)
glib.set("vfat2_"+str(VFAT2)+"_vthreshold2", 0)
glib.set("vfat2_"+str(VFAT2)+"_latency", 37)

for channel in range(1, 129): glib.set("vfat2_"+str(VFAT2)+"_channel"+str(channel), 0)

glib.set("scan_reset", 1)
glib.set("t1_reset", 1)

"""
Threshold scan using SBits
"""

print "Threshold scan using SBits"

f = open('all-threshold-sbits.txt', 'w')
f.write("Threshold\tCount\n")

glib.set('scan_reset', 1)
glib.set('scan_mode', 0)
glib.set('scan_vfat2', VFAT2)
glib.set('scan_min', 0)
glib.set('scan_max', 255)
glib.set('scan_step', 1)
glib.set('scan_n', int(N_SBIT_EVENTS))
glib.set('scan_toggle', 1)
while (glib.get("scan_status") != 0): r = 1
data = glib.fifoRead('scan_data', 255)
for d in data:
    x = (d & 0xff000000) >> 24
    y = (d & 0xffffff) / N_SBIT_EVENTS
    f.write(str(x)+"\t"+str(y)+"\n")

glib.set("scan_reset", 1)

"""
Threshold scan using Tracking data
"""

print "Threshold scan using Tracking data"

f = open('all-threshold-tk.txt', 'w')
f.write("Channel\tThreshold\tCount\n")

glib.set("t1_reset", 1)
glib.set("t1_mode", 0)
glib.set("t1_n", 0)
glib.set("t1_interval", 200)
glib.set("t1_delay", 40)
glib.set("t1_toggle", 1)

for channel in range(0, 128):
    glib.set('scan_reset', 1)
    glib.set('scan_mode', 1)
    glib.set('scan_channel', channel)
    glib.set('scan_vfat2', VFAT2)
    glib.set('scan_min', 0)
    glib.set('scan_max', 255)
    glib.set('scan_step', 1)
    glib.set('scan_n', int(N_TK_EVENTS))
    glib.set('scan_toggle', 1)
    while (glib.get("scan_status") != 0): r = 1
    data = glib.fifoRead('scan_data', 255)
    for d in data:
        x = (d & 0xff000000) >> 24
        y = (d & 0xffffff) / N_TK_EVENTS
        f.write(str(channel)+"\t"+str(x)+"\t"+str(y)+"\n")

glib.set("scan_reset", 1)
glib.set("t1_reset", 1)

"""
Global SCurve at T15 and TRIM = 0
"""

print "Global SCurve at T15 and TRIM = 0"

f = open('all-scurve-generic-trim000.txt', 'w')
f.write("Cal\tCount\n")

glib.set("t1_reset", 1)
glib.set("t1_mode", 1)
glib.set("t1_n", 0)
glib.set("t1_interval", 200)
glib.set("t1_delay", 40)
glib.set("t1_toggle", 1)

glib.set("vfat2_"+str(VFAT2)+"_channel14", (1 << 6))

glib.set('scan_reset', 1)
glib.set('scan_mode', 3)
glib.set('scan_channel', 13)
glib.set('scan_vfat2', 0)
glib.set('scan_min', 0)
glib.set('scan_max', 255)
glib.set('scan_step', 1)
glib.set('scan_n', int(N_TK_EVENTS))
glib.set('scan_toggle', 1)
while (glib.get("scan_status") != 0): i = 1
data = glib.fifoRead("scan_data", 255)
for d in data:
    x = (d & 0xff000000) >> 24
    y = (d & 0xffffff) / N_TK_EVENTS
    f.write(str(x)+"\t"+str(y)+"\n")

glib.set("vfat2_"+str(VFAT2)+"_channel14", 0)

glib.set("scan_reset", 1)
glib.set("t1_reset", 1)

"""
Global SCurve at T15 and TRIM = 31
"""

print "Global SCurve at T15 and TRIM = 31"

f = open('all-scurve-generic-trim111.txt', 'w')
f.write("Cal\tCount\n")

glib.set("t1_reset", 1)
glib.set("t1_mode", 1)
glib.set("t1_n", 0)
glib.set("t1_interval", 200)
glib.set("t1_delay", 40)
glib.set("t1_toggle", 1)

glib.set("vfat2_"+str(VFAT2)+"_channel14", (1 << 6) + 31)

glib.set('scan_reset', 1)
glib.set('scan_mode', 3)
glib.set('scan_channel', 13)
glib.set('scan_vfat2', 0)
glib.set('scan_min', 0)
glib.set('scan_max', 255)
glib.set('scan_step', 1)
glib.set('scan_n', int(N_TK_EVENTS))
glib.set('scan_toggle', 1)
while (glib.get("scan_status") != 0): i = 1
data = glib.fifoRead("scan_data", 255)
for d in data:
    x = (d & 0xff000000) >> 24
    y = (d & 0xffffff) / N_TK_EVENTS
    f.write(str(x)+"\t"+str(y)+"\n")

glib.set("vfat2_"+str(VFAT2)+"_channel14", 0)

glib.set("scan_reset", 1)
glib.set("t1_reset", 1)
