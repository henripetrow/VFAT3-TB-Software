import sys
sys.path.append('../')
from reedmuller import *
from test_system_functions import dec_to_bin_with_stuffing

chip_id = 6000
chip_id_bin = dec_to_bin_with_stuffing(chip_id, 32)
print chip_id
print "Binary:"
print chip_id_bin
print ''.join(map(str, chip_id_bin))
rm = reedmuller.ReedMuller(2, 5)
chip_id_bin_rm = rm.encode(chip_id_bin[-16:])
chip_id = int(''.join(map(str, chip_id_bin_rm)), 2)
print "Reed-Muller encoded:"
print chip_id_bin_rm
print ''.join(map(str, chip_id_bin_rm))
