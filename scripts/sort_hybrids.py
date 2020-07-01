import os
import time
import sys
sys.path.append('../')
from scripts.DatabaseInterfaceBrowse import *
from luts import *

sort_type = 'red'
sort_type = 'yellow'


database = DatabaseInterfaceBrowse()

if sort_type == 'red':
    hybrid_list = database.list_hybrids_by_state('red', greater=6100, smaller=50000)
    i = 0
    cal_dac_list = [8636, 7334, 6820]
    buffer_offset_list = [9985, 9953, 9827, 7463]
    adc_list = [6105, 6560, 6631, 6632, 6810, 7460, 10371, 10393, 7439, 7042, 6641, 6448, 7330, 7111, 7731]
    old_syc_sc = [7393]
    register_test_list = [10742]

    noise_list = [6445, 6130] #noise?

    other_list = [7925, 7843, 7206, 6900, 6555, 6130, 10094]
    # 7925, iref 15.
    # 7843, iref 44.
    # 7206, somehow s-curve values missing. Maybe crashed?
    # 6900, no apparent reason.
    # 6555, no apparent reason.
    # 6130, iref 45.
    # 10094, system probably crashed.

    sc_problems = 0
    sync_problems = 0
    sbit_problems = 0
    cal_dac_problems = 0
    bo_problems = 0
    adc_problems = 0
    noise_problems = 0
    register_problems = 0
    other_problems = 0
    scurve_problems = 0

    for hybrid in hybrid_list:
        production_data_int = database.get_production_results(hybrid)
        production_data = []
        for item in production_data_int:
            if item is None or item == "None":
                production_data.append(0)
            else:
                production_data.append(item)

        print_text = "Hybrid: %s" % hybrid
        if int(production_data[1]) == 0 and int(production_data[21]) == 0:
            print_text += ", short circuit1"
            sc_problems += 1
        elif int(production_data[1]) == 0 and int(production_data[21]) != 0:
            print_text += ", sync problem1"
            sync_problems += 1
        elif int(production_data[40]) == 1:
            print_text += ", short circuit"
            sc_problems += 1
        elif int(production_data[41]) == 1 or hybrid in old_syc_sc:
            print_text += ", sync problem"
            sync_problems += 1
        elif int(production_data[36]) > 0:
            print_text += ", S-bit problem"
            sbit_problems += 1
        elif hybrid in cal_dac_list:
            print_text += ", CAL_DAC problem"
            cal_dac_problems += 1
        elif hybrid in buffer_offset_list:
            print_text += ", Buffer offset problem"
            bo_problems += 1
        elif hybrid in adc_list:
            print_text += ", ADC problem"
            adc_problems += 1
        elif hybrid in noise_list:
            print_text += ", Noise problem"
            noise_problems += 1
        elif hybrid in register_test_list:
            print_text += ", Register test problem"
            register_problems += 1
        elif hybrid in other_list:
            print_text += ", Other problem"
            other_problems += 1
        i += 1
        print print_text


    hybrid_list = database.list_hybrids_by_state('NULL', greater=6101, smaller=50000)

    for hybrid in hybrid_list:
        production_data_int = database.get_production_results(hybrid)
        production_data = []
        for item in production_data_int:
            if item is None or item == "None":
                production_data.append(0)
            else:
                production_data.append(item)

        print_text = "Hybrid: %s" % hybrid
        if int(production_data[21]) == 0:
            print_text += ", short circuit"
            sc_problems += 1
        elif float(production_data[9]) != 0 and float(production_data[12]) == 0:
            print_text += ", failed S-curve"
            scurve_problems += 1
        elif hybrid in other_list:
            print_text += ", Other problem"
            other_problems += 1
        print print_text

        i  += 1
    print ""
    print "-------------------------------------"
    print "Total Red Hybrids: %s" % i
    print "Short circuit: %s" % sc_problems
    print "Sync: %s" % sync_problems
    print "S-bit: %s" % sbit_problems
    print "CAL_DAC: %s" % cal_dac_problems
    print "Buffer offset: %s" % bo_problems
    print "ADC: %s" % adc_problems
    print "Register: %s" % register_problems
    print "S-curve crash: %s" % scurve_problems
    print "Other: %s" % other_problems
    print ""
    print "-------------------------------------"


if sort_type == 'yellow':
    hybrid_list = database.list_hybrids_by_state('yellow', greater=6100, smaller=50000)
    i = 0
    cal_dac_list = [8636, 7334, 6820]

    others = 0
    for hybrid in hybrid_list:
        production_data_int = database.get_production_results(hybrid)
        production_data = []
        for item in production_data_int:
            if item is None or item == "None":
                production_data.append(0)
            else:
                production_data.append(item)


        print_text = "Hybrid: %s" % hybrid
        if (int(production_data[20]) + int(production_data[19])) > lim_Problematic_Channels[1]:
            print_text += ", Bad channels"
        elif int(production_data[18]) > 0 or int(production_data[17]) > 0 or int(production_data[16]) > 0 or int(production_data[15]) > 0:
            print_text += ", Data packet problem"
        elif lim_BIST[0] > int(production_data[21]) or int(production_data[21]) > lim_BIST[1]:
            print_text += ", BIST problem"
        elif lim_ADC0m[0] > float(production_data[5]) or float(production_data[5]) > lim_ADC0m[1]:
            print_text += ", ADC0 problem"
        elif lim_ADC0b[0] > float(production_data[6]) or float(production_data[6]) > lim_ADC0b[1]:
            print_text += ", ADC0 problem"
        elif lim_ADC1m[0] > float(production_data[7]) or float(production_data[7]) > lim_ADC1m[1]:
            print_text += ", ADC1 problem"
        elif lim_ADC1b[0] > float(production_data[8]) or float(production_data[8]) > lim_ADC1b[1]:
            print_text += ", ADC1 problem"
        elif lim_iref[0] > float(production_data[31]) or float(production_data[31]) > lim_iref[1]:
            print_text += ", Iref problem"
        elif lim_Analog_Power_SLEEP[0] > float(production_data[23]) or float(production_data[23]) > lim_Analog_Power_SLEEP[1]:
            print_text += ", Analog_Power_SLEEP problem"
        elif lim_Digital_Power_SLEEP[0] > float(production_data[24]) or float(production_data[24]) > lim_Digital_Power_SLEEP[1]:
            print_text += ", Digital_Power_SLEEP problem"
        # elif lim_IOVDD_Power_SLEEP[0] > float(production_data[38]) or float(production_data[38]) > lim_IOVDD_Power_SLEEP[1]:
        #     print_text += ", IOVDD_Power_SLEEP problem"
        elif lim_Analog_Power_RUN[0] > float(production_data[25]) or float(production_data[25]) > lim_Analog_Power_RUN[1]:
            print_text += ", Analog_Power_RUN problem"
        elif lim_Digital_Power_RUN[0] > float(production_data[26]) or float(production_data[26]) > lim_Digital_Power_RUN[1]:
            print_text += ", Digital_Power_RUN problem"
        # elif lim_IOVDD_Power_RUN[0] > float(production_data[39]) or float(production_data[39]) > lim_IOVDD_Power_RUN[1]:
        #     print_text += ", IOVDD_Power_RUN problem"
        elif lim_Temperature_k2[0] > float(production_data[33]) or float(production_data[33]) > lim_Temperature_k2[1]:
            print_text += ", Temperature_k2 problem"
        elif lim_Temperature[0] > float(production_data[32]) or float(production_data[32]) > lim_Temperature[1]:
            print_text += ", Temperature problem"

        else:
            others += 1

        i += 1
        print print_text

    print i
    print "Others: %s" % others