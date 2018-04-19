from routines import *
from generator import *
from output_decoder import *
import time
import numpy as np


def test_data_packets(obj, nr_loops=10, save_result="yes"):
    print "Running data packet test."
    start = time.time()
    if save_result == "yes":
        save_data = 1
    else:
        save_data = 0
    nr_of_triggers = 10
    nr_of_bc_between_triggers = 30
    timestamp = time.strftime("%Y%m%d_%H%M")
    scan_name = "Consecutive_Triggers"
    file_name = "./routines/%s/FPGA_instruction_list.txt" % scan_name
    if save_result == "yes":
        output_file = "%s/concecutive_tiggers/%s_concecutive_triggers.dat" % (obj.data_folder, timestamp)
        if not os.path.exists(os.path.dirname(output_file)):
            try:
                os.makedirs(os.path.dirname(output_file))
            except OSError as exc:  # Guard against race condition
                print "Unable to create directory"
        open(output_file, 'w').close()

    instruction_text = []
    instruction_text.append("1 Send RunMode")
    instruction_text.append("10 Send EC0")
    instruction_text.append("10 Send BC0")
    instruction_text.append("%i Send_Repeat LV1A %i %i" % (nr_of_bc_between_triggers, nr_of_triggers, nr_of_bc_between_triggers))
    instruction_text.append("100 Send ReSync")

    # Write the instructions to the file.
    output_file_name = "./routines/%s/instruction_list.txt" % scan_name
    with open(output_file_name, "w") as mfile:
        for item in instruction_text:
            mfile.write("%s\n" % item)
    # Generate the instruction list for the FPGA.
    generator("Consecutive Triggers", obj.write_BCd_as_fillers, obj.register)

    obj.register[65535].RUN[0] = 1
    obj.write_register(65535)
    time.sleep(1)

    ecb = 0
    bcb = 0
    if ecb == 0:
        ecb_size = 1
    elif ecb == 1:
        ecb_size = 2
    elif ecb == 2:
        ecb_size = 3
    elif ecb == 3:
        ecb_size = 1
    else:
        print "-> Invalid ECb value. Using 0."
        ecb = 0

    if bcb == 0:
        bcb_size = 2
    elif bcb == 1:
        bcb_size = 3
    else:
        print "-> Invalid BCb value. Using 0."
        bcb = 0

    ecb_max = 2**(ecb_size*8)-1
    bcb_max = 2**(bcb_size*8)-1

    obj.register[130].ECb[0] = ecb
    obj.register[130].BCb[0] = bcb
    obj.write_register(130)
    obj.register[135].ARM_DAC[0] = 100
    obj.write_register(135)
    trigger_counter = 0
    data_packet_counter = 0
    hit_counter = 0
    crc_error_counter = 0
    ec_error_counter = 0
    bc_error_counter = 0
    start = time.time()

    for k in range(0, nr_loops):
        time.sleep(0.02)
        trigger_counter += nr_of_triggers
        previous_EC = 0
        previous_BC = 0
        output = obj.interfaceFW.send_fcc("", file_name)
        flag = 0
        reply_list = []
        for i in output:
            if flag == 0:
                reply_list.append(int(i,16))
                flag = 3
            else:
                flag -= 1
        output = decode_output_data(reply_list, obj.register)
        if output[0] == "Error":
            text = "%s: %s\n" % (output[0], output[1])
            obj.add_to_interactive_screen(text)
        else:
            for i in output[3]:
                if i.type == "data_packet":
                    data_packet_counter += 1
                    if i.hit_found == 1:
                        hit_counter += 1
                    if i.crc_error == 1:
                        crc_error_counter += 1
                    ec_diff = i.EC - previous_EC
                    if ec_diff != 1:
                        if previous_EC == ecb_max and i.EC == 0:
                            pass
                        else:
                            #print ""
                            print "->EC error"
                            print "Packet: %d" % data_packet_counter
                            print "Previous EC: %d" % previous_EC
                            print "Current EC: %d" % i.EC
                            ec_error_counter += 1
                    previous_EC = i.EC
                    bc_diff = i.BC - previous_BC
                    if bc_diff != nr_of_bc_between_triggers:
                        if i.BC+(bcb_max-previous_BC) == nr_of_bc_between_triggers-1:  # -1 since counter starts from zero.
                            pass
                        else:
                            print ""
                            print "->BC error"
                            print "Packet: %d" % data_packet_counter
                            print "Previous BC: %d" % previous_BC
                            print "Current BC: %d" % i.BC
                            bc_error_counter += 1
                    previous_BC = i.BC

        stop = time.time()
        run_time = (stop - start)
        result = []
        result.append("-> %d Triggers sent." % trigger_counter)
        result.append("%d Data packets received." % data_packet_counter)
        result.append("CRC errors: %d" % crc_error_counter)
        result.append("EC errors: %d" % ec_error_counter)
        result.append("BC errors: %d" % bc_error_counter)
        result.append("Hits found: %d" % hit_counter)
        result.append("Time elapsed: %f s" % run_time)
        result.append("***************")
        if save_result == "yes":
            with open(output_file, "a") as myfile:
                for line in result:
                    print line
                    myfile.write("%s\n" % line)
    error_list = [crc_error_counter, bc_error_counter, ec_error_counter, hit_counter]
    error_sum = error_list[0] + error_list[1] + error_list[2] + error_list[3]
    if obj.database:
        obj.database.save_data_test(error_list)

    obj.register[65535].RUN[0] = 0
    obj.write_register(65535)
    print "-> %d Triggers sent." % trigger_counter
    print "%d Data packets received." % data_packet_counter
    print "CRC errors: %d" % crc_error_counter
    print "EC errors: %d" % ec_error_counter
    print "BC errors: %d" % bc_error_counter
    print "Hits found: %d" % hit_counter
    print "Time elapsed: %f s" % run_time
    obj.register[130].ECb[0] = 0
    obj.register[130].BCb[0] = 0
    obj.write_register(130)
    stop = time.time()
    duration = stop - start
    print "\nData Packet test duration: %f s\n" % duration
    return error_sum


