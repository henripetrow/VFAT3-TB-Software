import os
import sys
sys.path.append('../')
from DatabaseInterfaceBrowse import *


user = "Henri Petrow"
location = "HybridSA"
start_timestamp = "2016-07-18 13:55:06"
stop_timestamp = "2016-07-18 14:55:03"
run_number = 1
comment_description = "VFAT3 Production Data from Testing at CERN"
run_type = "VFAT3 Production Data"

kind_of_part = "GEM VFAT3 Hybrid"

#file_path = "../results/xml/"
file_path = "/home/hpetrow/cernbox/Data/production_data_xml_test/"

test_hybrids = ['Hybrid333', 'Hybrid3333', 'Hybrid33333', 'Hybrid3333333', 'Hybrid333333', 'Hybrid324234', 'Hybrid354',
                'Hybrid34543', 'Hybrid444444', 'Hybrid44444']


def generate_header(file_name, table_name, name):
    if not os.path.exists(os.path.dirname(file_name)):
        try:
            os.makedirs(os.path.dirname(file_name))
        except OSError as exc:  # Guard against race condition
            print "Unable to create directory"
    data = "<ROOT>\n"
    data += "<HEADER>\n"
    data += "<TYPE>\n"
    data += "<EXTENSION_TABLE_NAME>%s</EXTENSION_TABLE_NAME>\n" % table_name
    data += "<NAME> %s</NAME>\n" % name
    data += "</TYPE>\n"
    data += "<RUN>\n"
    data += "<RUN_TYPE>%s</RUN_TYPE>\n" % run_type
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


database = DatabaseInterfaceBrowse()
hybrid_list = database.list_hybrids()
print "Listing hybrids from the database."
temp_list = []
for h in hybrid_list:
    if h in test_hybrids:
        pass
    else:
        temp_list.append(int(h[6:]))
temp_list.sort()
hybrid_list = []
for k in temp_list:
    hybrid_name = "Hybrid%s" % k
    hybrid_list.append(hybrid_name)
    #print hybrid_name
print "Number of found hybrids:"
print len(hybrid_list)

print ""
print "Generating xml-files for the found hybrids."
adcs = ["ADC0", "ADC1"]
dac6bits = ["CFD_DAC_1", "CFD_DAC_2", "HYST_DAC", "PRE_I_BLCC", "PRE_I_BSF", "SD_I_BSF"]
dac8bits = ["ARM_DAC", "CAL_DAC", "PRE_VREF", "PRE_I_BIT", "SD_I_BDIFF", "SH_I_BDIFF", "SD_I_BFCAS", "SH_I_BFCAS", "ZCC_DAC"]
dac_table = []
show_data = [1, 1, 1, 1, 1, 1]


# Generation of the production summary table xml-file

filename = "%sVFAT3_Production_summary.xml" % file_path
table_name = "VFAT3_PRODUCTION_SUMMARY"
name = "VFAT3 Production Summary Data"
generate_header(filename, table_name, name)

for hybrid in hybrid_list:

    production_data = database.get_production_results(hybrid)

    # Start of dataset.
    data = "<DATASET>\n"
    data += "<COMMENT_DESCRIPTION>GEM VFAT3 Production Summary Data</COMMENT_DESCRIPTION>\n"
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n"
    data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
    data += "</PART>\n"
    data += "<DATA>\n"
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

    outF = open(filename, "a")
    outF.write(data)
    outF.close()

generate_footer(filename)


# Generation xml tables for the DAC scans

dac_list = dac6bits
dac_list.extend(dac8bits)

for dac in dac_list:
    filename = "%sVFAT3_%s.xml" % (file_path, dac)
    name = "VFAT3 %s Lookup Table" % dac
    table_name = "VFAT3_%s_LUT" % dac
    description = "GEM VFAT3 %s Lookup Table" % dac
    generate_header(filename, table_name, name)

    for hybrid in hybrid_list:
        production_data = database.get_production_results(hybrid)

        data = "<DATASET>\n"
        data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % description
        data += "<VERSION>1</VERSION>\n"
        data += "<PART>\n"
        data += "<KIND_OF_PART>%s</KIND_OF_PART>\n" % kind_of_part
        data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
        data += "</PART>\n"
        for adc in adcs:

            db_data = database.get_table_values(hybrid, "%s_%s" % (dac, adc))
            for i, dat in enumerate(db_data):
                data += "<DATA>\n"
                if dat:
                    data += "<ADC_NAME> %s </ADC_NAME>\n" % adc
                    data += "<DAC_SETTING> DAC%s </DAC_SETTING>\n" % i
                    data += "<ADC_VALUE> %s </ADC_VALUE>\n" % dat
                else:
                    data += "<ADC_NAME> %s </ADC_NAME >\n" % adc
                    data += "<DAC_SETTING> DAC%s </DAC_SETTING>\n" % i
                    data += "<ADC_VALUE> NULL </ADC_VALUE>\n"
                data += "</DATA>\n"
        data += "</DATASET>\n"
        outF = open(filename, "a")
        outF.write(data)
        outF.close()

    generate_footer(filename)
    print "Generated xml-file for: %s" % dac


