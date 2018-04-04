############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################


import ROOT as r
import math
import time
import matplotlib.pyplot as plt
import numpy
import csv
from test_system_functions import *
from calibration_routines import *
from datapacket_routines import *
from trigger_routines import *
from generator import *


def find_threshold(obj):
    thresholds = []
    arm_values = []
    for i, arm_dac in enumerate(range(20, 220, 20)):
        print "ARM_DAC:"
        print arm_dac
        arm_values.append(arm_dac)
        if arm_dac < 180:
            dac_start = 250 - 5 * i
            dac_stop = 230 - 5 * i
        elif arm_dac == 180:
            dac_start = 200
            dac_stop = 180
        elif arm_dac == 200:
            dac_start = 190
            dac_stop = 170
        elif arm_dac == 220:
            dac_start = 170
            dac_stop = 150
        elif arm_dac == 240:
            dac_start = 160
            dac_stop = 140
        print dac_start
        print dac_stop
        output = scurve_all_ch_execute(obj, "S-curve", arm_dac=arm_dac, dac_range=[dac_stop, dac_start])
        thresholds.append(output[0])
    print arm_values
    print thresholds
    fig = plt.figure()
    plt.plot(arm_values, thresholds)
    plt.plot(arm_values, thresholds, 'x')
    plt.grid(True)
    plt.xlabel('ARM_DAC[DAC]')
    plt.ylabel('Threshold [fC]')
    #plt.xlim(0, 10)
    #plt.legend()
    plt.title("Threshold vs. ARM_DAC")
    timestamp = time.strftime("%Y%m%d_%H%M")
    filename = "%s/threshold/%sthresholds.png" % (obj.data_folder, timestamp)
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            print "Unable to create directory"
    fig.savefig(filename)


def scurve_all_ch_execute(obj, scan_name, arm_dac=100, ch=[0, 127], ch_step=1, configuration="yes",
                          dac_range=[220, 240], delay=50, bc_between_calpulses=2000, pulsestretch=3, latency=45,
                          cal_phi=0, folder="scurve", triggers=100):
    mean_th_fc = "n"
    all_ch_data = "n"
    noisy_channels = "n"
    thr_list = "n"

    if obj.cal_dac_fcM == 0 or obj.cal_dac_fcB == 0:
        print "CAL_DAC not calibrated."
    else:
        start = time.time()

        # Set channels and Cal dac range.
        start_ch = ch[0]
        stop_ch = ch[1]
        start_dac_value = dac_range[0]
        stop_dac_value = dac_range[1]
        print "Running S-curves for channels: %i-%i, for CAL_DAC range: %i-%i:" % (start_ch, stop_ch, start_dac_value, stop_dac_value)
        samples_per_dac_value = 100

        # Create list of cal dac values.
        cal_dac_values = range(start_dac_value, stop_dac_value+1)


        obj.register[131].TP_FE[0] = 7
        obj.write_register(131)

        cal_dac_values.reverse()
        cal_dac_values[:] = [255 - x for x in cal_dac_values]
        cal_dac_values[:] = [obj.cal_dac_fcM * x + obj.cal_dac_fcB for x in cal_dac_values]

        # Create a list of channels the s-curve is run on.
        channels = range(start_ch, stop_ch+1)

        # Launch S-curve routine in firmware.
        scurve_data = obj.interfaceFW.run_scurve(start_ch, stop_ch, start_dac_value, stop_dac_value, triggers=triggers, arm_dac=arm_dac)

        # Plot the s-curve data.
        if configuration == "yes":
            timestamp = time.strftime("%Y%m%d_%H%M")
            modified = scan_name.replace(" ", "_")
            text = "Results were saved to the folder:\n %s \n" % folder
            filename = "%s/%s/%sscurves.png" % (obj.data_folder, folder, timestamp)
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc:  # Guard against race condition
                    print "Unable to create directory"
            obj.add_to_interactive_screen(text)
            fig = plt.figure()
            print scurve_data
            print cal_dac_values
            for i in range(2, len(scurve_data)):
                plt.plot(cal_dac_values, scurve_data[i])
            plt.grid(True)
            plt.ylabel('[%]')
            plt.xlabel('Charge [fC]')
            plt.xlim(0, 10)
            plt.title(modified)
            fig.savefig(filename)

        # Analyze data.
        mean_th_fc, mean_enc_fc, noisy_channels, enc_list, thr_list = scurve_analyze(obj, cal_dac_values, channels, scurve_data, folder, save=configuration)

        # Save data to database.
        if obj.database:
            obj.database.save_mean_threshold(mean_th_fc)
            obj.database.save_mean_enc(mean_enc_fc)
            obj.database.save_threshold_data(thr_list)
            obj.database.save_enc_data(enc_list)
            obj.database.save_noisy_channels(noisy_channels)

        # Print routine duration.
        stop = time.time()
        run_time = (stop - start) / 60
        text = "Run time (minutes): %f\n" % run_time
        obj.add_to_interactive_screen(text)
    return [mean_th_fc, all_ch_data, noisy_channels, thr_list]


