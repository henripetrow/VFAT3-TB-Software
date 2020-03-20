import numpy
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit

# gain = 'High'
# arm_values = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
# thresholds = [1.348262002375149, 1.9220152953946463, 2.3640977196625594, 2.8369307126025629, 3.3124976163706239,
#               3.9601255830551101, 4.5572971315509685, 5.3493018228457476, 6.4051688171414192, 7.2418243803768041,
#               8.3334771549366735, 9.6298644804688429, 10.903228239070421, 12.198457683172119, 14.169913199830889,
#               16.299331595708555, 18.598998488265384, 22.784327925376502]

gain = 'Medium'
arm_values = numpy.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160])
thresholds = numpy.array([1.5737974242415889, 3.1065293496705233, 4.3476081986120079, 5.9706513717879259, 7.5594407063625058,
              8.9206746507261876, 10.541473135613805, 12.608970322443145, 14.507733880546388, 16.729497062165986,
              19.473473145434752, 22.0167733105664, 24.902603095877453, 28.630473169366493, 32.320441327236324,
              35.986788485746111])

arm_dac_fcM, arm_dac_fcB = numpy.polyfit(arm_values, numpy.log(thresholds), 1, w=numpy.sqrt(thresholds))
arm_dac_fcM_w, arm_dac_fcB_w = numpy.polyfit(arm_values, numpy.log(thresholds), 1)
arm_dac_fcM_l, arm_dac_fcB_l, r_value, p_value, std_err = stats.linregress(arm_values, thresholds)

print arm_dac_fcM, arm_dac_fcB
print arm_dac_fcM_l, arm_dac_fcB_l
print arm_dac_fcM_w, arm_dac_fcB_w

def exponential_func(x, a, b):
    return a*numpy.exp(-b*x)


output = curve_fit(exponential_func, arm_values, thresholds, p0=(1, 1 ))
print output[0]

# Plot Threshold in fC vs. ARM_DAC.
plt.figure()
fit_values = []

fit_values_l = []
for value in arm_values:
    fit_values_l.append(value * arm_dac_fcM_l + arm_dac_fcB_l)
plt.plot(arm_values, fit_values_l, label="Linear fit")

for value in arm_values:
    fit_values.append(numpy.exp(arm_dac_fcB) * numpy.exp(arm_dac_fcM * value))
plt.plot(arm_values, fit_values, label="exp fit")

fit_values_w = []
for value in arm_values:
    fit_values_w.append(numpy.exp(arm_dac_fcB_w) * numpy.exp(arm_dac_fcM_w * value))
plt.plot(arm_values, fit_values_w, label="exp weighted fit")

fit_values_s = []
for value in arm_values:
    fit_values_s.append(output[0][0] * numpy.exp(output[0][1] * value))
plt.plot(arm_values, fit_values_s, label="curve_fit")

for i, value in enumerate(arm_values):
    plt.plot(value, thresholds[i], 'r*')

plt.legend()
plt.grid(True)
plt.xlabel('ARM_DAC[DAC]')
plt.ylabel('Threshold [fC]')
plt.title("Threshold vs. ARM_DAC, %s Gain" % gain)
plt.show()
plt.clf()