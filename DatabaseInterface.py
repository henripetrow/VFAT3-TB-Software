import pymysql
import os
from scripts.DatabaseInterfaceBrowse import *
import matplotlib.pyplot as plt


class DatabaseInterface:
    def __init__(self, name):
        self.id_exists = 0
        self.name = name
        self.user = "VFAT3"
        self.passwd = "1234"
        self.dacs_8bit = ["ZCC_DAC", "ARM_DAC", "PRE_I_BIT", "PRE_VREF", "SH_I_BFCAS", "SH_I_BDIFF", "SD_I_BDIFF",
                          "SD_I_BFCAS", "CAL_DAC"]
        self.dacs_6bit = ["HYST_DAC", "CFD_DAC_1", "CFD_DAC_2", "PRE_I_BSF", "PRE_I_BLCC", "SD_I_BSF"]
        self.table_name = "Production"
        self.database_name = "VFAT3_Production"
        self.connection = pymysql.connect(host="localhost", user=self.user, passwd=self.passwd, database=self.database_name)
        self.cursor = self.connection.cursor()

        # Search if the name exists already.
        update_sql = "SELECT * FROM %s WHERE ChipID = '%s' ;" % (self.table_name, name)
        self.cursor.execute(update_sql)
        self.connection.commit()
        if self.cursor.rowcount == 0:
            print "Database entry not found. Creating a new entry."
            # Insert new row on Production table.
            insert1 = "INSERT INTO %s(ChipID) VALUES('%s');" % (self.table_name, self.name)
            self.cursor.execute(insert1)
            self.connection.commit()

            # Insert new table for Threshold data.
            insert1 = "INSERT INTO Threshold(ChipID) VALUES('%s');" % self.name
            self.cursor.execute(insert1)
            self.connection.commit()

            # Insert new table for Threshold data.
            insert1 = "INSERT INTO enc(ChipID) VALUES('%s');" % self.name
            self.cursor.execute(insert1)
            self.connection.commit()

            # Insert new table for Threshold data.
            insert1 = "INSERT INTO ADC0_CAL_LUT(ChipID) VALUES('%s');" % self.name
            self.cursor.execute(insert1)
            self.connection.commit()

            # Insert new table for Threshold data.
            insert1 = "INSERT INTO ADC1_CAL_LUT(ChipID) VALUES('%s');" % self.name
            self.cursor.execute(insert1)
            self.connection.commit()

            # Insert new table for Threshold data.
            insert1 = "INSERT INTO EXT_ADC_CAL_LUT(ChipID) VALUES('%s');" % self.name
            self.cursor.execute(insert1)
            self.connection.commit()

            # Insert new table for Threshold data.
            insert1 = "INSERT INTO CAL_DAC_FC(ChipID) VALUES('%s');" % self.name
            self.cursor.execute(insert1)
            self.connection.commit()

            # Insert new tables for DACs.
            adcs = ["ADC0", "ADC1"]
            for adc in adcs:
                for i in self.dacs_6bit:
                    insert1 = "INSERT INTO %s_%s(ChipID) VALUES('%s');" % (i, adc, self.name)
                    self.cursor.execute(insert1)
                    self.connection.commit()
                for i in self.dacs_8bit:
                    insert1 = "INSERT INTO %s_%s(ChipID) VALUES('%s');" % (i, adc, self.name)
                    self.cursor.execute(insert1)
            self.connection.commit()

        else:
            print "Database entry found."
            self.id_exists = 1
        self.connection.close()

    def open_connection(self):
        self.connection = pymysql.connect(host="localhost", user=self.user, passwd=self.passwd, database=self.database_name)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        self.connection.commit()
        self.connection.close()

    def set_string(self, field, data):
        self.open_connection()
        self.cursor.execute("UPDATE  %s SET %s='%s'  WHERE ChipID = '%s' ;" % (self.table_name, field, data, self.name))
        self.close_connection()

    def set_int(self, field, data):
        self.open_connection()
        self.cursor.execute("UPDATE  %s SET %s=%i  WHERE ChipID = '%s' ;" % (self.table_name, field, data, self.name))
        self.close_connection()

    def set_float(self, field, data):
        self.open_connection()
        self.cursor.execute("UPDATE  %s SET %s=%f  WHERE ChipID = '%s' ;" % (self.table_name, field, data, self.name))
        self.close_connection()

    def save_dac_data(self, table_name, adc, adc_values, dac_values):
        self.open_connection()
        table_sql = "UPDATE %s_%s SET " % (table_name, adc)
        table_sql += "DAC%i = %f" % (dac_values[0], adc_values[0])
        for i in range(1, len(dac_values)):
            table_sql += ", DAC%i = %f" % (dac_values[i], adc_values[i])
        table_sql += " WHERE ChipID = '%s';" % self.name
        self.cursor.execute(table_sql)
        self.close_connection()

    def save_lut_data(self, table_name, data, dac_values):
        self.open_connection()
        table_sql = "UPDATE %s SET " % table_name
        table_sql += "DAC%i = %i" % (dac_values[0], data[0])
        for i in range(1, len(data)):
            table_sql += ", DAC%i = %i" % (dac_values[i], data[i])
        table_sql += " WHERE ChipID = '%s';" % self.name
        self.cursor.execute(table_sql)
        self.close_connection()

    def save_lut_data_float(self, table_name, data, dac_values):
        self.open_connection()
        table_sql = "UPDATE %s SET " % table_name
        table_sql += "DAC%i = %f" % (dac_values[0], data[0])
        for i in range(1, len(data)):
            table_sql += ", DAC%i = %f" % (dac_values[i], data[i])
        table_sql += " WHERE ChipID = '%s';" % self.name
        self.cursor.execute(table_sql)
        self.close_connection()

    def save_ch_data(self, table_name, data):
        if data:
            self.open_connection()
            table_sql = "UPDATE %s SET " % table_name
            table_sql += "Ch%i = %f" % (0, data[0])
            for i in range(1, len(data)):
                table_sql += ", Ch%i = %f" % (i, data[i])
            table_sql += " WHERE ChipID = '%s';" % self.name
            self.cursor.execute(table_sql)
            self.close_connection()
        else:
            print "No data to save to database."

    def save_adc0(self, m_value, b_value):
        self.set_float("ADC0M", m_value)
        self.set_float("ADC0B", b_value)

    def save_adc1(self, m_value, b_value):
        self.set_float("ADC1M", m_value)
        self.set_float("ADC1B", b_value)

    def save_cal_dac(self, m_value, b_value):
        self.set_float("CAL_DACM", m_value)
        self.set_float("CAL_DACB", b_value)

    def save_iref(self, value):
        self.set_int("Iref", value)

    def save_mean_threshold(self, value):
        self.set_float("Mean_Threshold", value)

    def save_threshold_data(self, values):
        self.save_ch_data("Threshold", values)

    def save_mean_enc(self, value):
        self.set_float("Mean_enc", value)

    def save_enc_data(self, values):
        self.save_ch_data("enc", values)

    def save_register_test(self, errors):
        self.set_int("RegisterTest", errors)

    def save_data_test(self, error_list):
        self.set_int("CRC_errors", error_list[0])
        self.set_int("BC_errors", error_list[1])
        self.set_int("EC_errors", error_list[2])
        self.set_int("Hit_errors", error_list[3])

    def save_noisy_channels(self, value):
        self.set_string("NoisyChannels", len(value))

    def save_dead_channels(self, value):
        self.set_int("DeadChannels", len(value))

    def save_bist(self, value):
        self.set_int("BIST", value)

    def save_scanchain(self):
        self.set_int("ScanChain", 0)

    def save_barcode(self, value):
        self.set_int("Barcode", value)

    def save_power(self, ch1_power, ch2_power, mode):
        self.set_float("%s_Power_digital" % mode, ch1_power)
        self.set_float("%s_Power_analog" % mode, ch2_power)

    def save_hw_id_ver(self, hw_id_ver):
        self.set_int("HW_ID_VER", hw_id_ver)

    def save_vref(self, value):
        self.set_int("VREF_ADC", value)

    def save_vbgr(self, value):
        print "Saving VBGR value: %f" % value
        self.set_float("V_BGR", value)

    def save_adc_offset(self, value):
        self.set_float("BUFFER_OFFSET", value)

    def save_temperature(self, value):
        self.set_float("Temperature", value)

    def save_location(self, value):
        self.set_string("Location", value)

    def save_state(self, value):
        self.set_string("State", value)

    def create_xml_file(self):
        command = "mysql -uVFAT3 -p1234 --xml -e 'SELECT * FROM %s.%s WHERE ChipID = %s' > ./results/hybrid_%s.xml" % (self.database_name, self.table_name, self.name, self.name)
        os.system(command)


