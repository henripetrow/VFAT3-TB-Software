from routines import *
from generator import *
import ROOT as r
import numpy as np


def cal_dac_steps(obj):

    start_dac_value = 0
    stop_dac_value = 255

    obj.register[133].Monitor_Sel[0] = 33
    obj.write_register(133)

    obj.register[65535].RUN[0] = 1
    obj.write_register(65535)
    time.sleep(0.1)

    step_values = []
    dac_values = []
    charge_values = []
    obj.register[138].CAL_MODE[0] = 1
    obj.register[138].CAL_SEL_POL[0] = 1
    obj.write_register(138)
    time.sleep(0.1)

    baseADC = obj.read_adc()
    base = obj.adcM * baseADC + obj.adcB

    obj.register[138].CAL_SEL_POL[0] = 0
    obj.write_register(138)
    time.sleep(0.1)

    for i in range(0, 255, 5):

        obj.register[138].CAL_DAC[0] = i
        obj.write_register(138)

        stepADC = obj.read_adc()
        step = obj.adcM * stepADC + obj.adcB

        difference = step-base
        charge = (difference/1000.0) * 100.0  # 100 fF capacitor.

        step_values.append(step)
        dac_values.append(float(255-i))
        charge_values.append(charge)

        print "DAC value: %d" % i
        print "Base value: %f mV, step value: %f mV" % (base, step)
        print "Difference: %f mV, CHARGE: %f fC" % (difference, charge)
        print "--------------------------------"

    obj.cal_dac_fc_values = charge_values

    return dac_values, base, step_values, charge_values


def scan_cal_dac_fc(obj, scan_name, production="no"):
    error = 0
    if obj.adcM == 0:
        text = "\nADCs are not calibrated. Run ADC calibration first.\n"
        obj.add_to_interactive_screen(text)
        error = 1
    else:
        start = time.time()
        modified = scan_name.replace(" ", "_")
        modified = modified.replace(",", "_")

        dac_values, base_value, step_values, charge_values = cal_dac_steps(obj)

        calc_cal_dac_conversion_factor(obj, dac_values, charge_values, production=production)

        # data = [dac_values, charge_values]
        # timestamp = time.strftime("%Y%m%d%H%M")
        # folder = "./results/"
        # filename = "%s%s_%s_scan_data.dat" % (folder, timestamp, modified)
        #
        # outF = open(filename, "w")
        # outF.write("dacValue/D:baseV/D:stepV/D:Q/D\n")
        # for i,dacVal in enumerate(dac_values):
        #     outF.write('%f\t%f\t%f\t%f\n'%(dacVal,base_values[i],step_values[i],charge_values[i]))
        #     pass
        # outF.close()
        # text = "\nResults were saved to the file:\n %s \n" % filename
        #
        # obj.add_to_interactive_screen(text)

        stop = time.time()
        run_time = (stop - start) / 60
        text = "\nScan duration: %f min\n" % run_time
        obj.add_to_interactive_screen(text)
    if obj.cal_dac_fcM < 0.1 or obj.cal_dac_fcM > 0.3:
        error = 1
    return error


def calc_cal_dac_conversion_factor(obj, dac_values, charge_values, production="no"):

    r.gStyle.SetStatX(0.5)
    r.gStyle.SetStatY(0.8)
    r.gStyle.SetOptFit(True)

    cal_dac_fc_g = r.TGraph(len(dac_values), np.array(dac_values), np.array(charge_values))

    cal_dac_fc_g.SetName('cal_dac_fc_g')
    cal_dac_fc_g.SetTitle('CAL_DAC Calibration;255-CAL_DAC;Charge [fC]')
    cal_dac_fc_g.SetMarkerStyle(3)

    cal_dac_fc_fitR = cal_dac_fc_g.Fit('pol1', 'S')

    obj.cal_dac_fcM = cal_dac_fc_fitR.GetParams()[1]
    obj.cal_dac_fcB = cal_dac_fc_fitR.GetParams()[0]

    if production == "no":
        canv = r.TCanvas('canv', 'canv', 1000, 1000)
        canv.cd()

        timestamp = time.strftime("%Y%m%d_%H%M")
        output_file = '%s/calibration/%scal_dac_fc.png' % (obj.data_folder, timestamp)
        if not os.path.exists(os.path.dirname(output_file)):
            try:
                os.makedirs(os.path.dirname(output_file))
            except OSError as exc:  # Guard against race condition
                print "Unable to create directory"
        open(output_file, 'w').close()
        cal_dac_fc_g.Draw('ap')
        canv.SaveAs(output_file)


    text = "\nCAL_DAC conversion completed.\n"
    text += "CAL_DAC to fC: %f + %f\n" % (obj.cal_dac_fcM, obj.cal_dac_fcB)
    obj.add_to_interactive_screen(text)


