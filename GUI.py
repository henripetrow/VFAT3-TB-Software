############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################

import Tkinter, tkFileDialog, Tkconstants
from Tkinter import *
import ttk
import tkMessageBox
import time
import sys
import os
import subprocess  # For opening scans for edit in the system default editor.

from VFAT3_registers import *
from generator import *
from test_system_functions import *
from FW_interface import *
from DatabaseInterface import *
from routines.routines import *
from routines.calibration_routines import *
from routines.datapacket_routines import *
from tti_serial_interface import *
from luts import *
from reedmuller import *
from os1327dInterface import os1327dInterface


class VFAT3_GUI:
    def __init__(self, master):
        self.psu_mode = 1
        self.psu_found = 0
        conn_mode = 1
        self.db_mode = 1
        self.burn_mode = 1
        self.beep_mode = 0
        self.tti_if = 0
        self.iref_mode = 0
        self.temp_gun_mode = 1
        self.chipid_encoding_mode = 1
        # Pilot run flag. Defines if results of single tests are displayed on production test.
        self.pilot_run_flag = 0
        self.chip_id = 'n'
        # Communication mode selection.
        for arg in sys.argv:
            # print "sys.argv value: %s" % arg
            if arg == '-s':
                conn_mode = 0
            if arg == '-no_db':
                print "Entering no database-mode."
                self.db_mode = 0
            if arg == '-no_psu':
                print "Entering external Power Supply-mode."
                self.psu_mode = 0
            if arg == '-no_id_burn':
                print "Entering to mode with no chip id burn."
                self.burn_mode = 0
            if arg == '-pilot_run':
                print "Entering the Production Pilot Run -mode."
                self.pilot_run_flag = 1
                self.db_mode = 0
            if arg == '-beep':
                print "Usign system beep on Production test to indicate test end."
                self.beep_mode = 1
            if arg == '-iref':
                print "Entering Iref measurement-mode."
                self.iref_mode = 1
            if arg == '-no_temp_gun':
                print "Entering Infrared temperature measurement-mode."
                self.temp_gun_mode = 0
            if arg == '-no_chipid_encoding':
                print "Entering Chip ID Reed-Muller encoding-mode."
                self.chipid_encoding_mode = 0

        if self.psu_mode == 1:
            self.tti_if = TtiSerialInterface()
            if self.tti_if.psu_found:
                print "Found Power Supply"
                self.tti_if.set_outputs_off()
                self.tti_if.set_ch1_current_limit(0.4)
                self.tti_if.set_ch2_current_limit(0.4)
                self.tti_if.set_ch1_voltage(3)
                self.tti_if.set_ch2_voltage(3)
                self.psu_found = 1
            else:
                print "\n******* No Power Supply found *******"
                print "If power supply is connected, try to restart it.\n"
                self.psu_found = 0
        if conn_mode == 0:
            self.interfaceFW = FW_interface(1)  # 1 - Simulation mode
            self.mode = 1
        if conn_mode == 1:
            self.interfaceFW = FW_interface(0)  # 0 - IPbus mode
            self.mode = 0
        if self.temp_gun_mode == 1:
            self.temp_gun_interface = os1327dInterface()
        # Local variables.
        self.hybrid_model = "HV3b"
        self.default_bg_color = master.cget("bg")
        self.database = 0
        self.barcode_id = ""
        self.channel_register = 0
        self.value = ""
        self.write_BCd_as_fillers = 1
        self.adc0M = 0.0
        self.adc0B = 0.0
        self.adc1M = 0.0
        self.adc1B = 0.0
        self.adcM = 0.0
        self.adcB = 0.0
        self.cal_dac_fcM = 0.0
        self.cal_dac_fcB = 0.0
        self.cal_dac_fc_values = [0]*256
        self.Iref_cal = 1
        self.CalPulseLV1A_latency = 4
        self.xray_routine_flag = 0
        self.scurve_channel = 0
        self.transaction_ID = 0
        self.interactive_output_file = "./data/FPGA_instruction_list.dat"
        self.data_folder = "./results"
        self.COM_port = "/dev/ttyUSB0"
        self.register_mode = 'r'
        self.register_names = []
        self.temperature_k1 = 'n'
        self.temperature_k2 = 'n'
        self.temp_coeff = 3.79
        self.lot_nr = 0
        self.arrival_date = "00000000"
        self.read_lot_information()

        # Initiations
        self.SC_encoder = SC_encode()
        self.register = register
        s = ttk.Style()
        s.configure('My.TFrame', background='white')
        self.master = master
        # self.master.wm_iconbitmap('/home/a0312687/VFAT3-TB-Software/data/LUT_logo.ico')
        self.master.title("VFAT3 test platform")
        bwidth = 15
        self.master.minsize(width=300, height=450)
        self.master.configure(background='white')


        # ######MENUBAR#################################

        # create a top level menu
        menubar = Menu(self.master)

        # create a pull down menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Quit", command=master.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # create more pull down menus
        modemenu = Menu(menubar, tearoff=0)
        modemenu.add_command(label="Interactive", command=lambda: self.change_mode("interactive"))
        modemenu.add_command(label="Routines", command=lambda: self.change_mode("scans_tests"))
        modemenu.add_separator()
        modemenu.add_command(label="Production", command=lambda: self.change_mode("production"))
        # modemenu.entryconfig(1, state=DISABLED)
        # modemenu.entryconfig(3, state=DISABLED)
        menubar.add_cascade(label="Mode", menu=modemenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=helpmenu)

        # display the menu
        self.master.config(menu=menubar)

        ###############################################################################################################
        # ##################################################INTERACTIVE MODE###########################################
        ###############################################################################################################

        # #########NOTEBOOK##############################
        self.nb = ttk.Notebook(master, width=300)

        self.FCC_frame = ttk.Frame(self.nb)
        self.FCC_frame.grid()

        self.register_frame = ttk.Frame(self.nb)
        self.register_frame.grid()

        self.misc_frame = ttk.Frame(self.nb)
        self.misc_frame.grid()

        self.new_frame = ttk.Frame(self.nb)
        self.new_frame.grid()
        #self.new_frame.grid_propagate(False)

        # #########FCC TAB################################
        self.label = Label(self.FCC_frame, text="Send Fast Control Commands (FCC)")
        self.label.grid(columnspan=2)

        self.EC0_button = Button(self.FCC_frame, text="EC0", command=lambda: self.send_fcc("EC0"), width=bwidth)
        self.EC0_button.grid()

        self.BC0_button = Button(self.FCC_frame, text="BC0", command=lambda: self.send_fcc("BC0"), width=bwidth)
        self.BC0_button.grid()

        self.calpulse_button = Button(self.FCC_frame, text="CalPulse", command=lambda: self.send_fcc("CalPulse"), width=bwidth)
        self.calpulse_button.grid()

        self.resync_button = Button(self.FCC_frame, text="ReSync", command=lambda: self.send_fcc("ReSync"), width=bwidth)
        self.resync_button.grid()

        self.sconly_button = Button(self.FCC_frame, text="SCOnly", command=lambda: self.send_fcc("SCOnly"), width=bwidth)
        self.sconly_button.grid()

        self.runmode_button = Button(self.FCC_frame, text="RunMode", command=lambda: self.send_fcc("RunMode"), width=bwidth)
        self.runmode_button.grid()

        self.lv1a_button = Button(self.FCC_frame, text="LV1A", command=lambda: self.send_fcc("LV1A"), width=bwidth)
        self.lv1a_button.grid()

        self.sc0_button = Button(self.FCC_frame, text="SC0", command=lambda: self.send_fcc("SC0"), width=bwidth)
        self.sc0_button.grid()

        self.sc1_button = Button(self.FCC_frame, text="SC1", command=lambda: self.send_fcc("SC1"), width=bwidth)
        self.sc1_button.grid()

        self.resc_button = Button(self.FCC_frame, text="ReSC", command=lambda: self.send_fcc("ReSC"), width=bwidth)
        self.resc_button.grid()

        self.lv1aec0_button = Button(self.FCC_frame, text="LV1A+EC0", command=lambda: self.send_fcc("LV1A+EC0"), width=bwidth)
        self.lv1aec0_button.grid()

        self.lv1abc0_button = Button(self.FCC_frame, text="LV1A+BC0", command=lambda: self.send_fcc("LV1A+BC0"), width=bwidth)
        self.lv1abc0_button.grid()

        self.lv1aec0bc0_button = Button(self.FCC_frame, text="LV1A+EC0+BC0", command=lambda: self.send_fcc("LV1A+EC0+BC0"), width=bwidth)
        self.lv1aec0bc0_button.grid()

        self.EC0BC0_button = Button(self.FCC_frame, text="EC0+BC0", command=lambda: self.send_fcc("EC0+BC0"), width=bwidth)
        self.EC0BC0_button.grid()

        # #################REGISTERS TAB###################################

        OPTIONS = [
                "Channels",
                "Front End Settings",
                "Control Logic",
                "Data Packet",
                "Front End",
                "CFD",
                "Monitoring",
                "Global reference current",
                "Global Threshold",
                "Global Hysteresis",
                "Latency",
                "Calibration 0",
                "Calibration 1",
                "Biasing 0",
                "Biasing 1",
                "Biasing 2",
                "Biasing 3",
                "Biasing 4",
                "Biasing 5",
                "Biasing 6",
                "SLEEP/RUN",
                "HW_ID_ID",
                "HW_ID_VER",
                "HW_RW_REG",
                "HW_CHIP_ID"
                ]

        self.variable = StringVar(master)
        self.variable.set(OPTIONS[0])  # default value

        # REGISTER DROP DOWN MENU
        w = OptionMenu(self.register_frame, self.variable, *OPTIONS, command=self.update_registers)
        w.config(width=30)
        w.grid(row=0)

        # FRAME FOR THE REGISTER DATA
        self.register_data_frame = ttk.Frame(self.register_frame, height=500)
        self.register_data_frame.grid()  

        self.description_label = Label(self.register_data_frame, text="Choose a Register from the drop down menu.")
        self.description_label.grid()
        self.separator = ttk.Separator(self.register_data_frame, orient='horizontal')
        self.separator.grid(column=0, row=1, columnspan=2, sticky='ew')
        self.label = []
        self.entry = []
        self.range = []

        # REGISTER APPLY AND DEFAULT BUTTONS
        self.register_button_frame = ttk.Frame(self.register_frame)
        self.register_button_frame.grid()  
        self.apply_button = Button(self.register_button_frame, text="Apply", command=self.apply_register_values)
        self.apply_button.grid(column=0, row=0)
        self.default_button = Button(self.register_button_frame, text="Defaults")
        self.default_button.grid(column=1, row=0)
        self.default_button.config(state="disabled")
        self.refresh_button = Button(self.register_button_frame, text="Refresh", command=lambda: self.update_registers(self.value))
        self.refresh_button.grid(column=3, row=0)

        self.channel_label = Label(self.register_data_frame, text="Channel:")
        self.channel_label.grid(column=0, row=0, sticky='e')

        self.channel_entry = Entry(self.register_data_frame, width=5)
        self.channel_entry.grid(column=1, row=0, sticky='e')
        self.channel_entry.insert(0, self.channel_register)

        self.channel_button = Button(self.register_data_frame, text="Change", command = self.change_channel)
        self.channel_button.grid(column=2, row=0, sticky='e')

        self.channel_label.grid_forget()
        self.channel_entry.grid_forget()
        self.channel_button.grid_forget()


        # ###############MISC TAB #######################################

        self.sync_button = Button(self.misc_frame, text="Sync", command=lambda: self.send_sync(), width=bwidth)
        self.sync_button.grid(column=1, row=1, sticky='e')

        self.sync_check_button = Button(self.misc_frame, text="Sync check", command=lambda: self.send_sync_verif(), width=bwidth)
        self.sync_check_button.grid(column=1, row=2, sticky='e')

        self.idle_button = Button(self.misc_frame, text="SC Idle character", command=lambda: self.send_idle(), width=bwidth, state=DISABLED)
        self.idle_button.grid(column=1, row=3, sticky='e')

        self.close_button = Button(self.misc_frame, text="Read int. ADCs", command=lambda: self.read_adcs(), width=bwidth)
        self.close_button.grid(column=1, row=4, sticky='e')

        self.cal_button = Button(self.misc_frame, text="Read ext. ADC", command=lambda: self.ext_adc(), width=bwidth)
        self.cal_button.grid(column=1, row=5, sticky='e')

        self.CalPulse_LV1A_button = Button(self.misc_frame, text="CalPulse+LV1A", command=self.send_cal_trigger, width=bwidth, state=DISABLED)
        self.CalPulse_LV1A_button.grid(column=1, row=6, sticky='e')

        self.CalPulse_LV1A_label0 = Label(self.misc_frame, text="Latency")
        self.CalPulse_LV1A_label0.grid(column=2, row=6, sticky='e')

        self.CalPulse_LV1A_entry = Entry(self.misc_frame, width=5)
        self.CalPulse_LV1A_entry.grid(column=3, row=6, sticky='e')
        self.CalPulse_LV1A_entry.insert(0, self.CalPulseLV1A_latency)

        self.CalPulse_LV1A_label0 = Label(self.misc_frame, text="BC")
        self.CalPulse_LV1A_label0.grid(column=4, row=6, sticky='e')

        self.cont_trig_button = Button(self.misc_frame, text="Sync FPGA", command=lambda: self.send_reset(), width=bwidth)
        self.cont_trig_button.grid(column=1, row=15, sticky='e')

        self.cont_trig_button = Button(self.misc_frame, text="Charge distribution", command=lambda: charge_distribution_on_neighbouring_ch(self), width=bwidth, state=DISABLED)
        self.cont_trig_button.grid(column=1, row=16, sticky='e')

        self.temp_button = Button(self.misc_frame, text="Read temp.", command=lambda: self.read_temperature(), width=bwidth)
        self.temp_button.grid(column=1, row=17, sticky='e')
        # self.temp_label = Label(self.misc_frame, text="n/a", width=11)
        # self.temp_label.grid(column=2, row=17, sticky='e')

        self.temp_button = Button(self.misc_frame, text="Test S-bits", command=lambda: self.test_trigger_outputs(), width=bwidth)
        self.temp_button.grid(column=1, row=18, sticky='e')

        # ###############NEW TAB #######################################

        ########### INFO BORDER ###########
        self.info_border_frame = LabelFrame(self.new_frame, text='Chip Information', width=250, height=100)
        self.info_border_frame.grid(sticky='w')
        self.info_border_frame.grid_propagate(False)

        self.hw_id_id_label = Label(self.info_border_frame, text="HW_ID_ID:")
        self.hw_id_id_label.grid(column=1, row=1, sticky='e')
        self.hw_id_id_label0 = Label(self.info_border_frame, text="n/a", width=10)
        self.hw_id_id_label0.grid(column=2, row=1, sticky='w')
        self.hw_id_ver_label = Label(self.info_border_frame, text="HW_ID_VER:")
        self.hw_id_ver_label.grid(column=1, row=2, sticky='e')
        self.hw_id_ver_label0 = Label(self.info_border_frame, text="n/a", width=10)
        self.hw_id_ver_label0.grid(column=2, row=2, sticky='w')
        self.chip_id_label = Label(self.info_border_frame, text="CHIP ID:")
        self.chip_id_label.grid(column=1, row=3, sticky='e')
        self.chip_id_label0 = Label(self.info_border_frame, text="n/a", width=10)
        self.chip_id_label0.grid(column=2, row=3, sticky='w')
        self.fpga_sync_button = Button(self.info_border_frame, text="Connect (Hard Reset)", command=lambda: self.sync_fpga(), width=bwidth)
        self.fpga_sync_button.grid(column=1, row=4, sticky='e')


        ########### RUN MODE ###########
        self.run_frame = LabelFrame(self.new_frame, text='RUN mode', width=250, height=50)
        self.run_frame.grid(sticky='w')
        self.run_frame.grid_propagate(False)

        self.run_label = Label(self.run_frame, text="Status:")
        self.run_label.grid(column=0, row=0, sticky='e')
        self.run_status_label = Label(self.run_frame, width=6, bg="red")
        self.run_status_label.grid(column=1, row=0, sticky='w')

        self.run_button = Button(self.run_frame, text="Change", command=lambda: self.toggle_run_bit())
        self.run_button.grid(row=0, column=6, sticky='e')


        ########### CHANNELS ################

        self.ch_border_frame = LabelFrame(self.new_frame, text='Channels', width=250, height=100)
        self.ch_border_frame.grid(sticky='w')
        self.ch_border_frame.grid_propagate(False)

        self.channel_label = Label(self.ch_border_frame, text="Channel:")
        self.channel_label.grid(column=0, row=0, sticky='e')

        self.channel_entry = Entry(self.ch_border_frame, width=3)
        self.channel_entry.grid(column=1, row=0, sticky='e')
        self.channel_entry.insert(0, self.channel_register)

        self.channel_button = Button(self.ch_border_frame, text="Change ch.", command=self.new_change_channel)
        self.channel_button.grid(column=2, row=0, sticky='e')

        self.apply_button = Button(self.ch_border_frame, text="Apply", command=self.new_change_channel)
        self.apply_button.grid(column=3, row=0, sticky='e')

        cal_button = Checkbutton(self.ch_border_frame, text="cal")
        cal_button.grid(column=0, row=1, sticky='w')

        mask_button = Checkbutton(self.ch_border_frame, text="mask")
        mask_button.grid(column=0, row=2, sticky='w')

        self.zcc_label = Label(self.ch_border_frame, text="zcc_dac:")
        self.zcc_label.grid(column=2, row=1, sticky='e')

        self.zcc_entry = Entry(self.ch_border_frame, width=3)
        self.zcc_entry.grid(column=3, row=1, sticky='w')
        #self.data_dir_entry.insert(0, self.data_folder)

        self.arm_label = Label(self.ch_border_frame, text="arm_dac:")
        self.arm_label.grid(column=2, row=2, sticky='e')

        self.arm_entry = Entry(self.ch_border_frame, width=3)
        self.arm_entry.grid(column=3, row=2, sticky='w')
        #self.data_dir_entry.insert(0, self.data_folder)

        ########### SYNC BORDER ###########
        self.sync_border_frame = LabelFrame(self.new_frame, text='Synchronization', width=250, height= 100)
        self.sync_border_frame.grid(sticky='w')
        self.sync_border_frame.grid_propagate(False)

        self.sync_button = Button(self.sync_border_frame, text="Sync", command=lambda: self.send_sync(), width=bwidth)
        self.sync_button.grid(column=1, row=1, sticky='e')
        self.sync_label = Label(self.sync_border_frame, text="n/a", width=11)
        self.sync_label.grid(column=2, row=1, sticky='e')

        self.sync_check_button = Button(self.sync_border_frame, text="Sync check", command=lambda: self.send_sync_verif(), width=bwidth)
        self.sync_check_button.grid(column=1, row=2, sticky='e')
        self.sync_check_label = Label(self.sync_border_frame, text="n/a", width=11)
        self.sync_check_label.grid(column=2, row=2, sticky='e')

        ########### ADC BORDER ###########
        self.adc_border_frame = LabelFrame(self.new_frame, text='ADCs', width=250, height=100)
        self.adc_border_frame.grid(sticky='w')
        self.adc_border_frame.grid_propagate(False)

        self.sync_button = Button(self.adc_border_frame, text="Read ADCs", command=lambda: self.read_adcs(), width=bwidth)
        self.sync_button.grid(column=1, row=0, sticky='w', columnspan=6)

        self.ext_adc_label = Label(self.adc_border_frame, text="ext ADC:")
        self.ext_adc_label.grid(column=1, row=1, sticky='e')
        self.ext_adc_label0 = Label(self.adc_border_frame, text="n/a", width=10)
        self.ext_adc_label0.grid(column=2, row=1, sticky='w')

        self.adc0_label = Label(self.adc_border_frame, text="ADC0:")
        self.adc0_label.grid(column=1, row=2, sticky='e')
        self.adc0_label0 = Label(self.adc_border_frame, text="n/a", width=10)
        self.adc0_label0.grid(column=2, row=2, sticky='w')

        self.adc1_label = Label(self.adc_border_frame, text="ADC1:")
        self.adc1_label.grid(column=1, row=3, sticky='e')
        self.adc1_label0 = Label(self.adc_border_frame, text="n/a", width=10)
        self.adc1_label0.grid(column=2, row=3, sticky='w')

        ########### FRONT END BORDER ###########
        self.fe_border_frame = LabelFrame(self.new_frame, text='Front End Biasing', width=250, height=75)
        self.fe_border_frame.grid(sticky='w')
        self.fe_border_frame.grid_propagate(False)

        self.vfat3a_button = Button(self.fe_border_frame, text="VFAT3a nominal values", command=lambda: self.set_fe_nominal_values(chip="VFAT3a"), width=bwidth)
        self.vfat3a_button.grid(column=1, row=1, sticky='e')

        self.vfat3b_button = Button(self.fe_border_frame, text="VFAT3b nominal values", command=lambda: self.set_fe_nominal_values(chip="VFAT3b"), width=bwidth)
        self.vfat3b_button.grid(column=1, row=2, sticky='e')

        ########### CALIBRATION BORDER ###########
        self.calibration_border_frame = LabelFrame(self.new_frame, text='Calibration', width=250, height=140)
        self.calibration_border_frame.grid(sticky='w')
        self.calibration_border_frame.grid_propagate(False)

        self.run_calib_button = Button(self.calibration_border_frame, text="Run", command=lambda: self.run_full_calibration())
        self.run_calib_button.grid(column=1, row=0, sticky='e')
        self.load_calib_button = Button(self.calibration_border_frame, text="Load", command=lambda: self.send_sync())
        self.load_calib_button.grid(column=2, row=0, sticky='e')
        self.save_calib_button = Button(self.calibration_border_frame, text="Save", command=lambda: self.send_sync())
        self.save_calib_button.grid(column=3, row=0, sticky='e')

        self.irefc_label = Label(self.calibration_border_frame, text="Iref:")
        self.irefc_label.grid(column=1, row=1, sticky='e')
        self.irefc_label0 = Label(self.calibration_border_frame, text="n/a", width=4)
        self.irefc_label0.grid(column=2, row=1, sticky='w')
        self.adc0c_label = Label(self.calibration_border_frame, text="ADC0:")
        self.adc0c_label.grid(column=1, row=2, sticky='e')
        self.adc0c_label0 = Label(self.calibration_border_frame, text="n/a", width=12)
        self.adc0c_label0.grid(column=2, row=2, sticky='w')
        self.adc1c_label = Label(self.calibration_border_frame, text="ADC1:")
        self.adc1c_label.grid(column=1, row=3, sticky='e')
        self.adc1c_label0 = Label(self.calibration_border_frame, text="n/a", width=12)
        self.adc1c_label0.grid(column=2, row=3, sticky='w')
        self.cal_dacc_label = Label(self.calibration_border_frame, text="CAL_DAC:")
        self.cal_dacc_label.grid(column=1, row=4, sticky='e')
        self.cal_dacc_label0 = Label(self.calibration_border_frame, text="n/a", width=12)
        self.cal_dacc_label0.grid(column=2, row=4, sticky='w')
        self.temp_coeff_label = Label(self.calibration_border_frame, text="Temp coeff.:")
        self.temp_coeff_label.grid(column=1, row=5, sticky='e')
        self.temp_coeff_label0 = Label(self.calibration_border_frame, text="n/a", width=16)
        self.temp_coeff_label0.grid(column=2, row=5, sticky='w')

        # ADD TABS
        self.nb.add(self.FCC_frame, text="FCC")
        self.nb.add(self.register_frame, text="Registers")
        self.nb.add(self.misc_frame, text="misc.")
        self.nb.add(self.new_frame, text="new")

        self.nb.grid_forget()

        ###############################################################################################################
        # ##################################################SCAN MODE##################################################
        ###############################################################################################################

        self.scan_mode_nb = ttk.Notebook(master, width=300, height=400)

        self.calibration_frame = ttk.Frame(self.scan_mode_nb)
        self.calibration_frame.grid()
        self.scurve_frame = ttk.Frame(self.scan_mode_nb)
        self.scurve_frame.grid()
        self.routines_frame = ttk.Frame(self.scan_mode_nb)
        self.routines_frame.grid()
        self.scan_frame = ttk.Frame(self.scan_mode_nb)
        self.scan_frame.grid(column=0, row=0)
        self.scan_frame.grid_propagate(False)
        self.scan_label = ttk.Label(self.scan_frame, text="Available scans and tests.")
        self.scan_label.grid(column=0, row=0)

        self.scan_options = [
                "ZCC_DAC scan",
                "ARM_DAC scan",
                "HYST_DAC scan",
                "CFD_DAC_1 scan",
                "CFD_DAC_2 scan",
                "PRE_I_BSF scan",
                "PRE_I_BIT scan",
                "PRE_I_BLCC scan",
                "PRE_VREF scan",
                "SH_I_BFCAS scan",
                "SH_I_BDIFF scan",
                "SD_I_BDIFF scan",
                "SD_I_BSF scan",
                "SD_I_BFCAS scan",
                "CAL_DAC scan",
                ]

        self.scan_options_value = [36, 35, 12, 10, 11, 4, 2, 3, 34, 5, 6, 7, 9, 8, 33]
        self.dac_sizes = [8, 8, 6, 6, 6, 6, 8, 6, 8, 8, 8, 8, 6, 8, 8]


        self.chosen_scan = self.scan_options[0]
        self.scan_variable = StringVar(master)
        self.scan_variable.set(self.scan_options[0])  # default value

        # SCAN DROP DOWN MENU
        scan_drop_menu = OptionMenu(self.scan_frame, self.scan_variable, *self.scan_options, command=self.choose_scan)
        scan_drop_menu.config(width=30)
        scan_drop_menu.grid(row=1)
        
        self.verbose_var = IntVar()

        verbose_check_button = Checkbutton(self.scan_frame, text="Verbose", variable=self.verbose_var)
        verbose_check_button.grid()

        # SCAN RUN AND MODIFY BUTTONS
        self.scan_button_frame = ttk.Frame(self.scan_frame, width=302, height=200)
        self.scan_button_frame.grid()  
        self.scan_button_frame.grid_propagate(False)

        self.modify_button = Button(self.scan_button_frame, text="Modify", command=self.modify_scan, state=DISABLED)
        self.modify_button.grid(column=0, row=0)
        self.generate_button = Button(self.scan_button_frame, text="Generate", command=self.generate_routine, state=DISABLED)
        self.generate_button.grid(column=1, row=0)
        self.run_button = Button(self.scan_button_frame, text="RUN", command=self.run_routine)
        self.run_button.grid(column=2, row=0)

        # ###############CALIBRATION TAB #######################################

        self.cal_button = Button(self.calibration_frame, text="Adjust Iref", command=lambda: self.adjust_iref(), width=bwidth)
        self.cal_button.grid(column=1, row=0, sticky='e')

        self.adc_calibration_button = Button(self.calibration_frame, text="ADC calibration", command=lambda: self.adc_calibration(), width=bwidth)
        self.adc_calibration_button.grid(column=1, row=1, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="CAL_DAC to fC", command=lambda: self.scan_cal_dac_fc(), width=bwidth)
        self.cal_button.grid(column=1, row=2, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Save Calibration", command=lambda: self.save_calibration_values_to_file(), width=bwidth)
        self.cal_button.grid(column=1, row=3, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Load Calibration", command=lambda: self.load_calibration_values_from_file(), width=bwidth)
        self.cal_button.grid(column=2, row=3, sticky='e')

        self.FE_button = Button(self.calibration_frame, text="Set FE nominal values", command=lambda: self.set_fe_nominal_values(), width=bwidth, state=DISABLED)
        self.FE_button.grid(column=1, row=4, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Channel Calibration", command=lambda: adjust_local_thresholds(self), width=bwidth)
        self.cal_button.grid(column=1, row=5, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Apply ch. Calibration", command=lambda: self.apply_ch_local_adjustments(), width=bwidth)
        self.cal_button.grid(column=2, row=5, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Gain per channel", command=lambda: gain_histogram(self), width=bwidth, state=DISABLED)
        self.cal_button.grid(column=1, row=6, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Save registers", command=lambda: self.save_register_values_to_file(), width=bwidth)
        self.cal_button.grid(column=1, row=11, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Load registers", command=lambda: self.load_register_values_from_file(), width=bwidth)
        self.cal_button.grid(column=2, row=11, sticky='e')



        # ###############Routines-TAB #######################################

        self.hist_button = Button(self.routines_frame, text="Channel histogram", command=lambda: channel_histogram(self), width=bwidth)
        self.hist_button.grid(column=1, row=6, sticky='e')

        self.Trig1_set_button = Button(self.routines_frame, text="Set s-bit pattern", command=lambda: set_up_trigger_pattern(self, 0), width=bwidth, state=DISABLED)
        self.Trig1_set_button.grid(column=1, row=7, sticky='e')

        self.Trig_clear_button = Button(self.routines_frame, text="Clear s-bit pattern", command=lambda: set_up_trigger_pattern(self, 2), width=bwidth, state=DISABLED)
        self.Trig_clear_button.grid(column=1, row=8, sticky='e')

        self.cont_trig_button = Button(self.routines_frame, text="Continuous CalPulses", command=lambda: continuous_trigger(self), width=bwidth, state=DISABLED)
        self.cont_trig_button.grid(column=1, row=9, sticky='e')

        self.cal_button = Button(self.routines_frame, text="Production test",
                                 command=lambda: self.run_production_tests(), width=bwidth)
        self.cal_button.grid(column=1, row=10, sticky='e')

        self.cont_trig_button = Button(self.routines_frame, text="Test data packets", command=lambda: self.test_data_packets(), width=bwidth)
        self.cont_trig_button.grid(column=1, row=11, sticky='e')

        self.nr_trigger_loops = 5

        self.cont_trig_entry = Entry(self.routines_frame, width=5)
        self.cont_trig_entry.grid(column=3, row=11, sticky='e')
        self.cont_trig_entry.insert(0, self.nr_trigger_loops)

        self.cont_trig_label0 = Label(self.routines_frame, text="loops")
        self.cont_trig_label0.grid(column=4, row=11, sticky='e')

        self.cont_trig_button = Button(self.routines_frame, text="Scan all DACs", command=lambda: self.run_all_dac_scans(), width=bwidth)
        self.cont_trig_button.grid(column=1, row=12, sticky='e')

        self.cal_button = Button(self.routines_frame, text="W/R all registers", command=lambda: self.test_registers(), width=bwidth)
        self.cal_button.grid(column=1, row=13, sticky='e')

        self.cal_button = Button(self.routines_frame, text="X-ray routine cont", command=lambda: self.run_xray_tests(), width=bwidth, state=DISABLED)
        self.cal_button.grid(column=1, row=14, sticky='e')

        self.data_dir_label0 = Label(self.routines_frame, text="Data directory:")
        self.data_dir_label0.grid(column=1, row=15, sticky='w')

        self.data_dir_entry = Entry(self.routines_frame, width=18)
        self.data_dir_entry.grid(column=1, row=15, sticky='w')
        self.data_dir_entry.insert(0, self.data_folder)

        self.cont_trig_button = Button(self.routines_frame, text="Browse", command=lambda: self.ask_directory(), width=5)
        self.cont_trig_button.grid(column=3, row=15, sticky='e', columnspan=2)

        self.cal_button = Button(self.routines_frame, text="Run BIST", command=lambda: self.test_bist(), width=bwidth)
        self.cal_button.grid(column=1, row=16, sticky='e')

        self.cal_button = Button(self.routines_frame, text="Write Chip ID", command=lambda: self.burn_chip_id(), width=bwidth)
        self.cal_button.grid(column=1, row=17, sticky='e')

        self.cal_button = Button(self.routines_frame, text="Read HW_ID_VER", command=lambda: self.read_hw_id(), width=bwidth)
        self.cal_button.grid(column=1, row=18, sticky='e')

        self.cal_button = Button(self.routines_frame, text="Adjust ADC0 ref", command=lambda: self.adjust_adc0_ref(), width=bwidth)
        self.cal_button.grid(column=1, row=18, sticky='e')

        self.cal_button = Button(self.routines_frame, text="Meas. power", command=lambda: self.measure_power(), width=bwidth)
        self.cal_button.grid(column=1, row=19, sticky='e')

        # ############### S-curve tab #########################################

        self.start_channel = 0
        self.stop_channel = 127
        self.channel_step = 1
        self.delay = 19
        self.interval = 2000
        self.pulsestretch = 7
        self.latency = 50
        self.calphi = 0
        self.arm_dac = 100
        self.start_cal_dac = 210
        self.stop_cal_dac = 245

        self.start_ch_label = Label(self.scurve_frame, text="start ch.:")
        self.start_ch_label.grid(column=1, row=1, sticky='w')

        self.start_ch_entry = Entry(self.scurve_frame, width=5)
        self.start_ch_entry.grid(column=2, row=1, sticky='e')
        self.start_ch_entry.insert(0, self.start_channel)

        self.start_ch_label0 = Label(self.scurve_frame, text="0-127")
        self.start_ch_label0.grid(column=3, row=1, sticky='w')

        self.stop_ch_label = Label(self.scurve_frame, text="stop ch.:")
        self.stop_ch_label.grid(column=1, row=2, sticky='w')

        self.stop_ch_entry = Entry(self.scurve_frame, width=5)
        self.stop_ch_entry.grid(column=2, row=2, sticky='e')
        self.stop_ch_entry.insert(0, self.stop_channel)

        self.stop_ch_label0 = Label(self.scurve_frame, text="0-127")
        self.stop_ch_label0.grid(column=3, row=2, sticky='w')

        self.ch_step_label = Label(self.scurve_frame, text="ch. step:")
        self.ch_step_label.grid(column=1, row=3, sticky='w')

        self.ch_step_entry = Entry(self.scurve_frame, width=5)
        self.ch_step_entry.grid(column=2, row=3, sticky='e')
        self.ch_step_entry.insert(0, self.channel_step)

        self.ch_step_label0 = Label(self.scurve_frame, text="0-127")
        self.ch_step_label0.grid(column=3, row=3, sticky='w')

        self.delay_label = Label(self.scurve_frame, text="Pulse Delay:")
        self.delay_label.grid(column=1, row=4, sticky='w')

        self.delay_entry = Entry(self.scurve_frame, width=5)
        self.delay_entry.grid(column=2, row=4, sticky='e')
        self.delay_entry.insert(0, self.delay)
        #self.delay_entry.config(state='disabled')

        self.delay_label0 = Label(self.scurve_frame, text="0-4000")
        self.delay_label0.grid(column=3, row=4, sticky='w')

        self.interval_label = Label(self.scurve_frame, text="LV1A interval:")
        self.interval_label.grid(column=1, row=5, sticky='w')

        self.interval_entry = Entry(self.scurve_frame, width=5)
        self.interval_entry.grid(column=2, row=5, sticky='e')
        self.interval_entry.insert(0, self.interval)
        self.interval_entry.config(state='disabled')

        self.interval_label0 = Label(self.scurve_frame, text="0-4000")
        self.interval_label0.grid(column=3, row=5, sticky='w')

        self.pulsestretch_label = Label(self.scurve_frame, text="Pulse stretch:")
        self.pulsestretch_label.grid(column=1, row=6, sticky='w')

        self.pulsestretch_entry = Entry(self.scurve_frame, width=5)
        self.pulsestretch_entry.grid(column=2, row=6, sticky='e')
        self.pulsestretch_entry.insert(0, self.pulsestretch)
        self.pulsestretch_entry.config(state='disabled')

        self.pulsestretch_label0 = Label(self.scurve_frame, text="0-7")
        self.pulsestretch_label0.grid(column=3, row=6, sticky='w')

        self.latency_label = Label(self.scurve_frame, text="Latency:")
        self.latency_label.grid(column=1, row=7, sticky='w')

        self.latency_entry = Entry(self.scurve_frame, width=5)
        self.latency_entry.grid(column=2, row=7, sticky='e')
        self.latency_entry.insert(0, self.latency)
        self.latency_entry.config(state='disabled')

        self.latency_label0 = Label(self.scurve_frame, text="0-1023")
        self.latency_label0.grid(column=3, row=7, sticky='w')

        self.calphi_label = Label(self.scurve_frame, text="Cal Phi:")
        self.calphi_label.grid(column=1, row=8, sticky='w')

        self.calphi_entry = Entry(self.scurve_frame, width=5)
        self.calphi_entry.grid(column=2, row=8, sticky='e')
        self.calphi_entry.insert(0, self.calphi)
        self.calphi_entry.config(state='disabled')

        self.calphi_label0 = Label(self.scurve_frame, text="0-7")
        self.calphi_label0.grid(column=3, row=8, sticky='w')

        self.arm_dac_label = Label(self.scurve_frame, text="ARM_DAC:")
        self.arm_dac_label.grid(column=1, row=9, sticky='w')

        self.arm_dac_entry = Entry(self.scurve_frame, width=5)
        self.arm_dac_entry.grid(column=2, row=9, sticky='e')
        self.arm_dac_entry.insert(0, self.arm_dac)

        self.arm_dac_label0 = Label(self.scurve_frame, text="0-254")
        self.arm_dac_label0.grid(column=3, row=9, sticky='w')

        self.start_cal_dac_label = Label(self.scurve_frame, text="start CAL_DAC:")
        self.start_cal_dac_label.grid(column=1, row=10, sticky='w')

        self.start_cal_dac_entry = Entry(self.scurve_frame, width=5)
        self.start_cal_dac_entry.grid(column=2, row=10, sticky='e')
        self.start_cal_dac_entry.insert(0, self.start_cal_dac)

        self.start_cal_dac_label0 = Label(self.scurve_frame, text="0-254")
        self.start_cal_dac_label0.grid(column=3, row=10, sticky='w')

        self.stop_cal_dac_label = Label(self.scurve_frame, text="stop CAL_DAC:")
        self.stop_cal_dac_label.grid(column=1, row=11, sticky='w')

        self.stop_cal_dac_entry = Entry(self.scurve_frame, width=5)
        self.stop_cal_dac_entry.grid(column=2, row=11, sticky='e')
        self.stop_cal_dac_entry.insert(0, self.stop_cal_dac)

        self.stop_cal_dac_label0 = Label(self.scurve_frame, text="0-254  max diff 40")
        self.stop_cal_dac_label0.grid(column=3, row=11, sticky='w')

        self.scurve0_button = Button(self.scurve_frame, text="RUN S-curve", command=self.run_scurve, width=bwidth)
        self.scurve0_button.grid(column=1, sticky='e', columnspan=2)

        # ADD TABS

        self.scan_mode_nb.add(self.scan_frame, text="DAC Scans")
        self.scan_mode_nb.add(self.calibration_frame, text="Calibration")
        self.scan_mode_nb.add(self.routines_frame, text="Routines")
        self.scan_mode_nb.add(self.scurve_frame, text="S-curve")

        self.scan_mode_nb.grid_forget()

        ##############################################################################################################
        # ##################################################PRODUCTION MODE###########################################
        ##############################################################################################################

        self.production_frame = ttk.Frame(master, width=302, height=550)
        self.production_frame.grid(column=0, row=0)
        self.production_frame.grid_propagate(False)
        self.production_label = ttk.Label(self.production_frame, text="Production Test")
        self.production_label.grid(column=0, row=0)


        # SCAN RUN AND MODIFY BUTTONS
        self.production_button_frame = ttk.Frame(self.production_frame, width=302, height=50)
        self.production_button_frame.grid()
        self.production_button_frame.grid_propagate(False)

        #self.chip_id_label = Label(self.production_frame, text="Chip ID:")
        #self.chip_id_label.grid()
        #self.chip_id_entry = Entry(self.production_frame, width=20)
        #self.chip_id_entry.grid()
        #self.chip_id_entry.insert(0, self.chip_id)
        #self.chip_id_entry.config(state='disabled')

        self.lot_label = Label(self.production_frame, text="Lot nr.:")
        self.lot_label.grid()
        self.lot_label0 = Label(self.production_frame, text=self.lot_nr)
        self.lot_label0.grid()


        self.barcode_label = Label(self.production_frame, text="Barcode ID:")
        self.barcode_label.grid()
        self.barcode_entry = Entry(self.production_frame, width=20)
        self.barcode_entry.grid()
        self.barcode_entry.insert(0, self.barcode_id)

        if self.iref_mode:
            self.location_label = Label(self.production_frame, text="Location:")
            self.location_label.grid()
            self.location_entry = Entry(self.production_frame, width=20)
            self.location_entry.grid()

        if self.psu_found or not self.psu_mode:
            self.p_run_button = Button(self.production_frame, text="RUN", command=lambda: self.run_production_tests())
        else:
            self.p_run_button = Button(self.production_frame, state=DISABLED, text="RUN", command=lambda: self.run_production_tests())
        self.p_run_button.grid()

        self.checks_label = Label(self.production_frame, text="\nTest Result:", width=25)
        self.checks_label.grid()

        self.tests = ['Short Circuit Check',
                 'BIST',
                 #'Scan Chain',
                 'Sync',
                 #'ext ADC check',
                 #'Save Barcode',
                 'Register Test',
                 'Chip ID write',
                 'Iref adjustment',
                 'SLEEP power measurement',
                 'Internal ADC calibration',
                 'Temperature calibration',
                 'CAL_DAC conversion',
                 'Data packet test',
                 'S-bit test',
                 'Scan of all DACs',
                 'All Channel S-curves']
        self.test_label = []
        for i, test in enumerate(self.tests):
            if self.pilot_run_flag:
                self.test_label.append(Label(self.production_frame, text=test, width=25))
            else:
                self.test_label.append(Label(self.production_frame, width=25))
            self.test_label[i].grid()

        # self.production_frame.grid_forget()




        # INTERACTIVE SCREEN
        self.interactive_screen = Text(master, bg="black", fg="white", height=30, width=60)
        #self.interactive_screen.grid(column=1, row=0)
        #self.add_to_interactive_screen("\n")
        #self.add_to_interactive_screen("############################################################\n")
        #self.add_to_interactive_screen(" Welcome to the VFAT3 test system Graphical User Interface. \n")
        #self.add_to_interactive_screen("############################################################\n")
        #self.add_to_interactive_screen("\n")
        #self.scrollbar = Scrollbar(master, command=self.interactive_screen.yview)
        #self.scrollbar.grid(column=2, row=0, sticky='nsew')
        #self.interactive_screen['yscrollcommand'] = self.scrollbar.set

        # CLOSE- AND CLEAR-BUTTONS
        self.ctrlButtons_frame = ttk.Frame(master)
        self.ctrlButtons_frame.grid(column=0, sticky='e')
        self.clear_button = Button(self.ctrlButtons_frame, text="Clear", command=self.clear_interactive_screen)
        # self.clear_button.grid(column=1, row=0)
        self.close_button = Button(self.ctrlButtons_frame, text="Close", command=master.quit)
        self.close_button.grid(column=2, row=0)


####################################################################################
# ##################################FUNCTIONS#######################################
####################################################################################


# #################### GENERAL GUI FUNCTIONS ############################

    def change_directory(self):
        self.data_folder = self.data_dir_entry.get()
        self.xray_routine_flag = 0

    def ask_directory(self):
        dirtext = "Test"
        self.data_folder = tkFileDialog.askdirectory(parent=root, initialdir='/home/', title=dirtext)
        self.xray_routine_flag = 0
        self.data_dir_entry.delete(0, 'end')
        self.data_dir_entry.insert(0, self.data_folder)

    def save_calibration_values_to_file(self, filename=""):
        if filename == "":
            filename = tkFileDialog.asksaveasfilename(filetypes=[('Register file', '*.dat')])
            print "Saving calibration values to file: %s" % filename
        self.save_calibration_values_to_file_execute(filename)

    def save_calibration_values_to_file_execute(self, filename):
        if self.database:
            self.database.save_adc0(self.adc0M, self.adc0B)
            self.database.save_adc1(self.adc1M, self.adc1B)
            self.database.save_cal_dac(self.cal_dac_fcM, self.cal_dac_fcB)
            self.database.save_iref(self.register[134].Iref[0])
        else:
            #timestamp = time.strftime("%Y%m%d_%H%M")
            #filename = '%s/calibration/%scalibration.dat' % (self.data_folder, timestamp)
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc:  # Guard against race condition
                    print "Unable to create directory"
            open(filename, 'w').close()
            with open(filename, "w") as output_file:
                output_file.write("adc0M/D:adc0B/D:adc1M/D:adc1B/D:cal_dac_fcM/D:cal_dac_fcB/D:Iref/I\n")
                output_file.write('%f\t%f\t%f\t%f\t%f\t%f\t%d\n' % (self.adc0M, self.adc0B, self.adc1M, self.adc1B, self.cal_dac_fcM, self.cal_dac_fcB, self.register[134].Iref[0]))

    def load_calibration_values_from_file(self, filename=""):
        if filename == "":
            filename = tkFileDialog.askopenfilename(filetypes=[('Register file', '*.dat')])
        if filename != "":
            with open(filename, 'r') as f:
                for i, line in enumerate(f):

                    if i == 1:
                        line = line.rstrip()
                        line = [splits for splits in line.split("\t") if splits is not ""]
                        self.adc0M = float(line[0])
                        self.adc0B = float(line[1])
                        self.adc1M = float(line[2])
                        self.adc1B = float(line[3])
                        self.adcM = self.adc0M
                        self.adcB = self.adc0B
                        if self.adc0M <= 1 or self.adc0M > 2.5:
                            print "ADC0 broken"
                            self.adc0M = 0
                            self.adc0B = 0
                            self.adcM = self.adc1M
                            self.adcB = self.adc1B
                        if self.adc1M <= 1 or self.adc1M > 2.5:
                            print "ADC1 broken"
                            self.adc1M = 0
                            self.adc1B = 0
                            if self.adc0M == 0:
                                self.adcM = 0
                                self.adcB = 0
                        self.cal_dac_fcM = float(line[4])
                        self.cal_dac_fcB = float(line[5])
                        self.register[134].Iref[0] = int(line[6])
                        self.write_register(134)
                        text = "\nCalibration values were loaded from file.\n"
                        text += "ADC0: %f + %f\n" % (self.adc0M, self.adc0B)
                        text += "ADC1: %f + %f\n" % (self.adc1M, self.adc1B)
                        text += "CAL_DAC: %f + %f\n" % (self.cal_dac_fcM, self.cal_dac_fcB)
                        text += "Iref: %i\n" % self.register[134].Iref[0]
                        self.add_to_interactive_screen(text)
        else:
            print "Invalid file. Abort."

    def save_register_values_to_file(self):
        filename = tkFileDialog.asksaveasfilename(filetypes=[('Register file', '*.reg')])
        if filename != "":
            self.save_register_values_to_file_execute(filename)

    def save_register_values_to_file_execute(self, filename):
        with open(filename, "w") as output_file:
            for reg_nr in range(0, 146):
                data = []
                for x in register[reg_nr].reg_array:
                    data.extend(dec_to_bin_with_stuffing(x[0], x[1]))
                data = ''.join(str(e) for e in data)
                output_file.write("%s,%s\n" % (reg_nr, data))

    def load_register_values_from_file(self):
        filename = tkFileDialog.askopenfilename(filetypes=[('Register file', '*.reg')])
        if filename != "":
            # Check the validity of the file.
            prev_reg_nr = -1
            error_counter = 0
            with open(filename, 'r') as f:
                for line in f:
                    line = line.split(",")
                    reg_nr = int(line[0])
                    write_data = line[1]
                    if (reg_nr - prev_reg_nr) != 1:
                        print "Error in the register setting file ."
                        print reg_nr - prev_reg_nr
                        error_counter += 1
                    if len(write_data) != 17:
                        print "Error in the register setting file."
                        error_counter += 1
                        print len(write_data)
                    prev_reg_nr = reg_nr
            if error_counter == 0:
                self.load_register_values_from_file_execute(filename, multiwrite=1)
            else:
                print "Invalid file. Abort."

    def load_register_values_from_file_execute(self, filename, multiwrite=0):
        start = time.time()
        if multiwrite == 0:
            with open(filename, 'r') as f:
                for line in f:
                    #time.sleep(0.015)
                    line = line.split(",")
                    reg_nr = int(line[0])
                    write_data = line[1]
                    self.register[reg_nr].change_values(write_data)
                    # self.write_register(reg_nr)
        else:
            filler_16bits = [0]*16
            full_data = []
            nr_of_registers = 0
            reg_nr = 0
            with open(filename, 'r') as f:
                for h, line in enumerate(f):
                    line = line.split(",")
                    reg_nr = int(line[0])
                    #print reg_nr
                    write_data = line[1]
                    self.register[reg_nr].change_values(write_data)
                    data = []
                    for x in register[reg_nr].reg_array:
                        data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
                        data.extend(data_intermediate)
                    data.reverse()
                    data.extend(filler_16bits)
                    full_data.extend(data)
                    nr_of_registers += 1
                    if nr_of_registers > 30:
                        output = self.SC_encoder.create_SC_packet(reg_nr, full_data, "MULTI_WRITE", 0, nr_words=nr_of_registers)
                        paketti = output[0]
                        write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
                        for x in range(1, len(paketti)):
                            write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
                        self.interfaceFW.send_fcc(0, self.interactive_output_file)
                        nr_of_registers = 0
                        full_data = []
                        reg_nr = h + 1

            output = self.SC_encoder.create_SC_packet(reg_nr, full_data, "MULTI_WRITE", 0,
                                                                  nr_words=nr_of_registers)
            paketti = output[0]
            write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
            for x in range(1, len(paketti)):
                write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
            self.interfaceFW.send_fcc(0, self.interactive_output_file)
        stop = time.time()
        print stop-start

    def apply_ch_local_adjustments(self):
        filename = "./data/channel_registers.dat"
        text = "Reading channel calibration data...\n"
        self.add_to_interactive_screen(text)

        if os.path.isfile(filename):
            # Calculate the number of lines to verify valid data.
            with open(filename, 'r') as f:
                for nr_lines, l in enumerate(f):
                    pass
            if (nr_lines + 1) == 128:
                with open(filename, 'r') as f:
                    for reg, line in enumerate(f):
                        line = line.rstrip()
                        self.register[reg].change_values(line)
                        print "Write:%s to register:%d" % (line,reg)
                        self.write_register(reg)
                text = "Channel calibration data applied successfully.\n"
                self.add_to_interactive_screen(text)

            else:
                text = "Invalid channel calibration data.\n ->Recommended to rerun calibration.\n"
                self.add_to_interactive_screen(text)
        else:
            text = "Channel calibration data not found.\n ->Recommended to run calibration.\n"
            self.add_to_interactive_screen(text)

    def read_all_registers(self):
        # Read register value from the chip and save it to the register object.
        text = "Reading all of the chips registers:\n"
        self.add_to_interactive_screen(text)
        for i in range(129, 146):
            self.read_register(i)
        self.clear_interactive_screen()

    def read_register(self, reg, save_value='yes'):
        new_data = self.interfaceFW.read_register(reg)
        if new_data != 'Error':
            if save_value == 'yes':
                if reg == 0x10003:
                    self.register[reg].change_values(''.join(str(e) for e in new_data))
                else:
                    self.register[reg].change_values(''.join(str(e) for e in new_data[16:]))
        return new_data

    def add_to_interactive_screen(self, text):
        pass
        #self.interactive_screen.insert(END, text)
        #self.interactive_screen.see(END)

    def clear_interactive_screen(self):
        self.interactive_screen.delete(1.0, END)

    def execute(self, verbose="no"):
        output = self.interfaceFW.launch(register, self.interactive_output_file, self.COM_port)
        if output[0] == "Error":
            text = "%s: %s\n" % (output[0], output[1])
            self.add_to_interactive_screen(text)
        else:
            if output[0]:
                # text =  "Received SC replies:\n"
                # self.add_to_interactive_screen(text)
                for i in output[0]:
                    if i.info_code == 0:
                        if verbose == "yes":
                            text = "Transaction ok.\n"
                            self.add_to_interactive_screen(text)
                        print "Transaction ok."
                    else:
                        if verbose == "yes":
                            text = "Transaction error.\n"
                            self.add_to_interactive_screen(text)

                    # text = "Transaction ID:%d, %s\n" % (i.transaction_ID, data_ok)
                    # self.add_to_interactive_screen(text)
                    if i.type_ID == 0:
                        pass
                        # text = "Data:\n %s\n" % i.data
                        # self.add_to_interactive_screen(text)

            if output[1]:
                if verbose == "yes":
                    text = "Received data packets:\n"
                    self.add_to_interactive_screen(text)
                for i in output[1]:
                    if i.spzs_packet == 1:
                        if verbose == "yes":
                            text = "Data built from a SPZS packet.\n"
                            self.add_to_interactive_screen(text)
                    if i.header == "00011010" or i.header == "01010110":
                        if verbose == "yes":
                            text = "Header II received.\n"
                            self.add_to_interactive_screen(text)
                        if i.BC or i.EC:
                            if verbose == "yes":
                                text =  "BC:%d EC: %d\n" % (i.BC,i.EC)
                                self.add_to_interactive_screen(text)
   
                    else:
                        if verbose == "yes":
                            text =  "BC:%d EC: %d\n" % (i.BC,i.EC)
                            self.add_to_interactive_screen(text)
                            text  = "Hits, channels:128-1\n"
                            text +=  "%s\n" % i.data[0:16]
                            text +=  "%s\n" % i.data[16:32]
                            text +=  "%s\n" % i.data[32:48]
                            text +=  "%s\n" % i.data[48:64]
                            text +=  "%s\n" % i.data[64:80]
                            text +=  "%s\n" % i.data[80:96]
                            text +=  "%s\n" % i.data[96:112]
                            text +=  "%s\n" % i.data[112:128]
                            self.add_to_interactive_screen(text)
            if output[2]:
                if verbose == "yes":
                    text =  "Received sync replies:\n"
                    self.add_to_interactive_screen(text)
                for i in output[2]:
                    if verbose == "yes":
                        text =  "BC:%d, %s\n" % (i[0],i[1])
                        self.add_to_interactive_screen(text)

        return output                 

    def change_mode(self, mode):
        if mode == "interactive":
            self.scan_mode_nb.grid_forget()
            self.production_frame.grid_forget()
            self.nb.grid(column=0, row=0)
        if mode == "scans_tests":
            self.nb.grid_forget()
            self.production_frame.grid_forget()
            self.scan_mode_nb.grid(column=0, row=0)
        if mode == "production":
            self.nb.grid_forget()
            self.scan_mode_nb.grid_forget()
            self.production_frame.grid(column=0, row=0)
            self.production_frame.grid_propagate(False)


# ################ FW-TAB FUNCTIONS ################################

    def FW_sync(self):
        text = "-> Resynchronising Firmware.\n"
        self.add_to_interactive_screen(text)
        command_encoded = FCC_LUT["CC-A"]
        write_instruction(self.interactive_output_file, 1, command_encoded, 1)
        write_instruction(self.interactive_output_file, 1, command_encoded, 0)
        write_instruction(self.interactive_output_file, 1, command_encoded, 0)
        self.execute(verbose="yes")

    def change_com_port(self, port):
        self.COM_port = port

    def check_value_range(self, name, value, min, max):
        error = 0
        if not isinstance(value, (int, long) ):
            print "%s value is not an integer." % name
            error = 1
        else:
            if value > max:
                print "%s value is too high. Maximun is: %d" % (name, max)
                error = 1
            if value < min:
                print "%s value is too low. Minimun is: %d" % (name, min)
                error = 1
        return error


# ################ MISC-TAB FUNCTIONS ################################

    def measure_adc_offset(self):

        print "\nMeasuring ADC offset.\n"
        self.register[0xffff].RUN[0] = 1
        self.write_register(0xffff)
        time.sleep(0.01)
        self.register[133].Monitor_Sel[0] = 32
        self.write_register(133)
        time.sleep(0.01)
        output = self.read_ext_adc()
        vbgr = output[5]
        vmon = output[1]
        print vbgr
        print vmon
        adc_offset = vmon - vbgr
        print "ADC Offset: %s mV" % adc_offset
        self.register[0xffff].RUN[0] = 0
        self.write_register(0xffff)
        if self.database:
            self.database.save_vbgr(vbgr)
            self.database.save_adc_offset(adc_offset)
        print "*************************"
        print ""

    def adjust_adc0_ref(self):
        print "\nAdjusting ADC0 reference voltage."
        self.register[0xffff].RUN[0] = 0
        self.write_register(0xffff)
        time.sleep(0.01)
        self.register[0xffff].RUN[0] = 1
        self.write_register(0xffff)
        time.sleep(0.01)
        self.register[133].Monitor_Sel[0] = 39
        self.write_register(133)
        time.sleep(0.01)
        diff_values = []
        for i in range(0, 4):
            self.register[133].VREF_ADC[0] = i
            self.write_register(133)
            time.sleep(0.01)
            output = self.read_ext_adc()
            diff_values.append(abs(1000-output[1]))
        print diff_values
        chosen_value = diff_values.index(min(diff_values))
        print "Chosen VREF_ADC value: %s" % chosen_value
        self.register[133].VREF_ADC[0] = chosen_value
        self.write_register(133)
        if self.database:
            self.database.save_vref(chosen_value)

    def read_chip_id(self):
        with open('./data/chip_id.dat', 'r') as f:
            self.chip_id = int(f.readline())

    def increment_chip_id(self):
        self.read_chip_id()
        self.chip_id += 1
        with open('./data/chip_id.dat', 'w') as f:
            f.write(str(self.chip_id))
        self.read_chip_id()
        self.chip_id_entry.config(state='normal')
        self.chip_id_entry.delete(0, 'end')
        self.chip_id_entry.insert(0, self.chip_id)
        self.chip_id_entry.config(state='disabled')

    def unset_calibration_variables(self):
        self.adc0M = 0.0
        self.adc0B = 0.0
        self.adc1M = 0.0
        self.adc1B = 0.0
        self.adcM = 0.0
        self.adcB = 0.0
        self.cal_dac_fcM = 0.0
        self.cal_dac_fcB = 0.0
        self.temperature_k1 = 0
        self.temperature_k2 = 0
        #self.database = 0

    def check_short_circuit(self):
        print "\n*******************"
        print "* Checking short circuits.\n"
        error = 0
        time.sleep(0.8)
        ch1_current = self.tti_if.req_ch1_current()
        ch2_current = self.tti_if.req_ch2_current()
        print "ch1 current: %s" % ch1_current
        print "ch2 current: %s" % ch2_current
        if ch1_current > 0.300 or ch2_current > 0.300:
            self.tti_if.set_outputs_off()
            print "Short circuit detected.\n"
            error = 'r'
        else:
            print "Check ok."
        print "*******************"
        print ""
        return error

    def calibrate_temperature(self, production='yes'):
        print "*************************"
        print "* Calibrating Temperature.\n"
        result = 1
        register[133].Monitor_Sel[0] = 37
        self.write_register(133)
        output = self.read_adc()
        if self.temp_gun_mode:
            temperature_c = self.temp_gun_interface.read_value()
            result = self.check_selection_criteria(temperature_c, lim_Temperature, "Temperature measurement")

        if output != 'n' and result == 0:
            temperature_mv = output[1]
            offset = temperature_mv - self.temp_coeff * temperature_c
            self.temperature_k1 = 1 / self.temp_coeff
            self.temperature_k2 = -1 * offset / self.temp_coeff
            temperature_calc = self.temperature_k1 * temperature_mv + self.temperature_k2
            print temperature_calc
            print "Calculated K2: %f" % self.temperature_k2
            print "Temperature is %f mV, %f C" % (temperature_mv, temperature_calc)
            if self.database and production == 'yes':
                self.database.save_temperature(temperature_mv)
                if self.temp_gun_mode:
                    self.database.save_temperature_c(temperature_c)
                    self.database.save_temperature_k2(self.temperature_k2)
            result = self.check_selection_criteria(self.temperature_k2, lim_Temperature_k2, "Temperature calibration for K2.")
        print "*************************"
        print ""
        return result

    def read_temperature(self):
        if self.temperature_k1 != 0 and self.temperature_k2 != 0:
            register[133].Monitor_Sel[0] = 37
            self.write_register(133)
            output = self.read_adc()
            temperature_c = self.temp_gun_interface.read_value()
            temperature_mv = output[1]
            temperature_calc = self.temperature_k1 * temperature_mv + self.temperature_k2
            difference = temperature_calc - temperature_c
            print "Internal temperature is %f mV, %f C,   Temp gun: %0.1f C, difference is: %0.1f" % (temperature_mv, temperature_calc, temperature_c, difference)
        else:
            print "Temperature coefficients are not calibrated."

    def measure_power(self, mode=""):
        print "\n*************************"
        print "* Measuring power.\n"
        error = 0
        time.sleep(0.2)
        avdd_power = self.interfaceFW.read_avdd_power()
        time.sleep(0.2)
        dvdd_power = self.interfaceFW.read_dvdd_power()
        iovdd_power = self.interfaceFW.read_iovdd_power()
        errors = [0]*2
        if self.database:
            self.database.save_power(dvdd_power, avdd_power, mode)
            if mode == "SLEEP":
                errors[0] = self.check_selection_criteria(dvdd_power, lim_Digital_Power_SLEEP, "Power measurement Digital SLEEP")
                errors[1] = self.check_selection_criteria(avdd_power, lim_Analog_Power_SLEEP, "Power measurement Analog SLEEP")
            elif mode == "RUN":
                errors[0] = self.check_selection_criteria(dvdd_power, lim_Digital_Power_RUN, "Power measurement Digital RUN")
                errors[1] = self.check_selection_criteria(avdd_power, lim_Analog_Power_RUN, "Power measurement Analog RUN")
            else:
                print "ERROR. Mode not found."
                errors[0] = 'r'
                errors[1] = 'r'
            if 'y' in errors:
                error = 'y'
            if 'r' in errors:
                error = 'r'
        print "*************************"
        print ""
        return error

    def send_reset(self):
        print 'Synchronizing the chip.'
        counter = 0
        error = 0
        self.interfaceFW.send_ext_reset()
        while True:
            result = self.interfaceFW.send_sync()
            time.sleep(0.1)
            if result[0] == '0x3a':
                text = "->Sync success.\n"
                self.add_to_interactive_screen(text)
                print text
                break
            if counter > 1:
                error = 'r'
                text = "->Sync fail.\n"
                self.add_to_interactive_screen(text)
                print text
                break
            counter += 1
        return error

    def read_ext_adc(self, verbose='yes'):
        if verbose == 'yes':
            text = "->Reading the verification board external ADC.\n"
            self.add_to_interactive_screen(text)

        # Imon
        value = self.interfaceFW.read_ext_adc_imon()
        msb = int(value[1], 16) << 8
        lsb = int(value[0], 16)
        imon_value_int = msb + lsb
        imon_value_mv = imon_value_int * 0.0625
        time.sleep(0.1)
        # Vmon
        value = self.interfaceFW.read_ext_adc_vmon()
        msb = int(value[1], 16) << 8
        lsb = int(value[0], 16)
        vmon_value_int = msb + lsb
        vmon_value_mv = vmon_value_int * 0.0625
        time.sleep(0.1)

        # VBGR
        value = self.interfaceFW.read_ext_adc_vbgr()
        msb = int(value[1], 16) << 8
        lsb = int(value[0], 16)
        vbgr_value_int = msb + lsb
        vbgr_value_mv = vbgr_value_int * 0.0625
        if verbose == 'yes':
            text = "EXT ADC Imon: %d\t %f mV\n" % (imon_value_int, imon_value_mv)
            text += "EXT ADC Vmon: %d\t %f mV\n" % (vmon_value_int, vmon_value_mv)
            text += "EXT ADC VBGR: %d\t %f mV\n" % (vbgr_value_int, vbgr_value_mv)
            self.add_to_interactive_screen(text)
            print text
        return [vmon_value_int, vmon_value_mv, imon_value_int, imon_value_mv, vbgr_value_int, vbgr_value_mv]

    def test_ext_adc(self):
        error = 0
        value = self.ext_adc(verbose='no')
        if value > 50 and value < 150:
            pass
        else:
            error = 1
            text = "External ADC returned value: %f mV. should be 50-150mV\n" % value
            self.add_to_interactive_screen(text)
        return error

    def send_sync(self, verbose='yes'):
        result = 0
        if verbose == 'yes':
            text = "->Sending sync request.\n"
            self.add_to_interactive_screen(text)
        output = self.interfaceFW.send_fcc(["00010111", "00010111", "00010111"])
        if output[0] == "Error":
            if verbose == 'yes':
                text = "Error in sync\n"
                self.add_to_interactive_screen(text)
                self.sync_label.config(text="Error")
                self.sync_label.config(bg="red")
        elif output[0] == '0x3a':
            result = 1
            if verbose == 'yes':
                text = "Sync ok.\n"
                self.add_to_interactive_screen(text)
                self.sync_label.config(text="ok")
                self.sync_label.config(bg="green")
        else:
            if verbose == 'yes':
                text = "Sync fail.\n"
                self.add_to_interactive_screen(text)
                self.sync_label.config(text="Fail")
                self.sync_label.config(bg="red")
        return result

    def send_sync_verif(self, verbose='yes'):
        result = 0
        if verbose == 'yes':
            text = "->Sending sync verification request.\n"
            self.add_to_interactive_screen(text)
        output = self.interfaceFW.send_fcc("11101000")
        if output[0] == "Error":
            if verbose == 'yes':
                text = "Error in sync\n"
                self.add_to_interactive_screen(text)
                self.sync_check_label.config(text="Error")
                self.sync_check_label.config(bg="red")
        elif output[0] == '0xfe':
            result = 1
            if verbose == 'yes':
                text = "Sync verification ok.\n"
                self.add_to_interactive_screen(text)
                self.sync_check_label.config(text="ok")
                self.sync_check_label.config(bg="green")
        else:
            if verbose == 'yes':
                text = "Sync verification fail.\n"
                self.add_to_interactive_screen(text)
                self.sync_check_label.config(text="Fail")
                self.sync_check_label.config(bg="red")
        return result

    def adjust_iref(self, verbose='yes', production='no'):
        print "\n*************************"
        print "* Adjusting Iref.\n"
        start = time.time()

        result = 1
        self.register[0xffff].RUN[0] = 1
        self.write_register(0xffff)
        time.sleep(0.01)
        self.register[133].Monitor_Sel[0] = 0
        self.write_register(133)
        time.sleep(0.01)
        adc_values = []
        dac_values = []
        for i in range(15, 46, 5):
            self.register[134].Iref[0] = i
            self.write_register(134)
            time.sleep(0.01)
            output = self.read_ext_adc(verbose='no')
            adc_values.append(output[3])
            dac_values.append(i)
        find_closest_value('Iref', dac_values, adc_values)
        print hv3b_biasing_lut['Iref'][1]
        self.register[134].Iref[0] = hv3b_biasing_lut['Iref'][1]
        self.write_register(134)
        output = self.read_ext_adc(verbose='no')
        iref_mv = output[3]
        # print "Iref adjusted to: %s mV" % iref_mv
        if production == "yes":
            self.database.save_iref_mv(iref_mv)
            self.database.save_iref(hv3b_biasing_lut['Iref'][1])
        # output = self.interfaceFW.adjust_iref()
        # if output[0] != '00':
        #     result = 0
        #     if verbose == 'yes':
        #         text = "Iref adjusted to value %s.\n" % int(output[0], 16)
        #         self.add_to_interactive_screen(text)
        #         print text[:-2]

        # self.register[134].Iref[0] = int(output[0], 16)
        stop = time.time()
        run_time = (stop - start)
        result = self.check_selection_criteria(iref_mv, lim_iref, "Iref Adjustment")
        print "\niref routine time: %f sec" % run_time
        print "*************************"
        print ""
        return result

    def adc_calibration(self, production="no"):
        error = 0
        start = time.time()
        print "\n*************************"
        print "* Starting ADC calibration.\n"
        if self.Iref_cal == 0:
            text = "\nIref is not calibrated. Run Iref calibration first.\n"
            self.add_to_interactive_screen(text)
        else:
            self.adjust_adc0_ref()
            self.measure_adc_offset()
            start = time.time()

            output = self.interfaceFW.int_adc_calibration(0, 10, 255)
            ext_adc_values = []
            adc0_values = []
            adc1_values = []
            cal_dac_values = []
            adc_flag = 0
            for value in output:
                #print value
                if adc_flag == 0:
                    value_lsb = value[2:]
                    if len(value_lsb) == 1:
                        value_lsb = "0" + value_lsb
                    adc_flag = 1
                elif adc_flag == 1:
                    ivalue = value + value_lsb
                    ivalue_dec = int(ivalue, 16)
                    #print "DAC: %f" % ivalue_dec
                    cal_dac_values.append(ivalue_dec)
                    ivalue = ""
                    adc_flag = 2
                elif adc_flag == 2:
                    value_lsb = value[2:]
                    if len(value_lsb) == 1:
                        value_lsb = "0"+value_lsb
                    adc_flag = 3
                elif adc_flag == 3:
                    ivalue = value + value_lsb
                    ivalue_dec = float(int(ivalue, 16))
                    ivalue_mv = ivalue_dec * 0.0625
                    #print "ext ADC: %f" % ivalue_mv
                    ext_adc_values.append(ivalue_mv)
                    ivalue = ""
                    adc_flag = 4
                elif adc_flag == 4:
                    value_lsb = value[2:]
                    if len(value_lsb) == 1:
                        value_lsb = "0"+value_lsb
                    adc_flag = 5
                elif adc_flag == 5:
                    ivalue = value + value_lsb
                    ivalue_dec = float(int(ivalue, 16))
                    #print "ADC0: %f" % ivalue_dec
                    adc0_values.append(ivalue_dec)
                    ivalue = ""
                    adc_flag = 6
                elif adc_flag == 6:
                    value_lsb = value[2:]
                    if len(value_lsb) == 1:
                        value_lsb = "0"+value_lsb
                    adc_flag = 7
                elif adc_flag == 7:
                    ivalue = value + value_lsb
                    ivalue_dec = float(int(ivalue, 16))
                    #print "ADC1: %f" % ivalue_dec
                    adc1_values.append(ivalue_dec)
                    ivalue = ""
                    adc_flag = 0

            stop = time.time()
            run_time = (stop - start)
            text = "\nScan duration: %f sec\n" % run_time
            print text
            #self.add_to_interactive_screen(text)
            adc_values = calc_adc_conversion_constants(self, ext_adc_values, adc0_values, adc1_values, cal_dac_values,
                                                       production)
            self.adc0M = adc_values[0]
            self.adc0B = adc_values[1]
            self.adc1M = adc_values[2]
            self.adc1B = adc_values[3]

            text = "\nInternal ADCs calibrated. Values:\n"
            text += "ADC0: %f + %f\n" % (self.adc0M, self.adc0B)
            text += "ADC1: %f + %f\n" % (self.adc1M, self.adc1B)
            self.add_to_interactive_screen(text)
            self.adcM =self.adc0M
            self.adcB = self.adc0B
            if self.adc0M <= 1 or self.adc0M > 2.5:
                print "ADC0 broken"
                self.adc0M = 0
                self.adc0B = 0
                self.adcM = self.adc1M
                self.adcB = self.adc1B
            if self.adc1M <= 1 or self.adc1M > 2.5:
                print "ADC1 broken"
                self.adc1M = 0
                self.adc1B = 0
                if self.adc0M == 0:
                    self.adcM = 0
                    self.adcB = 0
            stop = time.time()
            run_time = (stop - start)
            text = "\nScan duration: %f sec\n" % run_time
            self.add_to_interactive_screen(text)
        print ""
        errors = [0]*4
        errors[0] = self.check_selection_criteria(self.adc0M, lim_ADC0m, "ADC0 Multiplier")
        errors[1] = self.check_selection_criteria(self.adc0B, lim_ADC0b, "ADC0 Offset")
        errors[2] = self.check_selection_criteria(self.adc1M, lim_ADC1m, "ADC1 Multiplier")
        errors[3] = self.check_selection_criteria(self.adc1B, lim_ADC1b, "ADC1 Offset")
        if 'y' in errors:
            error = 'y'
        if 'r' in errors:
            error = 'r'

        stop = time.time()
        run_time = (stop - start)
        print "\nADC calibration routine time: %f sec" % run_time
        print "*************************"
        print ""
        return error

    def scan_cal_dac_fc(self, production="no"):
        print "\n*************************"
        print "* Starting CAL_DAC calibration.\n"
        start_time = time.time()
        error = 0
        dac_start = 0
        dac_stop = 255
        step = 10

        if self.adcM == 0:
            text = "\nADCs are not calibrated. Run ADC calibration first.\n"
            self.add_to_interactive_screen(text)
            error = 1
        else:
            start = time.time()
            cal_dac_values = []
            output = self.interfaceFW.cal_dac_calibration(start=dac_start, stop=dac_stop, step=step)
            msb = int(output[1], 16) << 8
            lsb = int(output[0], 16)
            base_value_int = msb + lsb
            # base_value_hex = "%s%s" % (output[1], output[0][2:])
            # base_value_int = int(base_value_hex, 16)
            if self.hybrid_model == "HV3b":
                base_value_mv = base_value_int * 0.0625
            elif self.hybrid_model == "HV3a":
                base_value_mv = base_value_int * self.adc1M + self.adc1B
            else:
                print "Error hybrid model: %s not found" % self.hybrid_model
            ext_adc_values = []
            ext_adc_values_hex = output[2:]
            flag = 0
            for value in ext_adc_values_hex:
                if flag == 0:  # Start of CAL_DAC value collection.
                    lsb = int(value, 16)
                    # value_lsb = value[2:]
                    # if len(value_lsb) == 1:
                    #     value_lsb = "0"+value_lsb
                    flag = 1
                elif flag == 1:
                    # ivalue = value+value_lsb
                    # ivalue_dec = int(ivalue, 16)
                    msb = int(value, 16) << 8
                    ivalue_dec = msb + lsb
                    cal_dac_values.append(ivalue_dec)
                    # ivalue = ""
                    flag = 2
                elif flag == 2:  # Start of ext adc value collection.
                    lsb = int(value, 16)
                    # value_lsb = value[2:]
                    # if len(value_lsb) == 1:
                    #    value_lsb = "0"+value_lsb
                    flag = 3
                elif flag == 3:
                    msb = int(value, 16) << 8
                    ivalue_dec = msb + lsb
                    # ivalue = value+value_lsb
                    # ivalue_dec = int(ivalue, 16)
                    if self.hybrid_model == "HV3b":
                        ivalue_mv = ivalue_dec * 0.0625
                    elif self.hybrid_model == "HV3a":
                        ivalue_mv = ivalue_dec * self.adc1M + self.adc1B
                    else:
                        print "Error hybrid model: %s not found" % self.hybrid_model
                    ext_adc_values.append(ivalue_mv)
                    ivalue = ""
                    flag = 0
            #cal_dac_values.reverse()

            output = calc_cal_dac_conversion_factor(self, cal_dac_values, base_value_mv, ext_adc_values, production=production)
            self.cal_dac_fcM = output[0]
            self.cal_dac_fcB = output[1]

            text = "\nCAL_DAC conversion completed.\n"
            text += "CAL_DAC to fC: %f + %f\n" % (self.cal_dac_fcM, self.cal_dac_fcB)
            self.add_to_interactive_screen(text)
            stop = time.time()
            run_time = (stop - start)
            text = "\nScan duration: %f sec\n" % run_time
            self.add_to_interactive_screen(text)
        errors = [0]*2
        errors[0] = self.check_selection_criteria(self.cal_dac_fcM, lim_CAL_DACm, "CAL_DAD Conversion Multiplier")
        errors[1] = self.check_selection_criteria(self.cal_dac_fcB, lim_CAL_DACb, "CAL_DAD Conversion Offset")
        if 'y' in errors:
            error = 'y'
        if 'r' in errors:
            error = 'r'
        stop_time = time.time()
        run_time = stop_time - start_time
        print "\nCAL_DAC calibration time: %f s" % run_time
        print "*************************"
        print ""
        return error

    def send_idle(self):
        text = "->Sending IDLE transaction.\n"
        self.add_to_interactive_screen(text)
        output = self.SC_encoder.create_SC_packet(0, 0, "IDLE", 0)
        paketti = output[0]
        write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
        for x in range(1, len(paketti)):
            write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
        self.execute(verbose="yes")

    def read_adc0(self):
        addr = 131072  # ADC0 address
        output = self.read_register(addr, save_value='no')
        #output.reverse()
        int_adc_value = int(''.join(map(str, output[-16:])), 2)
        mv_adc_value = self.adc0M * int_adc_value + self.adc0B
        return [int_adc_value, mv_adc_value]

    def read_adc1(self):
        addr = 131073  # ADC1 address
        output = self.read_register(addr, save_value='no')
        #output.reverse()
        int_adc_value = int(''.join(map(str, output[-16:])), 2)
        mv_adc_value = self.adc1M * int_adc_value + self.adc1B
        return [int_adc_value, mv_adc_value]

    def read_adc(self):
        if self.adc0M != 0:
            adc0_value = self.read_adc0()
            adc_value = adc0_value
        elif self.adc1M != 0:
            adc1_value = self.read_adc1()
            adc_value = adc1_value
        else:
            adc_value = 'n'
        return adc_value

    def read_adcs(self):
        text = "->Reading the ADCs.\n"
        self.add_to_interactive_screen(text)

        adc0_value = self.read_adc0()
        text = "ADC0: %d\t %f mV\n" % (adc0_value[0], adc0_value[1])
        self.add_to_interactive_screen(text)
        self.adc0_label0.config(text="%.2f mV" % adc0_value[1])

        adc1_value = self.read_adc1()
        text = "ADC1: %d\t %f mV\n" % (adc1_value[0], adc1_value[1])
        self.add_to_interactive_screen(text)
        self.adc1_label0.config(text="%.2f mV" % adc1_value[1])

        ext_adc_value = self.read_ext_adc(verbose='yes')
        text = "EXT ADC: %d\t %f mV\n" % (ext_adc_value[0], ext_adc_value[1])
        self.add_to_interactive_screen(text)
        self.ext_adc_label0.config(text="%.2f mV" % ext_adc_value[1])

    def sync_fpga(self):
        self.unset_calibration_variables()
        self.send_reset()
        output = self.read_register(0x10000, save_value='no')
        value = int(''.join(map(str, output)), 2)
        self.hw_id_id_label0.config(text="%x" % value)
        output = self.read_register(0x10001, save_value='no')
        value = int(''.join(map(str, output)), 2)
        self.hw_id_ver_label0.config(text="%x" % value)
        output = self.read_register(0x10003, save_value='no')
        value = int(''.join(map(str, output)), 2)
        self.chip_id = value
        self.chip_id_label0.config(text="%i" % value)
        self.toggle_run_bit(change_value="no")

    def test_trigger_outputs(self, production='no'):
        print "\n*************************"
        print "* Starting trigger bit testing.\n"
        start_time = time.time()
        error = 0
        # Set RUN bit to one.
        self.register[0xffff].RUN[0] = 1
        self.write_register(0xffff)

        self.set_fe_nominal_values()


        self.register[132].PT[0] = 3
        self.register[132].SEL_POL[0] = 0
        self.register[132].SEL_COMP_MODE[0] = 0
        self.write_register(132)

        self.register[138].CAL_SEL_POL[0] = 0
        self.register[138].CAL_PHI[0] = 1
        self.register[138].CAL_MODE[0] = 1
        self.write_register(138)

        self.register[131].TP_FE[0] = 7
        self.write_register(131)

        self.register[139].CAL_DUR[0] = 200
        self.register[139].CAL_FS[0] = 1
        self.write_register(139)

        self.register[135].ARM_DAC[0] = 70
        self.write_register(135)

        self.register[129].PS[0] = 7
        self.write_register(129)

        # Send RUNMode fcc.
        self.interfaceFW.send_fcc("01100110")

        message0 = [0xca, 0xdd, 0x08, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0x00,0x04]
        message1 = [0xca, 0xdd, 0x08, 0,0,0,0,0,0,0,0,0,0,0,0,136,136,0,0,0x00,0x04]
        message2 = [0xca, 0xdd, 0x08, 0,0,0,0,0,0,0,0,0,0,136,136,0,0,0,0,0x00,0x04]
        message3 = [0xca, 0xdd, 0x08, 0,0,0,0,0,0,0,0,136,136,0,0,0,0,0,0,0x00,0x04]
        message4 = [0xca, 0xdd, 0x08, 0,0,0,0,0,0,136,136,0,0,0,0,0,0,0,0,0x00,0x04]
        message5 = [0xca, 0xdd, 0x08, 0,0,0,0,136,136,0,0,0,0,0,0,0,0,0,0,0x00,0x04]
        message6 = [0xca, 0xdd, 0x08, 0,0,136,136,0,0,0,0,0,0,0,0,0,0,0,0,0x00,0x04]
        message7 = [0xca, 0xdd, 0x08, 136,136,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x00,0x04]
        print "Trigger bit testing routine."

        errors = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        timee = 0.4
        output = self.interfaceFW.test_trigger_bits(message0, 0)
        errors[0] = output[0]
        errors[1] = output[1]
        time.sleep(timee)
        output = self.interfaceFW.test_trigger_bits(message1, 1)
        errors[0] = output[0]
        errors[2] = output[1]
        time.sleep(timee)
        output = self.interfaceFW.test_trigger_bits(message2, 2)
        errors[0] = output[0]
        errors[3] = output[1]
        time.sleep(timee)
        output = self.interfaceFW.test_trigger_bits(message3, 3)
        errors[0] = output[0]
        errors[4] = output[1]
        time.sleep(timee)
        output = self.interfaceFW.test_trigger_bits(message4, 4)
        errors[0] = output[0]
        errors[5] = output[1]
        time.sleep(timee)
        output = self.interfaceFW.test_trigger_bits(message5, 5)
        errors[0] = output[0]
        errors[6] = output[1]
        time.sleep(timee)
        output = self.interfaceFW.test_trigger_bits(message6, 6)
        errors[0] = output[0]
        errors[7] = output[1]
        time.sleep(timee)
        output = self.interfaceFW.test_trigger_bits(message7, 7)
        errors[0] = output[0]
        errors[8] = output[1]

        print errors
        if production == "yes":
            self.database.save_sbit_errors(''.join(str(e) for e in errors))

        error = self.check_selection_criteria(sum(errors), lim_sbits, "S-bit")
        stop_time = time.time()
        run_time = stop_time - start_time
        print "\nTrigger bit testing time: %f s" % run_time
        print "*************************"
        print ""
        return error

    def send_cal_trigger(self):
        latency = int(self.scurve_entry.get())
        self.CalPulseLV1A_latency = latency
        self.CalPulse_LV1A_entry.delete(0, END)
        self.CalPulse_LV1A_entry.insert(0, self.CalPulseLV1A_latency)
        text = "->Sending CalPulse and LV1A with %s BC latency \n" % latency
        self.add_to_interactive_screen(text)
        CalPulse_encoded = FCC_LUT["CalPulse"]
        LV1A_encoded = FCC_LUT["LV1A"]

        write_instruction(self.interactive_output_file, 1, CalPulse_encoded, 1)
        write_instruction(self.interactive_output_file, latency, LV1A_encoded, 0)
        self.execute(verbose="yes")

    def toggle_run_bit(self, change_value="yes"):
        output = self.read_register(0xffff)
        if output[0] == "Error":
            self.run_status_label.config(text="ERROR")
            self.run_status_label.config(bg="red")
        else:
            if self.register[0xffff].RUN[0] == 0:
                if change_value == "yes":
                    self.register[0xffff].RUN[0] = 1
                    self.write_register(0xffff)
                    self.run_status_label.config(text="RUN")
                    self.run_status_label.config(bg="green")
                else:
                    self.run_status_label.config(text="SLEEP")
                    self.run_status_label.config(bg="blue")
            elif self.register[0xffff].RUN[0] == 1:
                if change_value == "yes":
                    self.register[0xffff].RUN[0] = 0
                    self.write_register(0xffff)
                    self.run_status_label.config(text="SLEEP")
                    self.run_status_label.config(bg="blue")
                else:
                    self.run_status_label.config(text="RUN")
                    self.run_status_label.config(bg="green")
            else:
                print "Error"

    def run_scurve(self, production="no"):
        print "\n*************************"
        print "* Starting S-curve test.\n"
        if production == "no":
            configuration = "yes"
        else:
            configuration = "no"
        prod_error = 0
        error = 0
        self.start_channel = int(self.start_ch_entry.get())
        error += self.check_value_range("Start channel", self.start_channel, 0, 127)
        self.stop_channel = int(self.stop_ch_entry.get())
        error += self.check_value_range("Stop channel", self.stop_channel, 0, 127)
        if self.stop_channel < self.start_channel:
            print "Stop channel should be higher than start channel."
            error += 1
        self.channel_step = int(self.ch_step_entry.get())
        error += self.check_value_range("Channel Step Size", self.channel_step, 0, 127)
        self.delay = int(self.delay_entry.get())
        error += self.check_value_range("Delay", self.delay, 0, 4000)
        self.interval = int(self.interval_entry.get())
        error += self.check_value_range("Interval", self.interval, 0, 4000)
        self.pulsestretch = int(self.pulsestretch_entry.get())
        error += self.check_value_range("Pulse Stretch", self.pulsestretch, 0, 7)
        self.latency = int(self.latency_entry.get())
        error += self.check_value_range("Latency", self.latency, 0, 1023)
        self.calphi = int(self.calphi_entry.get())
        error += self.check_value_range("Cal Phi", self.calphi, 0, 7)
        self.arm_dac = int(self.arm_dac_entry.get())
        error += self.check_value_range("ARM_DAC", self.arm_dac, 0, 254)
        self.start_cal_dac = int(self.start_cal_dac_entry.get())
        error += self.check_value_range("Start CAL_DAC", self.start_cal_dac, 0, 254)
        self.stop_cal_dac = int(self.stop_cal_dac_entry.get())
        error += self.check_value_range("Stop CAL_DAC", self.stop_cal_dac, 0, 254)
        if self.stop_cal_dac < self.start_cal_dac:
            print "Stop CAL_DAC should be higher than start CAL_DAC."
            error += 1
        if (self.stop_cal_dac - self.start_cal_dac) > 40:
            print "Max CAL_DAC steps is 40."
            error += 1
        if error == 0:
            text = "->Running S-curve\n"
            self.add_to_interactive_screen(text)
            output = scurve_all_ch_execute(self, "S-curve", arm_dac=self.arm_dac, ch=[self.start_channel,
                                           self.stop_channel], ch_step=self.channel_step, configuration=configuration,
                                           dac_range=[self.start_cal_dac, self.stop_cal_dac],
                                           bc_between_calpulses=self.interval, pulsestretch=self.pulsestretch,
                                           latency=self.latency, cal_phi=self.calphi)
            if output[0] == 'n':
                errors = ['r']
            else:
                errors = [0] * 3
                errors[0] = self.check_selection_criteria(len(output[2]), lim_Noisy_Channels, "Noisy Channels")
                errors[1] = self.check_selection_criteria(len(output[4]), lim_Dead_Channels, "Dead Channels")
                problematic_channels = len(output[2]) + len(output[4]) + len(output[6])
                errors[1] = self.check_selection_criteria(problematic_channels, lim_Problematic_Channels, "Problematic Channels")
                errors[2] = self.check_selection_criteria(output[5], lim_Mean_enc, "Noise")
            if 'y' in errors:
                prod_error = 'y'
            if 'r' in errors:
                prod_error = 'r'
        else:
            print "Aborting s-curve run."
        print "\n*************************"
        return prod_error

    def set_fe_nominal_values(self, chip="VFAT3b"):
        if chip == "VFAT3a":
            print "Setting FE biasing for VFAT3a"
            register[141].PRE_I_BSF[0] = 13
            register[141].PRE_I_BIT[0] = 150
            register[142].PRE_I_BLCC[0] = 25
            register[142].PRE_VREF[0] = 86
            register[143].SH_I_BFCAS[0] = 250
            register[143].SH_I_BDIFF[0] = 150
            register[144].SD_I_BDIFF[0] = 255
            register[145].SD_I_BSF[0] = 15
            register[145].SD_I_BFCAS[0] = 255
        elif chip == "VFAT3b":
            print "Setting FE biasing for VFAT3b"
            register[141].PRE_I_BSF[0] = 13
            register[141].PRE_I_BIT[0] = 150
            register[142].PRE_I_BLCC[0] = 25
            register[142].PRE_VREF[0] = 86
            register[143].SH_I_BFCAS[0] = 130
            register[143].SH_I_BDIFF[0] = 80
            register[144].SD_I_BDIFF[0] = 140
            register[145].SD_I_BSF[0] = 15
            register[145].SD_I_BFCAS[0] = 135

        self.write_register(141)
        time.sleep(0.02)
        self.write_register(142)
        time.sleep(0.02)
        self.write_register(143)
        time.sleep(0.02)
        self.write_register(144)
        time.sleep(0.02)
        self.write_register(145)

    def run_concecutive_triggers(self):
        self.nr_trigger_loops = int(self.cont_trig_entry.get())
        concecutive_triggers(self, self.nr_trigger_loops)

    def test_bist(self):
        print "\n*******************"
        print "* Testing BIST.\n"
        start = time.time()
        error = 0
        output = self.interfaceFW.run_bist()
        if output[0] != 'Error':
            data3 = int(output[3], 16) << 24
            data2 = int(output[2], 16) << 16
            data1 = int(output[1], 16) << 8
            data0 = int(output[0], 16)
            bist_value_int = data3 + data2 + data1 + data0
            print "BIST: %i" % bist_value_int
            if self.database:
                self.database.save_bist(bist_value_int)
            error = self.check_selection_criteria(bist_value_int, lim_BIST, "BIST")
        else:
            print "Communication error."
            error = 'r'
        stop = time.time()
        run_time = (stop - start)
        print "\nBIST test routine time: %f sec" % run_time
        print "*******************"
        print ""
        return error

    def test_scan_chain(self):
        if self.database:
            self.database.save_scanchain()
        return 1

    def check_selection_criteria(self, value,  lim, name):
        result = 0
        if value < lim[0] or value > lim[1]:
            result = 'y'
            if lim[2] != 'n':
                if value < lim[2] or value > lim[3]:
                    result = "r"
                    print "%s result is RED." % name
                    timestamp = time.strftime("%Y:%m:%d:%H:%M")
                    with open('production_error.log', 'a') as outfile:
                        outfile.write('%s Hybrid:%s Test:%s is red with value: %s\n' % (timestamp, self.database.name, name, value))
                else:
                    print "%s result is YELLOW." % name
                    timestamp = time.strftime("%Y:%m:%d:%H:%M")
                    with open('production_error.log', 'a') as outfile:
                        outfile.write('%s Hybrid:%s Test:%s is yellow with value: %s\n' % (
                        timestamp, self.database.name, name, value))
            else:
                print "%s result is YELLOW." % name
                timestamp = time.strftime("%Y:%m:%d:%H:%M")
                with open('production_error.log', 'a') as outfile:
                        outfile.write('%s Hybrid:%s Test:%s is yellow with value: %s\n' % (timestamp, self.database.name, name, value))
        else:
            print "%s result is GREEN." % name
        return result

    def run_production_tests(self):
        os.system('clear')
        print ""
        print ""
        print ""
        print "***************************************"
        print "Starting production test. "
        print "***************************************"
        start = time.time()
        test_aborted = 0
        result = ['g'] * len(self.tests)
        self.clear_interactive_screen()
        self.save_barcode()
        if self.tti_if:
            self.tti_if.set_outputs_off()
            self.tti_if.set_ch1_current_limit(0.5)
            self.tti_if.set_ch2_current_limit(0.5)
            self.tti_if.set_ch1_voltage(3)
            self.tti_if.set_ch2_voltage(3)
            self.tti_if.set_outputs_on()
            result[0] = self.check_short_circuit()
        else:
            result[0] = 0
        if result[0] == 0:
            self.unset_calibration_variables()
            if not self.iref_mode:
                result[1] = self.test_bist()
                result[2] = self.send_reset()
                print "reset result"
                print result[2]
                if result[2] == 0:
                    self.read_hw_id()
                    result[3] = self.test_registers(production="yes")
                    result[4] = self.burn_chip_id(chip_id=self.database.name)
                    result[6] = self.measure_power('SLEEP')
                    result[5] = self.adjust_iref(production="yes")
                    result[7] = self.adc_calibration(production="yes")
                    if result[7] == 0 or result[7] == 'y':
                        result[8] = self.calibrate_temperature()
                        result[9] = self.scan_cal_dac_fc(production="yes")
                        result[10] = test_data_packets(self, save_result="no")
                        result[11] = self.test_trigger_outputs(production='yes')
                        result[12] = self.run_all_dac_scans(production="yes")
                        if result[9] == 0:
                            #self.send_reset()
                            result[13] = self.run_scurve(production="yes")
                        else:
                            print "S-curves are not run due to errors in data packets."
                    else:
                        print "Internal ADCs broken. Abort production test."
                else:
                    text = "->Production test aborted.\n"
                    # self.add_to_interactive_screen(text)
                    print text
            else:
                result = ['1'] * len(self.tests)
                result[2] = self.send_reset()
                if result[2] == 0:
                    result[5] = self.adjust_iref(production="yes")

                    self.database.save_location(self.location_entry.get())
                else:
                    print "Aborting test."
        else:
            print "Production test aborted."
            test_aborted = 0
        if not test_aborted:
            stop = time.time()
            duration = (stop - start) / 60
            self.register[0xffff].RUN[0] = 0
            self.write_register(0xffff)
            if self.tti_if:
                self.tti_if.set_outputs_off()

            print "Errors:"
            print result
            print "Duration of the production test: %f min" % duration
            if self.pilot_run_flag:
                for i, value in enumerate(result):
                    if value == 'y':
                        self.test_label[i].config(bg='yellow')
                        print "Yellow result in: %s" % self.tests[i]
                    elif value == 'g':
                        self.test_label[i].config(bg=self.default_bg_color)
                    elif value != 0:
                        self.test_label[i].config(bg='red')
                        print "Red result in: %s" % self.tests[i]
                    else:
                        self.test_label[i].config(bg='green')
                hybrid_browser(self.database.name)
            else:
                print ""
                print "**************"
                print "Error report:\n"
                report_text = ""
                for i, value in enumerate(result):
                    if value == 'y':
                        report_text += "Yellow result in: %s\n" % self.tests[i]
                    elif value == 'g':
                        pass
                    elif value != 0:
                        report_text += "Red result in: %s\n" % self.tests[i]
                if report_text == "":
                    print "Empty\n"
                else:
                    print report_text
                print "**************"
                print ""

                test_result = 'green'
                if 'y' in result:
                    test_result = 'yellow'
                if 'r' in result:
                    test_result = 'red'
                if 1 in result:
                    test_result = 'red'
                for label in self.test_label:
                    label.config(bg=test_result)

                if not self.iref_mode:
                    self.test_label[3].config(text='Hybrid:')
                    self.test_label[4].config(text=self.database.name)
                    self.update_statistics(test_result)
                    if self.database:
                        if not self.database.error:
                            self.database.save_state(test_result)
                else:
                    self.test_label[3].config(text='Iref adjusted for:')
                    self.test_label[4].config(text=self.database.name)
            self.barcode_entry.delete(0, END)
            self.unset_calibration_variables()

            if self.beep_mode == 1:
                print "\a"
            print "***************************************"
            print "Finished production test for the %s" % self.database.name
            print "***************************************"
        else:
            if self.tti_if:
                self.tti_if.set_outputs_off()


    def read_hw_id(self):
        print "\n*******************"
        print "* Reading hw_id.\n"
        value = self.read_register(0x10001, save_value='no')
        value = ''.join(str(e) for e in value)
        if self.database:
            self.database.save_hw_id_ver(int(value, 2))
        print "*******************"
        print ""

# ################# SCAN/TEST -FUNCTIONS #############################

    def update_statistics(self, result):
        filename = "./data/production_statistics.data"
        with open(filename, 'r') as read_file:
            lines = read_file.readlines()
            title = lines[0]
            values = lines[1].split(" ")
            total = int(values[0]) + 1
            green = int(values[1])
            yellow = int(values[2])
            red = int(values[3])
            if result == 'green':
                green += 1
            elif result == 'yellow':
                yellow += 1
            elif result == 'red':
                red += 1
        text = "%s%i %i %i %i" % (title, total, green, yellow, red)
        with open(filename, 'w') as write_file:
            write_file.write(text)

    def run_full_calibration(self):
        start = time.time()

        self.adjust_iref()
        self.adc_calibration(production="no")
        self.scan_cal_dac_fc(production="no")
        self.calibrate_temperature(production="no")

        stop = time.time()
        duration = (stop - start)

        self.irefc_label0.config(text="%i" % self.register[134].Iref[0])
        self.adc0c_label0.config(text="%0.2f %0.1f" % (self.adc0M, self.adc0B))
        self.adc1c_label0.config(text="%0.2f %0.1f" % (self.adc1M, self.adc1B))
        self.cal_dacc_label0.config(text="%0.2f %0.3f" % (self.cal_dac_fcM, self.cal_dac_fcB))
        self.temp_coeff_label0.config(text="K1:%0.2f K2:%0.2f" % (self.temperature_k1, self.temperature_k2))

        print "Duration of the full calibration: %f sec" % duration

    def write_chip_id(self):
        #self.increment_chip_id()
        return 1

    def burn_chip_id(self, chip_id=""):
        print "\n*******************"
        print "* Burning Chip ID.\n"
        start = time.time()
        error = 0
        if self.burn_mode == 1 and self.pilot_run_flag == 0:
            print "Register value before:"
            reg_value = self.read_register(0x10003)
            print reg_value
            if self.register[0x10003].CHIP_ID[0] == 0:
                self.register[0x10004].PRG_TIME[0] = 2000
                chip_id_bin = dec_to_bin_with_stuffing(chip_id, 32)
                print chip_id
                print "Binary:"
                print chip_id_bin
                if self.chipid_encoding_mode:
                    rm = reedmuller.ReedMuller(2, 5)
                    chip_id_bin_rm = rm.encode(chip_id_bin[-16:])
                    chip_id = int(''.join(map(str, chip_id_bin_rm)), 2)
                    print "Reed-Muller encoded:"
                    print chip_id_bin_rm
                    chip_id_bin = chip_id_bin_rm
                chip_id_bin.reverse()  # to use it in the for-loop.
                print chip_id
                print chip_id_bin
                for i, bit in enumerate(chip_id_bin):
                    if bit == 1:
                        time.sleep(0.1)
                        print ""
                        print i
                        self.register[0x10004].PRG_BIT_ADD[0] = i
                        data = []
                        for x in register[0x10004].reg_array:
                            data.extend(dec_to_bin_with_stuffing(x[0], x[1]))
                        print data
                        self.write_register(0x10004)
                print "Register value after:"
                print self.read_register(0x10003)
                if self.register[0x10003].CHIP_ID[0] == chip_id:
                    print "Chip ID burn was success."
                else:
                    print "Wrong Chip ID was burned."
                    print "Read chip ID: %s" % self.register[0x10003].CHIP_ID[0]
                    print "Written chip ID: %s" % chip_id
                    error = 'r'
            else:
                print "Chip id has already been burned."
                print "Register value:"
                print self.read_register(0x10003)
                error = 0
        else:
            print "No Chip ID burn -mode has been selected. No Chip ID was burned."
            error = 'r'
        stop = time.time()
        run_time = (stop - start)
        print "\nChip ID burning routine time: %f sec" % run_time
        print "*******************"
        print ""
        return error

    def read_lot_information(self):
        with open('./data/lot_info.dat', 'r') as f:
            line = f.readline()
            info = line.split()
            self.lot_nr = int(info[0])
            self.arrival_date = info[1]
            print "Lot info:"
            print self.lot_nr
            print self.arrival_date

    def save_barcode(self):
        error = 0
        print "\n*******************"
        print "* Reading the barcode.\n"
        if self.barcode_entry.get() != "":
            try:
                barcode = self.barcode_entry.get()
                if len(barcode) > 5:
                    print "Detected a long barcode: %s" % barcode
                    barcode = barcode[-5:]
                    print "Using only four digits: %s" % barcode
                barcode_value = int(barcode)
            except Exception as e:
                print(e)
                text = "Invalid barcode.\n"
                self.add_to_interactive_screen(text)
                error = 1
            if error == 0:
                print "Chip ID to be used: %s" % barcode_value
                #self.database.save_barcode(barcode_value)
                self.database = DatabaseInterface(barcode_value)
                self.database.update_values = self.db_mode
                self.database.save_date()
                self.database.save_arrival(self.arrival_date)
                self.database.save_lot(self.lot_nr)
                if not self.database.error:
                    if self.database.id_exists:
                        if not self.iref_mode:
                            result = tkMessageBox.askyesno("Barcode/Chip_ID found", "Would you like to re-run production tests for hybrid nr. %i" % barcode_value)
                            time.sleep(1)
                            if not result:
                                error = 1
                            else:
                                self.database.save_location(hybrid_location)
                    #text = "Read barcode: %s\n" % barcode_value
                    #self.add_to_interactive_screen(text)
                else:
                    error = 1
        else:
            print "No barcode scanned."
            error = 1
        print "*******************"
        print ""
        return error

    def test_registers(self, production="no"):
        print "\n*******************"
        print "* Testing the VFAT3 Slow Control registers.\n"
        if production == "no":
            timestamp = time.strftime("%Y%m%d_%H%M")
            output_file = "%s/register_test/%s_register_test.dat" % (self.data_folder, timestamp)
            if not os.path.exists(os.path.dirname(output_file)):
                try:
                    os.makedirs(os.path.dirname(output_file))
                except OSError as exc:  # Guard against race condition
                    print "Unable to create directory"
            open(output_file, 'w').close()
        temp_file = "./data/temp_register_file.reg"
        self.save_register_values_to_file_execute(temp_file)
        # Write max values to registers and read them back.
        filename = "./data/max_register_values.reg"
        error_counter = 0
        start = time.time()
        result = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.rstrip('\n')
                line = line.split(",")
                reg_nr = int(line[0])
                write_data = line[1]
                self.register[reg_nr].change_values(write_data)
                self.write_register(reg_nr)
                time.sleep(0.015)
                read_data = self.read_register(reg_nr)
                read_data = ''.join(str(e) for e in read_data[16:])
                if read_data == write_data:
                    line = "Register: %d. Write/Read ok." % reg_nr
                    print line
                    result.append(line)
                else:
                    line = "Register: %d. Write/Read error." % reg_nr
                    print line
                    result.append(line)
                    print write_data
                    print read_data
                    error_counter += 1
        line = "Write/Read test done. %d bad registers found." % error_counter
        print line
        if self.database:
            self.database.save_register_test(error_counter)

        result.append(line)

        result.append(line)
        if production == "no":
            with open(output_file, "a") as myfile:
                for line in result:
                    myfile.write("%s\n" % line)
        # print "Writing back previous register values."
        self.load_register_values_from_file_execute(temp_file, multiwrite=0)
        self.send_reset()
        print "Done"
        stop = time.time()
        run_time = (stop - start)
        line = "Run time (sec): %f\n" % run_time
        print line
        result = self.check_selection_criteria(error_counter, lim_Register_Test, "Register Test")
        print "*******************"
        print ""
        return result

    def write_register(self, register_nr, data=""):
        if data == "":
            data = []
            for x in register[register_nr].reg_array:
                data.extend(dec_to_bin_with_stuffing(x[0], x[1]))
            #data.reverse()
            #data_str = ''.join(str(e) for e in data)
        self.interfaceFW.write_register(register_nr, data)

    def generate_routine(self):
            text =  "->Generating the scan instruction file: %s\n" % self.chosen_scan
            self.add_to_interactive_screen(text)
            scan_name = self.chosen_scan
            modified = scan_name.replace(" ", "_")
            output = generator(scan_name, self.write_BCd_as_fillers, self.register)

            if self.verbose_var.get() == 1:
                for i in output[0]:
                    self.add_to_interactive_screen(i)
                    self.add_to_interactive_screen("\n")
            print output[2]
            text = "Lines: %d, Size:%d kb, Duration: %d BC, %f ms.\n" %(output[2][0], output[2][1], output[2][2], output[2][3])
            self.add_to_interactive_screen("Generated file:\n")
            self.add_to_interactive_screen(text)

    def run_routine(self):
        text = "->Running the scan: %s\n" % self.chosen_scan
        self.add_to_interactive_screen(text)
        scan_name = self.chosen_scan
        scan_nr = self.scan_options_value[self.scan_options.index(scan_name)]
        dac_size = self.dac_sizes[self.scan_options.index(scan_name)]
        print scan_name
        print scan_nr
        print dac_size
        scan_execute(self, scan_name, scan_nr, dac_size)

    def counter_resets_execute(self, scan_name):
        modified = scan_name.replace(" ", "_")
        file_name = "./routines/%s/FPGA_instruction_list.txt" % modified
        output = self.interfaceFW.launch(register, file_name, self.COM_port)
        if output[0] == "Error":
            text = "%s: %s\n" % (output[0], output[1])
            self.add_to_interactive_screen(text)
        else:
            text = "Received Packets:\n"
            self.add_to_interactive_screen(text)
            text = "SystemBC|EC|BC\n"
            self.add_to_interactive_screen(text)

            for i in output[1]:
                text = "%d|%d|%d\n" %(i.systemBC, i.EC, i.BC)
                self.add_to_interactive_screen(text)

    def modify_scan(self):
        text =  "->Modifying the scan: %s\n" % self.chosen_scan
        self.add_to_interactive_screen(text)
        scan_name = self.chosen_scan
        modified = scan_name.replace(" ", "_")
        file_name = "./routines/%s/instruction_list.txt" % modified
        proc = subprocess.Popen(['gedit', file_name])

    def choose_scan(self, value):
       self.chosen_scan = value
       if self.chosen_scan == "S-curve all ch" or self.chosen_scan == "S-curve all ch cont." or self.chosen_scan == "CAL_DAC scan, fC":
           self.modify_button.config(state="disabled")
           self.generate_button.config(state="disabled")
       else:
           self.modify_button.config(state="normal")
           self.generate_button.config(state="normal")

# ####################### FCC-TAB FUNCTIONS ##########################

    def send_fcc(self, command, verbose="yes"):
        text = "->Sending %s.\n" % command
        self.add_to_interactive_screen(text)
        command_encoded = FCC_LUT[command]
        output = self.interfaceFW.send_fcc(command_encoded)
        print output[0]
        if output[0] == '0x1e':
            i = 0
            for byte in output:
                if i == 4:
                    data_bit = dec_to_bin_with_stuffing(int(byte, 16), 8)
                    print ''.join(str(e) for e in data_bit)
                    i = 0
                i += 1
        return output

    def run_all_dac_scans(self, production="no"):
        print "\n*************************"
        print "* Running all DAC scans.\n"
        error = 0
        errors = []
        if production == "no":
            save_data = 1
        else:
            save_data = 0
        start = time.time()
        for scan in self.scan_options:
            time.sleep(0.05)
            print "\nRunning %s" % scan
            scan_nr = self.scan_options_value[self.scan_options.index(scan)]
            dac_size = self.dac_sizes[self.scan_options.index(scan)]
            output = scan_execute(self, scan, scan_nr, dac_size, save_data)
            if output != 'Error':
                errors.append(self.check_selection_criteria(output[0][-1], adc0_dac_selection_criteria_lut[scan[:-5]], scan))
            else:
                print "Error, Scan could not be performed."
                errors.append('r')
        stop = time.time()
        run_time = (stop - start)
        print "\nRuntime: %f s" % run_time
        if 'y' in errors:
            error = 'y'
        if 'r' in errors:
            error = 'r'
        print "*************************"
        print ""
        return error


    def run_xray_tests(self):
        while True:
            timestamp = time.strftime("%Y%m%d%H%M")
            if self.xray_routine_flag == 0:
                folder = "%s/%sresults/" % (self.data_folder, timestamp)
            else:
                folder = "%s/%sresults/" % (self.data_folder[:-20], timestamp)
            self.data_folder = folder
            self.xray_routine_flag = 1
            self.run_all_dac_scans()
            scurve_all_ch_execute(self, "S-curve", arm_dac=100, ch=[0, 127], configuration="yes",
                                              dac_range=[200, 240], delay=50, bc_between_calpulses=2000, pulsestretch=7,
                                             latency=45, cal_phi=0)
            gain_measurement(self, adc="int1")
            concecutive_triggers(self, 25)
            time.sleep(2100)
            #time.sleep(30)

# ######################## REGISTER-TAB FUNCTIONS ####################

    def apply_register_values(self):
        if self.register_mode == 'r':
            text = "The register is read only\n"
            self.add_to_interactive_screen(text)
        elif self.value == "Front End Settings":
            text = "->Setting the Front End DAC registers \n"
            self.add_to_interactive_screen(text)
            j = 0
            for i in self.register_names:

                new_value = int(self.entry[j].get())
                try:
                    key = LUT[i]
                except ValueError:
                    text =  "-IGNORED: Invalid value for Register: %s" % i
                    self.add_to_interactive_screen(text)
                    continue
                addr = key[0]
                variable = key[1]
                size = register[addr].reg_array[variable][1]
                if new_value < 0 or new_value > 2**(size)-1:
                    text = "-IGNORED: Value out of the range of the register: %d \n" % new_value
                    self.add_to_interactive_screen(text)
                else:
                    register[addr].reg_array[variable][0] = new_value
                    text = "Register: %s Value: %s \n" % (i,new_value)
                    self.add_to_interactive_screen(text)
                j += 1

            data = []
            for x in register[131].reg_array:
                data.extend(dec_to_bin_with_stuffing(x[0], x[1]))
            data.reverse()

            output = self.SC_encoder.create_SC_packet(131, data, "WRITE", 0)
            paketti = output[0]
            write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
            for x in range(1, len(paketti)):
                write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
            self.execute(verbose="yes")

            filler_16bits = [0]*16
            full_data = []
            data = []
            data_intermediate = []
            for x in register[141].reg_array:
                data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
                data.extend(data_intermediate)
            data.reverse()
            data.extend(filler_16bits)
            print data
            full_data.extend(data)

            data = []
            data_intermediate = []
            for x in register[142].reg_array:
                data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
                data.extend(data_intermediate)
            data.reverse()
            data.extend(filler_16bits)
            print data
            full_data.extend(data)

            data = []
            data_intermediate = []
            for x in register[143].reg_array:
                data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
                data.extend(data_intermediate)
            data.reverse()
            data.extend(filler_16bits)
            print data
            full_data.extend(data)

            data = []
            data_intermediate = []
            for x in register[144].reg_array:
                data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
                data.extend(data_intermediate)
            data.reverse()
            data.extend(filler_16bits)
            print data
            full_data.extend(data)

            data = []
            data_intermediate = []
            for x in register[145].reg_array:
                data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
                data.extend(data_intermediate)
            data.reverse()
            data.extend(filler_16bits)
            print data
            full_data.extend(data)

            output = self.SC_encoder.create_SC_packet(141,full_data,"MULTI_WRITE",0)
            paketti = output[0]
            write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
            for x in range(1, len(paketti)):
                write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
            self.execute(verbose="yes")
            
        else:
            text = "->Setting the register: %s \n" % self.value
            self.add_to_interactive_screen(text)
            j = 0
            for i in self.register_names:
                new_value = int(self.entry[j].get())
                try:
                    key = LUT[i]
                except ValueError:
                    text = "-IGNORED: Invalid value for Register: %s" % i
                    self.add_to_interactive_screen(text)
                    continue
                addr = key[0]
                variable = key[1]
                size = register[addr].reg_array[variable][1]
                if new_value < 0 or new_value > 2**(size)-1:
                    text = "-IGNORED: Value out of the range of the register: %d \n" % new_value
                    self.add_to_interactive_screen(text)
                else:
                    register[addr].reg_array[variable][0] = new_value
                    text = "Register: %s Value: %s \n" % (i,new_value)
                    self.add_to_interactive_screen(text)
                j += 1
            self.write_register(addr)

    def change_channel(self):
        chosen_register = int(self.channel_entry.get())
        if chosen_register >= 0 and chosen_register <= 128:
            self.channel_register = chosen_register
        else:
            text = "Channel value: %d is out of limits. Channels are 0-128 \n" % chosen_register
            self.add_to_interactive_screen(text)
        self.update_registers("Channels")

    def new_change_channel(self):
        chosen_register = int(self.channel_entry.get())
        if chosen_register >= 0 and chosen_register <= 128:
            self.channel_register = chosen_register
        else:
            text = "Channel value: %d is out of limits. Channels are 0-128 \n" % chosen_register
            self.add_to_interactive_screen(text)
        self.channel_entry.delete(0, END)
        self.channel_entry.insert(0, self.channel_register)

    def update_registers(self, value):
        self.value = value
        self.channel_label.grid_forget()
        self.channel_entry.grid_forget()
        self.channel_button.grid_forget()

        if self.value == "Channels":
            self.register_mode = 'rw'
            register_nr = 0
            description = "Settings for the channels."
            cal = "cal%d" % self.channel_register
            mask = "mask%d" % self.channel_register
            zcc_dac = "zcc_dac%d" % self.channel_register
            arm_dac = "arm_dac%d" % self.channel_register
            self.register_names = [cal, mask, zcc_dac, arm_dac]

            self.channel_label.grid(column=0, row=0, sticky='e')
            self.channel_entry.grid(column=1, row=0, sticky='e')
            self.channel_entry.delete(0, END)
            self.channel_entry.insert(0, self.channel_register)
            self.channel_button.grid(column=2, row=0, sticky='e')

        elif self.value == "Control Logic":
            self.register_mode = 'rw'
            register_nr = 129
            description = "Settings for the control logic."
            self.register_names = ["PS", "SyncLevelEnable", "ST", "DDR"]

        elif self.value == "Data Packet":
            self.register_mode = 'rw'
            register_nr = 130
            description = "Settings for the data packets."
            self.register_names = ["P16", "PAR", "DT", "SZP", "SZD", "TT", "ECb", "BCb"]

        elif self.value == "Front End":
            self.register_mode = 'rw'
            register_nr = 131
            description = "Settings for the Front End."
            self.register_names = ["TP_FE", "RES_PRE", "CAP_PRE"]

        elif self.value == "CFD":
            self.register_mode = 'rw'
            register_nr = 132
            description = "Settings for the CFD."
            self.register_names = ["PT", "EN_HYST", "SEL_POL", "Force_En_ZCC", "Force_TH", "SEL_COMP_MODE"]

        elif self.value == "Monitoring":
            self.register_mode = 'rw'
            register_nr = 133
            description = "Settings for the Monitoring."
            self.register_names = ["VREF_ADC", "Mon_Gain", "Monitor_Sel"]

        elif self.value == "Global reference current":
            self.register_mode = 'rw'
            register_nr = 134
            description = "Tuning of the global reference current."
            self.register_names = ["Iref"]

        elif self.value == "Global Threshold":
            self.register_mode = 'rw'
            register_nr = 135
            description = "Settings for the global thresholds."
            self.register_names = ["ZCC_DAC", "ARM_DAC"]

        elif self.value == "Global Hysteresis":
            self.register_mode = 'rw'
            register_nr = 136
            description = "Setting of the global hysteresis."
            self.register_names = ["HYST_DAC"]

        elif self.value == "Latency":
            self.register_mode = 'rw'
            register_nr = 137
            description = "Setting of the Latency."
            self.register_names = ["LAT"]

        elif self.value == "Calibration 0":
            self.register_mode = 'rw'
            register_nr = 138
            description = "Settings for the Calibration Pulse."
            self.register_names = ["CAL_SEL_POL", "CAL_PHI", "CAL_EXT", "CAL_DAC", "CAL_MODE"]

        elif self.value == "Calibration 1":
            self.register_mode = 'rw'
            register_nr = 139
            description = "Settings for the Calibration Pulse."
            self.register_names = ["CAL_FS", "CAL_DUR"]

        elif self.value == "Biasing 0":
            self.register_mode = 'rw'
            register_nr = 140
            description = "Settings for the CFD biasing."
            self.register_names = ["CFD_DAC_2", "CFD_DAC_1"]

        elif self.value == "Biasing 1":
            self.register_mode = 'rw'
            register_nr = 141
            description = "Settings for the Front End biasing."
            self.register_names = ["PRE_I_BSF", "PRE_I_BIT"]

        elif self.value == "Biasing 2":
            self.register_mode = 'rw'
            register_nr = 142
            description = "Settings for the Front End biasing."
            self.register_names = ["PRE_I_BLCC", "PRE_VREF"]

        elif self.value == "Biasing 3":
            self.register_mode = 'rw'
            register_nr = 143
            description = "Settings for the Front End biasing."
            self.register_names = ["SH_I_BFCAS", "SH_I_BDIFF"]

        elif self.value == "Biasing 4":
            self.register_mode = 'rw'
            register_nr = 144
            description = "Settings for the Front End biasing."
            self.register_names = ["SD_I_BDIFF"]

        elif self.value == "Biasing 5":
            self.register_mode = 'rw'
            register_nr = 145
            description = "Settings for the Front End biasing."
            self.register_names = ["SD_I_BSF", "SD_I_BFCAS"]

        elif self.value == "Biasing 6":
            self.register_mode = 'rw'
            register_nr = 146
            description = "Settings for the SLVS biasing."
            self.register_names = ["SLVS_IBIAS", "SLVS_VREF"]

        elif self.value == "SLEEP/RUN":
            self.register_mode = 'rw'
            register_nr = 65535
            description = "Setting of the RUN-bit to switch between SLEEP- and RUN-mode."
            self.register_names = ["RUN"]

        elif self.value == "HW_ID_ID":
            self.register_mode = 'r'
            register_nr = 65536
            description = "Hardware ID."
            self.register_names = ["ID"]

        elif self.value == "HW_ID_VER":
            self.register_mode = 'r'
            register_nr = 65537
            description = "Hardware version."
            self.register_names = ["VER"]

        elif self.value == "HW_RW_REG":
            self.register_mode = 'rw'
            register_nr = 65538
            description = "GEneral purpose register."
            self.register_names = ["RW_REG"]

        elif self.value == "HW_CHIP_ID":
            self.register_mode = 'r'
            register_nr = 65539
            description = "ID number of the chip."
            self.register_names = ["CHIP_ID"]

        elif self.value == "Front End Settings":
            self.register_mode = 'rw'
            register_nr = "FED"
            description = "Front End related registers."
            self.register_names = ["TP_FE", "RES_PRE", "CAP_PRE", "PRE_I_BSF", "PRE_I_BIT", "PRE_I_BLCC", "PRE_VREF", "SH_I_BFCAS", "SH_I_BDIFF", "SD_I_BDIFF", "SD_I_BSF", "SD_I_BFCAS"]

        else:
            self.register_names = []

        for i in self.label:
            i.grid_forget()
        for i in self.entry:
            i.grid_forget()
        for i in self.range:
            i.grid_forget()
        del self.label[:]
        del self.entry[:]
        del self.range[:]
        self.description_label.grid_forget()
        self.separator.grid_forget()
        self.description_label = Label(self.register_data_frame, text=description, wraplength=250)
        self.description_label.grid(column=0, row=1, columnspan=2)
        self.separator = ttk.Separator(self.register_data_frame, orient='horizontal')
        self.separator.grid(column=0, row=2, columnspan=2, sticky='ew')
        if register_nr == "FED":
            text = "Reading the Front end DAC registers\n"
            self.add_to_interactive_screen(text)

            output = self.SC_encoder.create_SC_packet(131, 0, "READ", 0)
            paketti = output[0]
            write_instruction(self.interactive_output_file, 150, FCC_LUT[paketti[0]], 1)
            for x in range(1, len(paketti)):
                write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
            output = self.execute(verbose="yes")
            if output[0] == "Error":
                text = "%s: %s\n" %(output[0], output[1])
                self.add_to_interactive_screen(text)
                text = "Register values might be incorrect.\n"
                self.add_to_interactive_screen(text)
            else:
                print "Read data:"
                new_data = output[0][0].data
                print new_data
                new_data = ''.join(str(e) for e in new_data[-16:])
                register[131].change_values(new_data)

            output = self.SC_encoder.create_SC_packet(141, 0, "MULTI_READ", 0)
            paketti = output[0]
            print paketti
            write_instruction(self.interactive_output_file, 150, FCC_LUT[paketti[0]], 1)
            for x in range(1, len(paketti)):
                write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
            output = self.execute(verbose="yes")
            if output[0] == "Error":
                text = "%s: %s\n" % (output[0], output[1])
                self.add_to_interactive_screen(text)
                text = "Register values might be incorrect.\n"
                self.add_to_interactive_screen(text)
            else:
                new_data = output[0][0].data[0]
                new_data = ''.join(str(e) for e in new_data[-16:])
                register[141].change_values(new_data)
                new_data = output[0][0].data[1]
                new_data = ''.join(str(e) for e in new_data[-16:])
                register[142].change_values(new_data)
                new_data = output[0][0].data[2]
                new_data = ''.join(str(e) for e in new_data[-16:])
                register[143].change_values(new_data)
                new_data = output[0][0].data[3]
                new_data = ''.join(str(e) for e in new_data[-16:])
                register[144].change_values(new_data)
                new_data = output[0][0].data[4]
                new_data = ''.join(str(e) for e in new_data[-16:])
                register[145].change_values(new_data)

        else:
            text = "Reading the register: %d\n" % register_nr
            self.add_to_interactive_screen(text)

            self.read_register(register_nr)

        j = 0
        for i in self.register_names:
            try:
                key = LUT[i]
            except ValueError:
                print "-IGNORED: Invalid value for Register: %s" % i
                continue
            addr = key[0]
            variable = key[1]
            current_value = register[addr].reg_array[variable][0]
            self.label.append(Label(self.register_data_frame, text=i))
            self.label[j].grid(column=0, row=j+3, sticky='e')
            if register_nr in [65536, 65537, 65538, 65539]:
                entry_width = 12
            else:
                entry_width = 5
            self.entry.append(Entry(self.register_data_frame, width=entry_width))
            self.entry[j].grid(column=1, row=j+3, sticky='w')
            self.entry[j].insert(0, current_value)
            if self.register_mode == 'r':
                self.entry[j].config(state='disabled')
            size = register[addr].reg_array[variable][1]
            text = "(0 - %d)" % (2**size-1)
            self.range.append(Label(self.register_data_frame, text=text))
            self.range[j].grid(column=2, row=j+3, sticky='w')
            j += 1

root = Tk()
my_gui = VFAT3_GUI(root)

root.mainloop()


