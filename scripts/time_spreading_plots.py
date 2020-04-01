import numpy
import matplotlib.pyplot as plt

timestamp = "010420201551"
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
print data.Low_data_ps0_lat2

