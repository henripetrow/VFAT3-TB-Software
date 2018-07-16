

# Location that is set to the database
hybrid_location = "Hybrid SA"


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
                    'CAL_DAC': ['n', 0]}



# Selection Criteria for the production test
# [yellow_low, yellow_high, red_low, red_high]
lim_BIST = [0, 1080300, 'n', 'n']
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
lim_Analog_Power_RUN = [64, 84, 'n', 'n']
lim_Digital_Power_RUN = [75.770665, 86.720968, 'n', 'n']

# Selection criteria
adc0_dac_selection_criteria_lut = {"CFD_DAC_1": [600, 850, 'n', 'n'],
                                   "CFD_DAC_2": [550, 900, 'n', 'n'],
                                   "HYST_DAC": [180, 300, 'n', 'n'],
                                   "PRE_I_BLCC": [180, 300, 'n', 'n'],
                                   "PRE_I_BSF": [640, 840, 'n', 'n'],
                                   "SD_I_BSF": [580, 720, 'n', 'n'],
                                   "ARM_DAC": [450, 700, 'n', 'n'],
                                   "CAL_DAC": [215, 260, 'n', 'n'],
                                   "PRE_VREF": [980, 1100, 'n', 'n'],
                                   "PRE_I_BIT": [720, 880, 'n', 'n'],
                                   "SD_I_BDIFF": [800, 980, 'n', 'n'],
                                   "SH_I_BDIFF": [860, 980, 'n', 'n'],
                                   "SD_I_BFCAS": [840, 1000, 'n', 'n'],
                                   "SH_I_BFCAS": [840, 980, 'n', 'n'],
                                   "ZCC_DAC": [400, 650, 'n', 'n']}

