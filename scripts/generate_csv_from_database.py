import os
import sys
import time
sys.path.append('../')
from DatabaseInterfaceBrowse import *
from test_system_functions import read_database_info


timestamp = time.strftime("%Y%m%d%H%M")
folder = "../results/production_files/csv_%s/" % timestamp

if not os.path.exists(os.path.dirname(folder)):
    try:
        os.makedirs(os.path.dirname(folder))
    except OSError as exc:  # Guard against race condition
        print "Unable to create directory"


database = DatabaseInterfaceBrowse()
hybrid_list = database.list_hybrids(greater=6000)
print "Listing hybrids from the database."
print "Number of found hybrids:"
print len(hybrid_list)


file = "%sproduction.csv" % folder

column_names = database.get_production_column_names()
text = column_names[0]
for name in column_names[1:]:
    text += ",%s" % name
text += "\n"
outF = open(file, "w")
outF.write(text)
outF.close()

print ""
print "Generating csv-files for the found hybrids."
# Generation of the production summary table csv-file


for hybrid in hybrid_list:
    production_data = database.get_production_results(hybrid)
    text = "%s" % production_data[0]
    for name in production_data[1:]:
        text += ",%s" % name
    text += "\n"
    outF = open(file, "a")
    outF.write(text)
    outF.close()
print "Generated csv-file for: Production"


tables = ['Threshold', 'enc', "CAL_DAC_FC", "EXT_ADC_CAL_LUT"]

for item in tables:
    file = "%s%s.csv" % (folder, item)
    text = "Data\n"
    outF = open(file, "w")
    outF.write(text)
    outF.close()

    for hybrid in hybrid_list:
        text = "%s" % hybrid
        db_data = database.get_table_values(hybrid, item)
        for dat in db_data:
            text += ",%s" % dat
        text += "\n"
        outF = open(file, "a")
        outF.write(text)
        outF.close()

    print "Generated csv-file for: %s" % item


tables = ['channel_category']

for item in tables:
    file = "%s%s.csv" % (folder, item)
    text = "Data\n"
    outF = open(file, "w")
    outF.write(text)
    outF.close()

    for hybrid in hybrid_list:
        text = "%s" % hybrid
        db_data = database.get_table_values(hybrid, item, allow_non_existing_hybrids=1)
        if db_data:
            for dat in db_data:
                text += ",%s" % dat
            text += "\n"
            outF = open(file, "a")
            outF.write(text)
            outF.close()

    print "Generated csv-file for: %s" % item


# Generation xml tables for the DAC scans
adcs = ["ADC0", "ADC1"]
dac6bits = ["CFD_DAC_1", "CFD_DAC_2", "HYST_DAC", "PRE_I_BLCC", "PRE_I_BSF", "SD_I_BSF"]
dac8bits = ["ARM_DAC", "CAL_DAC", "PRE_VREF", "PRE_I_BIT", "SD_I_BDIFF", "SH_I_BDIFF", "SD_I_BFCAS", "SH_I_BFCAS", "ZCC_DAC"]
dac_list = dac6bits
dac_list.extend(dac8bits)

for dac in dac_list:
    for adc in adcs:
        file = "%s%s_%s.csv" % (folder, dac, adc)
        text = "Data\n"
        outF = open(file, "w")
        outF.write(text)
        outF.close()
        for hybrid in hybrid_list:
            text = "%s" % hybrid
            db_data = database.get_table_values(hybrid, "%s_%s" % (dac, adc))
            for dat in db_data:
                text += ",%s" % dat
            text += "\n"
            outF = open(file, "a")
            outF.write(text)
            outF.close()
    print "Generated csv-file for: %s" % dac


dac = "CAL_LUT"


for adc in adcs:
    file = "%s%s_%s.csv" % (folder, adc, dac)
    text = "Data\n"
    outF = open(file, "w")
    outF.write(text)
    outF.close()
    for hybrid in hybrid_list:
        text = "%s" % hybrid
        db_data = database.get_table_values(hybrid, "%s_%s" % (adc, dac))
        for dat in db_data:
            text += ",%s" % dat
        text += "\n"
        outF = open(file, "a")
        outF.write(text)
        outF.close()

print "Generated csv-file for: %s" % dac
print "Results saved to the folder: %s " % folder



