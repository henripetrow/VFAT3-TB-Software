import os
import time
import sys
import glob
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *


user = "Henri Petrow"
location = "Cern"
start_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
stop_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
comment_description = "VFAT3 Production Data from Testing at CERN"


nr_of_days = input("Nr. of days of database modifications to include:")

database = DatabaseInterfaceBrowse()

hybrid_list = database.list_hybrids(greater=6000)
#hybrid_list = database.list_hybrids_modified_in_days(int(nr_of_days))

print "Listing hybrids from the database."
for hybrid in hybrid_list:
    print hybrid
print "Number of found hybrids:"
print len(hybrid_list)


run_number = input("Give the run number:")

kind_of_part = "GEM VFAT3"

file_path = "../results/xml/"

if not os.path.exists(os.path.dirname(file_path)):
    try:
        os.makedirs(os.path.dirname(file_path))
    except OSError as exc:  # Guard against race condition
        print "Unable to create directory"
else:
    filelist = glob.glob('%s*.xml' % file_path)
    print "Removing previous xml files.."
    for file in filelist:
        try:
            os.remove(file)
        except:
            print "Error while removing file: %s" % file


def generate_header(file_name, table_name, name, run_type):
    if not os.path.exists(os.path.dirname(file_name)):
        try:
            os.makedirs(os.path.dirname(file_name))
        except OSError as exc:  # Guard against race condition
            print "Unable to create directory"
    data = "<ROOT>\n"
    data += "<HEADER>\n"
    data += "<TYPE>\n"
    data += "<EXTENSION_TABLE_NAME>%s</EXTENSION_TABLE_NAME>\n" % table_name
    data += "<NAME>%s</NAME>\n" % name
    data += "</TYPE>\n"
    data += "<RUN>\n"
    data += "<RUN_TYPE>VFAT3 Production %s Data</RUN_TYPE>\n" % run_type
    data += "<RUN_NUMBER>%s</RUN_NUMBER>\n" % run_number
    data += "<RUN_BEGIN_TIMESTAMP>%s</RUN_BEGIN_TIMESTAMP>\n" % start_timestamp
    data += "<RUN_END_TIMESTAMP>%s</RUN_END_TIMESTAMP>\n" % stop_timestamp
    data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % comment_description
    data += "<LOCATION>%s</LOCATION>\n" % location
    data += "<INITIATED_BY_USER>%s</INITIATED_BY_USER>\n" % user
    data += "</RUN>\n"
    data += "</HEADER>\n"
    outF = open(file_name, "w")
    outF.write(data)
    outF.close()


def generate_footer(file_name):
    data = "</ROOT>\n"
    outF = open(file_name, "a")
    outF.write(data)
    outF.close()





print "\n\nGenerating xml-files for the found hybrids."
adcs = ["ADC0", "ADC1"]
dac6bits = ["CFD_DAC_1", "CFD_DAC_2", "HYST_DAC", "PRE_I_BLCC", "PRE_I_BSF", "SD_I_BSF"]
dac8bits = ["ARM_DAC", "CAL_DAC", "PRE_VREF", "PRE_I_BIT", "SD_I_BDIFF", "SH_I_BDIFF", "SD_I_BFCAS", "SH_I_BFCAS", "ZCC_DAC"]
dac_table = []
show_data = [1, 1, 1, 1, 1, 1]


# Generate list file of hybrids.


filename = "%spre_LoadVFAT3s.xml" % file_path

data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
data += '<ROOT xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
data += '<PARTS>\n'
outF = open(filename, "w")
outF.write(data)
outF.close()

for hybrid in hybrid_list:
    production_data = database.get_production_results(hybrid)
    barcode_base = "30630001100017"
    nr_fill_zeroes = 5 - len(str(production_data[0]))
    barcode = barcode_base + "0" * nr_fill_zeroes + str(production_data[0])
    data = '<PART mode="auto">\n'
    data += '<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n'
    data += '<SERIAL_NUMBER>0x%x</SERIAL_NUMBER>\n<BARCODE>%s</BARCODE>\n' % (int(production_data[0]), barcode)
    data += '</PART>\n'
    outF = open(filename, "a")
    outF.write(data)
    outF.close()

