import os
import time
import sys
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *

database = DatabaseInterfaceBrowse()


hybrid_list = database.list_hybrids_by_state('red', greater=6100, smaller=50000)

date_list = []

for hybrid in hybrid_list:
    production_data_int = database.get_production_results(hybrid)
    print production_data_int[30]