#!/usr/bin/env python2.7

import sys, os, random, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/kernel")
from ipbus import *
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

glib = GLIB()

N_EVENTS = 100.

glib.set("vfat2_0_ctrl0", 55)
glib.set("vfat2_0_ctrl1", 0)
glib.set("vfat2_0_ctrl2", 48)
glib.set("vfat2_0_ctrl3", 0)
glib.set("vfat2_0_ipreampin", 168)
glib.set("vfat2_0_ipreampfeed", 80)
glib.set("vfat2_0_ipreampout", 150)
glib.set("vfat2_0_ishaper", 150)
glib.set("vfat2_0_ishaperfeed", 150)
glib.set("vfat2_0_icomp", 75)
glib.set("vfat2_0_vthreshold2", 0)

glib.set("t1_reset", 1)
glib.set("t1_mode", 0)
glib.set("t1_n", 0)
glib.set("t1_interval", 200)
glib.set("t1_delay", 40)
glib.set("t1_toggle", 1)

xs = []
ys = []
zs = []

for i in range(0, 128):
    glib.set('scan_reset', 1)
    glib.set('scan_mode', 1)
    glib.set('scan_channel', i)
    glib.set('scan_vfat2', 0)
    glib.set('scan_min', 0)
    glib.set('scan_max', 256)
    glib.set('scan_step', 1)
    glib.set('scan_n', int(N_EVENTS))
    glib.set('scan_toggle', 1)
    while (glib.get("scan_status") != 0): r = 1
    data = glib.fifoRead('scan_data', 255)
    for d in data:
        xs.append((d & 0xff000000) >> 24)
        ys.append(i)
        zs.append((d & 0xffffff) / N_EVENTS)

    print i

glib.set("vfat2_0_ctrl0", 0)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(xs, ys, zs)
plt.show()
