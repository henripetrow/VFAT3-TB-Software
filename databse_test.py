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
show_data = [0, 0, 0, 0]

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

# filename = "%s_Production_table.xml" % hybrid
# if not os.path.exists(os.path.dirname(filename)):
#     try:
#         os.makedirs(os.path.dirname(filename))
#     except OSError as exc:  # Guard against race condition
#         print "Unable to create directory"
# text = "Results were saved to the folder:\n %s \n" % filename
#
# outF = open(filename, "w")
data = "<ROOT>\n"
data += "<HEADER>\n"
data += "<TYPE>\n"
data += "<EXTENSION_TABLE_NAME>VFAT3_PRODUCTION_SUMMARY</EXTENSION_TABLE_NAME>\n"
data += "<NAME>VFAT3 Production Summary Data</NAME>\n"
data += "</TYPE>\n"
data += "<RUN>\n"
data += "<RUN_TYPE>VFAT3 Production Data</RUN_TYPE>\n"
data += "<RUN_NUMBER>1</RUN_NUMBER>\n"
data += "<RUN_BEGIN_TIMESTAMP>2016-07-18 13:55:06</RUN_BEGIN_TIMESTAMP>\n"
data += "<RUN_END_TIMESTAMP>2016-07-18 14:55:03</RUN_END_TIMESTAMP>\n"
data += "<COMMENT_DESCRIPTION>VFAT3 Production Data from Testing at CERNV</COMMENT_DESCRIPTION>\n"
data += "<LOCATION>TIF</LOCATION>\n"
data += "<INITIATED_BY_USER>YourName</INITIATED_BY_USER>\n"
data += "</RUN>\n"
data += "</HEADER>\n"

# Start of dataset.
data += "<DATASET>\n"
data += "<COMMENT_DESCRIPTION>GEM VFAT3 Production Summary Data</COMMENT_DESCRIPTION>\n"
data += "<VERSION>1</VERSION>\n"
data += "<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n"
data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
data += "</PART><DATA>\n"
data += "<HW_ID_VERSION>%s</HW_ID_VERSION>\n" % production_data[1]
data += "<BUFFER_OFFSET>%s</BUFFER_OFFSET>\n" % production_data[1]
data += "<VREF_ADC>%s</VREF_ADC>\n" % production_data[1]
data += "<V_BGR>%s</V_BGR>\n" % production_data[1]
data += "<ADC0M>%s</ADC0M>\n" % production_data[5]
data += "<ADC0B>%s</ADC0B>\n" % production_data[6]
data += "<ADC1M>%s</ADC1M>\n" % production_data[7]
data += "<ADC1B>%s</ADC1B>\n" % production_data[8]
data += "<CAL_DACM>%s</CAL_DACM>\n" % production_data[9]
data += "<CAL_DACB>%s</CAL_DACB>\n" % production_data[10]
data += "<IREF>%s</IREF>\n" % production_data[11]
data += "<MEAN_THRESHOLD>%s</MEAN_THRESHOLD>\n" % production_data[12]
data += "<MEAN_ENC>%s</MEAN_ENC>\n" % production_data[13]
data += "<REGISTER_TEST>%s</REGISTER_TEST>\n" % production_data[14]
data += "<EC_ERRORS>%s</EC_ERRORS>\n" % production_data[15]
data += "<BC_ERRORS>%s</BC_ERRORS>\n" % production_data[16]
data += "<CRC_ERRORS>%s</CRC_ERRORS>\n" % production_data[17]
data += "<HIT_ERRORS>%s</HIT_ERRORS>\n" % production_data[18]
data += "<NOISY_CHANNELS>%s</NOISY_CHANNELS>\n" % production_data[19]
data += "<DEAD_CHANNELS>%s</DEAD_CHANNELS>\n" % production_data[20]
data += "<BIST>%s</BIST>\n" % production_data[21]
data += "<SCAN_CHAIN>%s</SCAN_CHAIN>\n" % production_data[22]
data += "<SLEEP_PWR_ANALOG>%s</SLEEP_PWR_ANALOG>\n" % production_data[23]
data += "<SLEEP_PWR_DIGITAL>%s</SLEEP_PWR_DIGITAL>\n" % production_data[24]
data += "<RUN_PWR_ANALOG>%s</RUN_PWR_ANALOG>\n" % production_data[25]
data += "<RUN_PWR_DIGITAL>%s</RUN_PWR_DIGITAL>\n" % production_data[26]
data += "</DATA>\n"
data += "</DATASET>\n"

print data


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
    if production_data[12]:
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
    if production_data[13]:
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