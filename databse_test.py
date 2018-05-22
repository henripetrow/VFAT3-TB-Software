from DatabaseInterfaceBrowse import *
import os

user = "Henri Petrow"

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
show_data = [1, 1, 1, 1, 1, 1]

production_data = database.get_production_results(hybrid)


filename = "./results/%s_PRODUCTION_SUMMARY.xml" % hybrid
if not os.path.exists(os.path.dirname(filename)):
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exc:  # Guard against race condition
        print "Unable to create directory"


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
data += "<INITIATED_BY_USER>%s</INITIATED_BY_USER>\n" % user
data += "</RUN>\n"
data += "</HEADER>\n"

# Start of dataset.
data += "<DATASET>\n"
data += "<COMMENT_DESCRIPTION>GEM VFAT3 Production Summary Data</COMMENT_DESCRIPTION>\n"
data += "<VERSION>1</VERSION>\n"
data += "<PART>\n"
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
data += "</ROOT>\n"

outF = open(filename, "w")
outF.write(data)
outF.close()


dac_list = dac6bits
dac_list.extend(dac8bits)


if show_data[0]:
    for dac in dac_list:
        filename = "./results/%s_%s.xml" % (hybrid, dac)
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                print "Unable to create directory"
        data = "<ROOT>\n"
        data += "<HEADER>\n"
        data += "<TYPE>\n"
        data += "<EXTENSION_TABLE_NAME>VFAT3_%s</EXTENSION_TABLE_NAME>\n" % dac
        data += "<NAME>VFAT3 Production Summary Data</NAME>\n"
        data += "</TYPE>\n"
        data += "<RUN>\n"
        data += "<RUN_TYPE>VFAT3 Production Data</RUN_TYPE>\n"
        data += "<RUN_NUMBER>1</RUN_NUMBER>\n"
        data += "<RUN_BEGIN_TIMESTAMP>2016-07-18 13:55:06</RUN_BEGIN_TIMESTAMP>\n"
        data += "<RUN_END_TIMESTAMP>2016-07-18 14:55:03</RUN_END_TIMESTAMP>\n"
        data += "<COMMENT_DESCRIPTION>VFAT3 Production Data from Testing at CERNV</COMMENT_DESCRIPTION>\n"
        data += "<LOCATION>TIF</LOCATION>\n"
        data += "<INITIATED_BY_USER>%s</INITIATED_BY_USER>\n" % user
        data += "</RUN>\n"
        data += "</HEADER>\n"
        data += "<DATASET>\n"
        data += "<COMMENT_DESCRIPTION>GEM VFAT3 Production Summary Data</COMMENT_DESCRIPTION>\n"
        data += "<VERSION>1</VERSION>\n"
        data += "<PART>\n"
        data += "<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n"
        data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
        data += "</PART>\n"
        for adc in adcs:
            data += "<DATA>\n"
            db_data = database.get_table_values(hybrid, "%s_%s" % (dac, adc))
            for i, dat in enumerate(db_data):
                if dat:
                    data += "< ADC_NAME > %s </ADC_NAME >" % adc
                    data += "< DAC_SETTING > DAC%s </DAC_SETTING >" % i
                    data += "< ADC_VALUE > %s </ADC_VALUE >" % dat
                else:
                    data += "< ADC_NAME > %s </ADC_NAME >" % adc
                    data += "< DAC_SETTING > DAC%s </DAC_SETTING >" % i
                    data += "< ADC_VALUE > NULL </ADC_VALUE >"
            data += "</DATA>\n"
        data += "</DATASET>\n"
        data += "</ROOT>\n"
        outF = open(filename, "w")
        outF.write(data)
        outF.close()