def iref_adjust(obj):
    error = 0
    # Read the current Iref dac value.
    obj.read_register(134)
    obj.register[134].Iref[0] = 10
    obj.write_register(134)
    previous_value = 10

    # Set monitoring to Iref
    obj.register[133].Monitor_Sel[0] = 0
    obj.write_register(133)

    # Set RUN bit to activate analog part.
    obj.register[65535].RUN[0] = 1
    obj.write_register(65535)
    time.sleep(1)

    previous_diff = 1000
    text = "\nAdjusting the global reference current.\n"
    print text
    obj.add_to_interactive_screen(text)
    while True:

        time.sleep(0.1)
        output = obj.interfaceFW.ext_adc()
        if output == "Error":
            error = 1
            print "No response from ADC, aborting Iref adjustment."
            break
        print "Iref: %f, target: 100 mV. DAC: %d" % (output, obj.register[134].Iref[0])
        new_diff = abs(100 - output)
        if obj.register[134].Iref[0] == 0 or obj.register[134].Iref[0] == 63:
            print "Iref could not be adjusted."
            error = 1
            break
        if previous_diff < new_diff:
            print "->Difference increasing. Choose previous value: %d." % previous_value
            obj.register[134].Iref[0] = previous_value
            obj.Iref = previous_value
            obj.write_register(134)
            break
        previous_value = obj.register[134].Iref[0]
        if output < 100:
            print "->Value too low, increase Iref register by 1."
            obj.register[134].Iref[0] += 1
        else:
            print "->Value too high, decrease Iref register by 1."
            obj.register[134].Iref[0] -= 1
        obj.write_register(134)
        previous_diff = new_diff

    obj.register[65535].RUN[0] = 0
    obj.write_register(65535)
    time.sleep(1)
    text = "- Iref adjusted.\n"
    text += "Register value: %i.\n" % obj.register[134].Iref[0]
    obj.Iref_cal = 1
    print text
    obj.add_to_interactive_screen(text)
    return error


