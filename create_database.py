import pymysql

connection = pymysql.connect(host="localhost", user="root", passwd="root", database="Hybrids_test")
cursor = connection.cursor()


# Create Production -table.

production_table = ["ChipID INT(10)", "Barcode INT(10)", "ADC0M FLOAT(8)", "ADC0B FLOAT(8)", "ADC1M FLOAT(8)",
                    "ADC1B FLOAT(8)", "CAL_DACM FLOAT", "CAL_DACB FLOAT", "Iref INT", "Mean_Threshold FLOAT", "Mean_enc FLOAT",
                    "RegisterTest CHAR(10)", "EC_errors INT", "BC_errors INT", "CRC_errors INT", "Hit_errors INT",
                    "NoisyChannels TEXT", "BIST BOOLEAN", "ScanChain BOOLEAN", "SLEEP_Power_analog FLOAT",
                    "SLEEP_Power_digital FLOAT", "RUN_Power_analog FLOAT",
                    "RUN_Power_digital FLOAT", "Threshold TEXT", "enc TEXT"]

adcs = ["ADC0", "ADC1"]
dac6bits = ["CFD_DAC_1", "CFD_DAC_2", "HYST_DAC", "PRE_I_BLCC", "PRE_I_BSF", "SD_I_BSF"]
dac8bits = ["ARM_DAC", "CAL_DAC", "PRE_VREF", "PRE_I_BIT", "SD_I_BDIFF", "SH_I_BDIFF", "SD_I_BFCAS", "SH_I_BFCAS", "ZCC_DAC"]
dac_table = []
for adc in adcs:
    for dac in dac6bits:
        dac_table.append("%s_%s TEXT" % (dac, adc))
    for dac in dac8bits:
        dac_table.append("%s_%s TEXT" % (dac, adc))

production_table.extend(dac_table)

production_table_sql = 'CREATE TABLE Test(%s' % production_table[0]
for i, item in enumerate(production_table):
    if i == 0:
        pass
    else:
        production_table_sql += ', %s' % item
production_table_sql += ')'
cursor.execute(production_table_sql)

production_table_sql = 'SET GLOBAL innodb_file_format=Barracuda;'
cursor.execute(production_table_sql)
production_table_sql = 'SET GLOBAL innodb_file_per_table=1;'
cursor.execute(production_table_sql)
production_table_sql = 'SET GLOBAL innodb_large_prefix=1;'
cursor.execute(production_table_sql)
production_table_sql = 'ALTER TABLE Test ROW_FORMAT=DYNAMIC;'
cursor.execute(production_table_sql)


# adcs = ["ADC0", "ADC1"]
# dac6bits = ["CFD_DAC_1", "CFD_DAC_2", "HYST_DAC", "PRE_I_BLCC", "PRE_I_BSF", "SD_I_BSF"]
# dac8bits = ["ARM_DAC", "CAL_DAC", "PRE_VREF", "PRE_I_BIT", "SD_I_BDIFF", "SH_I_BDIFF", "SD_I_BFCAS", "SH_I_BFCAS", "ZCC_DAC"]
# dac_table = []
# for adc in adcs:
#     for dac in dac6bits:
#         dac_table.append("%s_%s TEXT" % (dac, adc))
#     for dac in dac8bits:
#         dac_table.append("%s_%s TEXT" % (dac, adc))



# for adc in adcs:
#     for dac in dac6bits:
#         dac_table = 'CREATE TABLE %s_%s(ChipID INT' % (dac, adc)
#         for i in range(0, 64):
#             dac_table += ', DAC%i INT' % i
#         dac_table += ')'
#         cursor.execute(dac_table)
#
#     for dac in dac8bits:
#         dac_table = 'CREATE TABLE %s_%s(ChipID INT' % (dac, adc)
#         for i in range(0, 256):
#             dac_table += ', DAC%i INT' % i
#         dac_table += ')'
#         cursor.execute(dac_table)


# threshold_table = 'CREATE TABLE Threshold(ChipID INT'
# for i in range(0, 128):
#     threshold_table += ', CH%i FLOAT' % i
# threshold_table += ')'
# cursor.execute(threshold_table)
#
# enc_table = 'CREATE TABLE enc(ChipID INT'
# for i in range(0, 128):
#     enc_table += ', CH%i FLOAT' % i
# enc_table += ')'
# cursor.execute(enc_table)

connection.close()