def check_data_packet(data_packet, ec_size=1, bc_size=2, data="", szp=0):
    error = 0

    if len(data_packet[1]) == 1:
        if data_packet[1][0].crc_error == 1:
            print "crc error."
            error += 1
        if ec_size != data_packet[1][0].ec_size:
            print "Wrong EC size."
            error += 1
        if bc_size != data_packet[1][0].bc_size:
            print "Wrong BC size."
            error += 1
        if data == "empty" and data_packet[1][0].data != "":
            print "Missing data."
            error += 1
        if data != "empty" and data_packet[1][0].data == "":
            print "Found unexpected data."
            error += 1
        if data != "empty" and data != data_packet[1][0].data:
            print "Found faulty data."
            print data_packet[1][0].data
            print data
            error += 1
        if szp != data_packet[1][0].szp:
            print "Wrong header."
            error += 1
    elif len(data_packet[1]) == 0:
        print "No data packets."
    else:
        print "Too many data packets."
    return error


def test_data_packet_formatting(obj):
    temp_file = "./data/temp_register_file.reg"
    obj.save_register_values_to_file_execute(temp_file)

    timestamp = time.strftime("%Y%m%d_%H%M")
    output_file = "%s/data_packet_test/%s_data_packet_test.dat" % (obj.data_folder, timestamp)
    if not os.path.exists(os.path.dirname(output_file)):
        try:
            os.makedirs(os.path.dirname(output_file))
        except OSError as exc:  # Guard against race condition
            print "Unable to create directory"

    result = []

    obj.load_register_values_from_file_execute("./data/default_register_values.reg", multiwrite=1)

    cal_channels = [0]*128
    for k in range(0, 128, 8):
        line = "Set channel:%d to 1" % k
        print line
        result.append(line)
        cal_channels[k] = 1
        obj.register[k].cal[0] = 1
        obj.write_register(k)
    cal_channels.reverse()
    cal_channels = ''.join(str(e) for e in cal_channels)


    obj.set_fe_nominal_values()
    line =  "Set FE nominal values."
    print line
    result.append(line)

    obj.register[138].CAL_DAC[0] = 220
    obj.register[138].CAL_MODE[0] = 1
    obj.write_register(138)
    line = "Set CAL_DAC to: %d and CAL_MODE to: %d" % (obj.register[138].CAL_DAC[0], obj.register[138].CAL_MODE[0])
    print line
    result.append(line)

    obj.register[132].SEL_COMP_MODE[0] = 0
    obj.write_register(132)
    line = "Set SEL_COMP_MODE to: %d" % obj.register[132].SEL_COMP_MODE[0]
    print line
    result.append(line)

    obj.register[134].Iref[0] = 22
    obj.write_register(134)
    line = "Set Iref to: %d" % obj.register[134].Iref[0]
    print line
    result.append(line)

    obj.register[135].ZCC_DAC[0] = 10
    obj.register[135].ARM_DAC[0] = 50
    obj.write_register(135)
    line = "Set ZCC_DAC to: %d and Set ARM_DAC to: %d" % (obj.register[135].ZCC_DAC[0], obj.register[135].ARM_DAC[0])
    print line
    result.append(line)

    obj.register[139].CAL_FS[0] = 1
    obj.register[139].CAL_DUR[0] = 100
    obj.write_register(139)
    line = "Set CAL_FS to: %d and Set CAL_DUR to: %d" % (obj.register[139].CAL_FS[0], obj.register[139].CAL_DUR[0])
    print line
    result.append(line)

    obj.register[65535].RUN[0] = 1
    obj.write_register(65535)
    line = "Set RUN to: %d" % obj.register[65535].RUN[0]
    print line
    result.append(line)

    obj.register[129].ST[0] = 1
    obj.register[129].PS[0] = 0
    obj.write_register(129)
    line = "Set ST to: %d and Set PS to: %d" % (obj.register[129].ST[0], obj.register[129].PS[0])
    print line
    result.append(line)

    obj.register[130].P16[0] = 0
    obj.register[130].PAR[0] = 0
    obj.register[130].DT[0] = 0
    obj.register[130].SZP[0] = 0
    obj.register[130].SZD[0] = 0
    obj.register[130].TT[0] = 0
    obj.register[130].ECb[0] = 0
    obj.register[130].BCb[0] = 0
    obj.write_register(130)

    obj.send_fcc("RunMode", verbose="no")

    obj.send_fcc("CalPulse", verbose="no")

    error = 0
    line = "########START TEST########"
    print line
    result.append(line)

    line = "->Test EC counter."
    print line
    result.append(line)

    obj.register[130].TT[0] = 1
    obj.write_register(130)
    output_data = obj.send_fcc("CalPulse", verbose="no")
    error += check_data_packet(output_data, bc_size=0, data=cal_channels)
    obj.register[130].ECb[0] = 1
    obj.write_register(130)
    output_data = obj.send_fcc("CalPulse", verbose="no")
    error += check_data_packet(output_data, ec_size=2, bc_size=0, data=cal_channels)
    obj.register[130].ECb[0] = 2
    obj.write_register(130)
    output_data = obj.send_fcc("CalPulse", verbose="no")
    error += check_data_packet(output_data, ec_size=3, bc_size=0, data=cal_channels)
    obj.register[130].ECb[0] = 3
    obj.write_register(130)
    output_data = obj.send_fcc("CalPulse", verbose="no")
    error += check_data_packet(output_data, ec_size=1, bc_size=0, data=cal_channels)
    obj.register[130].ECb[0] = 0
    obj.write_register(130)

    line = "->Test BC counter."
    print line
    result.append(line)

    obj.register[130].TT[0] = 2
    obj.write_register(130)
    output = obj.send_fcc("CalPulse", verbose="no")
    error += check_data_packet(output, ec_size=0, data=cal_channels)
    obj.register[130].BCb[0] = 1
    obj.write_register(130)
    output_data = obj.send_fcc("CalPulse", verbose="no")
    error += check_data_packet(output_data, ec_size=0, bc_size=3, data=cal_channels)
    obj.register[130].BCb[0] = 0
    obj.write_register(130)
    obj.register[130].TT[0] = 0

    line = "->Test SZD."
    print line

    result.append(line)
    obj.register[130].SZD[0] = 1
    obj.write_register(130)
    output = obj.send_fcc("CalPulse", verbose="no")
    error += check_data_packet(output, data=cal_channels)

    obj.register[129].ST[0] = 0
    obj.write_register(129)
    output = obj.send_fcc("LV1A", verbose="no")
    error += check_data_packet(output, data="empty")
    obj.register[130].SZD[0] = 0

    line = "->Test SZP."
    print line
    result.append(line)
    obj.register[130].SZP[0] = 1
    obj.write_register(130)
    output = obj.send_fcc("LV1A", verbose="no")
    error += check_data_packet(output, ec_size=0, bc_size=0, data="empty", szp=1)
    obj.register[129].ST[0] = 1
    obj.write_register(129)
    output = obj.send_fcc("CalPulse", verbose="no")
    error += check_data_packet(output, data=cal_channels)
    obj.register[130].SZP[0] = 0

    line = "->Test SPZS."
    print line
    result.append(line)

    obj.register[130].DT[0] = 1
    for i in range(0, 16):
        obj.register[130].PAR[0] = i
        obj.write_register(130)
        output = obj.send_fcc("CalPulse", verbose="no")
        comp_data = cal_channels[:8*(i+1)] + '0' * 8*(15-i)
        error += check_data_packet(output, data=comp_data)


    line = "########END TEST########"
    print line
    result.append(line)
    line = "-> Errors found: %d" % error
    print line
    result.append(line)

    with open(output_file, "a") as myfile:
        for line in result:
            myfile.write("%s\n" % line)

    print "Writing back previous register values."
    obj.load_register_values_from_file_execute(temp_file, multiwrite=1)
    print "Done."