def scurve_analyze(obj, dac_values, channels, scurve_data, folder, save="yes"):

    r.gROOT.SetBatch(True)

    Nhits_h = {}
    Nev_h = {}

    for i in range(0, len(scurve_data)):
        data = scurve_data[i][:]
        channel = channels[i]

        Nhits_h[channel] = r.TH1D('Nhits%i_h' % channel, 'Nhits%i_h'% channel, len(dac_values)-1, dac_values[0], dac_values[-1])
        Nev_h[channel] = r.TH1D('Nev%i_h' % channel, 'Nev%i_h' % channel, len(dac_values)-1, dac_values[0], dac_values[-1])

        for j, Nhits in enumerate(data):
            Nhits_h[channel].AddBinContent(j, Nhits)
            Nev_h[channel].AddBinContent(j, 100)

    # Create directory.
    if save == "yes":
        timestamp = time.strftime("%Y%m%d_%H%M%s")
        filename = '%s/%s/scurves%s.root' % (obj.data_folder, folder, timestamp)
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                print "Unable to create directory"
        outF = r.TFile(filename, 'RECREATE')

    enc_h = r.TH1D('enc_h', 'ENC of all Channels;ENC [fC];Number of Channels', 100, 0.0, 0.5)
    thr_h = r.TH1D('thr_h', 'Threshold of all Channels;Thr [fC];Number of Channels', 160, 0.0, 10.0)
    chi2_h = r.TH1D('chi2_h', 'Fit #chi^{2};#chi^{2};Number of Channels / 0.001', 100, 0.0, 1.0)
    enc_list = []
    thr_list = []
    scurves_ag = {}

    # Open file.
    if save == "yes":
        txtOutF = open('%s/%s/scurveFits%s.dat' % (obj.data_folder, folder, timestamp), 'w')
        txtOutF.write('CH/I:thr/D:enc/D\n')
    noisy_channels = []
    for ch in Nhits_h:
        scurves_ag[ch] = r.TGraphAsymmErrors(Nhits_h[ch], Nev_h[ch])
        scurves_ag[ch].SetName('scurve%i_ag' % ch)
        fit_f = fitScurve(scurves_ag[ch])
        # Write to file
        if save == "yes":
            txtOutF.write('%i\t%f\t%f\n' % (ch, fit_f.GetParameter(0), fit_f.GetParameter(1)))
            scurves_ag[ch].Write()
        thr_fc = fit_f.GetParameter(0)
        enc_fc = fit_f.GetParameter(1)
        if enc_fc >= 1:      # Limit for noisy channel.
            noisy_channels.append(ch)
        else:
            # Fill the histograms.
            thr_h.Fill(fit_f.GetParameter(0))
            enc_h.Fill(fit_f.GetParameter(1))

        enc_list.append(enc_fc)
        thr_list.append(thr_fc)
        chi2_h.Fill(fit_f.GetChisquare())
        pass
    if save == "yes":
        txtOutF.close()

    cc = r.TCanvas('canv', 'canv', 1000, 1000)

    mean_th = thr_h.GetMean()
    mean_enc = enc_h.GetMean()

    # Plot.
    print "Mean Threshold: %f" % mean_th
    print "Mean enc: %f" % mean_enc
    print "Noisy Channels:"
    print noisy_channels

    text = "S-curve results:\n"
    text += "Mean Threshold: %f\n" % mean_th
    text += "Mean enc: %f\n" % mean_enc
    text += "Noisy Channels: %i\n" % len(noisy_channels)
    obj.add_to_interactive_screen(text)
    if save == "yes":
        drawHisto(thr_h, cc, '%s/%s/threshHiso%s.png' % (obj.data_folder, folder, timestamp))
        thr_h.Write()
        drawHisto(enc_h, cc, '%s/%s/encHisto%s.png' % (obj.data_folder, folder, timestamp))
        enc_h.Write()
        drawHisto(chi2_h, cc, '%s/%s/chi2Histo%s.png' % (obj.data_folder, folder, timestamp))
        chi2_h.Write()
        outF.Close()

    return mean_th, mean_enc, noisy_channels, enc_list, thr_list


