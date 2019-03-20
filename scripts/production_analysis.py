import sys
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *
import matplotlib.pyplot as plt
import os

folder = "../results/production_analysis/"
#folder = "/home/hpetrow/cernbox/Data/production_analysis/"


if not os.path.exists(os.path.dirname(folder)):
    try:
        os.makedirs(os.path.dirname(folder))
    except OSError as exc:  # Guard against race condition
        print "Unable to create directory"

print "Looking for hybrids in the database."
print "Ignoring test hybrids:"
# test_hybrids = ['Hybrid333', 'Hybrid3333', 'Hybrid33333', 'Hybrid3333333', 'Hybrid333333', 'Hybrid324234', 'Hybrid354',
#                'Hybrid34543', 'Hybrid444444', 'Hybrid44444']
test_hybrids = []
print test_hybrids

database = DatabaseInterfaceBrowse()
hybrid_list = database.list_hybrids()
temp_list = []
for h in hybrid_list:
    if h in test_hybrids:
        pass
    else:
        temp_list.append(int(h[6:]))
temp_list.sort()
hybrid_list = []
for k in temp_list:
    hybrid_list.append("Hybrid%s" % k)
print "Found %s hybrids." % len(hybrid_list)

print "Generating analysis for the production test results..."

adcs = ["ADC0", "ADC1"]
dacs = ["CFD_DAC_1", "CFD_DAC_2", "HYST_DAC", "PRE_I_BLCC", "PRE_I_BSF", "SD_I_BSF", "ARM_DAC", "CAL_DAC", "PRE_VREF", "PRE_I_BIT", "SD_I_BDIFF", "SH_I_BDIFF", "SD_I_BFCAS", "SH_I_BFCAS", "ZCC_DAC"]
for dac in dacs:
    final_value = 0
    adc0m_list = []
    adc0b_list = []
    adc1m_list = []
    adc1b_list = []
    cal_dacm_list = []
    cal_dacb_list = []
    final_value_list = []
    final_value_hybrids = []
    adc0_list = []
    iref_list = []
    buffer_offsets = []
    vref_adcs = []
    v_bgrs = []
    register_tests = []
    ec_errors = []
    bc_errors = []
    crc_errors = []
    hit_errors = []
    mean_encs = []
    mean_thresholds = []
    fig = plt.figure(figsize=(10, 20))
    sub1 = plt.subplot(211)
    for hybrid in hybrid_list:
        production_data = database.get_production_results(hybrid)
        adc0m = production_data[5]
        adc0b = production_data[6]
        adc1m = production_data[7]
        adc1b = production_data[8]
        adc0m_list.append(adc0m)
        adc0b_list.append(adc0b)
        adc1m_list.append(adc1m)
        adc1b_list.append(adc1b)
        cal_dacm = production_data[9]
        cal_dacb = production_data[10]
        cal_dacm_list.append(cal_dacm)
        cal_dacb_list.append(cal_dacb)
        buffer_offsets.append(production_data[2])
        vref_adcs.append(production_data[3])
        v_bgrs.append(production_data[4])
        register_tests.append(production_data[14])
        ec_errors.append(production_data[15])
        bc_errors.append(production_data[16])
        crc_errors.append(production_data[17])
        hit_errors.append(production_data[18])
        mean_encs.append(production_data[13])
        mean_thresholds.append(production_data[12])
        #print "SLEEP POWER:\t A: %s D: %s" % (production_data[23], production_data[24])
        #print "RUN POWER:\t A: %s D: %s" % (production_data[25], production_data[26])
        iref_list.append(production_data[11])
        adc = "ADC0"
        data = database.get_table_values(hybrid, "%s_%s" % (dac, adc))
        x_data = []
        y_data = []
        for i, dat in enumerate(data):
            if dat:
                x_data.append(i)
                y_data.append(dat*adc0m+adc0b)
                final_value = dat*adc0m+adc0b
        sub1.plot(x_data, y_data, label=hybrid)
        final_value_list.append(final_value)
        final_value_hybrids.append(int(hybrid[6:]))

    #plt.legend(prop={'size': 10}, ncol=2)
    sub1.set_title("%s" % dac)
    #sub1.xlim([0, 100])
    sub1.set_ylabel("ADC value [mV]")
    sub1.set_xlabel("DAC count")
    sub1.grid(True)

    sub2 = plt.subplot(212)
    sub2.plot(final_value_list, 'b*')
    sub2.set_xlabel('Hybrid')
    sub2.set_ylabel('Last DAC value [mV]')
    sub2.set_title('Final DAC Value of the Hybrids')
    sub2.grid(True)

    fig.savefig("%s%s.png" % (folder, dac))
    print "Generated a plot for %s." % dac

    # iref_list = []
    # buffer_offsets = []
    # vref_adcs = []
    # v_bgrs = []
    # register_tests = []
    # ec_errors = []
    # bc_errors = []
    # crc_errors = []
    # hit_errors = []
    # mean_encs = []
    # mean_thresholds = []


