from xml.dom import minidom
import matplotlib.pyplot as plt
import numpy
import os


# parse an xml file by name
mydoc = minidom.parse('/home/a0312687/Downloads/results/xml/VFAT3_ENC.xml')
# mydoc = minidom.parse('/home/a0312687/cernbox/Data/production_data_xml_test/VFAT3_ENC.xml')

datasets = mydoc.getElementsByTagName('DATASET')

print datasets[0].childNodes[5].childNodes[3].firstChild.data  # serial number
for i, dataset in enumerate(datasets):
    print "[%s] %s" % (i, dataset.childNodes[5].childNodes[3].firstChild.data)  # serial number

hybrid_nr = raw_input("Choose hybrid:")
for hybrid_nr in range(0, 62):
    data = datasets[int(hybrid_nr)].childNodes
    data = data[1:]
    data = data[::2]

    channels = []
    encs = []

    for dat in data[3:]:
        channel = dat.childNodes[1].firstChild.data  # channel
        enc = dat.childNodes[2].firstChild.data  # enc
        channels.append(int(channel))

        try:
            encs.append(float(enc))
        except ValueError:
            encs.append(0)

    mean_data = [numpy.mean(encs)] * 128
    plt.plot(channels, mean_data)
    plt.plot(channels, encs)
    plt.text(100, 0.8, "Mean enc:\n %f" % numpy.mean(encs), bbox=dict(alpha=0.5))
    plt.title("%s enc" % datasets[int(hybrid_nr)].childNodes[5].childNodes[3].firstChild.data)
    plt.ylim([0, 0.3])
    plt.xlim([0, 128])
    plt.xlabel("Channel")
    plt.ylabel("enc [fC]")
    plt.grid(True)
    plt.show()
