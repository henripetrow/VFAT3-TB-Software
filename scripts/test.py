import sys
sys.path.append('../')
from reedmuller import *
from test_system_functions import dec_to_bin_with_stuffing


for chip_id in range(20000,20010):
    chip_id_bin = dec_to_bin_with_stuffing(chip_id, 32)
    print "Dec:"
    print chip_id
    print "Binary:"
    print ''.join(map(str, chip_id_bin))
    rm = reedmuller.ReedMuller(2, 5)
    chip_id_bin_rm = rm.encode(chip_id_bin[-16:])
    chip_id = int(''.join(map(str, chip_id_bin_rm)), 2)
    print "Reed-Muller encoded:"
    print ''.join(map(str, chip_id_bin_rm))