# Plot ADC-calibration values

fig = plt.figure(figsize=(10, 20))
sub1 = plt.subplot(411)
sub1.plot(adc0m_list, 'b*')
sub1.set_xlabel('Hybrid')
sub1.set_ylabel('Multiplier [mV/DAC count]')
sub1.set_title('ADC0M')
sub1.grid(True)

sub2 = plt.subplot(412)
sub2.plot(adc0b_list, 'b*')
sub2.set_xlabel('Hybrid')
sub2.set_ylabel('Offset [mV]')
sub2.set_title('ADC0B')
sub2.grid(True)

sub3 = plt.subplot(413)
sub3.plot(adc1m_list, 'b*')
sub3.set_xlabel('Hybrid')
sub3.set_ylabel('Multiplier [mV/DAC count]')
sub3.set_title('ADC1M')
sub3.grid(True)

sub4 = plt.subplot(414)
sub4.plot(adc1b_list, 'b*')
sub4.set_xlabel('Hybrid')
sub4.set_ylabel('Offset [mV]')
sub4.set_title('ADC1B')
sub4.grid(True)

fig.savefig("%sadc-calibration.png" % folder)
print "Generated a plot for ADC-calibration."


# Plot CAL_DAC-calibration values

fig = plt.figure(figsize=(10, 20))
sub1 = plt.subplot(211)
sub1.plot(cal_dacm_list, 'b*')
sub1.set_xlabel('Hybrid')
sub1.set_ylabel('Multiplier [fC/DAC count]')
sub1.set_title('CAL_DACM')
sub1.grid(True)

sub2 = plt.subplot(212)
sub2.plot(cal_dacb_list, 'b*')
sub2.set_xlabel('Hybrid')
sub2.set_ylabel('Offset [fC]')
sub2.set_title('CAL_DACB')
sub2.grid(True)

fig.savefig("%scal_dac-calibration.png" % folder)
print "Generated a plot for CAL_DAC-calibration."

# Plot calibration values.

fig = plt.figure(figsize=(10, 20))
sub1 = plt.subplot(411)
sub1.plot(iref_list, 'b*')
sub1.set_xlabel('Hybrid')
sub1.set_ylabel('Ired [DAC count]')
sub1.set_title('Iref of the Hybrids')
sub1.grid(True)

sub2 = plt.subplot(412)
sub2.plot(buffer_offsets, 'b*')
sub2.set_xlabel('Hybrid')
sub2.set_ylabel('Buffer Offset [mV]')
sub2.set_title('Buffer offset')
sub2.grid(True)

sub3 = plt.subplot(413)
sub3.plot(vref_adcs, 'b*')
sub3.set_xlabel('Hybrid')
sub3.set_ylabel('VREF_ADC []')
sub3.set_title('VREF_ADC')
sub3.grid(True)

sub4 = plt.subplot(414)
sub4.plot(v_bgrs, 'b*')
sub4.set_xlabel('Hybrid')
sub4.set_ylabel('v_bgr []')
sub4.set_title('Bandgap Reference')
sub4.grid(True)

fig.savefig("%scalibration.png" % folder)
print "Generated a plot for calibration."


# Plot s-curve values

fig = plt.figure(figsize=(10, 20))
sub1 = plt.subplot(211)
sub1.plot(mean_thresholds, 'b*')
sub1.set_xlabel('Hybrid')
sub1.set_ylabel('Threshold [fC]')
sub1.set_title('Thresholds')
sub1.grid(True)

sub2 = plt.subplot(212)
sub2.plot(mean_encs, 'b*')
sub2.set_xlabel('Hybrid')
sub2.set_ylabel('enc [fC]')
sub2.set_title('Noise')
sub2.grid(True)

fig.savefig("%ss-curve.png" % folder)
print "Generated a plot for S-curves."

print "Analysis creation ready. Thank you."