# Thresholds
if show_data[1]:
    filename = "./results/%s_THRESHOLD.xml" % hybrid
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            print "Unable to create directory"
    data = "<ROOT>\n"
    data += "<HEADER>\n"
    data += "<TYPE>\n"
    data += "<EXTENSION_TABLE_NAME>VFAT3_THRESHOLD</EXTENSION_TABLE_NAME>\n"
    data += "<NAME>VFAT3 Production Summary Data</NAME>\n"
    data += "</TYPE>\n"
    data += "<RUN>\n"
    data += "<RUN_TYPE>VFAT3 Production Data</RUN_TYPE>\n"
    data += "<RUN_NUMBER>1</RUN_NUMBER>\n"
    data += "<RUN_BEGIN_TIMESTAMP>2016-07-18 13:55:06</RUN_BEGIN_TIMESTAMP>\n"
    data += "<RUN_END_TIMESTAMP>2016-07-18 14:55:03</RUN_END_TIMESTAMP>\n"
    data += "<COMMENT_DESCRIPTION>VFAT3 Production Data from Testing at CERNV</COMMENT_DESCRIPTION>\n"
    data += "<LOCATION>TIF</LOCATION>\n"
    data += "<INITIATED_BY_USER>%s</INITIATED_BY_USER>\n" % user
    data += "</RUN>\n"
    data += "</HEADER>\n"
    data += "<DATASET>\n"
    data += "<COMMENT_DESCRIPTION>GEM VFAT3 Production Summary Data</COMMENT_DESCRIPTION>\n"
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n"
    data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
    data += "</PART>\n"
    db_data = database.get_table_values(hybrid, "Threshold")
    for i, dat in enumerate(db_data):
        if dat:
            data += "<CHANNEL> %s </CHANNEL>" % i
            data += "<THR_VALUE> %s </THR_VALUE>" % dat
        else:
            data += "<CHANNEL> %s </CHANNEL>" % i
            data += "<THR_VALUE> NULL </THR_VALUE>"
    data += "</DATA>\n"
    data += "</DATASET>\n"
    data += "</ROOT>\n"
    outF = open(filename, "w")
    outF.write(data)
    outF.close()

# enc
if show_data[2]:
    filename = "./results/%s_ENC.xml" % hybrid
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            print "Unable to create directory"
    data = "<ROOT>\n"
    data += "<HEADER>\n"
    data += "<TYPE>\n"
    data += "<EXTENSION_TABLE_NAME>VFAT3_ENC</EXTENSION_TABLE_NAME>\n"
    data += "<NAME>VFAT3 Production Summary Data</NAME>\n"
    data += "</TYPE>\n"
    data += "<RUN>\n"
    data += "<RUN_TYPE>VFAT3 Production Data</RUN_TYPE>\n"
    data += "<RUN_NUMBER>1</RUN_NUMBER>\n"
    data += "<RUN_BEGIN_TIMESTAMP>2016-07-18 13:55:06</RUN_BEGIN_TIMESTAMP>\n"
    data += "<RUN_END_TIMESTAMP>2016-07-18 14:55:03</RUN_END_TIMESTAMP>\n"
    data += "<COMMENT_DESCRIPTION>VFAT3 Production Data from Testing at CERNV</COMMENT_DESCRIPTION>\n"
    data += "<LOCATION>TIF</LOCATION>\n"
    data += "<INITIATED_BY_USER>%s</INITIATED_BY_USER>\n" % user
    data += "</RUN>\n"
    data += "</HEADER>\n"
    data += "<DATASET>\n"
    data += "<COMMENT_DESCRIPTION>GEM VFAT3 Production Summary Data</COMMENT_DESCRIPTION>\n"
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n"
    data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
    data += "</PART>\n"
    db_data = database.get_table_values(hybrid, "enc")
    for i, dat in enumerate(db_data):
        if dat:
            data += "<CHANNEL> %s </CHANNEL>" % i
            data += "<ENC_VALUE> %s </THR_VALUE>" % dat
        else:
            data += "<CHANNEL> %s </CHANNEL>" % i
            data += "<ENC_VALUE> NULL </THR_VALUE>"
    data += "</DATA>\n"
    data += "</DATASET>\n"
    data += "</ROOT>\n"
    outF = open(filename, "w")
    outF.write(data)
    outF.close()
    if show_data[0]:
        for dac in dac_list:
            filename = "./results/%s_%s.xml" % (hybrid, dac)
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc:  # Guard against race condition
                    print "Unable to create directory"
            data = "<ROOT>\n"
            data += "<HEADER>\n"
            data += "<TYPE>\n"
            data += "<EXTENSION_TABLE_NAME>VFAT3_%s</EXTENSION_TABLE_NAME>\n" % dac
            data += "<NAME>VFAT3 Production Summary Data</NAME>\n"
            data += "</TYPE>\n"
            data += "<RUN>\n"
            data += "<RUN_TYPE>VFAT3 Production Data</RUN_TYPE>\n"
            data += "<RUN_NUMBER>1</RUN_NUMBER>\n"
            data += "<RUN_BEGIN_TIMESTAMP>2016-07-18 13:55:06</RUN_BEGIN_TIMESTAMP>\n"
            data += "<RUN_END_TIMESTAMP>2016-07-18 14:55:03</RUN_END_TIMESTAMP>\n"
            data += "<COMMENT_DESCRIPTION>VFAT3 Production Data from Testing at CERNV</COMMENT_DESCRIPTION>\n"
            data += "<LOCATION>TIF</LOCATION>\n"
            data += "<INITIATED_BY_USER>%s</INITIATED_BY_USER>\n" % user
            data += "</RUN>\n"
            data += "</HEADER>\n"
            data += "<DATASET>\n"
            data += "<COMMENT_DESCRIPTION>GEM VFAT3 Production Summary Data</COMMENT_DESCRIPTION>\n"
            data += "<VERSION>1</VERSION>\n"
            data += "<PART>\n"
            data += "<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n"
            data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
            data += "</PART>\n"
            for adc in adcs:
                data += "<DATA>\n"
                db_data = database.get_table_values(hybrid, "%s_%s" % (dac, adc))
                for i, dat in enumerate(db_data):
                    if dat:
                        data += "< ADC_NAME > %s </ADC_NAME >" % adc
                        data += "< DAC_SETTING > DAC%s </DAC_SETTING >" % i
                        data += "< ADC_VALUE > %s </ADC_VALUE >" % dat
                    else:
                        data += "< ADC_NAME > %s </ADC_NAME >" % adc
                        data += "< DAC_SETTING > DAC%s </DAC_SETTING >" % i
                        data += "< ADC_VALUE > NULL </ADC_VALUE >"
                data += "</DATA>\n"
            data += "</DATASET>\n"
            data += "</ROOT>\n"
            outF = open(filename, "w")
            outF.write(data)
            outF.close()


