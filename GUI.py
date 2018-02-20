############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################

import Tkinter, tkFileDialog, Tkconstants
from Tkinter import *
import ttk
import time
import sys
import os
import subprocess  # For opening scans for edit in the system default editor.
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/python_scripts_thomas/kernel")
from ipbus import *
from VFAT3_registers import *
from generator import *
from test_system_functions import *
from FW_interface import *
from DatabaseInterface import *
from routines import *
from calibration_routines import *
from tti_serial_interface import *


class VFAT3_GUI:
    def __init__(self, master):

        psu_mode = 1
        conn_mode = 1
        db_mode = 1

        # Communication mode selection.
        for arg in sys.argv:
            # print "sys.argv value: %s" % arg
            if arg == '-s':
                conn_mode = 0
            if arg == '-no_db':
                print "Entering no database-mode."
                self.chip_id = 'n/a'
                db_mode = 0
            if arg == '-no_psu':
                print "Entering no Power Supply-mode."
                psu_mode = 0

        if psu_mode == 1:
            self.tti_if = TtiSerialInterface()
            if self.tti_if.psu_found:
                print "Found Power Supply"
                print "Device ID:"
                print self.tti_if.req_device_id()
                self.tti_if.set_outputs_off()
                self.tti_if.set_ch1_current_limit(0.2)
                self.tti_if.set_ch2_current_limit(0.2)
                self.tti_if.set_ch1_voltage(1.2)
                self.tti_if.set_ch2_voltage(1.2)
            else:
                print "No Power Supply found"
        if conn_mode == 0:
            self.interfaceFW = FW_interface(1)  # 1 - Simulation mode
            self.mode = 1
        if conn_mode == 1:
            self.interfaceFW = FW_interface(0)  # 0 - IPbus mode
            self.mode = 0
        if db_mode == 1:
            self.read_chip_id()
            print "Using Hybrid: %s" % self.chip_id
        # Local variables.
        self.barcode_id = ""
        self.channel_register = 0
        self.value = ""
        self.write_BCd_as_fillers = 0
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

        # Initiations
        self.SC_encoder = SC_encode()
        self.register = register
        s = ttk.Style()
        s.configure('My.TFrame', background='white')
        self.master = master
        # self.master.wm_iconbitmap('/home/a0312687/VFAT3-TB-Software/data/LUT_logo.ico')
        self.master.title("GUI for the VFAT3 test system.")
        bwidth = 15
        self.master.minsize(width=680, height=450)
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

        self.sync_check_button = Button(self.misc_frame, text="Sync check", command=lambda: self.send_fcc("CC-B"), width=bwidth)
        self.sync_check_button.grid(column=1, row=2, sticky='e')

        self.idle_button = Button(self.misc_frame, text="SC Idle character", command=lambda: self.send_idle(), width=bwidth)
        self.idle_button.grid(column=1, row=3, sticky='e')

        self.close_button = Button(self.misc_frame, text="Read int. ADCs", command=lambda: self.read_adcs(), width=bwidth)
        self.close_button.grid(column=1, row=4, sticky='e')

        self.cal_button = Button(self.misc_frame, text="Read ext. ADC", command=lambda: self.ext_adc(), width=bwidth)
        self.cal_button.grid(column=1, row=5, sticky='e')

        self.CalPulse_LV1A_button = Button(self.misc_frame, text="CalPulse+LV1A", command=self.send_cal_trigger, width=bwidth)
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


        # ADD TABS
        self.nb.add(self.FCC_frame, text="FCC")
        self.nb.add(self.register_frame, text="Registers")
        self.nb.add(self.misc_frame, text="misc.")

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
                #"CAL_DAC scan, fC",
                # "Counter Resets"
                # "S-curve",
                # "S-curve all ch",
                # "S-curve all ch cont."
                ]
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

        self.modify_button = Button(self.scan_button_frame, text="Modify", command=self.modify_scan)
        self.modify_button.grid(column=0, row=0)
        self.generate_button = Button(self.scan_button_frame, text="Generate", command=self.generate_routine)
        self.generate_button.grid(column=1, row=0)
        self.run_button = Button(self.scan_button_frame, text="RUN", command=self.run_routine)
        self.run_button.grid(column=2, row=0)

        # ###############CALIBRATION TAB #######################################

        self.cal_button = Button(self.calibration_frame, text="Adjust Iref", command=lambda: iref_adjust(self), width=bwidth)
        self.cal_button.grid(column=1, row=0, sticky='e')

        self.adc_calibration_button = Button(self.calibration_frame, text="ADC calibration", command=lambda: adc_calibration(self), width=bwidth)
        self.adc_calibration_button.grid(column=1, row=1, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="CAL_DAC to fC", command=lambda: scan_cal_dac_fc(self, "CAL_DAC scan, fC"), width=bwidth)
        self.cal_button.grid(column=1, row=2, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Save Calibration", command=lambda: self.save_calibration_values_to_file(), width=bwidth)
        self.cal_button.grid(column=1, row=3, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Load Calibration", command=lambda: self.load_calibration_values_from_file(filename="/home/a0312687/cernbox/Hybrid_tests/hbrdnp026/calibration/20171114_1416calibration.dat"), width=bwidth)
        self.cal_button.grid(column=2, row=3, sticky='e')

        self.FE_button = Button(self.calibration_frame, text="Set FE nominal values", command=lambda: self.set_fe_nominal_values(), width=bwidth)
        self.FE_button.grid(column=1, row=4, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Channel Calibration", command=lambda: adjust_local_thresholds(self), width=bwidth)
        self.cal_button.grid(column=1, row=5, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Apply ch. Calibration", command=lambda: self.apply_ch_local_adjustments(), width=bwidth)
        self.cal_button.grid(column=2, row=5, sticky='e')

#        self.cal_button = Button(self.calibration_frame, text="Gain measurement", command=lambda: gain_measurement(self), width=bwidth)
#        self.cal_button.grid(column=1, row=6, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Gain per channel", command=lambda: gain_histogram(self), width=bwidth)
        self.cal_button.grid(column=1, row=6, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Save registers", command=lambda: self.save_register_values_to_file(), width=bwidth)
        self.cal_button.grid(column=1, row=11, sticky='e')

        self.cal_button = Button(self.calibration_frame, text="Load registers", command=lambda: self.load_register_values_from_file(), width=bwidth)
        self.cal_button.grid(column=2, row=11, sticky='e')



        # ###############Routines-TAB #######################################

        self.Trig1_set_button = Button(self.routines_frame, text="Set s-bit pattern", command=lambda: set_up_trigger_pattern(self, 0), width=bwidth)
        self.Trig1_set_button.grid(column=1, row=7, sticky='e')

        self.Trig_clear_button = Button(self.routines_frame, text="Clear s-bit pattern", command=lambda: set_up_trigger_pattern(self, 2), width=bwidth)
        self.Trig_clear_button.grid(column=1, row=8, sticky='e')

        self.cont_trig_button = Button(self.routines_frame, text="Continuous CalPulses", command=lambda: continuous_trigger(self), width=bwidth)
        self.cont_trig_button.grid(column=1, row=9, sticky='e')

        self.cal_button = Button(self.routines_frame, text="Production test",
                                 command=lambda: self.run_production_tests(), width=bwidth)
        self.cal_button.grid(column=1, row=10, sticky='e')

        self.cont_trig_button = Button(self.routines_frame, text="Test data packets", command=lambda: self.run_concecutive_triggers(), width=bwidth)
        self.cont_trig_button.grid(column=1, row=11, sticky='e')

        self.nr_trigger_loops = 25

        self.cont_trig_entry = Entry(self.routines_frame, width=5)
        self.cont_trig_entry.grid(column=3, row=11, sticky='e')
        self.cont_trig_entry.insert(0, self.nr_trigger_loops)

        self.cont_trig_label0 = Label(self.routines_frame, text="loops")
        self.cont_trig_label0.grid(column=4, row=11, sticky='e')

        self.cont_trig_button = Button(self.routines_frame, text="Scan all DACs", command=lambda: self.run_all_dac_scans(), width=bwidth)
        self.cont_trig_button.grid(column=1, row=12, sticky='e')

        self.cal_button = Button(self.routines_frame, text="W/R all registers", command=lambda: self.test_registers(), width=bwidth)
        self.cal_button.grid(column=1, row=13, sticky='e')

        self.cal_button = Button(self.routines_frame, text="X-ray routine cont", command=lambda: self.run_xray_tests(), width=bwidth)
        self.cal_button.grid(column=1, row=14, sticky='e')

        self.data_dir_label0 = Label(self.routines_frame, text="Data directory:")
        self.data_dir_label0.grid(column=1, row=15, sticky='w')

        self.data_dir_entry = Entry(self.routines_frame, width=18)
        self.data_dir_entry.grid(column=1, row=15, sticky='w')
        self.data_dir_entry.insert(0, self.data_folder)

        self.cont_trig_button = Button(self.routines_frame, text="Browse", command=lambda: self.ask_directory(), width=5)
        self.cont_trig_button.grid(column=3, row=15, sticky='e', columnspan=2)

        # ############### S-curve tab #########################################

        self.start_channel = 0
        self.stop_channel = 127
        self.channel_step = 1
        self.delay = 50
        self.interval = 2000
        self.pulsestretch = 3
        self.latency = 45
        self.calphi = 0
        self.arm_dac = 100
        self.start_cal_dac = 215
        self.stop_cal_dac = 235

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

        self.delay_label0 = Label(self.scurve_frame, text="0-4000")
        self.delay_label0.grid(column=3, row=4, sticky='w')

        self.interval_label = Label(self.scurve_frame, text="LV1A interval:")
        self.interval_label.grid(column=1, row=5, sticky='w')

        self.interval_entry = Entry(self.scurve_frame, width=5)
        self.interval_entry.grid(column=2, row=5, sticky='e')
        self.interval_entry.insert(0, self.interval)

        self.interval_label0 = Label(self.scurve_frame, text="0-4000")
        self.interval_label0.grid(column=3, row=5, sticky='w')

        self.pulsestretch_label = Label(self.scurve_frame, text="Pulse stretch:")
        self.pulsestretch_label.grid(column=1, row=6, sticky='w')

        self.pulsestretch_entry = Entry(self.scurve_frame, width=5)
        self.pulsestretch_entry.grid(column=2, row=6, sticky='e')
        self.pulsestretch_entry.insert(0, self.pulsestretch)

        self.pulsestretch_label0 = Label(self.scurve_frame, text="0-7")
        self.pulsestretch_label0.grid(column=3, row=6, sticky='w')

        self.latency_label = Label(self.scurve_frame, text="Latency:")
        self.latency_label.grid(column=1, row=7, sticky='w')

        self.latency_entry = Entry(self.scurve_frame, width=5)
        self.latency_entry.grid(column=2, row=7, sticky='e')
        self.latency_entry.insert(0, self.latency)

        self.latency_label0 = Label(self.scurve_frame, text="0-1023")
        self.latency_label0.grid(column=3, row=7, sticky='w')

        self.calphi_label = Label(self.scurve_frame, text="Cal Phi:")
        self.calphi_label.grid(column=1, row=8, sticky='w')

        self.calphi_entry = Entry(self.scurve_frame, width=5)
        self.calphi_entry.grid(column=2, row=8, sticky='e')
        self.calphi_entry.insert(0, self.calphi)

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

        self.chip_id_label = Label(self.production_frame, text="Chip ID:")
        self.chip_id_label.grid()
        self.chip_id_entry = Entry(self.production_frame, width=20)
        self.chip_id_entry.grid()
        self.chip_id_entry.insert(0, self.chip_id)
        self.chip_id_entry.config(state='disabled')

        self.barcode_label = Label(self.production_frame, text="Barcode ID:")
        self.barcode_label.grid()
        self.barcode_entry = Entry(self.production_frame, width=20)
        self.barcode_entry.grid()
        self.barcode_entry.insert(0, self.barcode_id)

        self.p_run_button = Button(self.production_frame, text="RUN", command=lambda: self.run_production_tests())
        self.p_run_button.grid()

        self.checks_label = Label(self.production_frame, text="\nTests:", width=25)
        self.checks_label.grid()

        tests = ['Check Short Circuit', 'Sync', 'ext ADC check', 'Save Barcode', 'BIST', 'Scan Chain', 'Iref adjustment', 'SLEEP power measurement', 'Internal ADC calibration',
                 'CAL_DAC conversion', 'Register Test', 'Chip ID write', 'Data packet test', 'Scan of all DACs',
                 'All Channel S-curves']
        self.test_label = []
        for i, test in enumerate(tests):
            self.test_label.append(Label(self.production_frame, text=test, width=25))
            self.test_label[i].grid()

        # self.production_frame.grid_forget()




        # INTERACTIVE SCREEN
        self.interactive_screen = Text(master, bg="black", fg="white", height=30, width=60)
        self.interactive_screen.grid(column=1, row=0)
        self.add_to_interactive_screen("\n")
        self.add_to_interactive_screen("############################################################\n")
        self.add_to_interactive_screen(" Welcome to the VFAT3 test system Graphical User Interface. \n")
        self.add_to_interactive_screen("############################################################\n")
        self.add_to_interactive_screen("\n")
        self.scrollbar = Scrollbar(master, command=self.interactive_screen.yview)
        self.scrollbar.grid(column=2, row=0, sticky='nsew')
        self.interactive_screen['yscrollcommand'] = self.scrollbar.set

        # CLOSE- AND CLEAR-BUTTONS
        self.ctrlButtons_frame = ttk.Frame(master)
        self.ctrlButtons_frame.grid(column=1, sticky='e')
        self.close_button = Button(self.ctrlButtons_frame, text="Clear", command=self.clear_interactive_screen)
        self.close_button.grid(column=1, row=0)
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
            filename = tkFileDialog.asksaveasfilename(filetypes=[('Register file', '*.reg')])
        else:
            timestamp = time.strftime("%Y%m%d_%H%M")
            filename = '%s/calibration/%scalibration.dat' % (self.data_folder, timestamp)
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc:  # Guard against race condition
                    print "Unable to create directory"
            open(filename, 'w').close()

        self.save_calibration_values_to_file_execute(filename)

    def save_calibration_values_to_file_execute(self, filename):
        if self.database:
            self.database.save_adc0(self.adc0M, self.adc0B)
            self.database.save_adc1(self.adc1M, self.adc1B)
            self.database.save_cal_dac(self.cal_dac_fcM, self.cal_dac_fcB)
            self.database.save_iref(self.register[134].Iref[0])
        else:
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
        if multiwrite == 0:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.split(",")
                    reg_nr = int(line[0])
                    write_data = line[1]
                    self.register[reg_nr].change_values(write_data)
                    self.write_register(reg_nr)
        else:
            filler_16bits = [0]*16
            full_data = []

            with open(filename, 'r') as f:
                for line in f:
                    line = line.split(",")
                    reg_nr = int(line[0])
                    write_data = line[1]
                    self.register[reg_nr].change_values(write_data)
                    data = []
                    for x in register[reg_nr].reg_array:
                        data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
                        data.extend(data_intermediate)
                    data.reverse()
                    data.extend(filler_16bits)
                    full_data.extend(data)

            output = self.SC_encoder.create_SC_packet(0, full_data, "MULTI_WRITE", 0, nr_words=146)
            paketti = output[0]
            write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
            for x in range(1, len(paketti)):
                write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
            self.execute()

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

    def read_register(self, reg):
        new_data = self.read_reg_execute(reg)
        self.register[reg].change_values(new_data)

    def read_reg_execute(self, reg):
        output = self.SC_encoder.create_SC_packet(reg, 0, "READ", 0)
        paketti = output[0]
        write_instruction(self.interactive_output_file, 150, FCC_LUT[paketti[0]], 1)
        for x in range(1, len(paketti)):
            write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
        while True:
            output = self.execute()
            if output[0] == "Error":
                text = "%s: %s\n" % (output[0], output[1])
                text += "Register values might be incorrect.\n"
                self.add_to_interactive_screen(text)
            if not output[0]:
                print "Error trying again"
            else:
                new_data = output[0][0].data
                new_data = ''.join(str(e) for e in new_data)
                break
        return new_data

    def add_to_interactive_screen(self, text):
        self.interactive_screen.insert(END,text)
        self.interactive_screen.see(END)

    def clear_interactive_screen(self):
        self.interactive_screen.delete(1.0,END)

    def execute(self, verbose="no"):
        output = self.interfaceFW.launch(register, self.interactive_output_file, self.COM_port)
        if output[0] == "Error":
            text = "%s: %s\n" % (output[0], output[1])
            self.add_to_interactive_screen(text)
        else:
            if output[0]:
                #text =  "Received SC replies:\n"
                # self.add_to_interactive_screen(text)
                for i in output[0]:
                    if i.info_code == 0:
                        if verbose == "yes":
                            text = "Transaction ok.\n"
                            #self.add_to_interactive_screen(text)
                        print "Transaction ok."
                    else:
                        if verbose == "yes":
                            text = "Transaction error.\n"
                            self.add_to_interactive_screen(text)

                    #text = "Transaction ID:%d, %s\n" % (i.transaction_ID, data_ok)
                    #self.add_to_interactive_screen(text)
                    if i.type_ID == 0:
                        pass
                        #text = "Data:\n %s\n" % i.data
                        #self.add_to_interactive_screen(text)

            if output[1]:
                if verbose == "yes":
                    text =  "Received data packets:\n"
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

    def check_short_circuit(self):
        error = 0
        ch1_current = self.tti_if.req_ch1_current()
        ch2_current = self.tti_if.req_ch2_current()
        print ch1_current
        print ch2_current
        if ch1_current > 0.1 or ch2_current > 0.1:
            text = "Short circuit detected.\n"
            self.add_to_interactive_screen(text)
            error = 1
        return error

    def measure_power(self, mode):
        error = 0
        ch1_current = self.tti_if.req_ch1_current()
        ch2_current = self.tti_if.req_ch2_current()
        ch1_voltage = self.tti_if.req_ch1_voltage()
        ch2_voltage = self.tti_if.req_ch2_voltage()
        ch1_power = ch1_voltage * ch1_current
        ch2_power = ch2_voltage * ch2_current
        print "Power Measurements:"
        print ch1_power
        print ch2_power

        self.database.save_power(ch1_power, ch2_power, mode)
        if ch1_power > 0.1:
            error = 1
        if ch2_power > 0.1:
            error = 1
        return error

    def send_reset(self):
        counter = 0
        error = 0
        while True:
            self.interfaceFW.reset_vfat3()
            time.sleep(0.1)
            result = self.send_sync(verbose='no')
            if result == 1:
                text = "->Sync success.\n"
                self.add_to_interactive_screen(text)
                break
            if counter > 16:
                error = 1
                text = "->Sync fail.\n"
                self.add_to_interactive_screen(text)
                break
            counter += 1
        return error

    def ext_adc(self, verbose='yes'):
        if verbose == 'yes':
            text = "->Reading the verification board external ADC.\n"
            self.add_to_interactive_screen(text)
        value = self.interfaceFW.ext_adc()
        if verbose == 'yes':
            s_value = str(value)
            text = "Value: %s mV\n" % s_value
            self.add_to_interactive_screen(text)
        return value

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
        command_encoded = FCC_LUT["CC-A"]
        write_instruction(self.interactive_output_file, 1, command_encoded, 1)
        write_instruction(self.interactive_output_file, 1, command_encoded, 0)
        write_instruction(self.interactive_output_file, 1, command_encoded, 0)
        output = self.interfaceFW.launch(register, self.interactive_output_file, self.COM_port, 2)
        if output[0] == "Error":
            if verbose == 'yes':
                text = "%s: %s\n" % (output[0], output[1])
                self.add_to_interactive_screen(text)
        elif output[2]:
            result = 1
            if verbose == 'yes':
                text = "Sync ok.\n"
                self.add_to_interactive_screen(text)
            for i in output[2]:
                if verbose == 'yes':
                    text = "BC:%d, %s\n" % (i[0], i[1])
                    self.add_to_interactive_screen(text)
        else:
            if verbose == 'yes':
                text = "Sync fail.\n"
                self.add_to_interactive_screen(text)
        return result

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

        output = self.SC_encoder.create_SC_packet(addr, 0, "READ", 0)
        paketti = output[0]
        write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
        for x in range(1, len(paketti)):
            write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
        counter = 0
        while True:
            counter += 1
            output = self.execute(verbose="yes")
            if counter == 10:
                print "No reply from ADC."
                break
            if output[0] == "Error":
                print "Error."
            else:
                if output[0]:
                    int_adc_value = int(''.join(map(str, output[0][0].data)), 2)
                    break
        return int_adc_value

    def read_adc1(self):

        addr = 131073  # ADC0 address

        output = self.SC_encoder.create_SC_packet(addr, 0, "READ", 0)
        paketti = output[0]
        write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
        for x in range(1, len(paketti)):
            write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
        counter = 0
        while True:
            counter += 1
            output = self.execute(verbose="yes")
            if counter == 10:
                print "No reply from ADC."
                break
            if output[0] == "Error":
                print "Error."
            else:
                if output[0]:
                    int_adc_value = int(''.join(map(str, output[0][0].data)), 2)
                    break
        return int_adc_value

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
        text = "ADC0: %d\t %f mV\n" % (adc0_value, self.adc0M * adc0_value + self.adc0B)
        self.add_to_interactive_screen(text)

        adc1_value = self.read_adc1()
        text = "ADC1: %d\t %f mV\n" % (adc1_value, self.adc1M * adc1_value + self.adc1B)
        self.add_to_interactive_screen(text)

    def send_cal_trigger(self):
        latency = int(self.scurve_entry.get())
        self.CalPulseLV1A_latency = latency
        self.CalPulse_LV1A_entry.delete(0, END)
        self.CalPulse_LV1A_entry.insert(0, self.CalPulseLV1A_latency)
        text = "->Sending CalPulse and LV1A with %s BC latency \n" % latency
        self.add_to_interactive_screen(text)
        CalPulse_encoded = FCC_LUT["CalPulse"]
        LV1A_encoded = FCC_LUT["LV1A"]

        write_instruction(self.interactive_output_file,1, CalPulse_encoded, 1)
        write_instruction(self.interactive_output_file,latency, LV1A_encoded, 0)
        self.execute(verbose="yes")

    def run_scurve(self):
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
            print "MAx CAL_DAC steps is 40."
            error += 1
        if error == 0:
            text = "->Running S-curve"
            self.add_to_interactive_screen(text)
            output = scurve_all_ch_execute(self, "S-curve", arm_dac=self.arm_dac, ch=[self.start_channel, self.stop_channel], ch_step=self.channel_step, configuration="yes", dac_range=[self.start_cal_dac, self.stop_cal_dac], delay=self.delay, bc_between_calpulses=self.interval, pulsestretch=self.pulsestretch, latency=self.latency, cal_phi=self.calphi)
            if output[2] != "":
                prod_error = 'y'
            if output[2] == "n":
                prod_error = 1
        else:
            print "Aborting s-curve run."
        return prod_error

    def set_fe_nominal_values(self):
        register[141].PRE_I_BSF[0] = 13
        register[141].PRE_I_BIT[0] = 150
        register[142].PRE_I_BLCC[0] = 25
        register[142].PRE_VREF[0] = 86
        register[143].SH_I_BFCAS[0] = 250
        register[143].SH_I_BDIFF[0] = 150
        register[144].SD_I_BDIFF[0] = 255
        register[145].SD_I_BSF[0] = 15
        register[145].SD_I_BFCAS[0] = 255

        self.write_register(141)
        self.write_register(142)
        self.write_register(143)
        self.write_register(144)
        self.write_register(145)
        # filler_16bits = [0]*16
        # full_data = []
        # data = []
        #
        # for x in register[141].reg_array:
        #     data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
        #     data.extend(data_intermediate)
        # data.reverse()
        # data.extend(filler_16bits)
        # print data
        # full_data.extend(data)
        #
        # data = []
        # for x in register[142].reg_array:
        #     data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
        #     data.extend(data_intermediate)
        # data.reverse()
        # data.extend(filler_16bits)
        # print data
        # full_data.extend(data)
        #
        # data = []
        # for x in register[143].reg_array:
        #     data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
        #     data.extend(data_intermediate)
        # data.reverse()
        # data.extend(filler_16bits)
        # print data
        # full_data.extend(data)
        #
        # data = []
        # for x in register[144].reg_array:
        #     data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
        #     data.extend(data_intermediate)
        # data.reverse()
        # data.extend(filler_16bits)
        # print data
        # full_data.extend(data)
        #
        # data = []
        # for x in register[145].reg_array:
        #     data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
        #     data.extend(data_intermediate)
        # data.reverse()
        # data.extend(filler_16bits)
        # print data
        # full_data.extend(data)
        #
        # output = self.SC_encoder.create_SC_packet(141, full_data, "MULTI_WRITE", 0)
        # paketti = output[0]
        # write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
        # for x in range(1, len(paketti)):
        #     write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
        # self.execute()

    def run_concecutive_triggers(self):
        self.nr_trigger_loops = int(self.cont_trig_entry.get())
        concecutive_triggers(self, self.nr_trigger_loops)

    def test_bist(self):
        if self.database:
            self.database.save_bist()
        return 1

    def test_scan_chain(self):
        if self.database:
            self.database.save_scanchain()
        return 1

    def run_production_tests(self):
        start = time.time()
        self.database = DatabaseInterface(self.chip_id)
        self.unset_calibration_variables()
        self.tti_if.set_outputs_on()
        result = []
        time.sleep(2)
        result.append(self.check_short_circuit())
        if result[0] == 0:
            print "Short Circuit test ok"
            result.append(self.send_reset())
            result.append(self.test_ext_adc())
            result.append(self.save_barcode())
            print "Test BIST ok"
            result.append(self.test_scan_chain())
            print "Test Scan Chain ok"
            result.append(iref_adjust(self))
            if result[1] == 0 and result[2] == 0 and result[3] == 0:
                print "Sync ok"
                print "Ext adc ok"
                print "Save barcode ok"
                self.send_idle()
                print "Send Idle ok."
                result.append(self.test_bist())
                print "Iref adjustment ok"
                result.append(self.measure_power('SLEEP'))
                result.append(adc_calibration(self))
                result.append(scan_cal_dac_fc(self, "CAL_DAC scan, fC"))
                self.save_calibration_values_to_file("s")
                result.append(self.test_registers())
                result.append(self.write_chip_id())
                result.append(concecutive_triggers(self))
                result.append(self.run_all_dac_scans())
                result.append(self.run_scurve())
                stop = time.time()
                duration = (stop - start)/60
                print "Errors:"
                print result
                print "Duration of the production test: %f min" % duration
                for i, value in enumerate(result):
                    if value == 'y':
                        self.test_label[i].config(bg='yellow')
                    elif value != 0:
                        self.test_label[i].config(bg='red')
                    else:
                        self.test_label[i].config(bg='green')
            else:
                text = "->Production test aborted.\n"
                self.add_to_interactive_screen(text)
        else:
            text = "->Production test aborted.\n"
            self.add_to_interactive_screen(text)
        time.sleep(1)
        self.unset_calibration_variables()
        self.tti_if.set_outputs_off()

# ################# SCAN/TEST -FUNCTIONS #############################

    def write_chip_id(self):
        self.increment_chip_id()
        return 1

    def save_barcode(self):
        error = 0
        try:
            barcode_value = int(self.barcode_entry.get())
        except Exception as e:
            print(e)
            text = "Invalid barcode.\n"
            self.add_to_interactive_screen(text)
            error = 1
        if error == 0:
            self.database.save_barcode(barcode_value)
            text = "Read barcode: %s\n" % barcode_value
            self.add_to_interactive_screen(text)
        return error

    def test_registers(self):
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
                read_data = self.read_reg_execute(reg_nr)
                read_data = read_data[16:]
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
            if error_counter == 0:
                self.database.save_register_ok()
            else:
                self.database.save_register_error()
        result.append(line)
        stop = time.time()
        run_time = (stop - start) / 60
        line = "Run time (minutes): %f\n" % run_time
        print line
        result.append(line)
        with open(output_file, "a") as myfile:
            for line in result:
                myfile.write("%s\n" % line)
        print "Writing back previous register values."
        self.load_register_values_from_file_execute(temp_file, multiwrite=1)
        print "Done"
        return error_counter

    def write_register(self, register_nr):
        filler_16bits = [0]*16
        data = []
        for x in register[register_nr].reg_array:
            data.extend(dec_to_bin_with_stuffing(x[0], x[1]))
        data.reverse()
        data.extend(filler_16bits)
        self.write_register_execute(register_nr, data)

    def write_register_execute(self, register_nr, data):
        flag = 0
        while True:
            output = self.SC_encoder.create_SC_packet(register_nr, data, "WRITE", 0)
            paketti = output[0]
            write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[0]], 1)
            for x in range(1, len(paketti)):
                write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
            output = self.interfaceFW.launch(register, self.interactive_output_file, self.COM_port)
            if output[0] == "Error":
                text = "%s: %s\n" % (output[0], output[1])
                self.add_to_interactive_screen(text)
            else:
                if output[0]:
                    for i in output[0]:
                        if i.info_code == 0:
                            # print "Transaction ok."
                            flag = 1
                        else:
                            print "Transaction error. Error code."

                else:
                    print "Transaction error. No reply."
                    print output
                    #raw_input("Press Enter to continue...")
                    print "Trying again."
                    self.send_sync()
                    time.sleep(1)
                    continue
            if flag == 1:
                break

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
        modified = scan_name.replace(" ", "_")
        if self.chosen_scan == "Counter Resets":
            self.counter_resets_execute(scan_name)
        elif self.chosen_scan == "CAL_DAC scan, fC":
            scan_cal_dac_fc(self, "CAL_DAC scan, fC")
        elif self.chosen_scan == "S-curve":
            scurve_execute(self, scan_name)
        elif self.chosen_scan == "S-curve all ch":
            scurve_all_ch_execute(self, scan_name)
        elif self.chosen_scan == "S-curve all ch cont.":
            while True:
                scurve_all_ch_execute(self, scan_name)
                self.send_reset()
                for i in range(0, 5):
                    print "->Sending sync request."
                    command_encoded = FCC_LUT["CC-A"]
                    write_instruction(self.interactive_output_file, 1, command_encoded, 1)
                    write_instruction(self.interactive_output_file, 1, command_encoded, 0)
                    write_instruction(self.interactive_output_file, 1, command_encoded, 0)
                    output = self.interfaceFW.launch(register, self.interactive_output_file, self.COM_port)
                    if output[0] == "Error":
                        text = "%s: %s\n" % (output[0], output[1])
                        self.add_to_interactive_screen(text)
                    elif output[2]:
                        print "Synch ok."
                        for i in output[2]:
                            print "BC:%d, %s\n" % (i[0], i[1])
                    else:
                        print "Synch fail."
                    time.sleep(60)
        else:
            scan_execute(self, scan_name)

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
        # text = "->Sending %s.\n" % command
        # self.add_to_interactive_screen(text)
        command_encoded = FCC_LUT[command]
        write_instruction(self.interactive_output_file, 1, command_encoded, 1)
        output = self.execute(verbose=verbose)

        return output

    def run_all_dac_scans(self):
        start = time.time()
        for scan in self.scan_options:
            print "Running %s" % scan
            scan_execute(self, scan, plot=1)
            print "Scan done."
        stop = time.time()
        run_time = (stop - start) / 60
        print "Runtime: %f" % run_time
        return 'y'

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
            write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[0]], 1)
            for x in range(1, len(paketti)):
                write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[x]], 0)
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
            data_intermediate = []
            for x in register[addr].reg_array:
                data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
                data.extend(data_intermediate)
            data.reverse()
            output = self.SC_encoder.create_SC_packet(addr,data,"WRITE",0)
            paketti = output[0]
            write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[0]], 1)
            for x in range(1,len(paketti)):
                write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[x]], 0)
            self.execute(verbose="yes")

    def change_channel(self):
        chosen_register = int(self.channel_entry.get())
        if chosen_register >= 0 and chosen_register <= 128:
            self.channel_register = chosen_register
        else:
            text = "Channel value: %d is out of limits. Channels are 0-128 \n" % chosen_register
            self.add_to_interactive_screen(text)
        self.update_registers("Channels")

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

            output = self.SC_encoder.create_SC_packet(register_nr, 0, "READ", 0)
            paketti = output[0]
            write_instruction(self.interactive_output_file, 150, FCC_LUT[paketti[0]], 1)
            for x in range(1, len(paketti)):
                write_instruction(self.interactive_output_file, 1, FCC_LUT[paketti[x]], 0)
            output = self.execute(verbose="yes")
            if not output[0]:
                text = "No read data found. Register values might be incorrect.\n"
                self.add_to_interactive_screen(text)
            elif output[0] == "Error":
                text = "%s: %s\n" %(output[0], output[1])
                text += "Register values might be incorrect.\n"
                self.add_to_interactive_screen(text)
            else:
                print "Read data:"
                new_data = output[0][0].data
                print new_data
                if register_nr in [65536, 65537, 65538, 65539]:
                    new_data = ''.join(str(e) for e in new_data)
                else:
                    new_data = ''.join(str(e) for e in new_data[-16:])
                register[register_nr].change_values(new_data)

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


