#!/bin/env python

import os
import time
import sys
import glob
import subprocess
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *
from DatabaseInterface import *


user = "Henri Petrow"
location = "Cern"
start_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
stop_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
comment_description = "VFAT3 Production Data from Testing at CERN"

with open('./gem_db_info.dat', 'r') as f:
    line = f.readline()
    info = line.split()
    gem_user = info[0]
    gem_passwd = info[1]

nr_of_days = 1

database = DatabaseInterfaceBrowse()
hybrid_list = database.list_hybrids_modified_in_days(int(nr_of_days))

print "Listing hybrids from the database."
for hybrid in hybrid_list:
    print hybrid
print "Number of found hybrids:"
print len(hybrid_list)
if len(hybrid_list) > 0:
    print "Fetching RUN_NUMBER"
    run_number = database.get_run_number()
    print run_number

    database.set_run_number(run_number + 1)

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
        data = '<PART mode="auto">\n'
        data += '<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n'
        data += '<SERIAL_NUMBER>0x%x</SERIAL_NUMBER>\n<BARCODE>%i</BARCODE>\n' % (int(production_data[0]), int(production_data[0]))
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
        # Start of DATA_SET.
        data = "<DATA_SET>\n"
        data += "<COMMENT_DESCRIPTION>GEM VFAT3 Production Summary Data</COMMENT_DESCRIPTION>\n"
        data += "<VERSION>1</VERSION>\n"
        data += "<PART>\n"
        data += "<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n"
        data += "<BARCODE>%s</BARCODE>\n" % production_data[0]
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

    print "xml-file generation done."

    print "Sending xml-files to the server."
    localfile1 = "../results/xml/pre_LoadVFAT3s.xml"
    localfile2 = "../results/xml/VFAT3_Production_summary.xml"
    remotehost = "gem-machine-a"
    remotefile = "/home/dbspool/spool/gem/int2r/"
    #remotefile = "~/testaus/"
    print subprocess.Popen(['scp', '%s' % localfile1, '%s:%s' % (remotehost, remotefile)], stdout=subprocess.PIPE).communicate()
    time.sleep(30)
    print subprocess.Popen(['scp', '%s' % localfile2, '%s:%s' % (remotehost, remotefile)], stdout=subprocess.PIPE).communicate()
    time.sleep(30)

    #os.system('python checkVFATs.py INT2R %s %s ../results/xml/pre_LoadVFAT3s.xml' % (gem_user, gem_passwd))

else:
    print "No hybrids found."