if show_data[3]:
    dac = "CAL_LUT"
    filename = "./results/%s_%s.xml" % (hybrid, dac)
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            print "Unable to create directory"
    data = "<ROOT>\n"
    data += "<HEADER>\n"
    data += "<TYPE>\n"
    data += "<EXTENSION_TABLE_NAME>VFAT3_%s</EXTENSION_TABLE_NAME>\n" % dac
    data += "<NAME>VFAT3 Production Summary Data</NAME>\n"
    data += "</TYPE>\n"
    data += "<RUN>\n"
    data += "<RUN_TYPE>VFAT3 Production Data</RUN_TYPE>\n"
    data += "<RUN_NUMBER>1</RUN_NUMBER>\n"
    data += "<RUN_BEGIN_TIMESTAMP>2016-07-18 13:55:06</RUN_BEGIN_TIMESTAMP>\n"
    data += "<RUN_END_TIMESTAMP>2016-07-18 14:55:03</RUN_END_TIMESTAMP>\n"
    data += "<COMMENT_DESCRIPTION>VFAT3 Production Data from Testing at CERNV</COMMENT_DESCRIPTION>\n"
    data += "<LOCATION>TIF</LOCATION>\n"
    data += "<INITIATED_BY_USER>%s</INITIATED_BY_USER>\n" % user
    data += "</RUN>\n"
    data += "</HEADER>\n"
    data += "<DATASET>\n"
    data += "<COMMENT_DESCRIPTION>GEM VFAT3 Production Summary Data</COMMENT_DESCRIPTION>\n"
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n"
    data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
    data += "</PART>\n"
    for adc in adcs:
        data += "<DATA>\n"
        db_data = database.get_table_values(hybrid, "%s_%s" % (adc, dac))
        for i, dat in enumerate(db_data):
            if dat:
                data += "< ADC_NAME > %s </ADC_NAME >" % adc
                data += "< DAC_SETTING > DAC%s </DAC_SETTING >" % i
                data += "< ADC_VALUE > %s </ADC_VALUE >" % dat
            else:
                data += "< ADC_NAME > %s </ADC_NAME >" % adc
                data += "< DAC_SETTING > DAC%s </DAC_SETTING >" % i
                data += "< ADC_VALUE > NULL </ADC_VALUE >"
        data += "</DATA>\n"
    data += "</DATASET>\n"
    data += "</ROOT>\n"
    outF = open(filename, "w")
    outF.write(data)
    outF.close()


