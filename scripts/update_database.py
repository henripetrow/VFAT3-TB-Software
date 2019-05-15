import pymysql

connection = pymysql.connect(host="localhost", user="VFAT3", passwd="1234", database="VFAT3_Production")
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