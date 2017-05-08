#!/usr/bin/env python2.7

import sys, struct
import matplotlib.pyplot as plt

####################################################

print "Analyzing tracking data"

f = open(sys.argv[1], "rb")

bcs = []
ecs = []
bxs = []
flagss = []
chipIDs = []
crcs = []

while (True):
    packets = [0, 0, 0, 0, 0, 0, 0]
    packets[0] = struct.unpack(">I", f.read(4))[0]
    if (not packets[0]): break
    if (packets[0] & 0xF0000000 != 0xA0000000): continue
    if (packets[0] & 0xF000 != 0xC000): continue
    packets[1] = struct.unpack(">I", f.read(4))[0]
    packets[2] = struct.unpack(">I", f.read(4))[0]
    packets[3] = struct.unpack(">I", f.read(4))[0]
    packets[4] = struct.unpack(">I", f.read(4))[0]
    packets[5] = struct.unpack(">I", f.read(4))[0]
    packets[6] = struct.unpack(">I", f.read(4))[0]

    bc = (0x0fff0000 & packets[0]) >> 16;
    ec = (0x00000ff0 & packets[0]) >> 4;
    flags = packets[0] & 0xf;
    chipID = (0x0fff0000 & packets[1]) >> 16;
    strips0 = ((0x0000ffff & packets[1]) << 16) | ((0xffff0000 & packets[2]) >> 16);
    strips1 = ((0x0000ffff & packets[2]) << 16) | ((0xffff0000 & packets[3]) >> 16);
    strips2 = ((0x0000ffff & packets[3]) << 16) | ((0xffff0000 & packets[4]) >> 16);
    strips3 = ((0x0000ffff & packets[4]) << 16) | ((0xffff0000 & packets[5]) >> 16);
    crc = 0x0000ffff & packets[5];
    bx = packets[6];

    bcs.append(bc)
    ecs.append(ec)
    bxs.append(bx)
    flagss.append(flags)
    chipIDs.append(chipID)
    crcs.append(crc)

(fig, ((plt1, plt2, plt3), (plt4, plt5, plt6))) = plt.subplots(2, 3)    

plt1.hist(bcs)
plt1.set_title("BC")
plt2.hist(ecs, bins = 256)
plt2.set_title("EC")
plt3.hist(bxs)
plt3.set_title("BX")
plt4.hist(flagss)
plt4.set_title("Flags")
plt5.hist(chipIDs)
plt5.set_title("Chip ID")
plt6.hist(crcs)
plt6.set_title("CRC")


plt.show()

f.close()
