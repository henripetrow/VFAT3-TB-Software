from scipy import stats
import matplotlib.pyplot as plt


def calc_cal_dac_conversion_factor(obj, dac_values, base_value, ext_adc_values, production="no"):

    charge_values = []
    for step in ext_adc_values:
        difference = step - base_value
        charge = (difference / 1000.0) * 100.0  # 100 fF capacitor.
        charge_values.append(charge)

    if production == "yes":
        obj.database.save_lut_data_float("CAL_DAC_FC", charge_values, dac_values)

    # print dac_values
    # print charge_values
    cal_dac_fcM, cal_dac_fcB, r_value, p_value, std_err = stats.linregress(dac_values, charge_values)

    # print "CAL_DAC std_err: %f" % std_err
    print "CAL_DAC: %s %s" % (cal_dac_fcM, cal_dac_fcB)

    if production == "no":
        fit_values = []
        fig = plt.figure()
        for value in dac_values:
            fit_values.append(value * cal_dac_fcM + cal_dac_fcB)
        plt.plot(dac_values, fit_values, label="fit")
        for i, value in enumerate(dac_values):
            plt.plot(value, charge_values[i], 'r*')
        plt.legend()
        plt.grid(True)
        fig.savefig('cal_dac.png')
    else:
        obj.database.save_cal_dac(cal_dac_fcM, cal_dac_fcB)

    return [cal_dac_fcM, cal_dac_fcB]


def calc_adc_conversion_constants(obj, ext_adc, int_adc0, int_adc1, dac_values, production="no"):
    if production == "yes":
        obj.database.save_lut_data("ADC0_CAL_LUT", int_adc0, dac_values)
        obj.database.save_lut_data("ADC1_CAL_LUT", int_adc1, dac_values)
        obj.database.save_lut_data("EXT_ADC_CAL_LUT", ext_adc, dac_values)

    adc0M, adc0B, r_value, p_value, std_err0 = stats.linregress(int_adc0, ext_adc)
    adc1M, adc1B, r_value, p_value, std_err1 = stats.linregress(int_adc1, ext_adc)

    # print std_err0
    if std_err0 > 1:
        adc0M = 0
        adc0B = 0
    # print std_err1
    if std_err1 > 1:
        adc1M = 0
        adc1B = 0
    print "ADC0: %f %f" % (adc0M, adc0B)
    print "ADC1: %f %f" % (adc1M, adc1B)
    if production == "yes":
        obj.database.save_adc0(adc0M, adc0B)
        obj.database.save_adc1(adc1M, adc1B)

    if production == 'no':
        int_adc0_calibrated = []
        int_adc1_calibrated = []
        for value in int_adc0:
            int_adc0_calibrated.append(value * adc0M + adc0B)
        for value in int_adc1:
            int_adc1_calibrated.append(value * adc1M + adc1B)
        fig = plt.figure()
        plt.plot(dac_values, int_adc0_calibrated, label="ADC0")
        plt.plot(dac_values, int_adc1_calibrated, label="ADC1")
        plt.plot(dac_values, ext_adc, label="extADC")
        plt.legend()
        plt.grid(True)
        fig.savefig('adcs.png')

    return [adc0M, adc0B, adc1M, adc1B]




