from FW_interface import *

class Vfat3Object:
    def __init__(self):
        self.cal_dac_fcM = 0
        self.cal_dac_fcB = 0
        self.rerun_scurve_channel_list = []
        self.cal_dac_start_rerun = 0
        self.cal_dac_stop_rerun = 0
        self.d1 = 0
        self.d2 = 0
        self.interfaceFW = FW_interface(0)


vfat3_obj = Vfat3Object()

start = time.time()

# Set channels and Cal dac range.
start_ch = 0
stop_ch = 127
start_dac_value = dac_range[0]
stop_dac_value = dac_range[1]
print "Running S-curves for channels: %i-%i, for CAL_DAC range: %i-%i:" % (start_ch, stop_ch, start_dac_value, stop_dac_value)
samples_per_dac_value = 100

# Create list of cal dac values.
cal_dac_values = range(start_dac_value, stop_dac_value+1)
cal_dac_values.reverse()
cal_dac_values[:] = [vfat3_obj.cal_dac_fcM * x + vfat3_obj.cal_dac_fcB for x in cal_dac_values]

# Create a list of channels the s-curve is run on.
channels = range(start_ch, stop_ch+1, ch_step)

# Launch S-curve routine in firmware.
scurve_data = vfat3_obj.interfaceFW.run_scurve(start_ch, stop_ch, ch_step, start_dac_value, stop_dac_value, arm_dac, triggers, latency, vfat3_obj)

# Analyze data.
mean_th_fc, mean_enc_fc, noisy_channels, dead_channels, enc_list, thr_list, channel_category, unbonded_channels, untrimmable_channels = scurve_analyze_numpy(vfat3_obj, cal_dac_values, channels, scurve_data, verbose=verbose)



# Print routine duration.
stop = time.time()
run_time = (stop - start) / 60
text = "S-curve Run time (minutes): %f\n" % run_time
print text
