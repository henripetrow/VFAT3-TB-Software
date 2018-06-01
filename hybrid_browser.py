from DatabaseInterfaceBrowse import *
import matplotlib.pyplot as plt

database = DatabaseInterfaceBrowse()
hybrid_list = database.list_hybrids()
print "List of tested hybrids:"
for i, hybrid in enumerate(hybrid_list):
    print "[%i] %s" % (i, hybrid)

hybrid_nr = raw_input("Choose hybrid:")
adcs = ["ADC0", "ADC1"]
dac6bits = ["CFD_DAC_1", "CFD_DAC_2", "HYST_DAC", "PRE_I_BLCC", "PRE_I_BSF", "SD_I_BSF"]
dac8bits = ["ARM_DAC", "CAL_DAC", "PRE_VREF", "PRE_I_BIT", "SD_I_BDIFF", "SH_I_BDIFF", "SD_I_BFCAS", "SH_I_BFCAS", "ZCC_DAC"]
dac_table = []
hybrid = hybrid_list[int(hybrid_nr)]
show_data = [1, 1, 1, 1]

production_data = database.get_production_results(hybrid)
adc0m = production_data[5]
adc0b = production_data[6]
adc1m = production_data[7]
adc1b = production_data[8]
cal_dacm = production_data[9]
cal_dacb = production_data[10]
print ""
print "------------------------"
print hybrid
print "------------------------"
print "HV_ID_VER:\t %s" % production_data[1]
print "BUFFER_OFFSET:\t %s" % production_data[2]
print "VREF_ADC:\t %s" % production_data[3]
print "V_BGR:\t\t %s" % production_data[4]
print "Iref:\t\t %s" % production_data[11]
print "ADC0:\t\t %s %s" % (adc0m, adc0b)
print "ADC1:\t\t %s %s" % (adc1m, adc1b)
print "CAL_DAC:\t %s + %s" % (cal_dacm, cal_dacb)
print "Register Test:\t %s" % production_data[14]
print "EC errors:\t %s" % production_data[15]
print "BC errors:\t %s" % production_data[16]
print "CRC errors:\t %s" % production_data[17]
print "Hit errors:\t %s" % production_data[18]
print "Noisy Channels:\t %s" % production_data[19]
print "Dead Channels:\t %s" % production_data[20]
print "BIST:\t\t %s" % production_data[21]
print "Scan Chain:\t %s" % production_data[22]
print "SLEEP POWER:\t A: %s D: %s" % (production_data[23], production_data[24])
print "RUN POWER:\t A: %s D: %s" % (production_data[25], production_data[26])
print "------------------------"


# 6-bit DACs
if show_data[0]:
    for adc in adcs:
        for dac in dac6bits:
            data = database.get_table_values(hybrid, "%s_%s" % (dac, adc))
            x_data = []
            y_data = []
            for i, dat in enumerate(data):
                if dat:
                    x_data.append(i)
                    if adc == "ADC0":
                        y_data.append(dat*adc0m+adc0b)
                    if adc == "ADC1":
                        y_data.append(dat*adc1m+adc1b)
            plt.plot(x_data, y_data, label=dac)
    plt.legend()
    plt.title("%s 6-bit DACs" % hybrid)
    plt.xlim([0, 100])
    plt.ylabel("ADC value [mV]")
    plt.xlabel("DAC count")
    plt.grid(True)
    plt.show()


# 8-bit DACs
if show_data[1]:
    for adc in adcs:
        for dac in dac8bits:
            data = database.get_table_values(hybrid, "%s_%s" % (dac, adc))
            x_data = []
            y_data = []
            for i, dat in enumerate(data):
                if dat:
                    x_data.append(i)
                    if adc == "ADC0":
                        y_data.append(dat*adc0m+adc0b)
                    if adc == "ADC1":
                        y_data.append(dat*adc1m+adc1b)
            plt.plot(x_data, y_data, label=dac)
    plt.legend(prop={'size': 10})
    plt.title("%s 8-bit DACs" % hybrid)
    plt.xlim([0, 400])
    plt.ylabel("ADC value [mV]")
    plt.xlabel("DAC count")
    plt.grid(True)
    plt.show()


# Thresholds
if show_data[2]:
    data = database.get_table_values(hybrid, "Threshold")
    x_data = range(0, 128)
    if production_data[12]:  # Plot the mean value as horizontal line if the value exists.
        mean_data = [production_data[12]]*128
        plt.plot(x_data, mean_data)
    plt.plot(x_data, data)
    if production_data[12]:
        plt.text(80, 8, "Mean Threshold:\n %f" % production_data[12], bbox=dict(alpha=0.5))
    plt.plot(x_data, data)
    plt.title("%s Threshold" % hybrid)
    plt.ylim([0, 10])
    plt.xlim([0, 128])
    plt.xlabel("Channel")
    plt.ylabel("Threshold [fC]")
    plt.grid(True)
    plt.show()


# enc
if show_data[3]:
    data = database.get_table_values(hybrid, "enc")
    x_data = range(0, 128)
    if production_data[13]:  # Plot the mean value as horizontal line if the value exists.
        mean_data = [production_data[13]]*128
        plt.plot(x_data, mean_data)
    plt.plot(x_data, data)
    if production_data[13]:
        plt.text(100, 0.8, "Mean enc:\n %f" % production_data[13], bbox=dict(alpha=0.5))
    plt.title("%s enc" % hybrid)
    plt.ylim([0, 1])
    plt.xlim([0, 128])
    plt.xlabel("Channel")
    plt.ylabel("enc [fC]")
    plt.grid(True)
    plt.show()