def drawHisto(hist, canv, filename):
    canv.cd()
    hist.SetLineWidth(2)
    hist.GetXaxis().CenterTitle()
    hist.GetYaxis().CenterTitle()
    hist.Draw()
    canv.SaveAs(filename)
    

def fitScurve(scurve_g):
    import copy
    erf_f = r.TF1('erf_f', '0.5*TMath::Erf((x-[0])/(TMath::Sqrt(2)*[1]))+0.5', 0.0, 80.0)
    minChi2 = 9999.9
    bestI = -1
    for i in range(20):
        erf_f.SetParameter(0, 1.0*i+15.0)
        erf_f.SetParameter(1, 2.0)
        scurve_g.Fit(erf_f, 'Q')
        chi2 = erf_f.GetChisquare()
        if chi2 < minChi2 and chi2 > 0.0:
            bestI = i
            minChi2 = chi2
            bestFit_f = copy.deepcopy(erf_f)
            pass
        pass
    erf_f.SetParameter(0, 2.0*bestI+1.0)
    erf_f.SetParameter(1, 2.0)
    scurve_g.Fit(erf_f, 'Q')
    return bestFit_f


def scan_execute(obj, scan_name, scan_nr, dac_size, plot=1,):

    if obj.adcM == 0:
        text = "\nADCs are not calibrated. Run ADC calibration first.\n"
        obj.add_to_interactive_screen(text)
        output = "error"
    else:
        start = time.time()

        reg_values = []
        scan_values0 = []
        scan_values1 = []
        dac_values = []
        scan_values0_adccount = []
        scan_values1_adccount = []
        modified = scan_name.replace(" ", "_")
        file_name = "./routines/%s/FPGA_instruction_list.txt" % modified

        output = obj.interfaceFW.run_dac_scan(0, 1, 2**dac_size-1, scan_nr)

        if output[0] == "Error":
            text = "%s: %s\n" % (output[0], output[1])
            obj.add_to_interactive_screen(text)
        else:
            adc_flag = 0
            int_adc0_values = []
            int_adc1_values = []
            for value in output:
                if adc_flag == 0:
                    value_lsb = value[2:]
                    if len(value_lsb) == 1:
                        value_lsb = "0" + value_lsb
                    adc_flag = 1
                elif adc_flag == 1:
                    ivalue = value + value_lsb
                    ivalue_dec = int(ivalue, 16)
                    dac_values.append(ivalue_dec)
                    ivalue = ""
                    adc_flag = 2
                elif adc_flag == 2:
                    value_lsb = value[2:]
                    if len(value_lsb) == 1:
                        value_lsb = "0"+value_lsb
                    adc_flag = 3
                elif adc_flag == 3:
                    ivalue = value + value_lsb
                    ivalue_dec = int(ivalue, 16)
                    int_adc0_values.append(obj.adc0M * ivalue_dec + obj.adc0B)
                    ivalue = ""
                    adc_flag = 4
                elif adc_flag == 4:
                    value_lsb = value[2:]
                    if len(value_lsb) == 1:
                        value_lsb = "0"+value_lsb
                    adc_flag = 5
                elif adc_flag == 5:
                    ivalue = value + value_lsb
                    ivalue_dec = int(ivalue, 16)
                    int_adc1_values.append(obj.adc1M * ivalue_dec + obj.adc1B)
                    ivalue = ""
                    adc_flag = 0
        # Save the results.
        if obj.database:
            obj.database.save_dac_data(modified[:-5], "ADC0", int_adc0_values)
            obj.database.save_dac_data(modified[:-5], "ADC1", int_adc1_values)

        data = [reg_values, scan_values0, scan_values1]
        timestamp = time.strftime("%Y%m%d%H%M")
        filename = "%s/dac_scans/%s_%s_scan_data.dat" % (obj.data_folder, timestamp, modified)
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                print "Unable to create directory"
        text = "Results were saved to the folder:\n %s \n" % filename
        obj.add_to_interactive_screen(text)

        outF = open(filename, "w")
        outF.write("regVal/I:ADC0/I:ADC1/I\n")
        for i, regVal in enumerate(reg_values):
            outF.write('%i\t%i\t%i\n' % (regVal, scan_values0[i], scan_values1[i]))
            pass
        outF.close()

        filename = "%s/dac_scans/%s_%s_scan.png" % (obj.data_folder, timestamp, modified)
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                print "Unable to create directory"
        if plot == 1:
            #fig = plt.figure(1)
            plt.clf()
            plt.plot(dac_values, int_adc0_values, label="ADC0")
            plt.plot(dac_values, int_adc1_values, label="ADC1")
            #plt.ylabel('voltage [mV]')
            plt.ylabel('ADC counts')
            plt.xlabel('DAC counts')
            plt.legend()
            plt.title(modified)
            plt.grid(True)
            plt.savefig(filename)
            #plt.close(fig)

        stop = time.time()
        run_time = (stop - start)
        text = "Scan duration: %f s\n" % run_time
        obj.add_to_interactive_screen(text)

    return output