if show_data[4]:
    dac = "CAL_DAC_FC"
    filename = "./results/%s_%s.xml" % (hybrid, dac)
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            print "Unable to create directory"
    data = "<ROOT>\n"
    data += "<HEADER>\n"
    data += "<TYPE>\n"
    data += "<EXTENSION_TABLE_NAME>VFAT3_%s</EXTENSION_TABLE_NAME>\n" % dac
    data += "<NAME>VFAT3 Production Summary Data</NAME>\n"
    data += "</TYPE>\n"
    data += "<RUN>\n"
    data += "<RUN_TYPE>VFAT3 Production Data</RUN_TYPE>\n"
    data += "<RUN_NUMBER>1</RUN_NUMBER>\n"
    data += "<RUN_BEGIN_TIMESTAMP>2016-07-18 13:55:06</RUN_BEGIN_TIMESTAMP>\n"
    data += "<RUN_END_TIMESTAMP>2016-07-18 14:55:03</RUN_END_TIMESTAMP>\n"
    data += "<COMMENT_DESCRIPTION>VFAT3 Production Data from Testing at CERNV</COMMENT_DESCRIPTION>\n"
    data += "<LOCATION>TIF</LOCATION>\n"
    data += "<INITIATED_BY_USER>%s</INITIATED_BY_USER>\n" % user
    data += "</RUN>\n"
    data += "</HEADER>\n"
    data += "<DATASET>\n"
    data += "<COMMENT_DESCRIPTION>GEM VFAT3 Production Summary Data</COMMENT_DESCRIPTION>\n"
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n"
    data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
    data += "</PART>\n"
    data += "<DATA>\n"
    db_data = database.get_table_values(hybrid, "%s" % dac)
    for i, dat in enumerate(db_data):
        if dat:
            data += "< DAC_SETTING > DAC%s </DAC_SETTING >" % i
            data += "< CHRG_VALUE > %s </CHRG_VALUE >" % dat
        else:
            data += "< DAC_SETTING > DAC%s </DAC_SETTING >" % i
            data += "< CHRG_VALUE > NULL </CHRG_VALUE >"
    data += "</DATA>\n"
    data += "</DATASET>\n"
    data += "</ROOT>\n"
    outF = open(filename, "w")
    outF.write(data)
    outF.close()


if show_data[5]:
    dac = "EXT_ADC_CAL_LUT"
    filename = "./results/%s_%s.xml" % (hybrid, dac)
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            print "Unable to create directory"
    data = "<ROOT>\n"
    data += "<HEADER>\n"
    data += "<TYPE>\n"
    data += "<EXTENSION_TABLE_NAME>VFAT3_%s</EXTENSION_TABLE_NAME>\n" % dac
    data += "<NAME>VFAT3 Production Summary Data</NAME>\n"
    data += "</TYPE>\n"
    data += "<RUN>\n"
    data += "<RUN_TYPE>VFAT3 Production Data</RUN_TYPE>\n"
    data += "<RUN_NUMBER>1</RUN_NUMBER>\n"
    data += "<RUN_BEGIN_TIMESTAMP>2016-07-18 13:55:06</RUN_BEGIN_TIMESTAMP>\n"
    data += "<RUN_END_TIMESTAMP>2016-07-18 14:55:03</RUN_END_TIMESTAMP>\n"
    data += "<COMMENT_DESCRIPTION>VFAT3 Production Data from Testing at CERNV</COMMENT_DESCRIPTION>\n"
    data += "<LOCATION>TIF</LOCATION>\n"
    data += "<INITIATED_BY_USER>%s</INITIATED_BY_USER>\n" % user
    data += "</RUN>\n"
    data += "</HEADER>\n"
    data += "<DATASET>\n"
    data += "<COMMENT_DESCRIPTION>GEM VFAT3 Production Summary Data</COMMENT_DESCRIPTION>\n"
    data += "<VERSION>1</VERSION>\n"
    data += "<PART>\n"
    data += "<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n"
    data += "<SERIAL_NUMBER>%s</SERIAL_NUMBER>\n" % production_data[0]
    data += "</PART>\n"
    data += "<DATA>\n"
    db_data = database.get_table_values(hybrid, "%s" % dac)
    for i, dat in enumerate(db_data):
        if dat:
            data += "< DAC_SETTING > DAC%s </DAC_SETTING >" % i
            data += "< ADC_VALUE > %s </ADC_VALUE >" % dat
        else:
            data += "< DAC_SETTING > DAC%s </DAC_SETTING >" % i
            data += "< ADC_VALUE > NULL </ADC_VALUE >"
    data += "</DATA>\n"
    data += "</DATASET>\n"
    data += "</ROOT>\n"
    outF = open(filename, "w")
    outF.write(data)
    outF.close()