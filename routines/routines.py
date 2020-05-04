############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################
import sys
sys.path.append('../')


import math
import time
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy
import csv
import os
if os.path.isfile("./luts_custom.py"):
    from luts_custom import *
else:
    from luts import *
import numpy as np
from scipy.optimize import curve_fit
from scipy.special import erf
from scipy import sqrt
from scipy import stats
import scipy.signal
from test_system_functions import *
from output_decoder import *
from generator import *


def find_threshold(obj):
    fit = 'exp'
    start = time.time()
    obj.load_calibration_values_from_file(filename="vfat3_60_calibration_values.dat")
    thresholds = []
    threshold_rms = []
    enc_values = []
    arm_values = []
    # arm_dac_stop = [201, 161, 136]
    # dac_start = [254, 240, 225]
    # dac_stop = [120, 90, 10]
    # gains = ['High', 'Medium', 'Low']
    # arm_dac_start = [30, 10, 5]
    arm_dac_start = [10]
    arm_dac_stop = [150]
    dac_start = [254]
    dac_stop = [10]
    gains = ['Medium']
    arm_dac_step = 5

    for j, gain in enumerate(gains):

        # Generate output file names.
        timestamp = time.strftime("%Y%m%d_%H%M")
        # folder = obj.data_folder
        folder = "../cernbox/VFAT3_charge_distribution/Data/threshold/"
        filename = "%s%sthresholds_%s_gain.png" % (folder, timestamp, gain)
        data_file = "%s%sthresholds_%s_gain.dat" % (folder, timestamp, gain)
        if not os.path.exists(os.path.dirname(folder)):
            try:
                os.makedirs(os.path.dirname(folder))
            except OSError as exc:
                print "Unable to create directory"

        for arm_dac in range(arm_dac_start[j], arm_dac_stop[j], arm_dac_step):
            print "ARM_DAC: %s" % arm_dac
            arm_values.append(arm_dac)
            output = scurve_all_ch_execute(obj, "S-curve", arm_dac=arm_dac, dac_range=[dac_stop[j], dac_start[j]], gain=gain, configuration='no')
            thresholds.append(output[0])
            enc_values.append(output[5])
            threshold_rms.append(numpy.std(output[3]))
            save_list_to_file_and_print('arm_values', arm_values, data_file)
            save_list_to_file_and_print('thresholds', thresholds, data_file)
            save_list_to_file_and_print('threshold_rms', threshold_rms, data_file)
            save_list_to_file_and_print('enc_values', enc_values, data_file)

        if fit == 'linear':
            # Make a linear fit for the values.
            arm_dac_fcM, arm_dac_fcB, r_value, p_value, std_err = stats.linregress(arm_values, thresholds)
        elif fit == 'exp':
            arm_dac_fcM, arm_dac_fcB = numpy.polyfit(arm_values, numpy.log(thresholds), 1, w=numpy.sqrt(thresholds))

        # Plot Threshold in fC vs. ARM_DAC.
        plt.figure()

        if fit == 'linear':
            fit_values = []
            for value in arm_values:
                fit_values.append(value * arm_dac_fcM + arm_dac_fcB)
            plt.plot(arm_values, fit_values, label="fit")
            for i, value in enumerate(arm_values):
                plt.plot(value, thresholds[i], 'r*')
        elif fit == 'exp':
            fit_values = []
            for value in arm_values:
                fit_values.append(numpy.exp(arm_dac_fcB) * numpy.exp(arm_dac_fcM * value))
            plt.plot(arm_values, fit_values, label="fit")
            for i, value in enumerate(arm_values):
                plt.plot(value, thresholds[i], 'r*')
        else:
            plt.plot(arm_values, thresholds)
            plt.plot(arm_values, thresholds, 'x')

        plt.grid(True)
        plt.xlabel('ARM_DAC[DAC]')
        plt.ylabel('Threshold [fC]')
        plt.title("Threshold vs. ARM_DAC, %s Gain" % gain)
        plt.savefig(filename)
        plt.clf()

        # Save values to a file.
        save_list_to_file_and_print('arm_values', arm_values, data_file)
        save_list_to_file_and_print('thresholds',thresholds, data_file)
        save_list_to_file_and_print('threshold_rms', threshold_rms, data_file)
        save_list_to_file_and_print('enc_values', enc_values, data_file)
        if fit:
            save_to_file_and_print('arm_dac_fcM %s' % arm_dac_fcM, data_file)
            save_to_file_and_print('arm_dac_fcB %s' % arm_dac_fcB, data_file)

    stop = time.time()
    run_time = (stop - start) / 60
    print("Runtime: %f min" % run_time)