data = '</PARTS>\n'
data += '</ROOT>\n'
outF = open(filename, "a")
outF.write(data)
outF.close()


# Generation of the production summary table xml-file

filename = "%sVFAT3_Production_summary.xml" % file_path
table_name = "VFAT3_PRODUCTION_SUMMARY"
name = "VFAT3 Production Summary Data"
run_type = "Summary"
generate_header(filename, table_name, name, run_type)

for hybrid in hybrid_list:

    production_data_int = database.get_production_results(hybrid)
    production_data = []
    for item in production_data_int:
        if item is None or item == "None":
            production_data.append("")
        else:
            production_data.append(item)

    barcode_base = "30630001100017"
    nr_fill_zeroes = 5 - len(str(production_data[0]))
    barcode = barcode_base + "0" * nr_fill_zeroes + str(production_data[0])


    # Start of DATA_SET.
    data = "<DATA_SET>\n"
    data += "<COMMENT_DESCRIPTION>GEM VFAT3 Production Summary Data</COMMENT_DESCRIPTION>\n"
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n"
    data += "<BARCODE>%s</BARCODE>\n" % barcode
    data += "</PART>\n"
    data += "<DATA>\n"
    data += "<HW_ID_VERSION>%s</HW_ID_VERSION>\n" % production_data[1]
    data += "<BUFFER_OFFSET>%s</BUFFER_OFFSET>\n" % production_data[2]
    data += "<VREF_ADC>%s</VREF_ADC>\n" % production_data[3]
    data += "<V_BGR>%s</V_BGR>\n" % production_data[4]
    data += "<ADC0M>%s</ADC0M>\n" % production_data[5]
    data += "<ADC0B>%s</ADC0B>\n" % production_data[6]
    data += "<ADC1M>%s</ADC1M>\n" % production_data[7]
    data += "<ADC1B>%s</ADC1B>\n" % production_data[8]
    data += "<CAL_DACM>%s</CAL_DACM>\n" % production_data[9]
    data += "<CAL_DACB>%s</CAL_DACB>\n" % production_data[10]
    data += "<IREF>%s</IREF>\n" % production_data[11]
    data += "<MEAN_THRSHLD>%s</MEAN_THRSHLD>\n" % production_data[12]
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
    data += "<LOCATION>%s</LOCATION>\n" % production_data[27]
    data += "<TEMPERATURE>%s</TEMPERATURE>\n" % production_data[28]
    data += "<STATE>%s</STATE>\n" % production_data[29]
    data += "<TEMPERATURE_K2>%s</TEMPERATURE_K2>\n" % production_data[33]
    data += "</DATA>\n"
    data += "</DATA_SET>\n"

    outF = open(filename, "a")
    outF.write(data)
    outF.close()

generate_footer(filename)
print "Generated xml-file for: %s" % name


# Generation xml tables for the DAC scans

dac_list = dac6bits

