import math
import time
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy
import csv


def scurve_all_ch_execute(obj, scan_name):
    start = time.time()

    modified = scan_name.replace(" ", "_")
    file_name = "./routines/%s/FPGA_instruction_list.txt" % modified

    # Setting the needed registers.
    obj.set_FE_nominal_values()

    obj.register[130].DT[0] = 0
    obj.write_register(130)


    # register[138].CAL_MODE[0] = 2
    # obj.write_register(138)

    obj.register[132].SEL_COMP_MODE[0] = 0
    obj.write_register(132)

    obj.register[134].Iref[0] = 29
    obj.write_register(134)

    obj.register[135].ZCC_DAC[0] = 10
    obj.register[135].ARM_DAC[0] = 100
    obj.write_register(135)

    obj.register[139].CAL_FS[0] = 0
    obj.register[139].CAL_DUR[0] = 200
    obj.write_register(139)

    obj.register[65535].RUN[0] = 1
    obj.write_register(65535)
    time.sleep(1)

    obj.register[129].ST[0] = 0
    obj.register[129].PS[0] = 7
    obj.write_register(129)

    all_ch_data = []
    all_ch_data.append(["", "255-CAL_DAC"])
    all_ch_data.append(["Channel", 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35])
    for k in range(0, 128):
        print "Channel: %d" % k
        while True:
            # Set calibration to right channel.
            obj.register[k].cal[0] = 1
            obj.write_register(k)
            time.sleep(0.5)

            scurve_data = []
            # Run the predefined routine.
            output = obj.interfaceFW.launch(obj.register, file_name, obj.COM_port, 1)

            # Check the received data from the routine.
            if output[0] == "Error":
                text = "%s: %s\n" % (output[0], output[1])
                obj.add_to_interactive_screen(text)
            else:
                hits = 0
                for i in output[3]:
                    if i.type == "IPbus":
                        scurve_data.append(hits)
                        hits = 0
                    elif i.type == "data_packet":
                        if i.data[127 - k] == "1":
                            hits += 1
            print scurve_data

            # Check that there is enough data and it is not all zeroes.
            if len(scurve_data) != 22:
                print "Not enough values, trying again."
                continue
            if scurve_data[3] == 0:
                print "All zeroes, trying again."
                continue
            if len(scurve_data) == 22 and scurve_data[3] != 0:
                break

        # Unset the calibration to the channel.
        obj.register[k].cal[0] = 0
        obj.write_register(k)
        time.sleep(0.5)

        # Modify the decoded data.
        saved_data = []
        saved_data.append(k)
        scurve = scurve_data[2:]
        scurve.reverse()
        saved_data.extend(scurve)
        all_ch_data.append(saved_data)

    # Save the results.
    timestamp = time.strftime("%Y%m%d_%H%M")
    folder = "./results/"
    text = "Results were saved to the folder:\n %s \n" % folder

    with open("%s%sS-curve_data.csv" % (folder, timestamp), "wb") as f:
        writer = csv.writer(f)
        writer.writerows(all_ch_data)
    obj.add_to_interactive_screen(text)


    # Analyze data.
    scurve_analyze(obj, all_ch_data, folder)
    stop = time.time()
    run_time = (stop - start) / 60
    text = "Run time (minutes): %f\n" % run_time
    obj.add_to_interactive_screen(text)


