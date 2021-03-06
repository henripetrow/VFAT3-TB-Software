from xml.dom import minidom
import matplotlib.pyplot as plt
import numpy
import os


def conv_float(value):
    try:
        converted_value = float(value)
    except ValueError:
        converted_value = None
    return converted_value


def conv_int(value):
    try:
        converted_value = int(value)
    except ValueError:
        converted_value = None
    return converted_value


def plot_data(data, title, ylabel, ylim, value_limits=""):
    rejected_indexes = []
    rejected_values = []
    rejected_serial_numbers = []

    # print title
    # print data

    if value_limits:
        valid_values = []
        for position, item in enumerate(data):
            if item < value_limits[0] or item > value_limits[1]:
                rejected_indexes.append(position)
                rejected_values.append(item)
                rejected_serial_numbers.append(serial_numbers[position])
            else:
                valid_values.append(item)
        # Remove None values.
        data_nones_removed = []
        for data_item in valid_values:
            if data_item is not None:
                data_nones_removed.append(data_item)
        sigma = numpy.std(data_nones_removed)
        mean = numpy.mean(data_nones_removed)
        max_value = max(data_nones_removed)
        min_value = min(data_nones_removed)
    else:
        # Remove None values.
        data_nones_removed = []
        for data_item in data:
            if data_item is not None:
                data_nones_removed.append(data_item)
        sigma = numpy.std(data_nones_removed)
        mean = numpy.mean(data_nones_removed)
        max_value = max(data_nones_removed)
        min_value = min(data_nones_removed)
    mean_data = [mean] * len(data)
    minus_3sigma_data = [mean-3*sigma] * len(data)
    plus_3sigma_data = [mean+3*sigma] * len(data)
    minus_4sigma_data = [mean-4*sigma] * len(data)
    plus_4sigma_data = [mean+4*sigma] * len(data)
    title_m = title.replace(" ", "_")
    print "lim_%s = [%f, %f]" % (title_m, mean-4*sigma, mean+4*sigma)
    fig = plt.figure()
    plt.plot(data, label=title)
    plt.plot(mean_data, label="Mean")
    plt.plot(minus_3sigma_data, "g--", label="3 sigma")
    plt.plot(plus_3sigma_data, "g--")
    plt.plot(minus_4sigma_data, "r--", label="4 sigma")
    plt.plot(plus_4sigma_data, "r--")
    if rejected_indexes:
        for i, index in enumerate(rejected_indexes):
            if rejected_values[i] < ylim[0]:
                plt.text(index, ylim[0], rejected_serial_numbers[i])
                if i == 0:
                    plt.plot(index, ylim[0], "rX", label="rejected value")
                else:
                    plt.plot(index, ylim[0], "rX")
            elif rejected_values[i] > ylim[1]:
                plt.text(index, ylim[1], rejected_serial_numbers[i])
                if i == 0:
                    plt.plot(index, ylim[1], "rX", label="rejected value")
                else:
                    plt.plot(index, ylim[1], "rX")
            else:
                plt.text(index, rejected_values[i], rejected_serial_numbers[i])
                if i == 0:
                    plt.plot(index, rejected_values[i], "rX", label="rejected value")
                else:
                    plt.plot(index, rejected_values[i], "rX")
    if mean >= 0:
        text_pos = ylim[0]+(ylim[1]-ylim[0])*0.8
    else:
        text_pos = ylim[0]-(ylim[0]-ylim[1])*0.8
    plt.text(1, text_pos, "Mean: %.2f\nMax: %.2f\nMin: %.2f\nstd: %.2f" % (mean, max_value, min_value, sigma),
             bbox=dict(alpha=0.5))
    # plt.title("%s before Glob-top" % title)
    plt.title("%s" % title)
    plt.ylim(ylim)
    plt.xlabel("Hybrids")
    plt.ylabel(ylabel)
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.xticks([])
    title = title.replace(" ", "_")
    # filename = "./results/xml_analysis/%s_pre" % title
    filename = "./results/xml_analysis/%s" % title
    fig.savefig(filename)




# parse an xml file by name

mydoc = minidom.parse('/home/a0312687/Downloads/results/xml/VFAT3_Production_summary.xml')
# mydoc = minidom.parse('/home/a0312687/cernbox/Data/production_data_xml_test/VFAT3_Production_summary.xml')

datasets = mydoc.getElementsByTagName('DATASET')

serial_numbers = []
adc0ms = []
adc0bs = []
adc1ms = []
adc1bs = []
cal_dacms = []
cal_dacbs = []
irefs = []
mean_thrs = []
mean_encs = []
register_tests = []
ec_errors = []
bc_errors = []
crc_errors = []
hit_errors = []
noisy_channels = []
dead_channels = []
bists = []
sleep_analog = []
sleep_digital = []
run_analog = []
run_digital = []

filename = "./results/xml/pre_LoadVFAT3s.xml"
try:
    os.makedirs(os.path.dirname(filename))
except OSError as exc:  # Guard against race condition
    print "Unable to create directory"


# print datasets[0].childNodes[5].childNodes[3].firstChild.data  # serial number


