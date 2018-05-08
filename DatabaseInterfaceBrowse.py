import pymysql


class DatabaseInterfaceBrowse:
    def __init__(self):
        self.user = "VFAT3"
        self.passwd = "1234"
        self.database_name = "VFAT3_Production"
        self.connection = pymysql.connect(host="localhost", user=self.user, passwd=self.passwd, database=self.database_name)
        self.cursor = self.connection.cursor()
        self.connection.close()

    def open_connection(self):
        self.connection = pymysql.connect(host="localhost", user=self.user, passwd=self.passwd, database=self.database_name)
        self.cursor = self.connection.cursor()

    def list_hybrids(self):
        hybrid_list = []
        self.open_connection()
        self.cursor.execute("SELECT * FROM Production;")
        output = self.cursor.fetchall()
        for row in output:
            hybrid_list.append("Hybrid%i" % row[0])
        self.connection.close()
        return hybrid_list

    def get_production_results(self, chip_id):
        data_list = []
        self.open_connection()
        self.cursor.execute("SELECT * FROM Production WHERE ChipID = '%s';" % chip_id[6:])
        output = self.cursor.fetchall()
        for row in output[0]:
            data_list.append(row)
        self.connection.close()
        return data_list


    def get_table_values(self, chip_id, table):
        data_list = []
        self.open_connection()
        self.cursor.execute("SELECT * FROM %s WHERE ChipID = '%s';" % (table, chip_id[6:]))
        output = self.cursor.fetchall()
        for row in output[0]:
            data_list.append(row)
        self.connection.close()
        return data_list[1:]

    def get_enc_values(self, chip_id):
        return self.get_table_values(chip_id, "enc")

    def get_threshold_values(self, chip_id):
        return self.get_table_values(chip_id, "Threshold")