def scurve_analyze(obj, scurve_data, folder):
    timestamp = time.strftime("%d.%m.%Y %H:%M")
    full_data = []
    mean_list = []
    rms_list = []
    full_data.append([""])
    full_data.append(["Differential data"])
    full_data.append(["", "255-CAL_DAC"])
    full_data.append(
        ["Channel", 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, "mean", "RMS"])
    dac_values = scurve_data[1][1:]

    fig = plt.figure(figsize=(10, 20))
    sub1 = plt.subplot(411)

    for i in range(2, 130):
        diff = []

        mean_calc = 0
        summ = 0
        data = scurve_data[i][1:]
        channel = scurve_data[i][0]
        l = 0
        diff.append(channel)
        diff.append("")
        for j in data:
            if l != 0:
                diff_value = j - previous_value
                diff.append(diff_value)
                mean_calc += dac_values[l] * diff_value
                summ += diff_value
            previous_value = j
            l += 1
        mean = mean_calc / float(summ)
        mean_list.append(mean)
        l = 1
        rms = 0
        for r in diff[2:]:
            rms += r * (mean - dac_values[l]) ** 2
            l += 1
        rms = math.sqrt(rms / summ)
        rms_list.append(rms)
        diff.append(mean)
        diff.append(rms)
        full_data.append(diff)
        plt.plot(dac_values, data)

    rms_mean = numpy.mean(rms_list)
    rms_rms = numpy.std(rms_list)

    mean_mean = numpy.mean(mean_list)
    mean_rms = numpy.std(mean_list)

    sub1.set_xlabel('255-CAL_DAC')
    sub1.set_ylabel('%')
    sub1.set_title('S-curves of all channels')
    sub1.grid(True)
    text = "%s \n S-curves, 128 channels, HG, 25 ns." % timestamp
    sub1.text(25, 140, text, horizontalalignment='center', verticalalignment='center')

    sub2 = plt.subplot(413)
    sub2.plot(range(0, 128), rms_list)
    sub2.set_xlabel('Channel')
    sub2.set_ylabel('RMS')
    sub2.set_title('RMS of all channels')
    sub2.grid(True)
    text = "mean: %.2f RMS: %.2f" % (rms_mean, rms_rms)
    sub2.text(10, 0.85, text, horizontalalignment='center', verticalalignment='center', bbox=dict(alpha=0.5))

    sub3 = plt.subplot(412)
    sub3.plot(range(0, 128), mean_list)
    sub3.set_xlabel('Channel')
    sub3.set_ylabel('255-CAL_DAC')
    sub3.set_title('mean of all channels')
    sub3.grid(True)
    text = "Mean: %.2f RMS: %.2f" % (mean_mean, mean_rms)
    sub3.text(10, 31, text, horizontalalignment='center', verticalalignment='center', bbox=dict(alpha=0.5))

    sub4 = plt.subplot(427)
    n, bins, patches = sub4.hist(mean_list, bins=30)
    # y = mlab.normpdf(bins, mean_mean, mean_rms)
    # sub4.plot(bins, y, 'r--', linewidth=1)

    sub5 = plt.subplot(428)
    n, bins, patches = sub5.hist(rms_list, bins=30)
    # y = mlab.normpdf(bins, rms_mean, rms_rms)
    # sub5.plot(bins, y, 'r--', linewidth=1)

    fig.subplots_adjust(hspace=.5)

    timestamp = time.strftime("%Y%m%d_%H%M")

    fig.savefig("%s%sS-curve_plot.pdf" % (folder, timestamp))

    with open("%s%sS-curve_data.csv" % (folder, timestamp), "ab") as f:
        writer = csv.writer(f)
        writer.writerows(full_data)

    text = "Results were saved to the folder:\n %s \n" % folder
    obj.add_to_interactive_screen(text)


def scurve_execute(obj, scan_name):

    start = time.time()
    channel = 127
    # Set calibration to right channel.
    obj.register[channel].cal[0] = 1
    obj.write_register(channel)

    obj.set_FE_nominal_values()

    obj.register[130].DT[0] = 0
    obj.write_register(130)

    # register[138].CAL_MODE[0] = 2
    # obj.write_register(138)

    obj.register[132].SEL_COMP_MODE[0] = 0
    obj.write_register(132)

    obj.register[134].Iref[0] = 29
    obj.write_register(134)

    obj.register[135].ZCC_DAC[0] = 10
    obj.register[135].ARM_DAC[0] = 100
    obj.write_register(135)

    obj.register[139].CAL_FS[0] = 0
    obj.register[139].CAL_DUR[0] = 200
    obj.write_register(139)

    obj.register[65535].RUN[0] = 1
    obj.write_register(65535)
    time.sleep(1)

    obj.register[129].ST[0] = 0
    obj.register[129].PS[0] = 7
    obj.write_register(129)

    modified = scan_name.replace(" ", "_")
    file_name = "./routines/%s/FPGA_instruction_list.txt" % modified
    scurve_data = []

    output = obj.interfaceFW.launch(obj.register, file_name, obj.COM_port)
    if output[0] == "Error":
        text = "%s: %s\n" % (output[0], output[1])
        obj.add_to_interactive_screen(text)
    else:
        hits = 0
        dac = 38
        for i in output[3]:
            if i.type == "IPbus":
                dac -= 1
                scurve_data.append([dac, hits])
                hits = 0
            elif i.type == "data_packet":
                if i.data[127 - channel] == "1":
                    hits += 1

    text = "CAL_DAC|HITS \n"
    obj.add_to_interactive_screen(text)
    for k in scurve_data[2:]:
            text = "%d %d\n" % (k[0], k[1])
            obj.add_to_interactive_screen(text)

    obj.register[channel].cal[0] = 0
    obj.write_register(channel)

    stop = time.time()
    run_time = (stop - start) / 60
    text = "Run time (minutes): %f" % run_time
    obj.add_to_interactive_screen(text)


