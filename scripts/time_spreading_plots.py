import numpy
import matplotlib.pyplot as plt

mapped_target_channels = [25, 50, 75, 100]


timestamp = "010420201612"
folder = "../../cernbox/VFAT3_charge_distribution/Data/run_%s/" % timestamp
output_folder = "../../cernbox/VFAT3_charge_distribution/Data/analysed/"
data_file = "%s%soutput_data.dat" % (folder, timestamp)


def getVarFromFile(filename):
    import imp
    f = open(filename)
    global data
    data = imp.load_source('data', '', f)
    f.close()

# path to "config" file
getVarFromFile(data_file)
print data.High_gain_data_ps0_lat3[0]

for axis in range(0, len(mapped_target_channels)):
    main_ch = mapped_target_channels[axis]
    plt.figure()

    plt.plot(thresholds, data.High_gain_data_ps0_lat0[1:, main_ch], label='LAT 0')
    plt.plot(thresholds, data.High_gain_data_ps0_lat1[1:, main_ch], label='LAT 1')
    plt.plot(thresholds, data.High_gain_data_ps0_lat2[1:, main_ch], label='LAT 2')
    plt.plot(thresholds, data.High_gain_data_ps0_lat3[1:, main_ch], label='LAT 3')
    plt.plot(thresholds, data.High_gain_data_ps0_lat4[1:, main_ch], label='LAT 4')
    plt.plot(thresholds, data.High_gain_data_ps0_lat5[1:, main_ch], label='LAT 5')


    plt.grid()
    plt.legend()
    plt.ylabel('# Hits')
    plt.xlabel('Threshold [DAC counts]')
    plt.title('Charge distribution')
    plt.savefig('%stime_spread_ps_0_ch_%s.png' % (folder, main_ch))