def scurve_analyze_one_ch(scurve_data):
    dac_values = scurve_data[1][1:]

    Nhits_h = r.TH1D('Nhitsi_h', 'Nhitsi_h', 256, -0.5, 255.5)
    Nev_h = r.TH1D('Nevi_h', 'Nevi_h', 256, -0.5, 255.5)

    data = scurve_data[2][1:]

    for j, Nhits in enumerate(data):
        Nhits_h.AddBinContent(dac_values[j] - 1, Nhits)
        Nev_h.AddBinContent(dac_values[j] - 1, 100)

    scurves_ag = r.TGraphAsymmErrors(Nhits_h, Nev_h)
    scurves_ag.SetName('scurvei_ag')
    fit_f = fitScurve(scurves_ag)
    thr_h = fit_f.GetParameter(0)

    return thr_h


def adjust_local_thresholds(obj):
    start = time.time()
    # Measure the mean threshold of the channels, that will be used as a target.
    mean_threshold, all_ch_data, noisy_channels, thr_list = scurve_all_ch_execute(obj, "S-curve")
    correction = []
    print "Found the mean threshold for the 128 channels: %f" % mean_threshold
    for k in range(0, 128):
        obj.send_reset()
        obj.send_sync()
        thresholds = []
        diff_values = []

        # Read the current dac values
        #obj.read_register(k)
        print "Adjusting the channel %d local arm_dac." % k
        output = scurve_all_ch_execute(obj, "S-curve", arm_dac=100, ch=[k, k], configuration="no", triggers=250)
        threshold = output[0]
        print "Threshold: %f, target: %f. DAC: %d" % (threshold, mean_threshold, obj.register[k].arm_dac[0])
        previous_diff = abs(mean_threshold - threshold)
        previous_value = 0
        thresholds.append(threshold)
        diff_values.append(previous_diff)
        if threshold < mean_threshold:
            print "->Value too low, increase arm_dac register."
            obj.register[k].arm_dac[0] = 0
            obj.write_register(k)
            max_value = 63
            direction = "up"
        if threshold > mean_threshold:
            print "->Value too high, decrease arm_dac register."
            obj.register[k].arm_dac[0] = 64
            obj.write_register(k)
            max_value = 128
            direction = "down"

        while True:
            obj.register[k].arm_dac[0] += 1
            obj.write_register(k)

            output = scurve_all_ch_execute(obj, "S-curve", arm_dac=100, ch=[k, k], configuration="no", triggers=250)
            threshold = output[0]
            if abs(mean_threshold - threshold) > 5:
                print "Broken channel."
                break
            print "Threshold: %f, target: %f. DAC: %d" % (threshold, mean_threshold, obj.register[k].arm_dac[0])
            thresholds.append(threshold)
            new_diff = abs(mean_threshold - threshold)
            diff_values.append(new_diff)
            if direction == "up" and threshold > mean_threshold:
                if previous_diff < new_diff:
                    print "->Difference increasing. Choose previous value: %d." % previous_value
                    obj.register[k].arm_dac[0] = previous_value

                print "-> Channel calibrated."
                correction.append(obj.register[k].arm_dac[0])
                break
            if direction == "down" and threshold < mean_threshold:
                if previous_diff < new_diff:
                    print "->Difference increasing. Choose previous value: %d." % previous_value
                    obj.register[k].arm_dac[0] = previous_value
                print "-> Channel calibrated."
                correction.append(obj.register[k].arm_dac[0])
                break

            previous_value = obj.register[k].arm_dac[0]
            if previous_value == max_value-1:
                print "Channel could not be calibrated."
                break
            previous_diff = new_diff

    # Save the channel calibration settings to a file.
    open("./data/channel_registers.dat", 'w').close()
    for register_nr in range(0, 128):
        data = []
        for x in register[register_nr].reg_array:
            data.extend(dec_to_bin_with_stuffing(x[0], x[1]))
        data = ''.join(str(e) for e in data)
        with open("./data/channel_registers.dat", "a") as mfile:
            mfile.write("%s\n" % data)

    stop = time.time()
    run_time = (stop - start) / 60
    print "Run time (minutes): %f\n" % run_time
    print correction


