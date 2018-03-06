from routines import *
from generator import *
import ROOT as r
import numpy as np


def calc_cal_dac_conversion_factor(dac_values, charge_values, production="no"):

    r.gStyle.SetStatX(0.5)
    r.gStyle.SetStatY(0.8)
    r.gStyle.SetOptFit(True)

    cal_dac_fc_g = r.TGraph(len(dac_values), np.array(dac_values), np.array(charge_values))

    cal_dac_fc_g.SetName('cal_dac_fc_g')
    cal_dac_fc_g.SetTitle('CAL_DAC Calibration;255-CAL_DAC;Charge [fC]')
    cal_dac_fc_g.SetMarkerStyle(3)

    cal_dac_fc_fitR = cal_dac_fc_g.Fit('pol1', 'S')

    cal_dac_fcM = cal_dac_fc_fitR.GetParams()[1]
    cal_dac_fcB = cal_dac_fc_fitR.GetParams()[0]

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
    return [cal_dac_fcM, cal_dac_fcB]


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

    adc0M = adc0fitR.GetParams()[1]
    adc0B = adc0fitR.GetParams()[0]

    adc1M = adc1fitR.GetParams()[1]
    adc1B = adc1fitR.GetParams()[0]

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
    return [adc0M, adc0B, adc1M, adc1B]