def hybrid_browser(hybrid=""):
    database = DatabaseInterfaceBrowse()
    # hybrid_list = database.list_hybrids()
    # print "List of tested hybrids:"
    # for i, hybrid in enumerate(hybrid_list):
    #    print "[%i] %s" % (i, hybrid)

    # hybrid_nr = raw_input("Choose hybrid:")
    adcs = ["ADC0", "ADC1"]
    dac6bits = ["CFD_DAC_1", "CFD_DAC_2", "HYST_DAC", "PRE_I_BLCC", "PRE_I_BSF", "SD_I_BSF"]
    dac8bits = ["ARM_DAC", "CAL_DAC", "PRE_VREF", "PRE_I_BIT", "SD_I_BDIFF", "SH_I_BDIFF", "SD_I_BFCAS", "SH_I_BFCAS",
                "ZCC_DAC"]
    dac_table = []
    hybrid = "Hybrid%s" % hybrid
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
                            y_data.append(dat * adc0m + adc0b)
                        if adc == "ADC1":
                            y_data.append(dat * adc1m + adc1b)
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
                            y_data.append(dat * adc0m + adc0b)
                        if adc == "ADC1":
                            y_data.append(dat * adc1m + adc1b)
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
            mean_data = [production_data[12]] * 128
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
            mean_data = [production_data[13]] * 128
            plt.plot(x_data, mean_data)
        plt.plot(x_data, data)
        if production_data[13]:
            plt.text(100, 0.8, "Mean enc:\n %f" % production_data[13], bbox=dict(alpha=0.5))
        plt.title("%s enc" % hybrid)
        plt.ylim([0, 0.5])
        plt.xlim([0, 128])
        plt.xlabel("Channel")
        plt.ylabel("enc [fC]")
        plt.grid(True)
        plt.show()


















