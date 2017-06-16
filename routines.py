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
from generator import *


def scurve_all_ch_execute(obj, scan_name):
    start = time.time()

    modified = scan_name.replace(" ", "_")
    file_name = "./routines/%s/FPGA_instruction_list.txt" % modified

    # Setting the needed registers.
    obj.set_fe_nominal_values()

    obj.register[130].DT[0] = 0
    obj.write_register(130)

    # register[138].CAL_MODE[0] = 2
    # obj.write_register(138)

    obj.register[132].SEL_COMP_MODE[0] = 0
    obj.write_register(132)

    # obj.register[134].Iref[0] = 32
    # obj.write_register(134)

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

    Nhits_h = {}
    Nev_h = {}

    for i in range(2, 130):
        diff = []

        Nhits_h[i-2] = r.TH1D('Nhits%i_h'%(i-2),'Nhits%i_h'%(i-2),256,-0.5,255.5)
        Nev_h[i-2] = r.TH1D('Nev%i_h'%(i-2),'Nev%i_h'%(i-2),256,-0.5,255.5)

        data = scurve_data[i][1:]
        channel = scurve_data[i][0]

        for j,Nhits in enumerate(data): 
            Nhits_h[i-2].AddBinContent(dac_values[j]-1,Nhits)
            Nev_h[i-2].AddBinContent(dac_values[j]-1,100)
            pass

        pass
    
    outF = r.TFile('results/scurves.root','RECREATE')
    enc_h = r.TH1D('enc_h','ENC of all Channels;ENC [DAC Units];Number of Channels',100,0.0,1.0)
    thr_h = r.TH1D('thr_h','Threshold of all Channels;ENC [DAC Units];Number of Channels',160,0.0,80.0)
    chi2_h = r.TH1D('fitChi2_h','Fit #chi^{2};#chi^{2};Number of Channels / 0.001',100,0.0,1.0)
    scurves_ag = {}
    for ch in range(128):
        scurves_ag[ch] = r.TGraphAsymmErrors(Nhits_h[ch],Nev_h[ch])
        scurves_ag[ch].SetName('scurve%i_ag'%ch)
        scurves_ag[ch].Write()
        fit_f = fitScurve(scurves_ag[ch])
        thr_h.Fill(fit_f.GetParameter(0))
        enc_h.Fill(fit_f.GetParameter(1))
        chi2_h.Fill(fit_f.GetChisquare())
        pass

    cc = r.TCanvas('canv','canv',1000,1000)

    drawHisto(thr_h,cc,'results/threshHiso.png')
    outF.cd()
    thr_h.Write()
    drawHisto(enc_h,cc,'results/encHisto.png')
    outF.cd()
    enc_h.Write()
    drawHisto(chi2_h,cc,'results/chi2Histo.png')
    outF.cd()
    chi2_h.Write()
    outF.Write()
    outF.Close()

def drawHisto(hist,canv,filename):
    canv.cd()
    hist.SetLineWidth(2)
    hist.Draw()
    canv.SaveAs(filename)
    

def fitScurve(scurve_g):
    import copy
    erf_f = r.TF1('erf_f','0.5*TMath::Erf((x-[0])/(TMath::Sqrt(2)*[1]))+0.5',0.0,80.0)
    minChi2 = 9999.9
    for i in range(40):
        erf_f.SetParameter(0,2.0*i+1.0)
        erf_f.SetParameter(1,2.0)
        scurve_g.Fit(erf_f)
        chi2 = erf_f.GetChisquare()
        if chi2 < minChi2 and chi2 > 0.0:
            minChi2 = chi2
            bestFit_f = copy.deepcopy(erf_f)
            pass
        pass
    return bestFit_f