xml_data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
xml_data += '<ROOT xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
xml_data += '<PARTS>\n'
outF = open(filename, "w")
outF.write(xml_data)
outF.close()
for dataset in datasets:
    if int(dataset.childNodes[5].childNodes[3].firstChild.data) < 70:
        pass
    else:
        xml_data = '<PART mode="auto">\n'
        xml_data += '<KIND_OF_PART>GEM VFAT3</KIND_OF_PART>\n'
        serial_number = dataset.childNodes[5].childNodes[3].firstChild.data
        print serial_number
        xml_data += '<SERIAL_NUMBER>0x%x</SERIAL_NUMBER>\n<BARCODE>%i</BARCODE>\n' % (int(serial_number), int(serial_number))
        serial_numbers.append(dataset.childNodes[5].childNodes[3].firstChild.data)
        adc0ms.append(conv_float(dataset.childNodes[7].childNodes[9].firstChild.data))  # ad0m
        adc0bs.append(conv_float(dataset.childNodes[7].childNodes[11].firstChild.data))  # adc0b
        adc1ms.append(conv_float(dataset.childNodes[7].childNodes[13].firstChild.data))  # adc1m
        adc1bs.append(conv_float(dataset.childNodes[7].childNodes[15].firstChild.data))  # adc1b
        cal_dacms.append(conv_float(dataset.childNodes[7].childNodes[17].firstChild.data))  # cal_dacm
        cal_dacbs.append(conv_float(dataset.childNodes[7].childNodes[19].firstChild.data))  # cal_dacb
        irefs.append(conv_int(dataset.childNodes[7].childNodes[21].firstChild.data))  # iref
        mean_thrs.append(conv_float(dataset.childNodes[7].childNodes[23].firstChild.data))  # mean thr
        mean_encs.append(conv_float(dataset.childNodes[7].childNodes[25].firstChild.data))  # mean enc
        register_tests.append(conv_int(dataset.childNodes[7].childNodes[27].firstChild.data))  # register test
        ec_errors.append(conv_int(dataset.childNodes[7].childNodes[29].firstChild.data))  # ec errors
        bc_errors.append(conv_int(dataset.childNodes[7].childNodes[31].firstChild.data))  # bc errors
        crc_errors.append(conv_int(dataset.childNodes[7].childNodes[33].firstChild.data))  # crc errors
        hit_errors.append(conv_int(dataset.childNodes[7].childNodes[35].firstChild.data))  # hit errors
        noisy_channels.append(conv_int(dataset.childNodes[7].childNodes[37].firstChild.data))  # noisy channels
        dead_channels.append(conv_int(dataset.childNodes[7].childNodes[39].firstChild.data))  # dead channels
        bists.append(conv_int(dataset.childNodes[7].childNodes[41].firstChild.data))  # BIST
        sleep_analog.append(conv_float(dataset.childNodes[7].childNodes[45].firstChild.data))  # SLEEP analog
        sleep_digital.append(conv_float(dataset.childNodes[7].childNodes[47].firstChild.data))  # SLEEP digital
        run_analog.append(conv_float(dataset.childNodes[7].childNodes[49].firstChild.data))  # RUN analog
        run_digital.append(conv_float(dataset.childNodes[7].childNodes[51].firstChild.data))  # RUN digital
        xml_data += '</PART>\n'
        outF = open(filename, "a")
        outF.write(xml_data)
        outF.close()
xml_data = '</PARTS>\n'
xml_data += '</ROOT>\n'
outF = open(filename, "a")
outF.write(xml_data)
outF.close()

plot_data(adc0ms, "ADC0m", "multiplier [mV/DAC count]", [1.6, 2.5])
plot_data(adc0bs, "ADC0b", "offset [mV]", [-400, -200])
plot_data(adc1ms, "ADC1m", "multiplier [mV/DAC count]", [2, 2.5])
plot_data(adc1bs, "ADC1b", "offset [mV]", [-550, -350])
plot_data(cal_dacms, "CAL_DACm", "multiplier [fC/DAC count]", [-0.4, -0.14])
plot_data(cal_dacbs, "CAL_DACb", "offset [fC]", [0, 100])
plot_data(irefs, "iref", "iref_dac [DAC count]", [0, 50])
plot_data(mean_thrs, "Mean Thresholds", "Threshold [fC]", [0, 10], value_limits=[2, 8])
plot_data(mean_encs, "Mean enc", "enc [fC]", [0, 0.4], value_limits=[0.1, 1])
plot_data(register_tests, "Register Test", "Errors", [0, 10])
plot_data(ec_errors, "EC Errors", "Errors", [0, 10])
plot_data(bc_errors, "BC Errors", "Errors", [0, 10])
plot_data(crc_errors, "CRC Errors", "Errors", [0, 10])
plot_data(hit_errors, "Hit Errors", "Errors", [0, 10])
plot_data(noisy_channels, "Noisy Channels", "Noisy channels", [0, 100], value_limits=[-1,1])
plot_data(dead_channels, "Dead Channels", "Dead channels", [0, 100], value_limits=[-1,1])
plot_data(sleep_analog, "Analog Power SLEEP", "Power [mW]", [20, 120], value_limits=[20, 90])
plot_data(sleep_digital, "Digital Power SLEEP", "Power [mW]", [40, 120], value_limits=[25, 80])
plot_data(run_analog, "Analog Power RUN", "Power [mW]", [150, 400], value_limits=[150, 400])
plot_data(run_digital, "Digital Power RUN", "Power [mW]", [40, 120], value_limits=[50, 150])