for dac in dac_list:
    file_nr = 0
    k = 0
    for hybrid in hybrid_list:
        if k == 0:
            file_nr = file_nr + 1
            filename = "%sVFAT3_%s_%s.xml" % (file_path, dac, file_nr)
            print "Generating file: %s" % filename
            print "From %s" % hybrid
            name = "VFAT3 %s DAC Lookup Table" % dac
            # Exceptions for GEM database naming
            if dac == "HYST_DAC":
                name = "VFAT3 HYST DAC Lookup Table"
            if dac == "ZCC_DAC":
                name = "VFAT3 ZCC DAC Lookup Table"
            if dac == "CFD_DAC_1":
                name = "VFAT3 CFD DAC_1 Lookup Table"
            if dac == "CFD_DAC_2":
                name = "VFAT3 CFD DAC_2 Lookup Table"
            if dac == "ARM_DAC":
                name = "VFAT3 ARM DAC Lookup Table"
            if dac == "CAL_DAC":
                name = "VFAT3 Calib Pulse DAC Lookup Table"
            table_name = "VFAT3_%s" % dac
            description = "GEM VFAT3 %s Lookup Table" % dac
            run_type = "%s_LUT" % dac
            generate_header(filename, table_name, name, run_type)
            data = "<DATA_SET>\n"
        else:
            data += "<DATA_SET>\n"
        k = k + 1

        data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % description
        data += "<VERSION>1</VERSION>\n"
        data += "<PART>\n"
        data += "<KIND_OF_PART>%s</KIND_OF_PART>\n" % kind_of_part
        data += "<BARCODE>%s</BARCODE>\n" % hybrid
        data += "</PART>\n"
        for adc in adcs:
            db_data = database.get_table_values(hybrid, "%s_%s" % (dac, adc))
            for i, dat in enumerate(db_data):
                data += "<DATA>\n"
                if dat:
                    data += "<ADC_NAME>%s</ADC_NAME>\n" % adc
                    data += "<DAC_SETTING>DAC%s</DAC_SETTING>\n" % i
                    data += "<ADC_VALUE>%s</ADC_VALUE>\n" % dat
                else:
                    data += "<ADC_NAME>%s</ADC_NAME>\n" % adc
                    data += "<DAC_SETTING>DAC%s</DAC_SETTING>\n" % i
                    data += "<ADC_VALUE></ADC_VALUE>\n"
                data += "</DATA>\n"
        data += "</DATA_SET>\n"
        if k == 120:
            outF = open(filename, "a")
            outF.write(data)
            outF.close()
            generate_footer(filename)
            print "To %s" % hybrid
            k = 0
    if k != 0:
        outF = open(filename, "a")
        outF.write(data)
        outF.close()
        generate_footer(filename)
        print "To %s" % hybrid
        k = 0
    print "Generated xml-file for: %s" % dac

dac_list = dac8bits

for dac in dac_list:
    file_nr = 0
    k = 0
    for hybrid in hybrid_list:
        if k == 0:
            file_nr = file_nr + 1
            filename = "%sVFAT3_%s_%s.xml" % (file_path, dac, file_nr)
            print "Generating file: %s" % filename
            print "From %s" % hybrid
            name = "VFAT3 %s DAC Lookup Table" % dac
            # Exceptions for GEM database naming
            if dac == "HYST_DAC":
                name = "VFAT3 HYST DAC Lookup Table"
            if dac == "ZCC_DAC":
                name = "VFAT3 ZCC DAC Lookup Table"
            if dac == "CFD_DAC_1":
                name = "VFAT3 CFD DAC_1 Lookup Table"
            if dac == "CFD_DAC_2":
                name = "VFAT3 CFD DAC_2 Lookup Table"
            if dac == "ARM_DAC":
                name = "VFAT3 ARM DAC Lookup Table"
            if dac == "CAL_DAC":
                name = "VFAT3 Calib Pulse DAC Lookup Table"
            table_name = "VFAT3_%s" % dac
            description = "GEM VFAT3 %s Lookup Table" % dac
            run_type = "%s_LUT" % dac
            generate_header(filename, table_name, name, run_type)
            data = "<DATA_SET>\n"
        else:
            data += "<DATA_SET>\n"
        k = k + 1

        data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % description
        data += "<VERSION>1</VERSION>\n"
        data += "<PART>\n"
        data += "<KIND_OF_PART>%s</KIND_OF_PART>\n" % kind_of_part
        data += "<BARCODE>%s</BARCODE>\n" % hybrid
        data += "</PART>\n"
        for adc in adcs:
            db_data = database.get_table_values(hybrid, "%s_%s" % (dac, adc))
            for i, dat in enumerate(db_data):
                data += "<DATA>\n"
                if dat:
                    data += "<ADC_NAME>%s</ADC_NAME>\n" % adc
                    data += "<DAC_SETTING>DAC%s</DAC_SETTING>\n" % i
                    data += "<ADC_VALUE>%s</ADC_VALUE>\n" % dat
                else:
                    data += "<ADC_NAME>%s</ADC_NAME>\n" % adc
                    data += "<DAC_SETTING>DAC%s</DAC_SETTING>\n" % i
                    data += "<ADC_VALUE></ADC_VALUE>\n"
                data += "</DATA>\n"
        data += "</DATA_SET>\n"
        if k == 25:
            outF = open(filename, "a")
            outF.write(data)
            outF.close()
            generate_footer(filename)
            print "To %s" % hybrid
            k = 0
    if k != 0:
        outF = open(filename, "a")
        outF.write(data)
        outF.close()
        generate_footer(filename)
        print "To %s" % hybrid
        k = 0
    print "Generated xml-file for: %s" % dac