def gain_measurement(obj):

    start = time.time()

    obj.register[65535].RUN[0] = 1
    obj.write_register(65535)
    time.sleep(1)

    obj.register[133].Monitor_Sel[0] = 14
    obj.write_register(133)

    arm_dac_values = []
    extADC = []
    ADC0 = []
    ADC1 = []
    threshold_fc = []

    for arm_dac in range(100, 151, 10):
        arm_dac_values.append(arm_dac)
        obj.register[135].ARM_DAC[0] = arm_dac
        obj.write_register(135)
        time.sleep(1)
        extADC.append(obj.interfaceFW.ext_adc())
        # if not isinstance(extADC,(int, long)):
        # extADC.append(0)
        ADC0.append(obj.read_adc0())
        ADC1.append(obj.read_adc1())
        output = scurve_all_ch_execute(obj, "S-curve", arm_dac=arm_dac, ch=[41, 46], configuration="yes",
                                              dac_range=[200, 240], delay=50, bc_between_calpulses=2000, pulsestretch=7,
                                             latency=45, cal_phi=0, folder="gain_meas")
        threshold_fc.append(output[0])
    timestamp = time.strftime("%Y%m%d_%H%M")
    filename = "%s/%s/%sgain_measurement.dat" % (obj.data_folder, "gain_meas", timestamp)
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            print "Unable to create directory"
    text = "Results were saved to the folder:\n %s \n" % filename

    outF = open(filename, "w")
    outF.write("arm_dac/I:ADC0/I:ADC1/I:extADC/I:thr_scurve/D\n")
    for i, armdac in enumerate(arm_dac_values):
        outF.write('%i\t%i\t%i\t%i\t%f\n' % (armdac, ADC0[i], ADC1[i], extADC[i], threshold_fc[i]))
        pass
    outF.close()

    stop = time.time()
    run_time = (stop - start) / 60
    print "Runtime: %f" % run_time
    # # Calculate the gain.
    # if adc == "ext":
    #     print "Thresholds in mV TH0: %f and TH1: %f" % (threshold_mv0, threshold_mv1)
    # else:
    #     print "Thresholds in dac counts TH0: %f and TH1: %f" % (threshold_mv0, threshold_mv1)
    # print "Thresholds in fC TH0: %f and TH1: %f" % (threshold_fc0, threshold_fc1)
    # gain = (threshold_mv1 - threshold_mv0)/(threshold_fc1 - threshold_fc0)
    # print gain


def gain_histogram(obj):

    start = time.time()

    obj.register[65535].RUN[0] = 1
    obj.write_register(65535)
    time.sleep(1)

    obj.register[133].Monitor_Sel[0] = 14
    obj.write_register(133)

    arm_dac0 = 100
    arm_dac1 = 150

    obj.register[135].ARM_DAC[0] = arm_dac0
    obj.write_register(135)
    time.sleep(1)
    thr_v = obj.read_adc()
    threshold_mv0 = obj.adcM * thr_v + obj.adcB
    output = scurve_all_ch_execute(obj, "S-curve", arm_dac=arm_dac0, configuration="yes",
                                          dac_range=[200, 240], delay=50, bc_between_calpulses=2000, pulsestretch=7,
                                         latency=45, cal_phi=0, folder="gain_meas")
    threshold_fc0 = output[3]

    obj.register[135].ARM_DAC[0] = arm_dac1
    obj.write_register(135)
    time.sleep(1)
    thr_v = obj.read_adc()
    threshold_mv1 = obj.adcM * thr_v + obj.adcB
    output = scurve_all_ch_execute(obj, "S-curve", arm_dac=arm_dac1, configuration="yes",
                                          dac_range=[200, 240], delay=50, bc_between_calpulses=2000, pulsestretch=7,
                                         latency=45, cal_phi=0, folder="gain_meas")
    threshold_fc1 = output[3]

    print threshold_fc0
    print threshold_fc1
    print threshold_mv0
    print threshold_mv1
    # Calculate the gain.
    gain = []
    for i in range(0, len(threshold_fc0)):
        if threshold_fc1[i] != threshold_fc0[i]:
            print i
            print threshold_mv1
            print threshold_mv0
            print threshold_fc1[i]
            print threshold_fc0[i]
            gain_value = (threshold_mv1 - threshold_mv0)/(threshold_fc1[i] - threshold_fc0[i])
            gain.append(gain_value)
            print gain_value
        else:
            gain.append(0)
    print gain

    stop = time.time()
    run_time = (stop - start) / 60
    print "Runtime: %f" % run_time