# Thresholds

filename = "%sVFAT3_THRESHOLD.xml" % file_path
table_name = "VFAT3_THRESHOLD"
name = "VFAT3 Threshold Lookup Table"
description = "GEM VFAT3 Threshold Lookup Table"

generate_header(filename, table_name, name)

for hybrid in hybrid_list:
    production_data = database.get_production_results(hybrid)
    data = "<DATASET>\n"
    data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % description
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>%s</KIND_OF_PART>\n" % kind_of_part
    data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
    data += "</PART>\n"
    db_data = database.get_table_values(hybrid, "Threshold")
    for i, dat in enumerate(db_data):
        data += "<DATA>\n"
        if dat:
            data += "<CHANNEL> %s </CHANNEL>\n" % i
            data += "<THR_VALUE> %s </THR_VALUE>\n" % dat
        else:
            data += "<CHANNEL> %s </CHANNEL>\n" % i
            data += "<THR_VALUE> NULL </THR_VALUE>\n"
        data += "</DATA>\n"
    data += "</DATASET>\n"
    outF = open(filename, "a")
    outF.write(data)
    outF.close()
generate_footer(filename)
print "Generated xml-file for: Threshold"

# enc

filename = "%sVFAT3_ENC.xml" % file_path
name = "VFAT3 enc Lookup Table"
table_name = "VFAT3_ENC_LUT"
description = "GEM VFAT3 enc Lookup Table"

generate_header(filename, table_name, name)

for hybrid in hybrid_list:
    production_data = database.get_production_results(hybrid)
    data = "<DATASET>\n"
    data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % description
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>%s</KIND_OF_PART>\n" % kind_of_part
    data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
    data += "</PART>\n"
    db_data = database.get_table_values(hybrid, "enc")
    for i, dat in enumerate(db_data):
        data += "<DATA>\n"
        if dat:
            data += "<CHANNEL> %s </CHANNEL>" % i
            data += "<ENC_VALUE> %s </THR_VALUE>" % dat
        else:
            data += "<CHANNEL> %s </CHANNEL>" % i
            data += "<ENC_VALUE> NULL </THR_VALUE>"
        data += "</DATA>\n"
    data += "</DATASET>\n"
    outF = open(filename, "a")
    outF.write(data)
    outF.close()
generate_footer(filename)
print "Generated xml-file for: enc"


# for dac in dac_list:
#     filename = "%s%s_%s.xml" % (file_path, hybrid, dac)
#     table_name = "VFAT3_ENC"
#     name = "VFAT3 Production Summary Data"
#     generate_header(filename, table_name, name)
#
#     for hybrid in hybrid_list:
#         production_data = database.get_production_results(hybrid)
#         data = "<DATASET>\n"
#         data += "<COMMENT_DESCRIPTION>GEM VFAT3 Production Summary Data</COMMENT_DESCRIPTION>\n"
#         data += "<VERSION>1</VERSION>\n"
#         data += "<PART>\n"
#         data += "<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n"
#         data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
#         data += "</PART>\n"
#         for adc in adcs:
#             data += "<DATA>\n"
#             db_data = database.get_table_values(hybrid, "%s_%s" % (dac, adc))
#             for i, dat in enumerate(db_data):
#                 if dat:
#                     data += "< ADC_NAME > %s </ADC_NAME >" % adc
#                     data += "< DAC_SETTING > DAC%s </DAC_SETTING >" % i
#                     data += "< ADC_VALUE > %s </ADC_VALUE >" % dat
#                 else:
#                     data += "< ADC_NAME > %s </ADC_NAME >" % adc
#                     data += "< DAC_SETTING > DAC%s </DAC_SETTING >" % i
#                     data += "< ADC_VALUE > NULL </ADC_VALUE >"
#             data += "</DATA>\n"
#         data += "</DATASET>\n"
#     generate_footer(filename)


