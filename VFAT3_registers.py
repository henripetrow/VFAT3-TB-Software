############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################


register = [None]*65541

class GBL_CFG_CH:
    def __init__(self):
        self.cal = [0,1]
        self.mask = [0,1]
        self.zcc_dac = [0,7]
        self.arm_dac = [0,7]

        self.reg_array = [self.cal,self.mask,self.zcc_dac,self.arm_dac]

    def change_values(self, new_values):
 
        self.cal[0] = int(new_values[0],2)
        self.mask[0] = int(new_values[1],2)
        self.zcc_dac[0] = int(new_values[2:9],2)
        self.arm_dac[0] = int(new_values[9:],2)

for i in range(0,129):
    register[i] = GBL_CFG_CH()

class GBL_CFG_CTR_0:
    def __init__(self):
        self.PS = [0, 3]
        self.empty1 = [0, 10]
        self.SyncLevelEnable = [0, 1]
        self.ST = [0, 1]
        self.DDR = [0, 1]
        self.reg_array = [self.PS,self.empty1,self.SyncLevelEnable,self.ST,self.DDR]

    def change_values(self, new_values):
 
        self.PS[0] = int(new_values[0:3],2)
        self.SyncLevelEnable[0] = int(new_values[13],2)
        self.ST[0] = int(new_values[14],2)
        self.DDR[0] = int(new_values[15],2)

register[129] = GBL_CFG_CTR_0()


class GBL_CFG_CTR_1:
    def __init__(self): 
        self.P16 = [0,1]
        self.empty1 = [0, 1]
        self.PAR = [0,4]
        self.empty2 = [0, 1]
        self.DT = [0,1]
        self.SZP = [0,1]
        self.SZD = [0,1]
        self.TT = [0,2]
        self.empty3 = [0, 1]
        self.ECb = [0,2]
        self.BCb = [0,1]

        self.reg_array = [self.P16,self.empty1,self.PAR,self.empty2,self.DT,self.SZP,self.SZD,self.TT,self.empty2,self.ECb,self.BCb]

    def change_values(self, new_values):
        self.P16[0] = int(new_values[0],2)
        self.PAR[0] = int(new_values[2:6],2)
        self.DT[0] = int(new_values[7],2)
        self.SZP[0] = int(new_values[8],2)
        self.SZD[0] = int(new_values[9],2)
        self.TT[0] = int(new_values[10:12],2)
        self.ECb[0] = int(new_values[13:15],2)
        self.BCb[0] = int(new_values[15],2)    

register[130] = GBL_CFG_CTR_1()


class GBL_CFG_CTR_2:
    def __init__(self):
        self.empty1 = [0, 8]
        self.TP_FE = [0,3]
        self.RES_PRE = [1,3]
        self.CAP_PRE = [0,2]

        self.reg_array = [self.empty1,self.TP_FE,self.RES_PRE,self.CAP_PRE]

    def change_values(self, new_values):
 
        self.TP_FE[0] = int(new_values[8:11],2)
        self.RES_PRE[0] = int(new_values[11:14],2)
        self.CAP_PRE[0] = int(new_values[14:],2)


register[131] = GBL_CFG_CTR_2()



class GBL_CFG_CTR_3:
    def __init__(self):
        self.empty1 = [0, 6]
        self.PT = [1,4]
        self.EN_HYST = [1,1]
        self.SEL_POL = [0,1]
        self.Force_En_ZCC = [0,1]
        self.Force_TH = [0,1]
        self.SEL_COMP_MODE = [0,2]

        self.reg_array = [self.empty1,self.PT,self.EN_HYST,self.SEL_POL,self.Force_En_ZCC,self.Force_TH,self.SEL_COMP_MODE]

    def change_values(self, new_values):
        self.PT[0] = int(new_values[6:10],2)
        self.EN_HYST[0] = int(new_values[10],2)
        self.SEL_POL[0] = int(new_values[11],2)
        self.Force_En_ZCC[0] = int(new_values[12],2)
        self.Force_TH[0] = int(new_values[13],2)
        self.SEL_COMP_MODE[0] = int(new_values[14:],2)