# Thresholds

file_nr = 0
k = 0
for hybrid in hybrid_list:
    if k == 0:
        file_nr = file_nr + 1
        filename = "%sVFAT3_THRESHOLD_%s.xml" % (file_path, file_nr)
        table_name = "VFAT3_THRESHOLD"
        name = "VFAT3 Channel Threshold Values"
        description = "GEM VFAT3 Threshold Lookup Table"
        run_type = "THRESHOLD"
        generate_header(filename, table_name, name, run_type)

    data = "<DATA_SET>\n"
    k = k + 1

    data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % description
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>%s</KIND_OF_PART>\n" % kind_of_part
    data += "<BARCODE>%s</BARCODE>\n" % hybrid
    data += "</PART>\n"
    db_data = database.get_table_values(hybrid, "Threshold")
    for i, dat in enumerate(db_data):
        data += "<DATA>\n"
        if dat:
            data += "<CHANNEL>%s</CHANNEL>\n" % i
            data += "<THR_VALUE>%s</THR_VALUE>\n" % dat
        else:
            data += "<CHANNEL>%s</CHANNEL>\n" % i
            data += "<THR_VALUE></THR_VALUE>\n"
        data += "</DATA>\n"
    data += "</DATA_SET>\n"
    outF = open(filename, "a")
    outF.write(data)
    outF.close()
    if k == 150:
        generate_footer(filename)
        k = 0
if k != 0:
    generate_footer(filename)
print "Generated xml-file for: Threshold"

# enc
file_nr = 0
k = 0
for hybrid in hybrid_list:
    if k == 0:
        file_nr = file_nr + 1
        filename = "%sVFAT3_ENC_%s.xml" % (file_path, file_nr)
        name = "VFAT3 Channel Noise Values"
        table_name = "VFAT3_ENC"
        description = "GEM VFAT3 enc Lookup Table"
        run_type = "Channel Noise"
        generate_header(filename, table_name, name, run_type)
    k = k + 1
    data = "<DATA_SET>\n"
    data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % description
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>%s</KIND_OF_PART>\n" % kind_of_part
    data += "<BARCODE>%s</BARCODE>\n" % hybrid
    data += "</PART>\n"
    db_data = database.get_table_values(hybrid, "enc")
    for i, dat in enumerate(db_data):
        data += "<DATA>\n"
        if dat:
            data += "<CHANNEL>%s</CHANNEL>\n" % i
            data += "<ENC_VALUE>%s</ENC_VALUE>\n" % dat
        else:
            data += "<CHANNEL>%s</CHANNEL>\n" % i
            data += "<ENC_VALUE></ENC_VALUE>\n"
        data += "</DATA>\n"
    data += "</DATA_SET>\n"
    outF = open(filename, "a")
    outF.write(data)
    outF.close()
    if k == 150:
        generate_footer(filename)
        k = 0
if k != 0:
    generate_footer(filename)
print "Generated xml-file for: enc"

