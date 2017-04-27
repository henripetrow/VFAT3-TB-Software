############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################



from Tkinter import *
import ttk
import sys

from VFAT3_registers import *
from generator import *
from test_system_functions import *
from FW_interface import *


import subprocess # For opening scans for edit in the system default editor.

class VFAT3_GUI:
    def __init__(self, master):
        if len(sys.argv) >= 2:
            if sys.argv[1] == '-s':
                self.interfaceFW = FW_interface(1)      #  1 - Simulation mode(with simulation model)
            elif sys.argv[1] == '-a' or sys.argv[1] == '-a_nr':
                self.interfaceFW = FW_interface(2)      #  1 - Simulation mode(with simulation model)
            else:
                print "Unrecognised option."
                self.interfaceFW = FW_interface(2)      # 0 - Normal mode(with Firmware)
        else:
            self.interfaceFW = FW_interface(2)          # 0 - Normal mode(with Firmware)         
        self.SC_encoder = SC_encode()
        self.channel_register = 0
        self.value = ""
        self.CalPulseLV1A_latency = 4
        self.transaction_ID = 0
        self.interactive_output_file = "./data/FPGA_instruction_list.dat"
        s = ttk.Style()
        s.configure('My.TFrame', background='white')
        self.COM_port = "COM2"
        self.register_mode = 'r'
        self.register_names = []
        self.master = master
        self.master.title("GUI for the VFAT3 test system.")
        bwidth = 15
        self.master.minsize(width=680, height=450)
        self.master.configure(background='white')

        #######MENUBAR#################################

        # create a toplevel menu
        menubar = Menu(self.master)

        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Quit", command=master.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # create more pulldown menus
        modemenu = Menu(menubar, tearoff=0)
        modemenu.add_command(label="Interactive", command=lambda:self.change_mode("interactive"))
        modemenu.add_command(label="Routines", command=lambda:self.change_mode("scans_tests"))
        modemenu.add_separator()
        modemenu.add_command(label="Production", command=lambda:self.change_mode("production"))
        modemenu.entryconfig(1, state=DISABLED)
        modemenu.entryconfig(3, state=DISABLED)
        menubar.add_cascade(label="Mode", menu=modemenu)



        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=helpmenu)

        # display the menu
        self.master.config(menu=menubar)


        #####################################################################################################################################
        ###################################################INTERACTIVE MODE##################################################################
        #####################################################################################################################################

        ##########NOTEBOOK##############################
        self.nb = ttk.Notebook(master, width = 300)

        self.FCC_frame = ttk.Frame(self.nb)
        self.FCC_frame.grid()

        self.register_frame = ttk.Frame(self.nb)
        self.register_frame.grid()

        self.misc_frame = ttk.Frame(self.nb)
        self.misc_frame.grid()

        self.FW_frame = ttk.Frame(self.nb)
        self.FW_frame.grid()

        ##########FCC TAB################################
        self.label = Label(self.FCC_frame, text="Send Fast Control Commands (FCC)")
        self.label.grid(columnspan = 2)

        self.EC0_button = Button(self.FCC_frame, text="EC0", command= lambda: self.send_FCC("EC0"), width = bwidth)
        self.EC0_button.grid()

        self.BC0_button = Button(self.FCC_frame, text="BC0", command= lambda: self.send_FCC("BC0"), width = bwidth)
        self.BC0_button.grid()

        self.calpulse_button = Button(self.FCC_frame, text="CalPulse", command= lambda: self.send_FCC("CalPulse"), width = bwidth)
        self.calpulse_button.grid()

        self.resync_button = Button(self.FCC_frame, text="ReSync", command= lambda: self.send_FCC("ReSync"), width = bwidth)
        self.resync_button.grid()

        self.sconly_button = Button(self.FCC_frame, text="SCOnly", command= lambda: self.send_FCC("SCOnly"), width = bwidth)
        self.sconly_button.grid()

        self.runmode_button = Button(self.FCC_frame, text="RunMode", command= lambda: self.send_FCC("RunMode"), width = bwidth)
        self.runmode_button.grid()

        self.lv1a_button = Button(self.FCC_frame, text="LV1A", command= lambda: self.send_FCC("LV1A"), width = bwidth)
        self.lv1a_button.grid()

        self.sc0_button = Button(self.FCC_frame, text="SC0", command= lambda: self.send_FCC("SC0"), width = bwidth)
        self.sc0_button.grid()

        self.sc1_button = Button(self.FCC_frame, text="SC1", command= lambda: self.send_FCC("SC1"), width = bwidth)
        self.sc1_button.grid()

        self.resc_button = Button(self.FCC_frame, text="ReSC", command= lambda: self.send_FCC("ReSC"), width = bwidth)
        self.resc_button.grid()

        self.lv1aec0_button = Button(self.FCC_frame, text="LV1A+EC0", command= lambda: self.send_FCC("LV1A+EC0"), width = bwidth)
        self.lv1aec0_button.grid()

        self.lv1abc0_button = Button(self.FCC_frame, text="LV1A+BC0", command= lambda: self.send_FCC("LV1A+BC0"), width = bwidth)
        self.lv1abc0_button.grid()

        self.lv1aec0bc0_button = Button(self.FCC_frame, text="LV1A+EC0+BC0", command= lambda: self.send_FCC("LV1A+EC0+BC0"), width = bwidth)
        self.lv1aec0bc0_button.grid()

        self.EC0BC0_button = Button(self.FCC_frame, text="EC0+BC0", command= lambda: self.send_FCC("EC0+BC0"), width = bwidth)
        self.EC0BC0_button.grid()

        ##################REGISTERS TAB###################################
        
    

        OPTIONS = [
                "Channels",
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
                "Front End DACs",
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
        self.variable.set(OPTIONS[0]) # default value

        # REGISTER DROP DOWN MENU
        w = OptionMenu(self.register_frame, self.variable, *OPTIONS, command=self.update_registers)
        w.config(width=30)
        w.grid(row=0)

        # FRAME FOR THE REGISTER DATA
        self.register_data_frame = ttk.Frame(self.register_frame, height = 500)
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
        self.apply_button = Button(self.register_button_frame, text="Apply", command = self.apply_register_values)
        self.apply_button.grid(column=0,row=0)
        self.default_button = Button(self.register_button_frame, text="Defaults")
        self.default_button.grid(column=1, row=0)
        self.default_button.config(state="disabled")
        self.refresh_button = Button(self.register_button_frame, text="Refresh", command = lambda: self.update_registers(self.value))
        self.refresh_button.grid(column=3, row=0)

        self.channel_label = Label(self.register_data_frame, text = "Channel:")
        self.channel_label.grid(column = 0, row= 0, sticky='e')

        self.channel_entry = Entry(self.register_data_frame, width=5)
        self.channel_entry.grid(column = 1, row= 0, sticky='e')
        self.channel_entry.insert(0, self.channel_register)

        self.channel_button = Button(self.register_data_frame, text="Change", command = self.change_channel)
        self.channel_button.grid(column = 2, row = 0, sticky='e')

        self.channel_label.grid_forget()
        self.channel_entry.grid_forget()
        self.channel_button.grid_forget()

        ################MISC TAB #######################################
        # Read ADCs
        self.close_button = Button(self.misc_frame, text="Read ADCs", command= lambda: self.read_ADCs(), width = bwidth)
        self.close_button.grid(column = 1, row= 0, sticky='e')

        self.idle_button = Button(self.misc_frame, text="SC Idle character", command= lambda: self.send_idle(), width = bwidth)
        self.idle_button.grid(column = 1, row= 1, sticky='e')

        self.sync_button = Button(self.misc_frame, text="Sync", command= lambda: self.send_sync(), width = bwidth)
        self.sync_button.grid(column = 1, row= 2, sticky='e')

        self.sync_check_button = Button(self.misc_frame, text="Sync check", command= lambda: self.send_FCC("CC-B"), width = bwidth)
        self.sync_check_button.grid(column = 1, row = 3, sticky='e')

        self.CalPulse_LV1A_button = Button(self.misc_frame, text="CalPulse+LV1A", command = self.send_Cal_trigger, width = bwidth)
        self.CalPulse_LV1A_button.grid(column = 1, row = 4, sticky='e')

        self.CalPulse_LV1A_label0 = Label(self.misc_frame, text = "Latency")
        self.CalPulse_LV1A_label0.grid(column = 2, row= 4, sticky='e')

        self.CalPulse_LV1A_entry = Entry(self.misc_frame, width=5)
        self.CalPulse_LV1A_entry.grid(column = 3, row= 4, sticky='e')
        self.CalPulse_LV1A_entry.insert(0, self.CalPulseLV1A_latency)

        self.CalPulse_LV1A_label0 = Label(self.misc_frame, text = "BC")
        self.CalPulse_LV1A_label0.grid(column = 4, row= 4, sticky='e')


        ################ FW CONFIGURE TAB #######################################


        self.fwsync_button = Button(self.FW_frame, text="ReSync Firmware", command= lambda: self.FW_sync(), width = bwidth)
        self.fwsync_button.grid(column = 1, row= 2, sticky='e')
        self.fwsync_button.config(state="disabled")

        self.serial_options = [
                "COM0",
                "COM1",
                "COM2",
                "COM3",
                "COM4",
                "COM5",
                "COM6",

                ]
        self.chosen_serial_port = self.serial_options[2]
        self.serial_port_variable = StringVar(master)
        self.serial_port_variable.set(self.serial_options[2]) # default value

        # SERIAL PORT DROP DOWN MENU
        serial_port_drop_menu = OptionMenu(self.FW_frame, self.serial_port_variable, *self.serial_options, command=self.change_com_port)
        serial_port_drop_menu.config(width=30)
        serial_port_drop_menu.grid(column = 1,row=3)


        # ADD TABS
        self.nb.add(self.FCC_frame, text="FCC")
        self.nb.add(self.register_frame, text="Registers")
        self.nb.add(self.misc_frame, text="misc.")
        self.nb.add(self.FW_frame, text="Firmware")
        self.nb.grid(column = 0, row = 0)

        #self.nb.grid_forget()

        ##############################################################################################################################
        ###################################################SCAN MODE##################################################################
        ##############################################################################################################################

        self.scan_frame = ttk.Frame(master, width = 302, height=450)
        self.scan_frame.grid(column=0,row=0)
        self.scan_frame.grid_propagate(False)


        self.scan_label = ttk.Label(self.scan_frame, text="Available scans and tests.")
        self.scan_label.grid(column=0,row=0)

     
        self.scan_options = [
                "FCC Check",
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
                "SD_I_BFCAS scan"
                ]
        self.chosen_scan = self.scan_options[0]
        self.scan_variable = StringVar(master)
        self.scan_variable.set(self.scan_options[0]) # default value

        # REGISTER DROP DOWN MENU
        scan_drop_menu = OptionMenu(self.scan_frame, self.scan_variable, *self.scan_options, command=self.choose_scan)
        scan_drop_menu.config(width=30)
        scan_drop_menu.grid(row=1)
        
        self.verbose_var = IntVar()

        verbose_check_button = Checkbutton(self.scan_frame, text="Verbose", variable=self.verbose_var)
        verbose_check_button.grid()

        # SCAN RUN AND MODIFY BUTTONS
        self.scan_button_frame = ttk.Frame(self.scan_frame, width = 302, height=200)
        self.scan_button_frame.grid()  
        self.scan_button_frame.grid_propagate(False)
        self.run_button = Button(self.scan_button_frame, text="RUN", command = self.run_scan)
        self.run_button.grid(column=0,row=0)
        self.modify_button = Button(self.scan_button_frame, text="Modify", command = self.modify_scan)
        self.modify_button.grid(column=1, row=0)



        self.scan_frame.grid_forget()



        # INTERACTIVE SCREEN
        self.interactive_screen = Text(master, bg="black", fg="white", height = 30, width = 60)
        self.interactive_screen.grid(column=1, row = 0)
        self.add_to_interactive_screen("\n")
        self.add_to_interactive_screen("############################################################\n")
        self.add_to_interactive_screen(" Welcome to the VFAT3 test system Graphical User Interface. \n")
        self.add_to_interactive_screen("############################################################\n")
        self.add_to_interactive_screen("\n")
        self.scrollbar = Scrollbar(master,command=self.interactive_screen.yview)
        self.scrollbar.grid(column=2,row=0, sticky='nsew')
        self.interactive_screen['yscrollcommand'] = self.scrollbar.set

        # CLOSE- AND CLEAR-BUTTONS
        self.ctrlButtons_frame = ttk.Frame(master)
        self.ctrlButtons_frame.grid(column=1,sticky='e')
        self.close_button = Button(self.ctrlButtons_frame, text="Clear", command=self.clear_interactive_screen)
        self.close_button.grid(column=1,row=0)
        self.close_button = Button(self.ctrlButtons_frame, text="Close", command=master.quit)
        self.close_button.grid(column=2,row=0)

       # self.read_all_registers()

####################################################################################
###################################FUNCTIONS########################################
####################################################################################


##################### GENERAL GUI FUNCTIONS ############################

    def read_all_registers(self):
        # Read register value from the chip and save it to the register object.
        text =  "Reading all of the chips registers:\n"
        self.add_to_interactive_screen(text)
        for i in range(129,146):
            paketti = self.SC_encoder.create_SC_packet(i,0,"READ",0)
            write_instruction(self.interactive_output_file,150, FCC_LUT[paketti[0]], 1)
            for x in range(1,len(paketti)):
                write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[x]], 0)
            output = self.execute()
            if output[0] == "Error":
                text =  "%s: %s\n" %(output[0],output[1])
                text =  "Register values might be incorrect.\n"
                self.add_to_interactive_screen(text)
                break
            else:
                new_data = output[0][0].data
                new_data = ''.join(str(e) for e in new_data)
                register[i].change_values(new_data)
        self.clear_interactive_screen()

    def add_to_interactive_screen(self,text):
        self.interactive_screen.insert(END,text)
        self.interactive_screen.see(END)

    def clear_interactive_screen(self):
        self.interactive_screen.delete(1.0,END)

    def execute(self):
        output = self.interfaceFW.launch(register,self.interactive_output_file,self.COM_port)
        if output[0] == "Error":
            text =  "%s: %s\n" %(output[0],output[1])
            self.add_to_interactive_screen(text)
        else:
            if output[0]:
                text =  "Received SC replies:\n"
                self.add_to_interactive_screen(text)
                for i in output[0]:
                    if i.info_code == 0:
                        data_ok = "Transaction ok."
                    else: 
                        data_ok = "Transaction error."                     

                    text =  "Transaction ID:%d, %s\n" % (i.transaction_ID, data_ok)
                    self.add_to_interactive_screen(text)                
                    if i.type_ID  == 0:
                        text = "Data:\n %s\n" % i.data
                        self.add_to_interactive_screen(text) 

            if output[1]:
                text =  "Received data packets:\n"
                self.add_to_interactive_screen(text)
                for i in output[1]:
                    if i.spzs_packet == 1:
                        text = "Data built from a SPZS packet.\n"
                        self.add_to_interactive_screen(text)             
                    if i.header == "00011010" or i.header == "01010110":
                        text = "Header II received.\n"
                        self.add_to_interactive_screen(text)
                        if i.BC or i.EC:
                            text =  "BC:%d EC: %d\n" % (i.BC,i.EC)
                            self.add_to_interactive_screen(text) 
   
                    else:
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
                text =  "Received sync replies:\n"
                self.add_to_interactive_screen(text)
                for i in output[2]:
                    text =  "BC:%d, %s\n" % (i[0],i[1])
                    self.add_to_interactive_screen(text) 

        return output                 


    def change_mode(self,mode):
        if mode == "interactive":
            self.scan_frame.grid_forget()
            self.nb.grid(column=0,row=0)
        if mode == "scans_tests":
            self.nb.grid_forget()
            self.scan_frame.grid(column=0,row=0)
            self.scan_frame.grid_propagate(False)