def set_up_trigger_pattern(obj, option):



    if option == 2:
        text = "Clearing trigger patterns\n"
        obj.add_to_interactive_screen(text)
        for k in range(0, 128):
                print "Clear channel: %d" %k
                obj.register[k].cal[0] = 0
                obj.write_register(k)
                time.sleep(0.1)
        obj.register[130].DT[0] = 0
        obj.write_register(130)

        obj.register[138].CAL_DAC[0] = 0
        obj.register[138].CAL_MODE[0] = 0
        obj.write_register(138)

        obj.register[132].SEL_COMP_MODE[0] = 0
        obj.write_register(132)

        obj.register[139].CAL_FS[0] = 0
        obj.register[139].CAL_DUR[0] = 0
        obj.write_register(139)

        obj.register[65535].RUN[0] = 0
        obj.write_register(65535)

        obj.register[129].ST[0] = 0
        obj.register[129].PS[0] = 0
        obj.write_register(129)
    else:

        if option == 0:
            text = "Setting trigger pattern 1.\n"
            obj.add_to_interactive_screen(text)
            for k in range(0, 128, 2):
                print "Set channel:%d" % k
                obj.register[k].cal[0] = 1
                obj.write_register(k)

        if option == 1:
            text = "Setting trigger pattern 2.\n"
            obj.add_to_interactive_screen(text)
            for k in range(1, 128, 2):
                print "Set channel:%d" % k
                obj.register[k].cal[0] = 1
                obj.write_register(k)

        obj.set_FE_nominal_values()
        print "Set FE nominal values."

        obj.register[130].DT[0] = 0
        obj.write_register(130)

        obj.register[138].CAL_DAC[0] = 200
        obj.register[138].CAL_MODE[0] = 1
        obj.write_register(138)
        print "Set CAL_DAC to: %d and CAL_MODE to: %d" % (obj.register[138].CAL_DAC[0], obj.register[138].CAL_MODE[0])

        obj.register[132].SEL_COMP_MODE[0] = 0
        obj.write_register(132)
        print "Set SEL_COMP_MODE to: %d" % obj.register[132].SEL_COMP_MODE[0]

        obj.register[134].Iref[0] = 29
        obj.write_register(134)
        print "Set Iref to: %d" % obj.register[134].Iref[0]

        obj.register[135].ZCC_DAC[0] = 10
        obj.register[135].ARM_DAC[0] = 100
        obj.write_register(135)
        print "Set ZCC_DAC to: %d and Set ARM_DAC to: %d" % (obj.register[135].ZCC_DAC[0], obj.register[135].ARM_DAC[0])

        obj.register[139].CAL_FS[0] = 3
        obj.register[139].CAL_DUR[0] = 100
        obj.write_register(139)
        print "Set CAL_FS to: %d and Set CAL_DUR to: %d" % (obj.register[139].CAL_FS[0], obj.register[139].CAL_DUR[0])

        obj.register[65535].RUN[0] = 1
        obj.write_register(65535)
        print "Set RUN to: %d" % obj.register[65535].RUN[0]

        obj.register[129].ST[0] = 1
        obj.register[129].PS[0] = 0
        obj.write_register(129)
        print "Set ST to: %d and Set PS to: %d" % (obj.register[129].ST[0], obj.register[129].PS[0])