dac = "CAL_LUT"
filename = "%sVFAT3_%s.xml" % (file_path, dac)
name = "VFAT3 %s Lookup Table" % dac
table_name = "VFAT3_%s_LUT" % dac
description = "GEM VFAT3 %s Lookup Table" % dac
generate_header(filename, table_name, name)

for hybrid in hybrid_list:
    production_data = database.get_production_results(hybrid)
    data = "<DATASET>\n"
    data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % description
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>%s</KIND_OF_PART>\n" % kind_of_part
    data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
    data += "</PART>\n"
    for adc in adcs:
        data += "<DATA>\n"
        db_data = database.get_table_values(hybrid, "%s_%s" % (adc, dac))
        for i, dat in enumerate(db_data):
            if dat:
                data += "<ADC_NAME > %s </ADC_NAME>\n" % adc
                data += "<DAC_SETTING > DAC%s </DAC_SETTING>\n" % i
                data += "<ADC_VALUE > %s </ADC_VALUE>\n" % dat
            else:
                data += "<ADC_NAME > %s </ADC_NAME>\n" % adc
                data += "<DAC_SETTING > DAC%s </DAC_SETTING>\n" % i
                data += "<ADC_VALUE > NULL </ADC_VALUE>\n"
        data += "</DATA>\n"
    data += "</DATASET>\n"
    outF = open(filename, "a")
    outF.write(data)
    outF.close()
generate_footer(filename)
print "Generated xml-file for: %s" % dac


dac = "CAL_DAC_FC"
filename = "%sVFAT3_%s.xml" % (file_path, dac)
name = "VFAT3 %s Lookup Table" % dac
table_name = "VFAT3_%s_LUT" % dac
description = "GEM VFAT3 %s Lookup Table" % dac
generate_header(filename, table_name, name)

for hybrid in hybrid_list:
    production_data = database.get_production_results(hybrid)
    data = "<DATASET>\n"
    data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % description
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>%s</KIND_OF_PART>\n" % kind_of_part
    data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
    data += "</PART>\n"

    db_data = database.get_table_values(hybrid, "%s" % dac)
    for i, dat in enumerate(db_data):
        data += "<DATA>\n"
        if dat:
            data += "<DAC_SETTING > DAC%s </DAC_SETTING>\n" % i
            data += "<CHRG_VALUE > %s </CHRG_VALUE>\n" % dat
        else:
            data += "<DAC_SETTING > DAC%s </DAC_SETTING>\n" % i
            data += "<CHRG_VALUE > NULL </CHRG_VALUE>\n"
        data += "</DATA>\n"
    data += "</DATASET>\n"
    outF = open(filename, "a")
    outF.write(data)
    outF.close()
generate_footer(filename)
print "Generated xml-file for: %s" % dac


dac = "EXT_ADC_CAL_LUT"
filename = "%sVFAT3_%s.xml" % (file_path, dac)
name = "VFAT3 %s Lookup Table" % dac
table_name = "VFAT3_%s_LUT" % dac
description = "GEM VFAT3 %s Lookup Table" % dac
generate_header(filename, table_name, name)

for hybrid in hybrid_list:
    production_data = database.get_production_results(hybrid)
    data = "<DATASET>\n"
    data += "<COMMENT_DESCRIPTION>%s</COMMENT_DESCRIPTION>\n" % description
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>%s</KIND_OF_PART>\n" % kind_of_part
    data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
    data += "</PART>\n"
    db_data = database.get_table_values(hybrid, dac)
    for i, dat in enumerate(db_data):
        data += "<DATA>\n"
        if dat:
            data += "<DAC_SETTING > DAC%s </DAC_SETTING>\n" % i
            data += "<ADC_VALUE > %s </ADC_VALUE >" % dat
        else:
            data += "<DAC_SETTING > DAC%s </DAC_SETTING>\n" % i
            data += "<ADC_VALUE > NULL </ADC_VALUE>\n"
        data += "</DATA>\n"
    data += "</DATASET>\n"
    outF = open(filename, "a")
    outF.write(data)
    outF.close()
generate_footer(filename)
print "Generated xml-file for: %s" % dac
print ""
print "xml-file generation done."