def scurve_all_ch_execute(obj, scan_name, arm_dac=100, ch=[0, 127], ch_step=1, configuration="yes",
                          dac_range=[200, 250], bc_between_calpulses=2000, pulsestretch=7, latency=50,
                          cal_phi=0, folder="scurve", triggers=100, verbose='yes', gain='High'):
    mean_th_fc = "n"
    all_ch_data = "n"
    noisy_channels = "n"
    thr_list = "n"
    dead_channels = "n"
    mean_enc_fc = "n"
    print "Gain: %s" % gain
    if obj.cal_dac_fcM == 0 or obj.cal_dac_fcB == 0:
        print "CAL_DAC not calibrated."
        print "Aborting S-curve routine."
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
        print configuration
        print verbose

        if gain == 'High':
            print("Setting Gain to High.")
            obj.register[131].RES_PRE[0] = 1
            obj.register[131].CAP_PRE[0] = 0
        elif gain == 'Medium':
            print("Setting Gain to Medium.")
            obj.register[131].RES_PRE[0] = 2
            obj.register[131].CAP_PRE[0] = 1
        elif gain == 'Low':
            print("Setting Gain to Low.")
            obj.register[131].RES_PRE[0] = 4
            obj.register[131].CAP_PRE[0] = 3
        else:
            print('ERROR: Invalid Gain Setting. Using High gain.')
            obj.register[131].RES_PRE[0] = 1
            obj.register[131].CAP_PRE[0] = 0

        obj.write_register(131)


        if configuration == "no":
            print "Setting s-curve for production."

            obj.register[0xffff].RUN[0] = 1
            obj.write_register(0xffff)

            print "Sending RUNMode."
            obj.interfaceFW.send_fcc("01100110")

            obj.register[131].TP_FE[0] = 7


            obj.register[132].PT[0] = 3
            obj.register[132].SEL_POL[0] = 0
            obj.register[132].SEL_COMP_MODE[0] = 1
            obj.write_register(132)

            obj.register[129].PS[0] = pulsestretch
            obj.write_register(129)

            obj.register[139].CAL_DUR[0] = 200
            obj.write_register(139)

            obj.register[138].CAL_PHI[0] = 1
            obj.register[138].CAL_MODE[0] = 1
            obj.write_register(138)

            obj.register[135].ARM_DAC[0] = arm_dac
            obj.write_register(135)
            print "Unmasking all channels."
            for k in range(0, 128):
                obj.register[k].mask[0] = 0
                obj.write_register(k)
                time.sleep(0.015)

            if obj.db_mode == 1:
                obj.measure_power("RUN")

        cal_dac_values.reverse()
        cal_dac_values[:] = [obj.cal_dac_fcM * x + obj.cal_dac_fcB for x in cal_dac_values]

        # Create a list of channels the s-curve is run on.
        channels = range(start_ch, stop_ch+1, ch_step)

        # Launch S-curve routine in firmware.
        scurve_data = obj.interfaceFW.run_scurve(start_ch, stop_ch, ch_step, start_dac_value, stop_dac_value, arm_dac, triggers, latency, obj)

        # Plot the s-curve data.
        if configuration == "yes" and verbose == 'yes':
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
            for i in range(2, len(scurve_data)):
                plt.plot(cal_dac_values, scurve_data[i])
            plt.grid(True)
            plt.ylabel('[%]')
            plt.xlabel('Charge [fC]')
            # plt.xlim(0, 10)
            plt.title(modified)
            fig.savefig(filename)

        # Analyze data.
        # mean_th_fc, mean_enc_fc, noisy_channels, dead_channels, enc_list, thr_list = scurve_analyze_root(obj, cal_dac_values, channels, scurve_data, folder, save=configuration)
        mean_th_fc, mean_enc_fc, noisy_channels, dead_channels, enc_list, thr_list, channel_category, unbonded_channels, untrimmable_channels = scurve_analyze_numpy(obj, cal_dac_values, channels, scurve_data, verbose=verbose)
        # print enc_list
        # Save data to database.
        if obj.database:
            obj.database.save_mean_threshold(mean_th_fc)
            obj.database.save_mean_enc(mean_enc_fc)
            obj.database.save_threshold_data(thr_list)
            obj.database.save_enc_data(enc_list)
            obj.database.save_noisy_channels(noisy_channels)
            obj.database.save_dead_channels(dead_channels)
            obj.database.save_channel_category(channel_category)

        # Print routine duration.
        stop = time.time()
        run_time = (stop - start) / 60
        text = "S-curve Run time (minutes): %f\n" % run_time
        print text
        if obj.plot_enc:
            timestamp = time.strftime("%Y%m%d_%H%M")
            enc_filename = "%s/%s/%sscurve_enc_%s.png" % (obj.data_folder, folder, timestamp, gain)
            thr_filename = "%s/%s/%sscurve_threshold_%s.png" % (obj.data_folder, folder, timestamp, gain)
            plt.figure()
            plt.plot(enc_list)
            plt.text(100, 0.8, "Mean enc:\n %f" % mean_enc_fc, bbox=dict(alpha=0.5))
            plt.title("enc, %s Gain" % gain)
            plt.ylim([0, mean_enc_fc + par_enc_plot_lim])
            plt.xlim([0, 128])
            plt.xlabel("Channel")
            plt.ylabel("enc [fC]")
            plt.grid(True)
            plt.savefig(enc_filename)

            plt.figure()
            plt.plot(thr_list)
            plt.text(100, 0.8, "Mean Thr:\n %f" % mean_th_fc, bbox=dict(alpha=0.5))
            plt.title("Threshold, %s Gain" % gain)
            #plt.ylim([0, mean_th_fc + par_enc_plot_lim])
            plt.ylim([0, mean_th_fc * 2])
            plt.xlim([0, 128])
            plt.xlabel("Channel")
            plt.ylabel("Threshold [fC]")
            plt.grid(True)
            plt.savefig(thr_filename)

    return [mean_th_fc, all_ch_data, noisy_channels, thr_list, dead_channels, mean_enc_fc, unbonded_channels, untrimmable_channels]


