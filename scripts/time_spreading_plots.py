import numpy
import matplotlib.pyplot as plt

timestamp = "010420201612"
folder = "../../cernbox/VFAT3_charge_distribution/Data/run_%s/" % timestamp
data_file = "%s%soutput_data.dat" % (folder, timestamp)

def getVarFromFile(filename):
    import imp
    f = open(filename)
    global data
    data = imp.load_source('data', '', f)
    f.close()

# path to "config" file
getVarFromFile(data_file)
print data.High_gain_data_ps1_lat3[0]

