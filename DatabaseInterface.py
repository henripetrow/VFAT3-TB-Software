import pymysql


class DatabaseInterface:
    def __init__(self, name):
        self.name = name
        self.passwd = "root"
        self.user = "root"
        self.table_name = "Test"
        self.database_name = "Hybrids_test"
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
        else:
            print "Database entry found."
        self.connection.close()

    def open_connection(self, db_name="Hybrids_test"):
        self.connection = pymysql.connect(host="localhost", user=self.user, passwd=self.passwd, database=db_name)
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

    def save_dac_data(self, dac_name, adc, data):
        name = "%s_%s" % (dac_name, adc)
        data_sql = "%i" % data[0]
        for i in range(1, len(data)):
            data_sql += " %i" % data[i]
        self.set_string(name, data_sql)

    def save_ch_data(self, name, data):
        data_sql = "%f" % data[0]
        for i in range(1, len(data)):
            data_sql += " %f" % data[i]
        self.set_string(name, data_sql)

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

    def save_register_ok(self):
        self.set_int("RegisterTest", 1)

    def save_register_error(self):
        self.set_int("RegisterTest", 0)

    def save_data_test(self, error_list):
        self.set_int("CRC_errors", error_list[0])
        self.set_int("BC_errors", error_list[1])
        self.set_int("EC_errors", error_list[2])
        self.set_int("Hit_errors", error_list[3])

    def save_noisy_channels(self, value):
        if len(value) == 0:
            pass
        elif len(value) > 10:
            output = "%i channels" % len(value)
            self.set_string("NoisyChannels", output)
        else:
            for i, ch in enumerate(value):
                if i == 0:
                    output = "%i" % ch
                else:
                    output += ", %i" % ch
            self.set_string("NoisyChannels", output)

    def save_bist(self):
        self.set_int("BIST", 0)

    def save_scanchain(self):
        self.set_int("ScanChain", 0)

    def save_barcode(self,value):
        self.set_int("Barcode", value)

    def save_power(self, ch1_power, ch2_power, mode):
        self.set_float("%s_Power_digital" % mode, ch1_power)
        self.set_float("%s_Power_analog" % mode, ch2_power)