################# FW-TAB FUNCTIONS ################################



    def FW_sync(self):
        text =  "-> Resynchronising Firmware.\n"
        self.add_to_interactive_screen(text)
        command_encoded = FCC_LUT["CC-A"]
        write_instruction(self.interactive_output_file,1, command_encoded,1)
        write_instruction(self.interactive_output_file,1, command_encoded,0)
        write_instruction(self.interactive_output_file,1, command_encoded,0)
        self.execute()

    def change_com_port(self,port):
        self.COM_port = port


################# MISC-TAB FUNCTIONS ################################



    def send_sync(self):
        text =  "->Sending sync request.\n"
        self.add_to_interactive_screen(text)
        command_encoded = FCC_LUT["CC-A"]
        write_instruction(self.interactive_output_file,1, command_encoded,1)
        write_instruction(self.interactive_output_file,1, command_encoded,0)
        write_instruction(self.interactive_output_file,1, command_encoded,0)
        self.execute()

    def send_idle(self):
        text =  "->Sending IDLE transaction.\n"
        self.add_to_interactive_screen(text)
        paketti = self.SC_encoder.create_SC_packet(0,0,"IDLE",0)
        write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[0]], 1)
        for x in range(1,len(paketti)):
            write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[x]], 0)
        self.execute()

    def read_ADCs(self):
        text =  "->Reading the ADCs.\n"
        self.add_to_interactive_screen(text)

        addr0 = 131072 # ADC0 address
        addr1 = 131073 # ADC0 address

        paketti = self.SC_encoder.create_SC_packet(addr0,0,"READ",0)
        write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[0]], 1)
        for x in range(1,len(paketti)):
            write_instruction(1, FCC_LUT[paketti[x]], 0)

        paketti = self.SC_encoder.create_SC_packet(addr1,0,"READ",0)
        write_instruction(self.interactive_output_file,150, FCC_LUT[paketti[0]], 0)
        for x in range(1,len(paketti)):
            write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[x]], 0)
        output = self.execute()
        if output[0] == "Error":
            text =  "%s: %s\n" %(output[0],output[1])
            self.add_to_interactive_screen(text)
        else:
            if output[0]:
                text =  "Received Values:\n"
                self.add_to_interactive_screen(text)
                text = "ADC0: %s\n" % int(''.join(map(str, output[0][0].data)),2)
                self.add_to_interactive_screen(text) 
                text = "ADC1: %s\n" % int(''.join(map(str, output[0][1].data)),2)
                self.add_to_interactive_screen(text) 


    def send_Cal_trigger(self):
        latency = int(self.CalPulse_LV1A_entry.get())
        self.CalPulseLV1A_latency = latency
        self.CalPulse_LV1A_entry.delete(0, END)
        self.CalPulse_LV1A_entry.insert(0, self.CalPulseLV1A_latency)
        text = "->Sending CalPulse and LV1A with %s BC latency \n" % latency
        self.add_to_interactive_screen(text)
        CalPulse_encoded = FCC_LUT["CalPulse"]
        LV1A_encoded = FCC_LUT["LV1A"]

        write_instruction(self.interactive_output_file,1, CalPulse_encoded, 1)
        write_instruction(self.interactive_output_file,latency, LV1A_encoded, 0)
        self.execute()