register[132] = GBL_CFG_CTR_3()

class GBL_CFG_CTR_4:
    def __init__(self):
        self.empty1 = [0, 6]
        self.VREF_ADC = [1,2]
        self.Mon_Gain = [0,1]
        self.empty2 = [0, 1]
        self.Monitor_Sel = [0,6]

        self.reg_array = [self.empty1,self.VREF_ADC,self.Mon_Gain,self.empty2,self.Monitor_Sel]

    def change_values(self, new_values):
        self.VREF_ADC[0] = int(new_values[6:8],2)
        self.Mon_Gain[0] = int(new_values[8],2)
        self.Monitor_Sel[0] = int(new_values[10:],2)


register[133] = GBL_CFG_CTR_4()

class GBL_CFG_CTR_5:
    def __init__(self):
        self.empty1 = [0,10]
        self.Iref = [32,6]

        self.reg_array = [self.empty1,self.Iref]

    def change_values(self, new_values):
        self.Iref[0] = int(new_values[10:],2)


register[134] = GBL_CFG_CTR_5()

class GBL_CFG_THR:
    def __init__(self):
        self.ZCC_DAC = [11,8]
        self.ARM_DAC = [32,8]

        self.reg_array = [self.ZCC_DAC,self.ARM_DAC]

    def change_values(self, new_values):
        self.ZCC_DAC[0] = int(new_values[0:8],2)
        self.ARM_DAC[0] = int(new_values[8:],2)

register[135] = GBL_CFG_THR()

class GBL_CFG_HYS:
    def __init__(self):
        self.empty1 = [0,10]
        self.HYST_DAC = [5,6]

        self.reg_array = [self.empty1,self.HYST_DAC]

    def change_values(self, new_values):
        self.HYST_DAC[0] = int(new_values[10:],2)

register[136] = GBL_CFG_HYS()

class GBL_CFG_LAT:
    def __init__(self):
        self.LAT = [0,16]

        self.reg_array = [self.LAT]

    def change_values(self, new_values):
        self.LAT[0] = int(new_values[:],2)


register[137] = GBL_CFG_LAT()


class GBL_CFG_CAL_0:
    def __init__(self):
        self.empty1 = [0,1]
        self.CAL_SEL_POL = [0,1]
        self.CAL_PHI = [0,3]
        self.CAL_EXT = [0,1]
        self.CAL_DAC = [0,8]
        self.CAL_MODE = [0,2]

        self.reg_array = [self.empty1,self.CAL_SEL_POL,self.CAL_PHI,self.CAL_EXT,self.CAL_DAC,self.CAL_MODE]

    def change_values(self, new_values):
        self.CAL_SEL_POL[0] = int(new_values[1],2)
        self.CAL_PHI[0] = int(new_values[2:5],2)
        self.CAL_EXT[0] = int(new_values[5],2)
        self.CAL_DAC[0] = int(new_values[6:14],2)
        self.CAL_MODE[0] = int(new_values[14:],2)

register[138] = GBL_CFG_CAL_0()


class GBL_CFG_CAL_1:
    def __init__(self):
        self.empty1 = [0,5]
        self.CAL_FS = [0,2]
        self.CAL_DUR = [511,9]

        self.reg_array = [self.empty1,self.CAL_FS,self.CAL_DUR]

    def change_values(self, new_values):
        self.CAL_FS[0] = int(new_values[5:7],2)
        self.CAL_DUR[0] = int(new_values[7:],2)


register[139] = GBL_CFG_CAL_1()


class GBL_CFG_BIAS_0:
    def __init__(self):
        self.empty1 = [0, 4]
        self.CFD_DAC_2 = [40,6]
        self.CFD_DAC_1 = [40,6]

        self.reg_array = [self.empty1,self.CFD_DAC_2,self.CFD_DAC_1]

    def change_values(self, new_values):
        self.CFD_DAC_2[0] = int(new_values[4:10],2)
        self.CFD_DAC_1[0] = int(new_values[10:],2)

register[140] = GBL_CFG_BIAS_0()