def scurve_analyze_root(obj, dac_values, channels, scurve_data, folder, save="yes", verbose='yes'):

    r.gROOT.SetBatch(True)

    Nhits_h = {}
    Nev_h = {}
    dead_channels = []
    for i in range(0, len(scurve_data)):
        data = scurve_data[i][:]
        channel = channels[i]

        Nhits_h[channel] = r.TH1D('Nhits%i_h' % channel, 'Nhits%i_h'% channel, len(dac_values)-1, dac_values[0], dac_values[-1])
        Nev_h[channel] = r.TH1D('Nev%i_h' % channel, 'Nev%i_h' % channel, len(dac_values)-1, dac_values[0], dac_values[-1])

        if all(v == 0 for v in data):
            dead_channels.append(channel)

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
        if enc_fc >= 0.2:      # Limit for noisy channel.
            if ch not in dead_channels:
                noisy_channels.append(ch)
                thr_h.Fill(fit_f.GetParameter(0))
                enc_h.Fill(fit_f.GetParameter(1))
        else:
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
    print "Dead Channels:"
    print dead_channels

    text = "S-curve results:\n"
    text += "Mean Threshold: %f\n" % mean_th
    text += "Mean enc: %f\n" % mean_enc
    text += "Noisy Channels: %i\n" % len(noisy_channels)
    text += "Dead Channels: %i\n" % len(dead_channels)
    obj.add_to_interactive_screen(text)
    if save == "yes":
        drawHisto(thr_h, cc, '%s/%s/threshHiso%s.png' % (obj.data_folder, folder, timestamp))
        thr_h.Write()
        drawHisto(enc_h, cc, '%s/%s/encHisto%s.png' % (obj.data_folder, folder, timestamp))
        enc_h.Write()
        drawHisto(chi2_h, cc, '%s/%s/chi2Histo%s.png' % (obj.data_folder, folder, timestamp))
        chi2_h.Write()
        outF.Close()

    return mean_th, mean_enc, noisy_channels, dead_channels, enc_list, thr_list


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


def find_closest_value(scan, dac_values, adc_values):
    #plt.plot(dac_values, adc_values)
    #plt.grid()
    value = hv3b_biasing_lut[scan][0]
    if value != 'n':
        trialX = np.linspace(dac_values[0], dac_values[-1], dac_values[-1]+1)
        # Fit a polynomial
        fitted = np.polyfit(dac_values, adc_values, 5)[::-1]
        y = np.zeros(len(trialX))
        for i in range(len(fitted)):
            y += fitted[i]*trialX**i
        # find closest value
        closest_value = np.where(y == (min(y, key=lambda x: abs(x - value))))[0][0]
        closest_dac_value = int(trialX[closest_value])
        hv3b_biasing_lut[scan][1] = closest_dac_value
        print "Found closest nominal DAC value: %i" % closest_dac_value
    #plt.plot(trialX, y)
    #plt.show()


def scan_execute(obj, scan_name, scan_nr, dac_size, save_data=1,):
    if obj.adcM == 0:
        text = "\nADCs are not calibrated. Run ADC calibration first.\n"
        obj.add_to_interactive_screen(text)
        return_value = "Error"
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

        output = obj.interfaceFW.run_dac_scan(0, 5, 2**dac_size-1, scan_nr)

        if output[0] == "Error":
            text = "%s: %s\n" % (output[0], output[1])
            obj.add_to_interactive_screen(text)
            return_value = 'Error'
        else:
            adc_flag = 0
            int_adc0_values = []
            int_adc1_values = []
            mv_adc0_values = []
            mv_adc1_values = []
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
                    mv_adc0_values.append(obj.adc0M * ivalue_dec + obj.adc0B)
                    int_adc0_values.append(ivalue_dec)
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
                    int_adc1_values.append(ivalue_dec)
                    mv_adc1_values.append(obj.adc1M * ivalue_dec + obj.adc1B)
                    ivalue = ""
                    adc_flag = 0
        # Save the results.
        # print mv_adc0_values

        # Use preferably values from ADC0. If it is broken, use values from ADC1.
        if obj.adc0M != 0:
            find_closest_value(scan_name[:-5], dac_values, mv_adc0_values)
        else:
            print "ADC0, broken, using ADC1 values."
            find_closest_value(scan_name[:-5], dac_values, mv_adc1_values)

        if obj.database:
            obj.database.save_dac_data(modified[:-5], "ADC0", int_adc0_values, dac_values)
            obj.database.save_dac_data(modified[:-5], "ADC1", int_adc1_values, dac_values)

        data = [reg_values, scan_values0, scan_values1]
        if save_data == 1:
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
            #fig = plt.figure(1)
            plt.clf()
            plt.plot(dac_values, mv_adc0_values, label="ADC0")
            plt.plot(dac_values, mv_adc1_values, label="ADC1")
            #plt.ylabel('voltage [mV]')
            plt.ylabel('Voltage [mV]')
            plt.xlabel('DAC counts')
            plt.legend()
            plt.title(modified)
            plt.grid(True)
            plt.savefig(filename)
            #plt.close(fig)

        stop = time.time()
        run_time = (stop - start)
        #text = "Scan duration: %f s\n" % run_time
        #obj.add_to_interactive_screen(text)

        return_value = [mv_adc0_values, mv_adc1_values]
    return return_value


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
    # mean_threshold, all_ch_data, noisy_channels, thr_list = scurve_all_ch_execute(obj, "S-curve", dac_range=[110, 160])
    mean_threshold, all_ch_data, noisy_channels, thr_list, dead_channels, mean_enc_fc, unbonded_channels, untrimmable_channels = scurve_all_ch_execute(obj, "S-curve", configuration='no')
    correction = []
    print "Found the mean threshold for the 128 channels: %f" % mean_threshold
    for k in range(0, 128):
        thresholds = []
        diff_values = []

        # Read the current dac values

        print "Adjusting the channel %d local arm_dac." % k
        output = scurve_all_ch_execute(obj, "S-curve", arm_dac=100, ch=[k, k], triggers=250, verbose='no')
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
            time.sleep(0.5)
            output = scurve_all_ch_execute(obj, "S-curve", arm_dac=100, ch=[k, k], triggers=250, verbose='no')
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


