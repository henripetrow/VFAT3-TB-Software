import pymysql
#import sys
#from test_system_functions import read_database_info
from datetime import datetime, timedelta


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
        hybrid_list.sort()
        return hybrid_list

    def list_hybrids_modified_in_days(self, nr_days):
        hybrid_list = []
        query = "SELECT * FROM Production WHERE "
        for days in range(0, nr_days+1):
            if days > 0:
                query += " OR "
            d = datetime.today() - timedelta(days=days)
            date = d.strftime("%d%m%Y")
            query += "Modified='%s'" % date
        query += ";"
        print query
        self.open_connection()
        self.cursor.execute(query)
        output = self.cursor.fetchall()
        for row in output:
            hybrid_list.append(row[0])
        self.connection.close()
        hybrid_list.sort()
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

    def get_run_number(self):
        self.open_connection()
        self.cursor.execute("select RUN_NUMBER from setup_info;")
        output = self.cursor.fetchall()
        self.connection.close()
        return output[0][0]

    def set_run_number(self, new_run_nr):
        self.open_connection()
        query = "UPDATE setup_info SET RUN_NUMBER='%i';" % new_run_nr
        print query
        self.cursor.execute(query)
        self.connection.commit()
        self.connection.close()

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


def read_database_info():
    fail = 0
    try:
        f = open("./data/database_login.dat", "r")
    except:
        fail = 1
    if fail:
        try:
            f = open("../data/database_login.dat", "r")
            fail = 0
        except:
            fail = 1
    if not fail:
        print "Resolving database login information."
        error = 0
        for line in f:
            data = line.split(" ")
            field_name = data[0]
            try:
                value = data[2]
            except:
                value = ""

            if field_name == 'host':
                [error, host] = check_data(field_name, value, error)
            if field_name == 'port':
                [error, port] = check_data(field_name, value, error)
            if field_name == 'user':
                [error, user] = check_data(field_name, value, error)
            if field_name == 'passwd':
                [error, passwd] = check_data(field_name, value, error)
            if field_name == 'database':
                [error, database] = check_data(field_name, value, error)
        if error:
            print "Invalid database information found, contact the database admin for correct info."
    else:
        print "Database login information not found. Please contact the database admin for login information."
        error = 1
        host = ""
        port = ""
        user = ""
        passwd = ""
        database = ""
    return [error, host, port, user, passwd, database]

def check_data(name, data, error):
    if data:
        if name == 'port':
            output_data = int(data.strip())
        else:
            output_data = data.strip()
    else:
        print "Invalid %s." % name
        output_data = 'error'
        error += 1
    return [error, output_data]