class GBL_CFG_BIAS_1:
    def __init__(self):
        self.empty1 = [0, 2]
        self.PRE_I_BSF = [1,6]
        self.PRE_I_BIT = [1,8]

        self.reg_array = [self.empty1,self.PRE_I_BSF,self.PRE_I_BIT]

    def change_values(self, new_values):
        self.PRE_I_BSF[0] = int(new_values[2:8],2)
        self.PRE_I_BIT[0] = int(new_values[8:],2)

register[141] = GBL_CFG_BIAS_1()


class GBL_CFG_BIAS_2:
    def __init__(self):
        self.empty1 = [0,2]
        self.PRE_I_BLCC = [15,6]
        self.PRE_VREF = [86,8]

        self.reg_array = [self.empty1,self.PRE_I_BLCC,self.PRE_VREF]

    def change_values(self, new_values):
        self.PRE_I_BLCC[0] = int(new_values[2:8],2)
        self.PRE_VREF[0] = int(new_values[8:],2)

register[142] = GBL_CFG_BIAS_2()

class GBL_CFG_BIAS_3:
    def __init__(self):
        self.SH_I_BFCAS = [1,8]
        self.SH_I_BDIFF = [1,8]

        self.reg_array = [self.SH_I_BFCAS,self.SH_I_BDIFF]

    def change_values(self, new_values):
        self.SH_I_BFCAS[0] = int(new_values[0:8],2)
        self.SH_I_BDIFF[0] = int(new_values[8:],2)

register[143] = GBL_CFG_BIAS_3()


class GBL_CFG_BIAS_4:
    def __init__(self):
        self.empty1 = [0,2]
        self.empty2 = [0,6]
        self.SD_I_BDIFF = [1,8]

        self.reg_array = [self.empty1,self.empty2,self.SD_I_BDIFF]

    def change_values(self, new_values):
        self.SD_I_BDIFF[0] = int(new_values[8:],2)

register[144] = GBL_CFG_BIAS_4()


class GBL_CFG_BIAS_5:
    def __init__(self):
        self.empty1 = [0,2]
        self.SD_I_BSF = [1,6]
        self.SD_I_BFCAS = [1,8]

        self.reg_array = [self.empty1,self.SD_I_BSF,self.SD_I_BFCAS]

    def change_values(self, new_values):
        self.SD_I_BSF[0] = int(new_values[2:8],2)
        self.SD_I_BFCAS[0] = int(new_values[8:],2)

register[145] = GBL_CFG_BIAS_5()

class GBL_CFG_BIAS_6:
    def __init__(self):
        self.empty1 = [0,4]
        self.SLVS_IBIAS = [40,6]
        self.SLVS_VREF = [40,6]

        self.reg_array = [self.empty1,self.SLVS_IBIAS,self.SLVS_VREF]

    def change_values(self, new_values):
        self.SLVS_IBIAS[0] = int(new_values[4:10],2)
        self.SLVS_VREF[0] = int(new_values[10:],2)

register[146] = GBL_CFG_BIAS_6()

class GBL_CFG_RUN:
    def __init__(self):
        self.empty1 = [0,15]
        self.RUN = [0,1]

        self.reg_array = [self.empty1,self.RUN]

    def change_values(self, new_values):
        self.RUN[0] = int(new_values[-1],2)

register[65535] = GBL_CFG_RUN()

class HW_ID_ID:
    def __init__(self):
        self.ID = [90464596,32]

        self.reg_array = [self.ID]

    def change_values(self, new_values):
        self.ID[0] = int(new_values,2)

register[65536] = HW_ID_ID()


class HW_ID_VER:
    def __init__(self):
        self.VER = [196608,32]

        self.reg_array = [self.VER]

    def change_values(self, new_values):
        self.VER[0] = int(new_values,2)

register[65537] = HW_ID_VER()

class HW_RW_REG:
    def __init__(self):
        self.RW_REG = [0,32]

        self.reg_array = [self.RW_REG]

    def change_values(self, new_values):
        self.RW_REG[0] = int(new_values,2)

register[65538] = HW_RW_REG()