def calibration(obj):

    output = generator("Calibration", 0, obj.register)
    for i in output[0]:
        print i
    file_name = "./routines/Calibration/FPGA_instruction_list.txt"
    output = obj.interfaceFW.launch(obj.register, file_name, obj.COM_port)

    cal_values = []

    if output[0] == "Error":
        text = "%s: %s\n" % (output[0], output[1])
        obj.add_to_interactive_screen(text)
    else:
        flag = 0
        print "Here"
        print len(output[0])
        for i in output[0]:
            if i.type_ID == 0:
                if flag == 0:
                    base_value = int(''.join(map(str, i.data)), 2)
                    print "Base value: %d" % base_value
                    flag = 1
                else:
                    step_value = int(''.join(map(str, i.data)), 2)
                    print "Step value: %d" % step_value
                    cal_value = step_value - base_value
                    print "Cal value: %d" % cal_value
                    cal_values.append(cal_value)

    print cal_values


def iref_adjust(obj):

    # Read the current Iref dac value.
    output = obj.SC_encoder.create_SC_packet(134, 0, "READ", 0)
    paketti = output[0]
    write_instruction(obj.interactive_output_file, 150, FCC_LUT[paketti[0]], 1)
    for x in range(1, len(paketti)):
        write_instruction(obj.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
    output = obj.execute()
    if not output[0]:
        print "No read data found. Register values might be incorrect.\n"
    elif output[0] == "Error":
        text = "%s: %s\n" % (output[0], output[1])
        text += "Register values might be incorrect.\n"
        print text
    else:
        print "Read data:"
        new_data = output[0][0].data
        print new_data

        new_data = ''.join(str(e) for e in new_data[-16:])
        register[134].change_values(new_data)

    obj.register[133].Monitor_Sel[0] = 0
    obj.write_register(133)

    obj.register[65535].RUN[0] = 1
    obj.write_register(65535)
    time.sleep(1)
    previous_diff = 100
    while True:

        time.sleep(1)
        output = obj.interfaceFW.ext_adc()
        print "Iref: %f, target: 100 mV. DAC: %d" % (output, register[134].Iref[0])
        new_diff = abs(100 - output)

        if previous_diff < new_diff:
            print "->Difference increasing. Choose previous value: %d." % previous_value
            register[134].Iref[0] = previous_value
            obj.write_register(134)
            break
        previous_value = register[134].Iref[0]
        if output < 100:
            print "->Value too low, increase Iref register by 1."
            register[134].Iref[0] += 1
        else:
            print "->Value too high, decrease Iref register by 1."
            register[134].Iref[0] -= 1
        obj.write_register(134)
        previous_diff = new_diff

    obj.register[65535].RUN[0] = 0
    obj.write_register(65535)
    time.sleep(1)


def adc_lsb(obj):

    obj.register[133].Monitor_Sel[0] = 33
    obj.write_register(133)

    obj.register[65535].RUN[0] = 1
    obj.write_register(65535)
    time.sleep(1)

    # CAL_DAC 0
    register[138].CAL_DAC[0] = 0
    obj.write_register(138)

    addr0 = 131073  # ADC0 address
    time.sleep(2)
    output = obj.SC_encoder.create_SC_packet(addr0, 0, "READ", 0)
    paketti = output[0]
    write_instruction(obj.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
    for x in range(1, len(paketti)):
        write_instruction(obj.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)

    output = obj.execute()
    if output[0] == "Error":
        print "Error."
    else:
        if output[0]:
            int_adc_output_0 = int(''.join(map(str, output[0][0].data)), 2)
    time.sleep(2)
    ext_adc_output0 = obj.interfaceFW.ext_adc()

    # CAL_DAC 100
    register[138].CAL_DAC[0] = 100
    obj.write_register(138)
    time.sleep(2)
    output = obj.SC_encoder.create_SC_packet(addr0, 0, "READ", 0)
    paketti = output[0]
    write_instruction(obj.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
    for x in range(1, len(paketti)):
        write_instruction(obj.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)

    output = obj.execute()
    if output[0] == "Error":
        print "Error."
    else:
        if output[0]:
            int_adc_output_1 = int(''.join(map(str, output[0][0].data)), 2)
    time.sleep(2)
    ext_adc_output1 = obj.interfaceFW.ext_adc()


    # CAL_DAC 200
    register[138].CAL_DAC[0] = 200
    obj.write_register(138)
    time.sleep(2)
    output = obj.SC_encoder.create_SC_packet(addr0, 0, "READ", 0)
    paketti = output[0]
    write_instruction(obj.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
    for x in range(1, len(paketti)):
        write_instruction(obj.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)

    output = obj.execute()
    if output[0] == "Error":
        print "Error."
    else:
        if output[0]:
            int_adc_output_2 = int(''.join(map(str, output[0][0].data)), 2)
    time.sleep(2)
    ext_adc_output2 = obj.interfaceFW.ext_adc()



    # CAL_DAC 255
    register[138].CAL_DAC[0] = 255
    obj.write_register(138)
    time.sleep(2)
    output = obj.SC_encoder.create_SC_packet(addr0, 0, "READ", 0)
    paketti = output[0]
    write_instruction(obj.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
    for x in range(1, len(paketti)):
        write_instruction(obj.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)

    output = obj.execute()
    if output[0] == "Error":
        print "Error."
    else:
        if output[0]:
            int_adc_output_3 = int(''.join(map(str, output[0][0].data)), 2)
    time.sleep(2)
    ext_adc_output3 = obj.interfaceFW.ext_adc()

    lsb0 = ext_adc_output0/int_adc_output_0
    lsb1 = ext_adc_output1/int_adc_output_1
    lsb2 = ext_adc_output2/int_adc_output_2
    lsb3 = ext_adc_output3/int_adc_output_3

    print "Internal ADC counts at 0: %d" % int_adc_output_0
    print "External voltage at 0: %f" % ext_adc_output0
    print "LSB: %f" % lsb0
    print "Internal ADC counts at 100: %d" % int_adc_output_1
    print "External voltage at 100: %f" % ext_adc_output1
    print "LSB: %f" % lsb1
    print "Internal ADC counts at 200: %d" % int_adc_output_2
    print "External voltage at 200: %f" % ext_adc_output2
    print "LSB: %f" % lsb2
    print "Internal ADC counts at 255: %d" % int_adc_output_3
    print "External voltage at 255: %f" % ext_adc_output3
    print "LSB: %f" % lsb3

    obj.register[133].Monitor_Sel[0] = 0
    obj.write_register(133)

    obj.register[65535].RUN[0] = 0
    obj.write_register(65535)
    time.sleep(1)


def scurve_execute(obj, scan_name):

    start = time.time()
    channel = 127
    # Set calibration to right channel.
    obj.register[channel].cal[0] = 1
    obj.write_register(channel)

    obj.set_fe_nominal_values()

    obj.register[130].DT[0] = 0
    obj.write_register(130)

    # register[138].CAL_MODE[0] = 2
    # obj.write_register(138)

    obj.register[132].SEL_COMP_MODE[0] = 0
    obj.write_register(132)

    # obj.register[134].Iref[0] = 27
    # obj.write_register(134)

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

    trigger_pattern = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                       0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
                       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    if option == 2:
        text = "Clearing trigger patterns\n"
        obj.add_to_interactive_screen(text)
        for k in range(0, 128):
                print "Clear channel: %d" % k
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

        text = "Setting trigger pattern.\n"
        obj.add_to_interactive_screen(text)
        for k in range(0, 128):
            print "Set channel:%d to: %d" % (k, trigger_pattern[k])
            obj.register[k].cal[0] = trigger_pattern[k]
            obj.write_register(k)

        obj.set_fe_nominal_values()
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

        obj.register[134].Iref[0] = 27
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

        text = "-Using self triggering.\n-With CalPulse from the FCC-tab you can trigger the channels."
        obj.add_to_interactive_screen(text)


def mask_bit_test(obj):


    obj.set_fe_nominal_values()
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

    obj.register[134].Iref[0] = 27
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

    for k in range(0, 128):
        print "Test channel:%d" % k
        for h in range(0, 4):
            if h % 2 == 0:
                obj.register[k].cal[0] = 1
                obj.write_register(k)
            else:
                obj.register[k].cal[0] = 0
                obj.write_register(k)

            write_instruction(obj.interactive_output_file, 1, FCC_LUT["CalPulse"], 1)
            output = obj.interfaceFW.launch(obj.register, obj.interactive_output_file, obj.COM_port)
            if output[0] == "Error":
                text = "%s: %s\n" % (output[0], output[1])
                obj.add_to_interactive_screen(text)
            else:
                for i in output[1]:
                    if i.data[127 - k] == "1":
                        hits += 1




        obj.register[k].mask[0] = 1
        obj.write_register(k)
        obj.send_fcc("CalPulse")
        obj.register[k].mask[0] = 0
        obj.write_register(k)
        obj.send_fcc("CalPulse")
        obj.register[k].cal[0] = 0
        obj.write_register(k)

    text = "Clearing trigger patterns\n"
    obj.add_to_interactive_screen(text)
    for k in range(0, 128):
        print "Clear channel: %d" % k
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


def scan_execute(obj, scan_name):
    scan_values0 = []
    scan_values1 = []
    modified = scan_name.replace(" ", "_")
    file_name = "./routines/%s/FPGA_instruction_list.txt" % modified
    output = obj.interfaceFW.launch(obj.register, file_name, obj.COM_port, 1)
    if output[0] == "Error":
        text = "%s: %s\n" % (output[0], output[1])
        obj.add_to_interactive_screen(text)
    else:
        text = "Received Values:\n"
        obj.add_to_interactive_screen(text)
        adc_flag = 0
        text = "%s|ADC0|ADC1|BC1|BC2|BC3|TransID1|TransID2|TransID3|\n" % scan_name[:-5]
        obj.add_to_interactive_screen(text)
        reg_value = 0
        bc_value = 0
        trans_id = 0
        print len(output[0])
        for i in output[0]:
            # for k in generation_events[2]:
            #     k = k.lstrip('[')
            #     k = k.rstrip(']')
            #     k = k.replace(" ", "")
            #     k = k.split(",")
            #     if k[1].strip('\'') != modified[:-5]:
            #         continue
            #     elif int(k[0]) > i.BCd:
            #         break
            #     else:
            #         reg_value = int(k[2])
            #         bc_value = int(k[0])
            #         trans_id = int(k[3])
            if i.type_ID == 0:
                if adc_flag == 0:
                    first_adc_value = int(''.join(map(str, i.data)), 2)
                    first_bc = i.BCd
                    first_trans_id = i.transaction_ID
                    adc_flag = 1
                else:
                    second_adc_value = int(''.join(map(str, i.data)), 2)
                    second_bc = i.BCd
                    second_trans_id = i.transaction_ID
                    text = "%d %d %d %d %d %d %d %d %d\n" % (reg_value, first_adc_value, second_adc_value, bc_value, first_bc, second_bc, trans_id, first_trans_id, second_trans_id)
                    obj.add_to_interactive_screen(text)
                    scan_values0.append(first_adc_value)
                    scan_values1.append(second_adc_value)
                    adc_flag = 0
    nr_points = len(scan_values0)
    x = range(0, nr_points)
    fig = plt.figure(1)
    plt.plot(x, scan_values0, label="ADC0")
    plt.plot(x, scan_values1, label="ADC1")
    plt.ylabel('ADC counts')
    plt.xlabel('DAC counts')
    plt.legend()
    plt.title(modified)
    plt.grid(True)
    fig.show()
    return output


def continuous_trigger(obj):

        obj.set_fe_nominal_values()
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

        obj.register[134].Iref[0] = 27
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

        obj.register[129].ST[0] = 0
        obj.register[129].PS[0] = 0
        obj.write_register(129)
        print "Set ST to: %d and Set PS to: %d" % (obj.register[129].ST[0], obj.register[129].PS[0])
        obj.send_fcc("RunMode")
        while True:
            obj.send_fcc("CalPulse")
            time.sleep(0.000000025)