def charge_distribution_on_neighbouring_ch(obj, nr_loops=10):
    target_channel = 64
    nr_of_triggers = 4000
    nr_of_bc_between_triggers = 300
    timestamp = time.strftime("%Y%m%d_%H%M")
    scan_name = "charge_distribution"
    file_name = "./routines/%s/FPGA_instruction_list.txt" % scan_name
    output_file = "%s/concecutive_tiggers/%s_concecutive_triggers.dat" % (obj.data_folder, timestamp)

    instruction_text = []
    instruction_text.append("1 Send RunMode")
    instruction_text.append("1000 Send_Repeat CalPulse_LV1A 10 3000 5")
    instruction_text.append("1000 Send SCOnly")

    # Write the instructions to the file.
    output_file_name = "./routines/%s/instruction_list.txt" % scan_name
    with open(output_file_name, "w") as mfile:
        for item in instruction_text:
            mfile.write("%s\n" % item)
    # Generate the instruction list for the FPGA.
    generator("charge distribution", obj.write_BCd_as_fillers, obj.register)


    print "1"
    obj.set_fe_nominal_values()

    register[138].CAL_MODE[0] = 1
    register[138].CAL_DAC[0] = 200
    obj.write_register(138)
    print "2"
    obj.register[132].PT[0] = 15
    obj.register[132].SEL_COMP_MODE[0] = 1
    obj.write_register(132)
    print "3"
    obj.register[135].ZCC_DAC[0] = 10
    obj.register[135].ARM_DAC[0] = 40
    obj.write_register(135)
    print "4"
    obj.register[139].CAL_DUR[0] = 200
    obj.write_register(139)
    print "5"
    obj.register[129].ST[0] = 0
    obj.register[129].PS[0] = 7
    obj.write_register(129)
    print "6"
    obj.register[target_channel].cal[0] = 1
    print "7"
    time.sleep(1)
    obj.write_register(target_channel)
    print "8"

    register[138].CAL_DAC[0] = 0
    obj.write_register(138)

    obj.register[65535].RUN[0] = 1
    obj.write_register(65535)
    time.sleep(1)
    start = time.time()
    print "Start"
    hits_on_channnels = [0]*128
    hits_on_channnels_normalized = [0]*128
    for k in range(0, 15):
        print "Enter loop"
        output = obj.interfaceFW.launch(obj.register, file_name, obj.COM_port, 1, save_data=1, obj=obj)
        print "Got output."
        if output[0] == "Error":
            text = "%s: %s\n" % (output[0], output[1])
            obj.add_to_interactive_screen(text)
        else:
            for i in output[3]:
                print i.data
                if i.type == "data_packet":
                    for j, hit in enumerate(i.data):
                        if hit == "1":
                            hits_on_channnels[j] += 1
        for i, item in enumerate(hits_on_channnels):
            hits_on_channnels_normalized[i] = item/k

    print hits_on_channnels_normalized
    print "set off channel"
    time.sleep(1)
    obj.register[target_channel].cal[0] = 0
    obj.write_register(target_channel)
    print "channel set off"
    obj.register[65535].RUN[0] = 0
    obj.write_register(65535)
    time.sleep(1)
    stop = time.time()
    run_time = (stop - start) / 60
    print run_time


