import os
import sys
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *



file = "../results/production_files/production.csv"

if not os.path.exists(os.path.dirname(file)):
    try:
        os.makedirs(os.path.dirname(file))
    except OSError as exc:  # Guard against race condition
        print "Unable to create directory"

# test_hybrids = ['Hybrid333', 'Hybrid3333', 'Hybrid33333', 'Hybrid3333333', 'Hybrid333333', 'Hybrid324234', 'Hybrid354',
#                'Hybrid34543', 'Hybrid444444', 'Hybrid44444']
test_hybrids = []


database = DatabaseInterfaceBrowse(database_name="VFAT3_Production_final")
hybrid_list = database.list_hybrids()
print "Listing hybrids from the database."
temp_list = []

for h in hybrid_list:
    hybrid_number = int(h[6:])
    temp_list.append(int(h[6:]))

temp_list.sort()
hybrid_list = []
for k in temp_list:
    hybrid_name = "Hybrid%s" % k
    hybrid_list.append(hybrid_name)
    # print hybrid_name
print "Number of found hybrids:"
print len(hybrid_list)

column_names = database.get_production_column_names()
text = column_names[0]
for name in column_names[1:]:
    text += ",%s" % name
text += "\n"
outF = open(file, "w")
outF.write(text)
outF.close()

print ""
print "Generating csv-files for the found hybrids."


# Generation of the production summary table csv-file


for hybrid in hybrid_list:

    production_data = database.get_production_results(hybrid)
    text = "%s" % production_data[0]
    for name in production_data[1:]:
        text += ",%s" % name
    text += "\n"
    print text
    outF = open(file, "a")
    outF.write(text)
    outF.close()


