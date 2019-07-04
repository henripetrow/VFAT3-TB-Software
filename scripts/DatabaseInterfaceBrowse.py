import pymysql
from test_system_functions import read_database_info


class DatabaseInterfaceBrowse:
    def __init__(self):
        [error, self.host, self.port, self.user, self.passwd, self.database_name] = read_database_info()
        self.db_error = 0
        if not error:
            self.connection = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, database=self.database_name)
            self.cursor = self.connection.cursor()
            self.connection.close()
        else:
            self.db_error = 1

    def open_connection(self):
        self.connection = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, database=self.database_name)
        self.cursor = self.connection.cursor()

    def list_hybrids(self, greater="", smaller=""):
        hybrid_list = []
        self.open_connection()
        if greater != "" and smaller != "":
            self.cursor.execute("SELECT * FROM Production WHERE ChipID >= '%s' AND ChipID <= '%s';" % (greater, smaller))
        elif greater != "":
            self.cursor.execute("SELECT * FROM Production WHERE ChipID >= %s;" % greater)
        elif smaller != "":
            self.cursor.execute("SELECT * FROM Production WHERE ChipID <= %s;" % smaller)
        else:
            self.cursor.execute("SELECT * FROM Production;")
        output = self.cursor.fetchall()
        for row in output:
            hybrid_list.append(row[0])
        self.connection.close()
        return hybrid_list

    def list_hybrids_by_lot(self, lot_nr):
        hybrid_list = []
        self.open_connection()
        self.cursor.execute("SELECT * FROM Production WHERE Lot='%s';" % lot_nr)
        output = self.cursor.fetchall()
        for row in output:
            hybrid_list.append(row[0])
        self.connection.close()
        return hybrid_list

    def get_production_column_names(self):
        data_list = []
        self.open_connection()
        self.cursor.execute("SHOW columns FROM Production;")
        output = self.cursor.fetchall()
        for row in output:
            data_list.append(row[0])
        self.connection.close()
        return data_list

    def get_production_results(self, chip_id):
        data_list = []
        self.open_connection()
        rows_count = self.cursor.execute("SELECT * FROM Production WHERE ChipID = '%s';" % chip_id)
        if rows_count > 0:
            output = self.cursor.fetchall()
            for row in output[0]:
                data_list.append(row)
        self.connection.close()

        return data_list

    def get_table_values(self, chip_id, table, allow_non_existing_hybrids=0):
        data_list = []
        return_list = []
        self.open_connection()
        self.cursor.execute("SELECT * FROM %s WHERE ChipID = '%s';" % (table, chip_id))
        output = self.cursor.fetchall()
        if len(output) != 0:
            for row in output[0]:
                data_list.append(row)
            self.connection.close()
            return_list = data_list[1:]
        else:
            if not allow_non_existing_hybrids:
                print "%s not found in the table." % chip_id
        return return_list

    def get_enc_values(self, chip_id):
        return self.get_table_values(chip_id, "enc")

    def get_threshold_values(self, chip_id):
        return self.get_table_values(chip_id, "Threshold")