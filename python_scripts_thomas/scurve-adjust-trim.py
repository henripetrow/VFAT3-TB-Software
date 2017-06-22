#!/usr/bin/env python2.7

import sys, os, random, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/kernel")
from ipbus import *
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

glib = GLIB()

N_EVENTS = 1000.
VCAL_MIN = 20
VCAL_MAX = 55

glib.set("oh_trigger_source", 1)

glib.set("vfat2_0_ctrl0", 55)
glib.set("vfat2_0_ctrl1", 0)
glib.set("vfat2_0_ctrl2", 48)
glib.set("vfat2_0_ctrl3", 0)
glib.set("vfat2_0_ipreampin", 168)
glib.set("vfat2_0_ipreampfeed", 80)
glib.set("vfat2_0_ipreampout", 150)
glib.set("vfat2_0_ishaper", 150)
glib.set("vfat2_0_ishaperfeed", 100)
glib.set("vfat2_0_icomp", 75)
glib.set("vfat2_0_vthreshold1", 25)
glib.set("vfat2_0_vthreshold2", 0)

glib.set("vfat2_0_latency", 37)

glib.set("t1_reset", 1)
glib.set("t1_mode", 1)
glib.set("t1_n", 0)
glib.set("t1_interval", 200)
glib.set("t1_delay", 40)
glib.set("t1_toggle", 1)

f = open('trims.txt', 'w')
f.write("channel\trimdac\n")

for channel in range(1, 128):
    regName = "vfat2_0_channel" + str(channel + 1)
    trimDAC = 31
    regValue = (1 << 6) + trimDAC
    if (channel == 0):
        regName = "vfat2_0_channel2"
        regValue = (1 << 7) + trimDAC
    foundGood = False

    while (foundGood == False):
        regValue = (1 << 6) + trimDAC
        glib.set(regName, regValue)

        glib.set('scan_reset', 1)
        glib.set('scan_mode', 3)
        glib.set('scan_channel', channel)
        glib.set('scan_vfat2', 0)
        glib.set('scan_min', VCAL_MIN)
        glib.set('scan_max', VCAL_MAX)
        glib.set('scan_step', 1)
        glib.set('scan_n', int(N_EVENTS))
        glib.set('scan_toggle', 1)

        while (glib.get("scan_status") != 0): i = 1
        data = glib.fifoRead('scan_data', VCAL_MAX - VCAL_MIN - 1)
        foundVCal = 0
        for d in data:
            Eff = (d & 0xffffff) / N_EVENTS
            VCal = (d & 0xff000000) >> 24
            if (Eff >= 0.5):
                foundVCal = VCal
                break

        print "Channel", channel, "TrimDAC is of", trimDAC, "and the VCal is of", foundVCal

        if (foundVCal > 35): trimDAC += 1
        elif (foundVCal < 35): trimDAC -= 1
        else: break

    f.write(str(channel)+"\t"+str(trimDAC)+"\n")

    glib.set(regName, 0)

glib.set("vfat2_0_ctrl0", 0)