def scurve_analyze_numpy(obj, dac_values, channels, scurve_data, folder="", verbose='yes'):
    timestamp = time.strftime("%d.%m.%Y %H:%M")
    mean_list = []
    rms_list = []
    dead_channels = []
    noisy_channels = []
    unbonded_channels = []
    untrimmable_channels = []
    channel_category = ['0000']*128
    dac_values_temp = dac_values
    for i, channel in enumerate(channels):
        data = scurve_data[i]

        if channel in obj.rerun_scurve_channel_list:
            cal_dac_values = range(obj.cal_dac_start_rerun, obj.cal_dac_stop_rerun + 1)
            cal_dac_values.reverse()
            cal_dac_values[:] = [obj.cal_dac_fcM * x + obj.cal_dac_fcB for x in cal_dac_values]
            dac_values = cal_dac_values
        else:
            dac_values = dac_values_temp

        print "Analyzing channel %s" % channel
        if len(data) == 1:
            data = data[0]

        filtered_data = scipy.signal.medfilt(data, par_kernel_size)  # Filter the scurve

        filtered_data[:] = [y / max(filtered_data) for y in filtered_data]  # Normalize filtered data
        data[:] = [x / 100 for x in data]
        if all(v == 0 for v in data):
            print "Dead channel."
            dead_channels.append(channel)
            mean_list.append(0)
            rms_list.append(0)
            channel_category[channel] = change_character_in_string(channel_category[channel], 3, 1)
        else:
            if len(par_st_x_list) == len(par_st_y_list):
                r_squared = 0
                for h, st_x in enumerate(par_st_x_list):
                    st_y = par_st_y_list[h]
                    if r_squared < 0.99:
                        # print "Trying a fit with starting values. %s %s" % (st_x, st_y)
                        pass
                    else:
                        break
                    try:
                        mean, rms, r_squared = fit_scurve(filtered_data, dac_values, st_x, st_y)
                    except:
                        print('Fit failed.')
                        mean = 0
                        rms = 0
                        r_squared = 0
                print mean, rms
            else:
                print "Error. Starting parameter lists are not of equal length."
            # Append values to list
            rms_list.append(rms)
            if 0 < mean < 100:
                mean_list.append(mean)
            else:
                mean_list.append(0)

    rms_mean = numpy.mean(rms_list)
    rms_rms = numpy.std(rms_list)
    if numpy.isnan(rms_mean):
        rms_mean = 0
    mean_mean = numpy.mean(mean_list)
    mean_rms = numpy.std(mean_list)

    for i, channel in enumerate(channels):
        # Set the limits according to the channel
        if rms_list[i] != 0:
            if channel == 2 or channel == 125:
                lim_noisy = lim_enc_noisy_channel_flex_end_channels
                lim_unbonded = lim_enc_unbonded_channel_flex_end_channels
                sigma = lim_sigma_flex_end_channels
            else:
                lim_noisy = rms_mean + lim_enc_noisy_channel
                lim_unbonded = lim_enc_unbonded_channel
                sigma = lim_sigma

            # Categorize the channel.

            # Untrimmable channel.
            if abs(mean_mean - mean_list[i]) > mean_rms * sigma + lim_trim_dac_scale/2 and mean_list[i] is not 0:

                channel_category[channel] = change_character_in_string(channel_category[channel], 0, 1)
                untrimmable_channels.append(channel)

            # Noisy channel.
            if rms_list[i] > lim_noisy:

                noisy_channels.append(channel)
                channel_category[channel] = change_character_in_string(channel_category[channel], 2, 1)

            # Unbonded channel.
            if rms_list[i] <= lim_unbonded:

                unbonded_channels.append(channel)
                channel_category[channel] = change_character_in_string(channel_category[channel], 1, 1)
    if verbose == 'yes':
        print ""
        print "Mean Threshold: %f fC, sigma: %f fC" % (mean_mean, mean_rms)
        print "Mean enc: %f fC, sigma: %f fC" % (rms_mean, rms_rms)
        print "Dead Channels:"
        print dead_channels
        print "Noisy Channels (lim1:%s fC, lim2:%s fC):" % (rms_mean + lim_enc_noisy_channel, lim_enc_noisy_channel_flex_end_channels)
        print noisy_channels
        print "Unbonded channels (lim1:%s fC, lim2:%s fC):" % (lim_enc_unbonded_channel, lim_enc_unbonded_channel_flex_end_channels)
        print unbonded_channels
        print "Untrimmable channels (lim1: %s*sigma + %s fC/2, lim2: %s*sigma + %s fC/2):" % (lim_sigma, lim_trim_dac_scale, lim_sigma_flex_end_channels, lim_trim_dac_scale)
        print untrimmable_channels
        print ""
        print channel_category



    # plt.hist(mean_list, bins=100)
    # plt.title('Threshold spread')
    # plt.xlabel('Thr [fC]')
    # plt.ylabel('#')
    # plt.grid()
    # plt.show()


    # fig, ax = plt.subplots()
    #
    # textstr = '\n'.join((
    #     'mean=%.2f$' % (mean_mean,),
    #     'rms=%.2f$' % (mean_rms,)))
    #
    # ax.hist(mean_list, 100)
    # # these are matplotlib.patch.Patch properties
    # props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    #
    # # place a text box in upper left in axes coords
    # ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
    #         verticalalignment='top', bbox=props)
    #
    # plt.show()


    if folder != "":
        fig = plt.figure(figsize=(10, 20))
        sub1 = plt.subplot(511)
        sub1.set_xlabel('255-CAL_DAC')
        sub1.set_ylabel('%')
        sub1.set_title('S-curves of all channels')
        sub1.grid(True)
        text = "%s \n S-curves, 128 channels, HG, 25 ns." % timestamp
        sub1.text(25, 140, text, horizontalalignment='center', verticalalignment='center')

        sub2 = plt.subplot(512)
        sub2.plot(range(0, 128), rms_list)
        sub2.set_xlabel('Channel')
        sub2.set_ylabel('RMS')
        sub2.set_title('RMS of all channels')
        sub2.grid(True)
        text = "mean: %.2f RMS: %.2f" % (rms_mean, rms_rms)
        sub2.text(10, rms_mean, text, horizontalalignment='center', verticalalignment='center', bbox=dict(alpha=0.5))

        sub3 = plt.subplot(513)
        sub3.plot(range(0, 128), mean_list)
        sub3.set_xlabel('Channel')
        sub3.set_ylabel('255-CAL_DAC')
        sub3.set_title('mean of all channels')
        sub3.grid(True)
        text = "Mean: %.2f RMS: %.2f" % (mean_mean, mean_rms)
        sub3.text(10, mean_mean, text, horizontalalignment='center', verticalalignment='center', bbox=dict(alpha=0.5))

        # sub4 = plt.subplot(514)
        # n, bins, patches = sub4.hist(mean_list, bins='auto')
        # y = mlab.normpdf(bins, mean_mean, mean_rms)
        # sub4.plot(bins, y, 'r--', linewidth=1)
        #
        # sub5 = plt.subplot(515)
        # n, bins, patches = sub5.hist(rms_list, bins='auto')
        # y = mlab.normpdf(bins, rms_mean, rms_rms)
        # sub5.plot(bins, y, 'r--', linewidth=1)

        fig.subplots_adjust(hspace=.5)

        timestamp = time.strftime("%Y%m%d_%H%M")

        fig.savefig("%s%sS-curve_plot.pdf" % (folder, timestamp))

        text = "Results were saved to the folder:\n %s \n" % folder
        print text

    return mean_mean, rms_mean, noisy_channels, dead_channels, rms_list, mean_list, channel_category, unbonded_channels, untrimmable_channels


