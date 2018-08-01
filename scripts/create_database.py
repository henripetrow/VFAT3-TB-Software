import pymysql

connection = pymysql.connect(host="localhost", user="VFAT3", passwd="1234", database="VFAT3_Production_final")
cursor = connection.cursor()


# Create Production -table.

production_table = ["ChipID INT(10)", "HW_ID_VER INT", "BUFFER_OFFSET FLOAT", "VREF_ADC INT", "V_BGR FLOAT", "ADC0M FLOAT(8)", "ADC0B FLOAT(8)", "ADC1M FLOAT(8)",
                    "ADC1B FLOAT(8)", "CAL_DACM FLOAT", "CAL_DACB FLOAT", "Iref INT", "Mean_Threshold FLOAT", "Mean_enc FLOAT",
                    "RegisterTest INT", "EC_errors INT", "BC_errors INT", "CRC_errors INT", "Hit_errors INT",
                    "NoisyChannels INT", "DeadChannels INT", "BIST INT", "ScanChain BOOLEAN", "SLEEP_Power_analog FLOAT",
                    "SLEEP_Power_digital FLOAT", "RUN_Power_analog FLOAT",
                    "RUN_Power_digital FLOAT", "Location VARCHAR(20)", 'Temperature FLOAT', 'State VARCHAR(20)']

production_table_sql = 'CREATE TABLE Production(%s' % production_table[0]
for i, item in enumerate(production_table):
    if i == 0:
        pass
    else:
        production_table_sql += ', %s' % item
production_table_sql += ')'
cursor.execute(production_table_sql)

adcs = ["ADC0", "ADC1"]
dac6bits = ["CFD_DAC_1", "CFD_DAC_2", "HYST_DAC", "PRE_I_BLCC", "PRE_I_BSF", "SD_I_BSF"]
dac8bits = ["ARM_DAC", "CAL_DAC", "PRE_VREF", "PRE_I_BIT", "SD_I_BDIFF", "SH_I_BDIFF", "SD_I_BFCAS", "SH_I_BFCAS", "ZCC_DAC"]
dac_table = []

for adc in adcs:
    for dac in dac6bits:
        dac_table = 'CREATE TABLE %s_%s(ChipID INT' % (dac, adc)
        for i in range(0, 64):
            dac_table += ', DAC%i INT' % i
        dac_table += ')'
        cursor.execute(dac_table)

    for dac in dac8bits:
        dac_table = 'CREATE TABLE %s_%s(ChipID INT' % (dac, adc)
        for i in range(0, 256):
            dac_table += ', DAC%i INT' % i
        dac_table += ')'
        cursor.execute(dac_table)


threshold_table = 'CREATE TABLE Threshold(ChipID INT'
for i in range(0, 128):
    threshold_table += ', CH%i FLOAT' % i
threshold_table += ')'
cursor.execute(threshold_table)

enc_table = 'CREATE TABLE enc(ChipID INT'
for i in range(0, 128):
    enc_table += ', CH%i FLOAT' % i
enc_table += ')'
cursor.execute(enc_table)

table = 'CREATE TABLE ADC0_CAL_LUT(ChipID INT'
for i in range(0, 256):
    table += ', DAC%i INT' % i
table += ')'
cursor.execute(table)

table = 'CREATE TABLE ADC1_CAL_LUT(ChipID INT'
for i in range(0, 256):
    table += ', DAC%i INT' % i
table += ')'
cursor.execute(table)

table = 'CREATE TABLE EXT_ADC_CAL_LUT(ChipID INT'
for i in range(0, 256):
    table += ', DAC%i FLOAT' % i
table += ')'
cursor.execute(table)

table = 'CREATE TABLE CAL_DAC_FC(ChipID INT'
for i in range(0, 256):
    table += ', DAC%i FLOAT' % i
table += ')'
cursor.execute(table)

connection.close()

