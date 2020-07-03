import os
import time
import sys
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *

database = DatabaseInterfaceBrowse()


hybrid_list = database.list_hybrids(greater=6100, smaller=50000)

months = []

for hybrid in hybrid_list:
    production_data_int = database.get_production_results(hybrid)
    if production_data_int[30] is not None or production_data_int[30] != "None":
        months.append(production_data_int[30][2:4])


print "January: %s" % months.count('01')
print "February: %s" % months.count('02')
print "March: %s" % months.count('03')
print "April: %s" % months.count('04')
print "May: %s" % months.count('05')
print "June: %s" % months.count('06')
print "July: %s" % months.count('07')
print "August: %s" % months.count('08')
print "September: %s" % months.count('09')
print "October: %s" % months.count('10')
print "November: %s" % months.count('11')
print "December: %s" % months.count('12')