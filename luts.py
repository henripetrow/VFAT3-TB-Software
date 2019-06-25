

# Location that is set to the database
hybrid_location = "CERN 14-5-28"


# Nominal biasing value in voltages read from ADC
# [nominal value in mv, DAC value found by scan]
hv3b_biasing_lut = {'PRE_I_BSF': [230, 0],
                    'PRE_I_BIT': [700, 0],
                    'PRE_I_BLCC': [150, 0],
                    'PRE_VREF': [430, 0],
                    'SH_I_BFCAS': [620, 0],
                    'SH_I_BDIFF': [420, 0],
                    'SD_I_BDIFF': [660, 0],
                    'SD_I_BSF': [250, 0],
                    'SD_I_BFCAS': [640, 0],
                    'CFD_DAC_1': [500, 0],
                    'CFD_DAC_2': [500, 0],
                    'HYST_DAC': [102, 0],
                    'ARM_DAC': [64, 0],
                    'ZCC_DAC': [22, 0],
                    'CAL_DAC': ['n', 0],
                    'Iref': [100, 0]}


par_psu_voltage = 3  # V
par_psu_current_limit = 0.5  # A
lim_short_circuit = 0.300  # A

# Selection Criteria for the production test
# [yellow_low, yellow_high, red_low, red_high]
lim_BIST = [1080298, 1080310, 'n', 'n']
lim_ADC0m = [1.785006, 2.065055, 0, 0]
lim_ADC0b = [-349.691160, -285.799496, 0, 0]
lim_ADC1m = [2.131612, 2.301601, 0, 0]
lim_ADC1b = [-527.874922, -404.574515, 0, 0]
lim_CAL_DACm = [-0.316457, -0.169669, 'n', 'n']
lim_CAL_DACb = [35.755304, 86.506418, 'n', 'n']
lim_iref = [95, 105, 94, 106]
lim_Mean_Thresholds = [2.733017, 7.105230, 'n', 'n']
lim_Mean_enc = [0.2, 0.55, 'n', 'n']
lim_Register_Test = [0., 0, 0, 0]
lim_EC_Errors = [0, 0, 0, 0]
lim_BC_Errors = [0, 0, 0, 0]
lim_CRC_Errors = [0, 0, 0, 0]
lim_Hit_Errors = [0, 0, 0, 100]
lim_Noisy_Channels = [0, 3, 'n', 'n']
lim_Dead_Channels = [0, 3, 'n', 'n']
lim_Problematic_Channels = [0, 3, 'n', 'n']
lim_Analog_Power_SLEEP = [36.144520, 71.543496, 'n', 'n']
lim_Digital_Power_SLEEP = [59.167197, 100, 'n', 'n']
lim_Analog_Power_RUN = [64, 300, 'n', 'n']
lim_Digital_Power_RUN = [75.770665, 110, 'n', 'n']
lim_Temperature_k2 = [-140, -70, 'n', 'n']
lim_Temperature = [20, 30, 'n', 'n']
lim_sbits = [0, 0, 0, 0]


# selection criteria for S-curve channel classification.

lim_enc_noisy_channel = 1
lim_enc_noisy_channel_flex_end_channels = 5

lim_enc_unbonded_channel = 0.13
lim_enc_unbonded_channel_flex_end_channels = 1

# Untrimmable channel calculation.
lim_sigma = 3
lim_sigma_flex_end_channels = 5
lim_trim_dac_scale = 4

# Selection criteria
adc0_dac_selection_criteria_lut = {"CFD_DAC_1": [500, 950, 'n', 'n'],
                                   "CFD_DAC_2": [450, 1000, 'n', 'n'],
                                   "HYST_DAC": [80, 400, 'n', 'n'],
                                   "PRE_I_BLCC": [80, 400, 'n', 'n'],
                                   "PRE_I_BSF": [540, 940, 'n', 'n'],
                                   "SD_I_BSF": [480, 820, 'n', 'n'],
                                   "ARM_DAC": [350, 800, 'n', 'n'],
                                   "CAL_DAC": [115, 360, 'n', 'n'],
                                   "PRE_VREF": [880, 1200, 'n', 'n'],
                                   "PRE_I_BIT": [620, 980, 'n', 'n'],
                                   "SD_I_BDIFF": [700, 1080, 'n', 'n'],
                                   "SH_I_BDIFF": [760, 1080, 'n', 'n'],
                                   "SD_I_BFCAS": [740, 1100, 'n', 'n'],
                                   "SH_I_BFCAS": [740, 1080, 'n', 'n'],
                                   "ZCC_DAC": [300, 750, 'n', 'n']}

# Production s-curve parameters
par_start_channel = 0
par_stop_channel = 127
par_channel_step = 1
par_pulsestretch = 7
par_latency = 50
par_calphi = 0
par_arm_dac = 90
par_start_cal_dac = 170
par_stop_cal_dac = 235
par_triggers = 400

# Enc plot y-range. mean enc plus

par_enc_plot_lim = 1

# Threshold plot y-range. mean thr plus

par_thr_plot_lim = 3

# For re-running the S-curve on certain channels with different cal dac window.
par_rerun_scurve_channel_list = []
par_cal_dac_start_rerun = 160
par_cal_dac_stop_rerun = 250

# Parameters for the median filtering.

par_kernel_size = 7

# Scurve fit starting value pairs
par_st_x_list = [13, 12, 11, 15]
par_st_y_list = [0.4, 0.3, 0.2, 5]