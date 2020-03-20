import numpy
import matplotlib.pyplot as plt

gain = 'High'
arm_values = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
thresholds = [1.348262002375149, 1.9220152953946463, 2.3640977196625594, 2.8369307126025629, 3.3124976163706239,
              3.9601255830551101, 4.5572971315509685, 5.3493018228457476, 6.4051688171414192, 7.2418243803768041,
              8.3334771549366735, 9.6298644804688429, 10.903228239070421, 12.198457683172119, 14.169913199830889,
              16.299331595708555, 18.598998488265384, 22.784327925376502]

# arm_dac_fcM, arm_dac_fcB = numpy.polyfit(arm_values, numpy.log(thresholds), 1, w=numpy.sqrt(thresholds))
arm_dac_fcM, arm_dac_fcB = numpy.polyfit(arm_values, numpy.log(thresholds), 1)

# Plot Threshold in fC vs. ARM_DAC.
plt.figure()
fit_values = []
for value in arm_values:
    fit_values.append(numpy.exp(arm_dac_fcB) * numpy.exp(arm_dac_fcM * value))
plt.plot(arm_values, fit_values, label="fit")
for i, value in enumerate(arm_values):
    plt.plot(value, thresholds[i], 'r*')

plt.grid(True)
plt.xlabel('ARM_DAC[DAC]')
plt.ylabel('Threshold [fC]')
plt.title("Threshold vs. ARM_DAC, %s Gain" % gain)
plt.show()
plt.clf()