def find_mean_and_enc(data, dac_values):
    diff = []
    mean_calc = 0
    summ = 0
    l = 0
    for j in data:
        if l != 0:
            diff_value = j - previous_value
            diff.append(diff_value)
            mean_calc += dac_values[l] * diff_value
            summ += diff_value
        previous_value = j
        l += 1
    if summ != 0:
        mean = mean_calc / float(summ)
    else:
        mean = 0
    if mean <= 0 or mean > 70:
        # print "Invalid threshold."
        mean = 0
    l = 1
    rms = 0
    for r in diff:
        rms += r * (mean - dac_values[l]) ** 2
        l += 1
    if 0 < (rms / summ):
        rms = math.sqrt(rms / summ)
    else:
        rms == 0

    return mean, rms


def fit_func(x, a, b):
    return 0.5 * erf((x-a)/(sqrt(2)*b)) + 0.5


def fit_scurve(hit_data, charge_data, st_x, st_y):

    np_x = np.array(charge_data)
    np_y = np.array(hit_data)
    params, params_covariance = curve_fit(fit_func, np_x, np_y, p0=[st_x, st_y])
    r_squared = calculate_r2_score(np_x, np_y, params)
    # print "R^2: %s" % r_squared
    # print params
    return params[0], params[1], r_squared