file_nr = 0
k = 0
for hybrid in hybrid_list:
    if k == 0:
        file_nr = file_nr + 1
        dac = "CAL_LUT"
        filename = "%sVFAT3_%s_%s.xml" % (file_path, dac, file_nr)
        name = "VFAT3 ADC Calib Lookup Table"
        table_name = "VFAT3_%s" % dac
        description = "GEM VFAT3 %s Lookup Table" % dac
        run_type = "CAL_LUT"
        generate_header(filename, table_name, name, run_type)
    k = k + 1

    data = "<DATA_SET>\n"
    data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % description
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>%s</KIND_OF_PART>\n" % kind_of_part
    data += "<BARCODE>%s</BARCODE>\n" % hybrid
    data += "</PART>\n"
    for adc in adcs:
        db_data = database.get_table_values(hybrid, "%s_%s" % (adc, dac))
        for i, dat in enumerate(db_data):
            data += "<DATA>\n"
            if dat:
                data += "<ADC_NAME>%s</ADC_NAME>\n" % adc
                data += "<DAC_SETTING>DAC%s</DAC_SETTING>\n" % i
                data += "<ADC_VALUE>%s</ADC_VALUE>\n" % dat
            else:
                data += "<ADC_NAME>%s</ADC_NAME>\n" % adc
                data += "<DAC_SETTING>DAC%s</DAC_SETTING>\n" % i
                data += "<ADC_VALUE></ADC_VALUE>\n"
            data += "</DATA>\n"
    data += "</DATA_SET>\n"
    outF = open(filename, "a")
    outF.write(data)
    outF.close()
    if k == 25:
        generate_footer(filename)
        k = 0
if k != 0:
    generate_footer(filename)
print "Generated xml-file for: %s" % dac



file_nr = 0
k = 0
for hybrid in hybrid_list:
    if k == 0:
        file_nr = file_nr + 1
        dac = "CAL_DAC_FC"
        filename = "%sVFAT3_%s_%s.xml" % (file_path, dac, file_nr)
        name = "VFAT3 Calib DAC Charge Lookup Table"
        table_name = "VFAT3_%s" % dac
        description = "GEM VFAT3 %s Lookup Table" % dac
        run_type = "%s_LUT" % dac
        generate_header(filename, table_name, name, run_type)
    k = k + 1
    data = "<DATA_SET>\n"
    data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % description
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>%s</KIND_OF_PART>\n" % kind_of_part
    data += "<BARCODE>%s</BARCODE>\n" % hybrid
    data += "</PART>\n"

    db_data = database.get_table_values(hybrid, "%s" % dac)
    for i, dat in enumerate(db_data):
        data += "<DATA>\n"
        if dat:
            data += "<DAC_SETTING>DAC%s</DAC_SETTING>\n" % i
            data += "<CHRG_VALUE>%s</CHRG_VALUE>\n" % dat
        else:
            data += "<DAC_SETTING>DAC%s</DAC_SETTING>\n" % i
            data += "<CHRG_VALUE></CHRG_VALUE>\n"
        data += "</DATA>\n"
    data += "</DATA_SET>\n"
    outF = open(filename, "a")
    outF.write(data)
    outF.close()
    if k == 80:
        generate_footer(filename)
        k = 0
if k != 0:
    generate_footer(filename)
print "Generated xml-file for: %s" % dac

file_nr = 0
k = 0
for hybrid in hybrid_list:
    if k == 0:
        file_nr = file_nr + 1
        dac = "EXT_ADC_CAL_LUT"
        filename = "%sVFAT3_%s_%s.xml" % (file_path, dac, file_nr)
        name = "VFAT3 Ext ADC Calib Lookup Table"
        table_name = "VFAT3_%s" % dac
        description = "GEM VFAT3 %s Lookup Table" % dac
        run_type = "%s" % dac
        generate_header(filename, table_name, name, run_type)
    k = k + 1
    data = "<DATA_SET>\n"
    data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % description
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>%s</KIND_OF_PART>\n" % kind_of_part
    data += "<BARCODE>%s</BARCODE>\n" % hybrid
    data += "</PART>\n"
    db_data = database.get_table_values(hybrid, dac)
    for i, dat in enumerate(db_data):
        data += "<DATA>\n"
        if dat:
            data += "<DAC_SETTING>DAC%s</DAC_SETTING>\n" % i
            data += "<ADC_VALUE>%s</ADC_VALUE>" % dat
        else:
            data += "<DAC_SETTING>DAC%s</DAC_SETTING>\n" % i
            data += "<ADC_VALUE></ADC_VALUE>\n"
        data += "</DATA>\n"
    data += "</DATA_SET>\n"
    outF = open(filename, "a")
    outF.write(data)
    outF.close()
    if k == 80:
        generate_footer(filename)
        k = 0
if k != 0:
    generate_footer(filename)
print "Generated xml-file for: %s" % dac
print ""
print "xml-file generation done."