def channel_histogram(obj):

    trigger_pattern = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

    for k in range(0, 128):
        obj.register[k].cal[0] = trigger_pattern[k]
        obj.write_register(k)
        time.sleep(0.05)


    obj.register[138].CAL_DAC[0] = 100
    obj.register[138].CAL_MODE[0] = 1
    obj.write_register(138)

    obj.register[132].SEL_COMP_MODE[0] = 1
    obj.write_register(132)

    obj.register[135].ZCC_DAC[0] = 10
    obj.register[135].ARM_DAC[0] = 150
    obj.write_register(135)

    obj.register[139].CAL_FS[0] = 1
    obj.register[139].CAL_DUR[0] = 100
    obj.write_register(139)

    obj.register[65535].RUN[0] = 1
    obj.write_register(65535)

    obj.register[129].ST[0] = 1
    obj.register[129].PS[0] = 0
    obj.write_register(129)

    obj.send_fcc("RunMode")
    lv1a = FCC_LUT["LV1A"]
    calpulse = FCC_LUT["CalPulse"]

    command_encoded = [calpulse]
    output = obj.interfaceFW.send_fcc(command_encoded)
    data_packet = []
    hit_map = [0]*128
    for k in range(0, 100):
        if output[0] == '0x1e':
            i = 0
            for byte in output:
                if i == 4:
                    data_bit = dec_to_bin_with_stuffing(int(byte, 16), 8)
                    data_packet.extend(data_bit)
                    #print ''.join(str(e) for e in data_bit)
                    i = 0
                i += 1
            data = data_packet[24:152]
            hit_map = np.add(hit_map, data)
        else:
            print "No data received."
            break

    print hit_map

    return output
    self.send_fcc("SCOnly")