def calculate_r2_score(xdata, ydata, popt):
    residuals = ydata - fit_func(xdata, popt[0], popt[1])
    ss_res = numpy.sum(residuals ** 2)
    ss_tot = numpy.sum((ydata - numpy.mean(ydata)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    return r_squared


def change_character_in_string(text, nr_character, new_character):
    new = list(text)
    new[nr_character] = "%s" % new_character
    return ''.join(new)


def measure_charge_distribution(obj):
    print("\n\n************STARTING CHARGE DISTRIBUTION TEST*************")
    start = time.time()
    timestamp = time.strftime("%d%m%Y%H%M")

    #gains = ['High', 'Medium', 'Low']
    gains = ['High']
    #dynamic_range = {'High': 9.5, 'Medium': 28, 'Low': 55}
    dynamic_range = {'High': 3, 'Medium': 55, 'Low': 55}
    arm_dac_fcM = {'Low': 0.308756078585, 'Medium': 0.160574730846, 'High': 0.0525736788946}
    arm_dac_fcB = {'Low': -0.20026469513, 'Medium': -0.344217476814, 'High': -0.225712925757}

    target_channels = [49, 100, 106, 55]  # check VFAT3-strip mapping
    mapped_target_channels = [25, 50, 75, 100]
    hybrid_version = "VFAT3b"
    hybrid_id = "#0060"

    pulse_stretch = 0
    delay = 30
    latency_start = 7
    latency_stop = 33
    latency_step = 1

    nr_of_triggers = 20

    arm_dac_min = 0
    arm_dac_max = 180
    arm_dac_step = 1



    # Create new data folder.
    # folder = "./results/charge_distribution/run_%s/" % timestamp
    folder = "../cernbox/VFAT3_charge_distribution/Data/run_%s/" % timestamp
    data_file = "%s%soutput_data.dat" % (folder, timestamp)
    if not os.path.exists(os.path.dirname(folder)):
        try:
            os.makedirs(os.path.dirname(folder))
        except OSError as exc:  # Guard against race condition
            print "Unable to create directory"

    save_to_file_and_print("pulse_stretch =  %s" % pulse_stretch, data_file)
    save_to_file_and_print("nr_of_triggers =  %s" % nr_of_triggers, data_file)
    save_list_to_file_and_print('mapped_target_channels', mapped_target_channels, data_file)

    for latency in range(latency_start, latency_stop+1, latency_step):

        output_file = "%s%soutput_lat%s.dat" % (folder, timestamp, latency)

        save_to_file_and_print(time.strftime("Time: %d.%m.%Y %H:%M"), output_file)
        save_to_file_and_print("Hybrid version: %s" % hybrid_version, output_file)
        save_to_file_and_print("Hybrid ID: %s" % hybrid_id, output_file)
        save_to_file_and_print("Target channels: %s" % ''.join(str(target_channels)), output_file)
        save_to_file_and_print("Nr. of triggers: %s" % nr_of_triggers, output_file)
        save_to_file_and_print("Latency: %s" % latency, output_file)
        save_to_file_and_print("Delay: %s" % delay, output_file)


        print("Setting RUN-bit to 1.")
        obj.register[0xffff].RUN[0] = 1
        obj.write_register(0xffff)

        for target_channel in target_channels:
            obj.register[target_channel].cal[0] = 1
            obj.write_register(target_channel)
            time.sleep(0.1)

        obj.load_calibration_values_from_file(filename="vfat3_60_calibration_values.dat")

        print "Sending RUNMode."
        obj.interfaceFW.send_fcc("01100110")

        save_to_file_and_print("Settings:", output_file)
        RES_PRE = {'High': 1, 'Medium': 2, 'Low': 4}
        CAP_PRE = {'High': 0, 'Medium': 1, 'Low': 3}
        obj.register[131].TP_FE[0] = 7
        obj.write_register(131)
        text = "TP_FE: %s" % obj.register[131].TP_FE[0]
        save_to_file_and_print(text, output_file)

        obj.register[132].PT[0] = 3
        obj.register[132].SEL_POL[0] = 1
        obj.register[132].SEL_COMP_MODE[0] = 0
        obj.write_register(132)
        text = "PT: %s, SEL_POL: %s, SEL_COMP_MODE: %s" % (obj.register[132].PT[0], obj.register[132].SEL_POL[0], obj.register[132].SEL_COMP_MODE[0])
        save_to_file_and_print(text, output_file)

        obj.register[129].PS[0] = pulse_stretch
        obj.write_register(129)
        text = "PS: %s" % obj.register[129].PS[0]
        save_to_file_and_print(text, output_file)

        obj.register[139].CAL_DUR[0] = 200
        obj.write_register(139)
        text = "CAL_DUR: %s" % obj.register[139].CAL_DUR[0]
        save_to_file_and_print(text, output_file)

        obj.register[138].CAL_SEL_POL[0] = 1
        obj.register[138].CAL_PHI[0] = 1
        obj.register[138].CAL_MODE[0] = 1
        obj.write_register(138)
        text = "CAL_PHI: %s, CAL_MODE: %s" % (obj.register[138].CAL_PHI[0], obj.register[138].CAL_MODE[0])
        save_to_file_and_print(text, output_file)

        obj.register[137].LAT[0] = latency
        obj.write_register(137)

        print('\n\n')
        obj.set_fe_nominal_values(chip=hybrid_version)
        print('\n')

        save_to_file_and_print("Channel data is from [1:128].", output_file)

        #command = []
        command = ["00111100"]
        for delay_i in range(1, delay + 1):
            if (delay_i % 2) == 0:
                command.append("11111111")
            else:
                command.append("00000000")
        command.append("01101001")
        save_list_to_file_and_print('command', command, output_file)

        for gain in gains:
            arm_dac_values = []
            thresholds = []
            save_to_file_and_print('Setting the Gain to: %s' % gain, output_file)
            print("RES_PRE: %s, CAP_PRE: %s" % (RES_PRE[gain], CAP_PRE[gain]))
            obj.register[131].RES_PRE[0] = RES_PRE[gain]
            obj.register[131].CAP_PRE[0] = CAP_PRE[gain]
            obj.write_register(131)
            print "Reading register:"
            obj.read_register(131)
            text = "RES_PRE: %s, CAP_PRE: %s" % (obj.register[131].RES_PRE[0], obj.register[131].CAP_PRE[0])
            save_to_file_and_print(text, output_file)

            print("Setting calibration pulse to")
            obj.register[138].CAL_DAC[0] = int(round((dynamic_range[gain] - obj.cal_dac_fcB) / obj.cal_dac_fcM))
            print("Setting calibration pulse to: %s" % obj.register[138].CAL_DAC[0])
            obj.write_register(138)
            obj.read_register(138)
            print("Reading register CAL_DAC: %s" % obj.register[138].CAL_DAC[0])
            text = "CAL_DAC: %s" % (obj.register[138].CAL_DAC[0])
            save_to_file_and_print(text, output_file)
            cal_dac_fc = obj.cal_dac_fcM * obj.register[138].CAL_DAC[0] + obj.cal_dac_fcB
            text = "Calibration Pulse: %s fC" % cal_dac_fc
            save_to_file_and_print(text, output_file)

            result_data_matrix = numpy.array([0] * 128)
            for arm_dac_value in range(arm_dac_min, arm_dac_max, arm_dac_step):
                arm_dac_values.append(arm_dac_value)
                obj.register[135].ARM_DAC[0] = arm_dac_value
                print("Setting ARM_DAC: %s" % obj.register[135].ARM_DAC[0])
                obj.write_register(135)
                obj.read_register(135)
                print("Reading ARM_DAC: %s" % obj.register[135].ARM_DAC[0])
                threshold = arm_dac_fcM[gain] * obj.register[135].ARM_DAC[0] + arm_dac_fcB[gain]
                thresholds.append(threshold)
                text = "ARM_DAC: %s, %s fC" % (obj.register[135].ARM_DAC[0], threshold)
                save_to_file_and_print(text, output_file)
                result_data_vector = numpy.array([0]*128)
                for loop in range(0, nr_of_triggers):
                    time.sleep(0.02)
                    output = obj.interfaceFW.send_fcc(command)
                    output_data = []
                    byte_counter = 0
                    for i in range(0, len(output)):
                        if byte_counter == 0 or byte_counter == 4:
                            output_data.append(int(output[i], 16))
                            byte_counter = 0
                        byte_counter += 1
                    decoded_data = decode_output_data(output_data, obj.register)
                    for i in decoded_data[3]:
                        i.data_list.reverse()
                        data_vector = numpy.array(i.data_list)
                        result_data_vector += data_vector
                result_data_vector = map_channels(result_data_vector)
                result_data_matrix = numpy.vstack((result_data_matrix, result_data_vector))
                save_to_file_and_print(numpy.array2string(result_data_vector, separator=','), output_file)
                for channel in mapped_target_channels:
                    previous_ch_charge = (result_data_vector[channel - 1] / float(nr_of_triggers)) * 100
                    target_ch_charge = (result_data_vector[channel] / float(nr_of_triggers)) * 100
                    next_ch_charge = (result_data_vector[channel + 1] / float(nr_of_triggers)) * 100
                    text = "Charge spread for channel: %s.  %3.1f %% %3.1f %% %3.1f %%" % (channel, previous_ch_charge, target_ch_charge, next_ch_charge)
                    save_to_file_and_print(text, output_file)
            print(result_data_matrix)
            save_to_file_and_print(numpy.array2string(result_data_matrix, separator=','), output_file)
            save_numpy_2d_array_to_file('%s_gain_data_lat%s' % (gain, latency), result_data_matrix, data_file)
            save_list_to_file_and_print('%s_gain_arm_dac_values' % gain, arm_dac_values, data_file)
            save_list_to_file_and_print('%s_gain_thresholds' % gain, thresholds, data_file)
            thresholds = arm_dac_values


            # Unset calibration pulses for the target channels.
            for target_channel in target_channels:
                obj.register[target_channel].cal[0] = 0
                obj.write_register(target_channel)
                time.sleep(0.1)

            # Plot 2D map.
            plt.figure()
            fig, ax = plt.subplots()
            plt.imshow(result_data_matrix, origin='lower', interpolation='none')
            y_ticks = range(20, arm_dac_max+1, 20)
            y_label_list = []
            y_label_list[:] = ["%.1f" % (arm_dac_fcM[gain] * y + arm_dac_fcB[gain]) for y in y_ticks]
            #ax.set_yticks(y_ticks)
            #ax.set_yticklabels(y_label_list)
            c_bar = plt.colorbar()
            c_bar.ax.set_ylabel('# hits')
            plt.title('Charge distribution, %s Gain, s=%s, Q=%.1f fC' % (gain, nr_of_triggers, cal_dac_fc))
            plt.xlabel('Channel')
            plt.ylabel('Threshold [DAC counts]')
            plt.savefig('%s%scharge_distribution_%s_lat%s.png' % (folder, timestamp, gain, latency))

            # Plot channels in subplots.
            plt.figure()
            fig, axs = plt.subplots(len(mapped_target_channels))
            fig.suptitle('Vertically stacked subplots')
            for axis in range(0,len(mapped_target_channels)):
                main_ch = mapped_target_channels[axis]
                previous_ch = mapped_target_channels[axis] - 1
                next_ch = mapped_target_channels[axis] + 1
                axs[axis].plot(thresholds, result_data_matrix[1:, previous_ch], label='ch %s' % previous_ch)
                axs[axis].plot(thresholds, result_data_matrix[1:,main_ch], label='ch %s' % main_ch)
                axs[axis].plot(thresholds, result_data_matrix[1:, next_ch], label='ch %s' % next_ch)
                axs[axis].grid()
                axs[axis].legend()
            plt.savefig('%s%scharge_distributions_%s_lat%s.png' % (folder, timestamp, gain, latency))

            # Plot channels.
            for axis in range(0,len(mapped_target_channels)):
                main_ch = mapped_target_channels[axis]
                previous_ch = mapped_target_channels[axis] - 1
                next_ch = mapped_target_channels[axis] + 1
                previous_2_ch = mapped_target_channels[axis] - 2
                next_2_ch = mapped_target_channels[axis] + 2
                plt.figure()
                plt.plot(thresholds, result_data_matrix[1:, previous_2_ch], label='ch %s' % previous_2_ch)
                plt.plot(thresholds, result_data_matrix[1:, previous_ch], label='ch %s' % previous_ch)
                plt.plot(thresholds, result_data_matrix[1:, main_ch], label='ch %s' % main_ch)
                plt.plot(thresholds, result_data_matrix[1:, next_ch], label='ch %s' % next_ch)
                plt.plot(thresholds, result_data_matrix[1:, next_2_ch], label='ch %s' % next_2_ch)
                plt.grid()
                plt.legend()
                plt.ylabel('# Hits')
                plt.xlabel('Threshold [DAC counts]')
                plt.title('Charge distribution, %s Gain, s=%s, Q=%.1f fC' % (gain, nr_of_triggers, cal_dac_fc))
                plt.savefig('%s%scharge_distribution_ch%s_%s_lat%s.png' % (folder, timestamp, main_ch, gain, latency))

        plt.close('all')
        print("************END OF THE CHARGE DISTRIBUTION TEST*************")
        stop = time.time()
        run_time = (stop - start) / 60
        print("Runtime: %f min" % run_time)


def save_to_file_and_print(text, filename):
    with open(filename, "a") as m_file:
        m_file.write("%s\n" % text)
    print(text)


def save_list_to_file_and_print(list_name, mylist, filename):
    list_string = ''.join(str(mylist))
    text = "%s = %s" % (list_name, list_string)
    with open(filename, "a") as mfile:
        mfile.write("%s\n" % text)
    print(text)


def save_numpy_2d_array_to_file(list_name, mylist, filename):
    text = "%s = [ \n" % list_name
    for i in range(mylist.shape[0]):
        text += "["
        list_string = ','.join(map(str, mylist[i, :]))
        text += "%s" % list_string
        text += "],\n"
    text += "]"
    with open(filename, "a") as mfile:
        mfile.write("%s\n" % text)


def map_channels(channel_data):
    file_name = "./data/hv3b_slot10_channel_mapping.dat"
    channel_map = [int(line.rstrip('\n')) for line in open(file_name)]
    mapped_data = [0]*128
    for i, position in enumerate(channel_map):
        mapped_data[position] = channel_data[i]
    numpy_mapped_data = numpy.array(mapped_data)
    return numpy_mapped_data


def find_noise_floor(obj, folder, data_file):
    save_to_file_and_print("Find noise floor.", data_file)
    sample_size = 5
    save_to_file_and_print("Nr. of triggers: %s/channel" % sample_size, data_file)
    noise_arm_dac = []
    noise_hits = []
    noise_hits_norm = []
    for arm_dac_value in range(0, 150, 1):
        obj.register[135].ARM_DAC[0] = arm_dac_value
        obj.write_register(135)
        result_data_vector = numpy.array([0]*128)
        for loop in range(0, sample_size):
            time.sleep(0.05)
            output = obj.interfaceFW.send_fcc("01101001")
            output_data = []
            byte_counter = 0
            for i in range(0, len(output)):
                if byte_counter == 0 or byte_counter == 4:
                    output_data.append(int(output[i], 16))
                    byte_counter = 0
                byte_counter += 1
            decoded_data = decode_output_data(output_data, obj.register)
            for i in decoded_data[3]:
                data_vector = numpy.array(i.data_list)
                result_data_vector += data_vector
        # print(result_data_vector)
        noise_arm_dac.append(arm_dac_value)
        noise_hits.append(sum(result_data_vector))
        noise_hits_norm.append(sum(result_data_vector)/(float(sample_size*128))*100)
        print("ARM_DAC: %s, hits: %s/%s" % (arm_dac_value, sum(result_data_vector), sample_size*128))
    save_list_to_file_and_print("noise_arm_dac", noise_arm_dac, data_file)
    save_list_to_file_and_print("noise_hits", noise_hits, data_file)
    save_list_to_file_and_print("noise_hits_norm", noise_hits_norm, data_file)

    # Plot the ARM_DAC vs. noise plot.
    plt.figure()
    plt.plot(noise_arm_dac, noise_hits)
    plt.title("Noise vs. Arming comparator threshold")
    plt.xlabel("ARM_DAC [DAC counts]")
    plt.ylabel("Normalized hits [#]")
    plt.grid(b=True, which='both')
    plt.savefig('%sARM_DAC_noise.png' % folder)