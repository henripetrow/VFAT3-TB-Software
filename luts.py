# hv3b_biasing_lut = {'PRE_I_BSF':,
#                     'PRE_I_BIT':,
#                     'PRE_I_BLCC':,
#                     'PRE_VREF':,
#                     'SH_I_BFCAS':,
#                     'SH_I_BDIFF':,
#                     'SD_I_BDIFF':,
#                     'SD_I_BSF':,
#                     'SD_I_BFCAS':}


# Selection Criteria for the production test
# [yellow_low, yellow_high, red_low, red_high]
lim_BIST = [1080300, 1080300, 'n', 'n']
lim_ADC0m = [1.785006, 2.065055, 'n', 'n']
lim_ADC0b = [-349.691160, -285.799496, 'n', 'n']
lim_ADC1m = [2.131612, 2.301601, 'n', 'n']
lim_ADC1b = [-527.874922, -404.574515, 'n', 'n']
lim_CAL_DACm = [-0.316457, -0.169669, 'n', 'n']
lim_CAL_DACb = [35.755304, 86.506418, 'n', 'n']
lim_iref = [19.965942, 44.659058, 'n', 'n']
lim_Mean_Thresholds = [2.733017, 6.105230, 'n', 'n']
lim_Mean_enc = [0.099091, 0.198734, 'n', 'n']
lim_Register_Test = [0., 0, 0, 0]
lim_EC_Errors = [0, 0, 0, 0]
lim_BC_Errors = [0, 0, 0, 0]
lim_CRC_Errors = [0, 0, 0, 0]
lim_Hit_Errors = [0, 0, 0, 100]
lim_Noisy_Channels = [0, 0.524326, 'n', 'n']
lim_Dead_Channels = [0, 0.520016, 'n', 'n']
lim_Analog_Power_SLEEP = [36.144520, 74.543496, 'n', 'n']
lim_Digital_Power_SLEEP = [59.167197, 69.376485, 'n', 'n']
lim_Analog_Power_RUN = [211.955885, 297.586341, 'n', 'n']
lim_Digital_Power_RUN = [75.770665, 86.720968, 'n', 'n']


adc0_dac_selection_criteria_lut = {"CFD_DAC_1": [600, 850],
                                   "CFD_DAC_2": [550, 900],
                                   "HYST_DAC": [180, 300],
                                   "PRE_I_BLCC": [180, 300],
                                   "PRE_I_BSF": [640, 840],
                                   "SD_I_BSF": [580, 720],
                                   "ARM_DAC": [450, 700],
                                   "CAL_DAC": [215, 260],
                                   "PRE_VREF": [980, 1100],
                                   "PRE_I_BIT": [720, 880],
                                   "SD_I_BDIFF": [800, 980],
                                   "SH_I_BDIFF": [860, 980],
                                   "SD_I_BFCAS": [840, 1000],
                                   "SH_I_BFCAS": [840, 980],
                                   "ZCC_DAC": [400, 650]}