################## SCAN/TEST -FUNCTIONS #############################


    def generate_scan(self):
        text =  "->Generating the scan instruction file: %s\n" % self.chosen_scan
        self.add_to_interactive_screen(text)
        scan_name = self.chosen_scan
        output = generator(scan_name)


    def run_scan(self):
        text =  "->Running the scan: %s\n" % self.chosen_scan
        self.add_to_interactive_screen(text)
        scan_name = self.chosen_scan
        modified = scan_name.replace(" ", "_")
        file_name = "./routines/%s.txt" % modified
        output = generator(scan_name)


        generation_events = output[3]

        print "size of generation events0:"
        print len(generation_events[0])
        print "size of generation events1:"
        print len(generation_events[1])
        print "size of generation events2:"
        print len(generation_events[2])
        print "size of generation events3:"
        print len(generation_events[3])

       

        if self.verbose_var.get() == 1:
            for i in output[0]:
                self.add_to_interactive_screen(i)
                self.add_to_interactive_screen("\n")
        print output[2]
        text = "Lines: %d, Size:%d kb, Duration: %d BC, %f ms.\n" %(output[2][0],output[2][1],output[2][2],output[2][3])
        self.add_to_interactive_screen("Generated file:\n")
        self.add_to_interactive_screen(text)
        self.scan_execute(scan_name,generation_events)

    def scan_execute(self,scan_name,generation_events):
        SC_writes = generation_events[3]
        modified = scan_name.replace(" ", "_")
        file_name = "./routines/%s/instruction_list.txt" % modified


        output = self.interfaceFW.launch(register,file_name,self.COM_port)
        if output[0] == "Error":
            text =  "%s: %s\n" %(output[0],output[1])
            self.add_to_interactive_screen(text)
        else:
            text =  "Received Values:\n"
            self.add_to_interactive_screen(text)
            ADC_flag = 0
            text = "%s|ADC0|ADC1\n" %scan_name[:-5]
            self.add_to_interactive_screen(text)
            for i in output[0]:
                for k in generation_events[2]:
                    if k[0] > i.BCd:
                        break
                    else:
                        reg_value = k[2]
        
                if i.type_ID  == 0:
                    if ADC_flag == 0:   
                        fist_ADC_value = int(''.join(map(str, i.data)),2)
                        ADC_flag = 1
                    else:
                        second_ADC_value = int(''.join(map(str, i.data)),2)
                        text = "%d %d %d\n" % (reg_value,fist_ADC_value,second_ADC_value)
                        self.add_to_interactive_screen(text)
                        ADC_flag = 0


        return output 



    def modify_scan(self):
        text =  "->Modifying the scan: %s\n" % self.chosen_scan
        self.add_to_interactive_screen(text)
        scan_name = self.chosen_scan
        modified = scan_name.replace(" ", "_")
        file_name = "./routines/%s/instruction_list.txt" % modified
        proc = subprocess.Popen(['gedit', file_name])

    def choose_scan(self,value):
       self.chosen_scan = value