class HW_CHIP_ID:
    def __init__(self):
        self.CHIP_ID = [0,32]

        self.reg_array = [self.CHIP_ID]

    def change_values(self, new_values):
        self.CHIP_ID[0] = int(new_values,2)

register[65539] = HW_CHIP_ID()


class HW_PROG:
    def __init__(self):
        self.PRG_TIME = [0,11]
        self.PRG_BIT_ADD = [0,5]

    def change_values(self, new_values):
        self.PRG_TIME[0] = int(new_values,2)
        self.PRG_BIT_ADD[0] = int(new_values,2)

register[65540] = HW_PROG()


# These are only read through the button so no need for extra components.

class ADC_READ_0:
    def __init__(self):
        self.ADC_0 = 0


class ADC_READ_1:
    def __init__(self):
        self.ADC_1 = 0





LUT = {
'cal0':[0,0],
'mask0':[0,1],
'zcc_dac0':[0,2],
'arm_dac0':[0,3],

'cal1':[1,0],
'mask1':[1,1],
'zcc_dac1':[1,2],
'arm_dac1':[1,3],

'cal2':[2,0],
'mask2':[2,1],
'zcc_dac2':[2,2],
'arm_dac2':[2,3],

'cal3':[3,0],
'mask3':[3,1],
'zcc_dac3':[3,2],
'arm_dac3':[3,3],

'cal4':[4,0],
'mask4':[4,1],
'zcc_dac4':[4,2],
'arm_dac4':[4,3],

'cal5':[5,0],
'mask5':[5,1],
'zcc_dac5':[5,2],
'arm_dac5':[5,3],

'cal6':[6,0],
'mask6':[6,1],
'zcc_dac6':[6,2],
'arm_dac6':[6,3],

'cal7':[7,0],
'mask7':[7,1],
'zcc_dac7':[7,2],
'arm_dac7':[7,3],

'cal8':[8,0],
'mask8':[8,1],
'zcc_dac8':[8,2],
'arm_dac8':[8,3],

'cal9':[9,0],
'mask9':[9,1],
'zcc_dac9':[9,2],
'arm_dac9':[9,3],

'cal10':[10,0],
'mask10':[10,1],
'zcc_dac10':[10,2],
'arm_dac10':[10,3],

'cal11':[11,0],
'mask11':[11,1],
'zcc_dac11':[11,2],
'arm_dac11':[11,3],

'cal12':[12,0],
'mask12':[12,1],
'zcc_dac12':[12,2],
'arm_dac12':[12,3],

'cal13':[13,0],
'mask13':[13,1],
'zcc_dac13':[13,2],
'arm_dac13':[13,3],

'cal14':[14,0],
'mask14':[14,1],
'zcc_dac14':[14,2],
'arm_dac14':[14,3],

'cal15':[15,0],
'mask15':[15,1],
'zcc_dac15':[15,2],
'arm_dac15':[15,3],

'cal16':[16,0],
'mask16':[16,1],
'zcc_dac16':[16,2],
'arm_dac16':[16,3],

'cal17':[17,0],
'mask17':[17,1],
'zcc_dac17':[17,2],
'arm_dac17':[17,3],

'cal18':[18,0],
'mask18':[18,1],
'zcc_dac18':[18,2],
'arm_dac18':[18,3],

'cal19':[19,0],
'mask19':[19,1],
'zcc_dac19':[19,2],
'arm_dac19':[19,3],

'cal20':[20,0],
'mask20':[20,1],
'zcc_dac20':[20,2],
'arm_dac20':[20,3],

'cal21':[21,0],
'mask21':[21,1],
'zcc_dac21':[21,2],
'arm_dac21':[21,3],

'cal22':[22,0],
'mask22':[22,1],
'zcc_dac22':[22,2],
'arm_dac22':[22,3],

'cal23':[23,0],
'mask23':[23,1],
'zcc_dac23':[23,2],
'arm_dac23':[23,3],

'cal24':[24,0],
'mask24':[24,1],
'zcc_dac24':[24,2],
'arm_dac24':[24,3],

'cal25':[25,0],
'mask25':[25,1],
'zcc_dac25':[25,2],
'arm_dac25':[25,3],

'cal26':[26,0],
'mask26':[26,1],
'zcc_dac26':[26,2],
'arm_dac26':[26,3],

'cal27':[27,0],
'mask27':[27,1],
'zcc_dac27':[27,2],
'arm_dac27':[27,3],

'cal28':[28,0],
'mask28':[28,1],
'zcc_dac28':[28,2],
'arm_dac28':[28,3],

'cal29':[29,0],
'mask29':[29,1],
'zcc_dac29':[29,2],
'arm_dac29':[29,3],

'cal30':[30,0],
'mask30':[30,1],
'zcc_dac30':[30,2],
'arm_dac30':[30,3],

'cal31':[31,0],
'mask31':[31,1],
'zcc_dac31':[31,2],
'arm_dac31':[31,3],

'cal32':[32,0],
'mask32':[32,1],
'zcc_dac32':[32,2],
'arm_dac32':[32,3],

'cal33':[33,0],
'mask33':[33,1],
'zcc_dac33':[33,2],
'arm_dac33':[33,3],

'cal34':[34,0],
'mask34':[34,1],
'zcc_dac34':[34,2],
'arm_dac34':[34,3],

'cal35':[35,0],
'mask35':[35,1],
'zcc_dac35':[35,2],
'arm_dac35':[35,3],

'cal36':[36,0],
'mask36':[36,1],
'zcc_dac36':[36,2],
'arm_dac36':[36,3],

'cal37':[37,0],
'mask37':[37,1],
'zcc_dac37':[37,2],
'arm_dac37':[37,3],

'cal38':[38,0],
'mask38':[38,1],
'zcc_dac38':[38,2],
'arm_dac38':[38,3],

'cal39':[39,0],
'mask39':[39,1],
'zcc_dac39':[39,2],
'arm_dac39':[39,3],

'cal40':[40,0],
'mask40':[40,1],
'zcc_dac40':[40,2],
'arm_dac40':[40,3],

'cal41':[41,0],
'mask41':[41,1],
'zcc_dac41':[41,2],
'arm_dac41':[41,3],

'cal42':[42,0],
'mask42':[42,1],
'zcc_dac42':[42,2],
'arm_dac42':[42,3],

'cal43':[43,0],
'mask43':[43,1],
'zcc_dac43':[43,2],
'arm_dac43':[43,3],

'cal44':[44,0],
'mask44':[44,1],
'zcc_dac44':[44,2],
'arm_dac44':[44,3],

'cal45':[45,0],
'mask45':[45,1],
'zcc_dac45':[45,2],
'arm_dac45':[45,3],

'cal46':[46,0],
'mask46':[46,1],
'zcc_dac46':[46,2],
'arm_dac46':[46,3],

'cal47':[47,0],
'mask47':[47,1],
'zcc_dac47':[47,2],
'arm_dac47':[47,3],

'cal48':[48,0],
'mask48':[48,1],
'zcc_dac48':[48,2],
'arm_dac48':[48,3],

'cal49':[49,0],
'mask49':[49,1],
'zcc_dac49':[49,2],
'arm_dac49':[49,3],

'cal50':[50,0],
'mask50':[50,1],
'zcc_dac50':[50,2],
'arm_dac50':[50,3],

'cal51':[51,0],
'mask51':[51,1],
'zcc_dac51':[51,2],
'arm_dac51':[51,3],

'cal52':[52,0],
'mask52':[52,1],
'zcc_dac52':[52,2],
'arm_dac52':[52,3],

'cal53':[53,0],
'mask53':[53,1],
'zcc_dac53':[53,2],
'arm_dac53':[53,3],

'cal54':[54,0],
'mask54':[54,1],
'zcc_dac54':[54,2],
'arm_dac54':[54,3],

'cal55':[55,0],
'mask55':[55,1],
'zcc_dac55':[55,2],
'arm_dac55':[55,3],

'cal56':[56,0],
'mask56':[56,1],
'zcc_dac56':[56,2],
'arm_dac56':[56,3],

'cal57':[57,0],
'mask57':[57,1],
'zcc_dac57':[57,2],
'arm_dac57':[57,3],

'cal58':[58,0],
'mask58':[58,1],
'zcc_dac58':[58,2],
'arm_dac58':[58,3],

'cal59':[59,0],
'mask59':[59,1],
'zcc_dac59':[59,2],
'arm_dac59':[59,3],

'cal60':[60,0],
'mask60':[60,1],
'zcc_dac60':[60,2],
'arm_dac60':[60,3],

'cal61':[61,0],
'mask61':[61,1],
'zcc_dac61':[61,2],
'arm_dac61':[61,3],

'cal62':[62,0],
'mask62':[62,1],
'zcc_dac62':[62,2],
'arm_dac62':[62,3],

'cal63':[63,0],
'mask63':[63,1],
'zcc_dac63':[63,2],
'arm_dac63':[63,3],

'cal64':[64,0],
'mask64':[64,1],
'zcc_dac64':[64,2],
'arm_dac64':[64,3],

'cal65':[65,0],
'mask65':[65,1],
'zcc_dac65':[65,2],
'arm_dac65':[65,3],

'cal66':[66,0],
'mask66':[66,1],
'zcc_dac66':[66,2],
'arm_dac66':[66,3],

'cal67':[67,0],
'mask67':[67,1],
'zcc_dac67':[67,2],
'arm_dac67':[67,3],

'cal68':[68,0],
'mask68':[68,1],
'zcc_dac68':[68,2],
'arm_dac68':[68,3],

'cal69':[69,0],
'mask69':[69,1],
'zcc_dac69':[69,2],
'arm_dac69':[69,3],

'cal70':[70,0],
'mask70':[70,1],
'zcc_dac70':[70,2],
'arm_dac70':[70,3],

'cal71':[71,0],
'mask71':[71,1],
'zcc_dac71':[71,2],
'arm_dac71':[71,3],

'cal72':[72,0],
'mask72':[72,1],
'zcc_dac72':[72,2],
'arm_dac72':[72,3],

'cal73':[73,0],
'mask73':[73,1],
'zcc_dac73':[73,2],
'arm_dac73':[73,3],

'cal74':[74,0],
'mask74':[74,1],
'zcc_dac74':[74,2],
'arm_dac74':[74,3],

'cal75':[75,0],
'mask75':[75,1],
'zcc_dac75':[75,2],
'arm_dac75':[75,3],

'cal76':[76,0],
'mask76':[76,1],
'zcc_dac76':[76,2],
'arm_dac76':[76,3],

'cal77':[77,0],
'mask77':[77,1],
'zcc_dac77':[77,2],
'arm_dac77':[77,3],

'cal78':[78,0],
'mask78':[78,1],
'zcc_dac78':[78,2],
'arm_dac78':[78,3],

'cal79':[79,0],
'mask79':[79,1],
'zcc_dac79':[79,2],
'arm_dac79':[79,3],

'cal80':[80,0],
'mask80':[80,1],
'zcc_dac80':[80,2],
'arm_dac80':[80,3],

'cal81':[81,0],
'mask81':[81,1],
'zcc_dac81':[81,2],
'arm_dac81':[81,3],

'cal82':[82,0],
'mask82':[82,1],
'zcc_dac82':[82,2],
'arm_dac82':[82,3],

'cal83':[83,0],
'mask83':[83,1],
'zcc_dac83':[83,2],
'arm_dac83':[83,3],

'cal84':[84,0],
'mask84':[84,1],
'zcc_dac84':[84,2],
'arm_dac84':[84,3],

'cal85':[85,0],
'mask85':[85,1],
'zcc_dac85':[85,2],
'arm_dac85':[85,3],

'cal86':[86,0],
'mask86':[86,1],
'zcc_dac86':[86,2],
'arm_dac86':[86,3],

'cal87':[87,0],
'mask87':[87,1],
'zcc_dac87':[87,2],
'arm_dac87':[87,3],

'cal88':[88,0],
'mask88':[88,1],
'zcc_dac88':[88,2],
'arm_dac88':[88,3],

'cal89':[89,0],
'mask89':[89,1],
'zcc_dac89':[89,2],
'arm_dac89':[89,3],

'cal90':[90,0],
'mask90':[90,1],
'zcc_dac90':[90,2],
'arm_dac90':[90,3],

'cal91':[91,0],
'mask91':[91,1],
'zcc_dac91':[91,2],
'arm_dac91':[91,3],

'cal92':[92,0],
'mask92':[92,1],
'zcc_dac92':[92,2],
'arm_dac92':[92,3],

'cal93':[93,0],
'mask93':[93,1],
'zcc_dac93':[93,2],
'arm_dac93':[93,3],

'cal94':[94,0],
'mask94':[94,1],
'zcc_dac94':[94,2],
'arm_dac94':[94,3],

'cal95':[95,0],
'mask95':[95,1],
'zcc_dac95':[95,2],
'arm_dac95':[95,3],

'cal96':[96,0],
'mask96':[96,1],
'zcc_dac96':[96,2],
'arm_dac96':[96,3],

'cal97':[97,0],
'mask97':[97,1],
'zcc_dac97':[97,2],
'arm_dac97':[97,3],

'cal98':[98,0],
'mask98':[98,1],
'zcc_dac98':[98,2],
'arm_dac98':[98,3],

'cal99':[99,0],
'mask99':[99,1],
'zcc_dac99':[99,2],
'arm_dac99':[99,3],

'cal100':[100,0],
'mask100':[100,1],
'zcc_dac100':[100,2],
'arm_dac100':[100,3],

'cal101':[101,0],
'mask101':[101,1],
'zcc_dac101':[101,2],
'arm_dac101':[101,3],

'cal102':[102,0],
'mask102':[102,1],
'zcc_dac102':[102,2],
'arm_dac102':[102,3],

'cal103':[103,0],
'mask103':[103,1],
'zcc_dac103':[103,2],
'arm_dac103':[103,3],

'cal104':[104,0],
'mask104':[104,1],
'zcc_dac104':[104,2],
'arm_dac104':[104,3],

'cal105':[105,0],
'mask105':[105,1],
'zcc_dac105':[105,2],
'arm_dac105':[105,3],

'cal106':[106,0],
'mask106':[106,1],
'zcc_dac106':[106,2],
'arm_dac106':[106,3],

'cal107':[107,0],
'mask107':[107,1],
'zcc_dac107':[107,2],
'arm_dac107':[107,3],

'cal108':[108,0],
'mask108':[108,1],
'zcc_dac108':[108,2],
'arm_dac108':[108,3],

'cal109':[109,0],
'mask109':[109,1],
'zcc_dac109':[109,2],
'arm_dac109':[109,3],

'cal110':[110,0],
'mask110':[110,1],
'zcc_dac110':[110,2],
'arm_dac110':[110,3],

'cal111':[111,0],
'mask111':[111,1],
'zcc_dac111':[111,2],
'arm_dac111':[111,3],

'cal112':[112,0],
'mask112':[112,1],
'zcc_dac112':[112,2],
'arm_dac112':[112,3],

'cal113':[113,0],
'mask113':[113,1],
'zcc_dac113':[113,2],
'arm_dac113':[113,3],

'cal114':[114,0],
'mask114':[114,1],
'zcc_dac114':[114,2],
'arm_dac114':[114,3],

'cal115':[115,0],
'mask115':[115,1],
'zcc_dac115':[115,2],
'arm_dac115':[115,3],

'cal116':[116,0],
'mask116':[116,1],
'zcc_dac116':[116,2],
'arm_dac116':[116,3],

'cal117':[117,0],
'mask117':[117,1],
'zcc_dac117':[117,2],
'arm_dac117':[117,3],

'cal118':[118,0],
'mask118':[118,1],
'zcc_dac118':[118,2],
'arm_dac118':[118,3],

'cal119':[119,0],
'mask119':[119,1],
'zcc_dac119':[119,2],
'arm_dac119':[119,3],

'cal120':[120,0],
'mask120':[120,1],
'zcc_dac120':[120,2],
'arm_dac120':[120,3],

'cal121':[121,0],
'mask121':[121,1],
'zcc_dac121':[121,2],
'arm_dac121':[121,3],

'cal122':[122,0],
'mask122':[122,1],
'zcc_dac122':[122,2],
'arm_dac122':[122,3],

'cal123':[123,0],
'mask123':[123,1],
'zcc_dac123':[123,2],
'arm_dac123':[123,3],

'cal124':[124,0],
'mask124':[124,1],
'zcc_dac124':[124,2],
'arm_dac124':[124,3],

'cal125':[125,0],
'mask125':[125,1],
'zcc_dac125':[125,2],
'arm_dac125':[125,3],

'cal126':[126,0],
'mask126':[126,1],
'zcc_dac126':[126,2],
'arm_dac126':[126,3],

'cal127':[127,0],
'mask127':[127,1],
'zcc_dac127':[127,2],
'arm_dac127':[127,3],

'cal128':[128,0],
'mask128':[128,1],
'zcc_dac128':[128,2],
'arm_dac128':[128,3],





"PS":[129,0],
"SyncLevelEnable":[129,2],
"ST":[129,3],
"DDR":[129,4],
#
"P16":[130,0],
"PAR":[130,2],
"DT":[130,4],
"SZP":[130,5],
"SZD":[130,6],
"TT":[130,7],
"ECb":[130,9],
"BCb":[130,10],
#
"TP_FE":[131,1],
"RES_PRE":[131,2],
"CAP_PRE":[131,3],
#
"PT":[132,1],
"EN_HYST":[132,2],
"SEL_POL":[132,3],
"Force_En_ZCC":[132,4],
"Force_TH":[132,5],
"SEL_COMP_MODE":[132,6],
#
"VREF_ADC":[133,1],
"Mon_Gain":[133,2],
"Monitor_Sel":[133,4],
#
"Iref":[134,1],
#
"ZCC_DAC":[135,0],
"ARM_DAC":[135,1],
#
"HYST_DAC":[136,1],
#
"LAT":[137,0],
#
"CAL_SEL_POL":[138,1],
"CAL_PHI":[138,2],
"CAL_EXT":[138,3],
"CAL_DAC":[138,4],
"CAL_MODE":[138,5],
#
"CAL_FS":[139,1],
"CAL_DUR":[139,2],
#
"CFD_DAC_2":[140,1],
"CFD_DAC_1":[140,2],
#
"PRE_I_BSF":[141,1],
"PRE_I_BIT":[141,2],
#
"PRE_I_BLCC":[142,1],
"PRE_VREF":[142,2],
#
"SH_I_BFCAS":[143,0],
"SH_I_BDIFF":[143,1],
#
"SH_I_BFAMP":[144,1],
"SD_I_BDIFF":[144,2],
#
"SD_I_BSF":[145,1],
"SD_I_BFCAS":[145,2],
#
"SLVS_IBIAS":[146,1],
"SLVS_VREF":[146,2],
#
"RUN":[65535,1],
"ID":[65536,0],
"VER":[65537,0],
"RW_REG":[65538,0],
"CHIP_ID":[65539,0],
"ADC_0":[131072,1],
"ADC_1":[131073,1]
}

FCC_LUT = {
"CC-A":"0000",
"CC-B":"1111",
"EC0":"0001",
"BC0":"0010",
"CalPulse":"0011",
"ReSync":"0100",
"SCOnly":"0101",
"RunMode":"0110",
"LV1A":"0111",
"SC0":"1000",
"SC1":"1001",
"ReSC":"1010",
"LV1A+EC0":"1011",
"LV1A+BC0":"1100",
"LV1A+EC0+BC0":"1101",
"EC0+BC0":"1110"
}

FCC_LUIT_L = {
"AAAA":"00000000",
"PPPP":"11111111",
"0000":"00010111",
"1111":"11101000",
"0001":"00001111",
"0010":"00110011",
"0011":"00111100",
"0100":"01010101",
"0101":"01011010",
"0110":"01100110",
"0111":"01101001",
"1000":"10010110",
"1001":"10011001",
"1010":"10100101",
"1011":"10101010",
"1100":"11000011",
"1101":"11001100",
"1110":"11110000"
}


