import pymysql
from test_system_functions import read_database_info

[error, host, port, user, passwd, database_name] = read_database_info()
connection = pymysql.connect(host=host, user=user, passwd=passwd, database=database_name)
cursor = connection.cursor()


# production_table_sql = 'ALTER TABLE Production ADD COLUMN Location VARCHAR(20), ADD COLUMN Temperature FLOAT, ADD COLUMN State VARCHAR(20);'
# cursor.execute(production_table_sql)
# connection.close()


channel_category_table = 'CREATE TABLE channel_category(ChipID INT'
for i in range(0, 128):
    channel_category_table += ', CH%i VARCHAR(20)' % i
channel_category_table += ')'
cursor.execute(channel_category_table)
connection.close()