######################## FCC-TAB FUNCTIONS ##########################

    def send_FCC(self,command):
        text = "->Sending %s.\n" % command
        self.add_to_interactive_screen(text)
        command_encoded = FCC_LUT[command]
        write_instruction(self.interactive_output_file,1, command_encoded,1)
        self.execute()

######################### REGISTER-TAB FUNCTIONS ####################

    def apply_register_values(self):
        if self.register_mode == 'r':
            text = "The register is read only\n"
            self.add_to_interactive_screen(text)
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
            paketti = self.SC_encoder.create_SC_packet(addr,data,"WRITE",0)
            write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[0]], 1)
            for x in range(1,len(paketti)):
                write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[x]], 0)
            self.execute()

    def apply_register_values(self):
        if self.register_mode == 'r':
            text = "The register is read only\n"
            self.add_to_interactive_screen(text)
        elif self.value == "Front End DACs":
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



            paketti = self.SC_encoder.create_SC_packet(141,full_data,"MULTI_WRITE",0)
            write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[0]], 1)
            for x in range(1,len(paketti)):
                write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[x]], 0)
            self.execute()
            
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
            paketti = self.SC_encoder.create_SC_packet(addr,data,"WRITE",0)
            write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[0]], 1)
            for x in range(1,len(paketti)):
                write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[x]], 0)
            self.execute()

    def change_channel(self):
        register = int(self.channel_entry.get())
        if register >= 0 and register <= 128:
            self.channel_register = register
        else:
            text = "Channel value: %d is out of limits. Channels are 0-128 \n" % register
            self.add_to_interactive_screen(text)
        self.update_registers("Channels")

    def update_registers(self,value):
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
            self.register_names = [cal,mask,zcc_dac,arm_dac]

            self.channel_label.grid(column = 0, row= 0, sticky='e')
            self.channel_entry.grid(column = 1, row= 0, sticky='e')
            self.channel_entry.delete(0, END)
            self.channel_entry.insert(0, self.channel_register)
            self.channel_button.grid(column = 2, row = 0, sticky='e')

        elif self.value == "Control Logic":
            self.register_mode = 'rw'
            register_nr = 129
            description = "Settings for the control logic."
            self.register_names = ["PS","SyncLevelEnable","ST","DDR"]

        elif self.value == "Data Packet":
            self.register_mode = 'rw'
            register_nr = 130
            description = "Settings for the data packets."
            self.register_names = ["P16","PAR","DT","SZP","SZD","TT","ECb","BCb"]

        elif self.value == "Front End":
            self.register_mode = 'rw'
            register_nr = 131
            description = "Settings for the Front End."
            self.register_names = ["TP_FE","RES_PRE","CAP_PRE"]

        elif self.value == "CFD":
            self.register_mode = 'rw'
            register_nr = 132
            description = "Settings for the CFD."
            self.register_names = ["PT","EN_HYST","SEL_POL","Force_En_ZCC","Force_TH","SEL_COMP_MODE"]

        elif self.value == "Monitoring":
            self.register_mode = 'rw'
            register_nr = 133
            description = "Settings for the Monitoring."
            self.register_names = ["VREF_ADC","Mon_Gain","Monitor_Sel"]

        elif self.value == "Global reference current":
            self.register_mode = 'rw'
            register_nr = 134
            description = "Tuning of the global reference current."
            self.register_names = ["Iref"]

        elif self.value == "Global Threshold":
            self.register_mode = 'rw'
            register_nr = 135
            description = "Settings for the global thresholds."
            self.register_names = ["ZCC_DAC","ARM_DAC"]

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
            self.register_names = ["CAL_SEL_POL","CAL_PHI","CAL_EXT","CAL_DAC","CAL_MODE"]

        elif self.value == "Calibration 1":
            self.register_mode = 'rw'
            register_nr = 139
            description = "Settings for the Calibration Pulse."
            self.register_names = ["CAL_FS","CAL_DUR"]

        elif self.value == "Biasing 0":
            self.register_mode = 'rw'
            register_nr = 140
            description = "Settings for the CFD biasing."
            self.register_names = ["CFD_DAC_2","CFD_DAC_1"]

        elif self.value == "Biasing 1":
            self.register_mode = 'rw'
            register_nr = 141
            description = "Settings for the Front End biasing."
            self.register_names = ["PRE_I_BSF","PRE_I_BIT"]

        elif self.value == "Biasing 2":
            self.register_mode = 'rw'
            register_nr = 142
            description = "Settings for the Front End biasing."
            self.register_names = ["PRE_I_BLCC","PRE_VREF"]

        elif self.value == "Biasing 3":
            self.register_mode = 'rw'
            register_nr = 143
            description = "Settings for the Front End biasing."
            self.register_names = ["SH_I_BFCAS","SH_I_BDIFF"]

        elif self.value == "Biasing 4":
            self.register_mode = 'rw'
            register_nr = 144
            description = "Settings for the Front End biasing."
            self.register_names = ["SD_I_BDIFF"]

        elif self.value == "Biasing 5":
            self.register_mode = 'rw'
            register_nr = 145
            description = "Settings for the Front End biasing."
            self.register_names = ["SD_I_BSF","SD_I_BFCAS"]

        elif self.value == "Biasing 6":
            self.register_mode = 'rw'
            register_nr = 146
            description = "Settings for the SLVS biasing."
            self.register_names = ["SLVS_IBIAS","SLVS_VREF"]

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


        elif self.value == "Front End DACs":
            self.register_mode = 'rw'
            register_nr = "FED"
            description = "Front End related DACs."
            self.register_names = ["PRE_I_BSF","PRE_I_BIT","PRE_I_BLCC","PRE_VREF","SH_I_BFCAS","SH_I_BDIFF","SD_I_BDIFF","SD_I_BSF","SD_I_BFCAS"]






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
        self.description_label.grid(column = 0, row= 1, columnspan = 2)
        self.separator = ttk.Separator(self.register_data_frame, orient='horizontal')
        self.separator.grid(column=0, row=2, columnspan=2, sticky='ew')
        if len(sys.argv) >= 2:
            

            if sys.argv[1] != '-a_nr': # If not in Aamir mode without read. we read the values from the chip
                # Read a register value from the chip and save it to the corresponding register object.

                if register_nr == "FED":
                    text =  "Reading the Front end DAC registers\n"
                    self.add_to_interactive_screen(text)
                    paketti = self.SC_encoder.create_SC_packet(141,0,"MULTI_READ",0)
                    print paketti
                    write_instruction(self.interactive_output_file,150, FCC_LUT[paketti[0]], 1)
                    for x in range(1,len(paketti)):
                        write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[x]], 0)
                    output = self.execute()
                    if output[0] == "Error":
                        text =  "%s: %s\n" %(output[0],output[1])
                        text =  "Register values might be incorrect.\n"
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
                    text =  "Reading the register: %d\n" %register_nr
                    self.add_to_interactive_screen(text)

                    paketti = self.SC_encoder.create_SC_packet(register_nr,0,"READ",0)
                    write_instruction(self.interactive_output_file,150, FCC_LUT[paketti[0]], 1)
                    for x in range(1,len(paketti)):
                        write_instruction(self.interactive_output_file,1, FCC_LUT[paketti[x]], 0)
                    output = self.execute()
                    if output[0] == "Error":
                        text =  "%s: %s\n" %(output[0],output[1])
                        text =  "Register values might be incorrect.\n"
                        self.add_to_interactive_screen(text)
                    else:
                        print "Read data:"
                        new_data = output[0][0].data
                        print new_data
                        if register_nr in [65536,65537,65538,65539]:
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
            self.label[j].grid(column=0,row = j+3, sticky='e')
            if register_nr in [65536,65537,65538,65539]:
                entry_width = 12
            else:
                entry_width = 5
            self.entry.append(Entry(self.register_data_frame, width=entry_width))
            self.entry[j].grid(column = 1, row = j+3, sticky= 'w')
            self.entry[j].insert(0, current_value)
            if self.register_mode == 'r':
                self.entry[j].config(state='disabled')
            size = register[addr].reg_array[variable][1]
            text = "(0 - %d)" % (2**size-1)
            self.range.append(Label(self.register_data_frame, text=text))
            self.range[j].grid(column=2,row = j+3, sticky='w')
            j += 1
        



root = Tk()
my_gui = VFAT3_GUI(root)
root.mainloop()