def adc_calibration(obj, production="no"):
    error = 0
    if obj.Iref_cal == 0:
        text = "\nIref is not calibrated. Run Iref calibration first.\n"
        obj.add_to_interactive_screen(text)
    else:
        obj.register[133].Monitor_Sel[0] = 2
        obj.write_register(133)

        obj.register[65535].RUN[0] = 1
        obj.write_register(65535)
        time.sleep(1)

        int_adc0_values = []
        int_adc1_values = []
        ext_adc_values = []
        dac_values = []
        for i in range(0, 252, 1):
            value = i
            dac_values.append(value)
            print "->Measuring DAC value %d" % value
            obj.register[141].PRE_I_BIT[0] = value
            obj.write_register(141)
            time.sleep(0.05)
            int_adc0_value = float(obj.read_adc0())
            int_adc0_values.append(int_adc0_value)

            int_adc1_value = float(obj.read_adc1())
            int_adc1_values.append(int_adc1_value)

            ext_adc_value = obj.interfaceFW.ext_adc()
            #ext_adc_value = 0
            print "ADC0: %d" % int_adc0_value
            print "ext. ADC: %f" % ext_adc_value
            ext_adc_values.append(ext_adc_value)

        #obj.interfaceFW.stop_ext_adc()
        obj.register[133].Monitor_Sel[0] = 0
        obj.write_register(133)

        obj.register[65535].RUN[0] = 0
        obj.write_register(65535)
        time.sleep(1)
        print int_adc0_values
        print dac_values
        calc_adc_conversion_constants(obj, ext_adc_values, int_adc0_values, int_adc1_values,production)

        adc0_values_conv = []
        for item in int_adc0_values:
            adc0_values_conv.append(item*obj.adc0M+obj.adc0B)

        adc1_values_conv = []
        for item in int_adc1_values:
            adc1_values_conv.append(item*obj.adc1M+obj.adc1B)

        text = "\nInternal ADCs calibrated. Values:\n"
        text += "ADC0: %f + %f\n" % (obj.adc0M, obj.adc0B)
        text += "ADC1: %f + %f\n" % (obj.adc1M, obj.adc1B)
        obj.add_to_interactive_screen(text)
        obj.adcM = obj.adc0M
        obj.adcB = obj.adc0B
        if obj.adc0M <= 1 or obj.adc0M > 2.5:
            error += 1
            print "ADC0 broken"
            obj.adc0M = 0
            obj.adc0B = 0
            obj.adcM = obj.adc1M
            obj.adcB = obj.adc1B
        if obj.adc1M <= 1 or obj.adc1M > 2.5:
            error += 1
            print "ADC1 broken"
            obj.adc1M = 0
            obj.adc1B = 0
            if obj.adc0M == 0:
                obj.adcM = 0
                obj.adcB = 0

    if error == 1:
        error = 'y'
    print obj.adcM
    print obj.adcB
    return error


def calc_adc_conversion_constants(obj, ext_adc, int_adc0, int_adc1, production="no"):

    r.gStyle.SetStatX(0.5)
    r.gStyle.SetStatY(0.8)
    r.gStyle.SetOptFit(True)

    adc0_Conv_g = r.TGraph(len(ext_adc), np.array(int_adc0), np.array(ext_adc))
    adc1_Conv_g = r.TGraph(len(ext_adc), np.array(int_adc1), np.array(ext_adc))

    adc0_Conv_g.SetName('adc0_Conv_g')
    adc1_Conv_g.SetName('adc1_Conv_g')
    adc0_Conv_g.SetTitle('ADC0 Calibration;ADC0;Vmean [mV]')
    adc1_Conv_g.SetTitle('ADC1 Calibration;ADC1;Vmean [mV]')
    adc0_Conv_g.SetMarkerStyle(3)
    adc1_Conv_g.SetMarkerStyle(3)

    adc0fitR = adc0_Conv_g.Fit('pol1', 'S')
    adc1fitR = adc1_Conv_g.Fit('pol1', 'S')

    obj.adc0M = adc0fitR.GetParams()[1]
    obj.adc0B = adc0fitR.GetParams()[0]

    obj.adc1M = adc1fitR.GetParams()[1]
    obj.adc1B = adc1fitR.GetParams()[0]

    if production == "no":
        canv = r.TCanvas('canv', 'canv', 1000, 1000)
        canv.cd()

        timestamp = time.strftime("%Y%m%d_%H%M")
        output_file = '%s/calibration/%sadc0_cal.png' % (obj.data_folder, timestamp)
        if not os.path.exists(os.path.dirname(output_file)):
            try:
                os.makedirs(os.path.dirname(output_file))
            except OSError as exc:  # Guard against race condition
                print "Unable to create directory"
        open(output_file, 'w').close()
        adc0_Conv_g.Draw('ap')
        canv.SaveAs(output_file)

        output_file = '%s/calibration/%sadc1_cal.png' % (obj.data_folder, timestamp)
        if not os.path.exists(os.path.dirname(output_file)):
            try:
                os.makedirs(os.path.dirname(output_file))
            except OSError as exc:  # Guard against race condition
                print "Unable to create directory"
        open(output_file, 'w').close()
        adc1_Conv_g.Draw('ap')
        canv.SaveAs(output_file)





