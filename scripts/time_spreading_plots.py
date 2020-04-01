import numpy
import matplotlib.pyplot as plt

timestamp = "010420201143"
folder = "../../cernbox/VFAT3_charge_distribution/Data/run_%s/" % timestamp
data_file = "%s%soutput_data.dat" % (folder, timestamp)

from data_file import *


print Low_data_ps0_lat2
