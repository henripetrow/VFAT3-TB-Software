############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################

from Tkinter import *
import ttk
from scripts.DatabaseInterfaceBrowse import *
import matplotlib.pyplot as plt


class ProductionTestBrowser:
    def __init__(self, master):
        # Initiations

        s = ttk.Style()
        s.configure('My.TFrame', background='white')
        self.master = master
        self.master.title("VFAT3 Production Test Browser")
        self.master.minsize(width=1000, height=800)
        self.master.configure(background='white')

        #self.browser_frame = Frame(self.master)
        #self.browser_frame.grid()

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

        self.database = DatabaseInterfaceBrowse()

        # ##################### Control Frame ##################################

        self.control_frame = LabelFrame(self.master, width=250, height=80, text='Controls')
        self.control_frame.grid()
        self.control_frame.grid_propagate(False)

        hybrid_list = self.database.list_hybrids()

        self.hybrid = StringVar(master)
        self.hybrid.set(hybrid_list[0])  # default value
        #self.hybrid_selection.trace("w", self.update_hybrid())

        # REGISTER DROP DOWN MENU
        self.hybrid_selection = OptionMenu(self.control_frame, self.hybrid, *hybrid_list, command=lambda x: self.update_hybrid())
        #self.hybrid_selection.config(width=30)
        self.hybrid_selection.grid(row=0)

        # ##################### Info Frame ##################################

        self.info_frame = LabelFrame(self.master, width=250, height=500, text='Information')
        self.info_frame.grid()
        self.info_frame.grid_propagate(False)

        label_width = 15
        self.hw_id_ver_label = Label(self.info_frame, text="HW_ID_VER:")
        self.hw_id_ver_label.grid(column=1, row=1, sticky='e')
        self.hw_id_ver_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.hw_id_ver_label0.grid(column=2, row=1, sticky='w')

        self.buff_offset_label = Label(self.info_frame, text="Buffer Offset:")
        self.buff_offset_label.grid(column=1, row=2, sticky='e')
        self.buff_offset_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.buff_offset_label0.grid(column=2, row=2, sticky='w')

        self.vref_adc_label = Label(self.info_frame, text="VREF_ADC:")
        self.vref_adc_label.grid(column=1, row=3, sticky='e')
        self.vref_adc_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.vref_adc_label0.grid(column=2, row=3, sticky='w')

        self.vbgr_label = Label(self.info_frame, text="V_BGR:")
        self.vbgr_label.grid(column=1, row=4, sticky='e')
        self.vbgr_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.vbgr_label0.grid(column=2, row=4, sticky='w')

        self.adc0_label = Label(self.info_frame, text="ADC0:")
        self.adc0_label.grid(column=1, row=5, sticky='e')
        self.adc0_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.adc0_label0.grid(column=2, row=5, sticky='w')

        self.adc1_label = Label(self.info_frame, text="ADC1:")
        self.adc1_label.grid(column=1, row=6, sticky='e')
        self.adc1_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.adc1_label0.grid(column=2, row=6, sticky='w')

        self.cal_dac_label = Label(self.info_frame, text="CAL_DAC:")
        self.cal_dac_label.grid(column=1, row=7, sticky='e')
        self.cal_dac_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.cal_dac_label0.grid(column=2, row=7, sticky='w')

        self.iref_label = Label(self.info_frame, text="Iref:")
        self.iref_label.grid(column=1, row=8, sticky='e')
        self.iref_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.iref_label0.grid(column=2, row=8, sticky='w')

        self.thr_label = Label(self.info_frame, text="Mean Threshold:")
        self.thr_label.grid(column=1, row=9, sticky='e')
        self.thr_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.thr_label0.grid(column=2, row=9, sticky='w')

        self.enc_label = Label(self.info_frame, text="Mean enc:")
        self.enc_label.grid(column=1, row=10, sticky='e')
        self.enc_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.enc_label0.grid(column=2, row=10, sticky='w')

        self.register_test_label = Label(self.info_frame, text="Register errors:")
        self.register_test_label.grid(column=1, row=11, sticky='e')
        self.register_test_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.register_test_label0.grid(column=2, row=11, sticky='w')

        self.ec_err_label = Label(self.info_frame, text="EC errors:")
        self.ec_err_label.grid(column=1, row=12, sticky='e')
        self.ec_err_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.ec_err_label0.grid(column=2, row=12, sticky='w')

        self.bc_err_label = Label(self.info_frame, text="BC errors:")
        self.bc_err_label.grid(column=1, row=13, sticky='e')
        self.bc_err_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.bc_err_label0.grid(column=2, row=13, sticky='w')

        self.crc_err_label = Label(self.info_frame, text="CRC errors:")
        self.crc_err_label.grid(column=1, row=14, sticky='e')
        self.crc_err_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.crc_err_label0.grid(column=2, row=14, sticky='w')

        self.hit_err_label = Label(self.info_frame, text="Hit errors:")
        self.hit_err_label.grid(column=1, row=15, sticky='e')
        self.hit_err_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.hit_err_label0.grid(column=2, row=15, sticky='w')

        self.noisy_ch_label = Label(self.info_frame, text="Noisy Channels:")
        self.noisy_ch_label.grid(column=1, row=16, sticky='e')
        self.noisy_ch_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.noisy_ch_label0.grid(column=2, row=16, sticky='w')

        self.dead_ch_label = Label(self.info_frame, text="Dead Channels:")
        self.dead_ch_label.grid(column=1, row=17, sticky='e')
        self.dead_ch_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.dead_ch_label0.grid(column=2, row=17, sticky='w')

        self.bist_label = Label(self.info_frame, text="BIST:")
        self.bist_label.grid(column=1, row=18, sticky='e')
        self.bist_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.bist_label0.grid(column=2, row=18, sticky='w')

        self.scan_chain_label = Label(self.info_frame, text="ScanChain:")
        self.scan_chain_label.grid(column=1, row=19, sticky='e')
        self.scan_chain_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.scan_chain_label0.grid(column=2, row=19, sticky='w')

        self.sleep_power_label = Label(self.info_frame, text="SLEEP Power[W]:")
        self.sleep_power_label.grid(column=1, row=20, sticky='e')
        self.sleep_power_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.sleep_power_label0.grid(column=2, row=20, sticky='w')

        self.run_power_label = Label(self.info_frame, text="RUN Power[W]:")
        self.run_power_label.grid(column=1, row=21, sticky='e')
        self.run_power_label0 = Label(self.info_frame, text="n/a", width=label_width)
        self.run_power_label0.grid(column=2, row=21, sticky='w')

        # Image-frame

        #logo = PhotoImage(file="./graphs/browser_enc.png")
        #w1 = Label(self.master, image=logo).grid(column=2)

    def update_hybrid(self):
        hybrid = self.hybrid.get()

        # Update info-section
        results = self.database.get_production_results(hybrid)

        self.hw_id_ver_label0.config(text=results[1])
        self.buff_offset_label0.config(text=results[2])
        self.vref_adc_label0.config(text=results[3])
        self.vbgr_label0.config(text=results[4])
        self.adc0_label0.config(text="%0.2f %0.2f" % (results[5], results[6]))
        self.adc1_label0.config(text="%0.2f %0.2f" % (results[7], results[8]))
        self.cal_dac_label0.config(text="%0.2f %0.2f" % (results[9], results[10]))
        self.iref_label0.config(text=results[11])
        self.thr_label0.config(text=results[12])
        self.enc_label0.config(text=results[13])
        self.register_test_label0.config(text=results[14])
        self.ec_err_label0.config(text=results[15])
        self.bc_err_label0.config(text=results[16])
        self.crc_err_label0.config(text=results[17])
        self.hit_err_label0.config(text=results[18])
        self.noisy_ch_label0.config(text=results[19])
        self.dead_ch_label0.config(text=results[20])
        self.bist_label0.config(text=results[21])
        self.scan_chain_label0.config(text=results[22])
        self.sleep_power_label0.config(text="A:%.3f, D:%0.3f" % (results[23], results[24]))
        self.run_power_label0.config(text="A:%.3f, D:%0.3f" % (results[25], results[26]))

        # Create enc-plot
        result = self.database.get_enc_values(hybrid)
        fig = plt.figure()
        plt.plot(result)
        plt.xlabel('Channel')
        plt.ylabel('enc [fC]')
        plt.grid(True)
        fig.savefig('./graphs/browser_enc.gif')

        # Create threshold-plot
        result = self.database.get_threshold_values(hybrid)
        fig = plt.figure()
        plt.plot(result)
        plt.xlabel('Channel')
        plt.ylabel('Threshold [fC]')
        plt.grid(True)
        fig.savefig('./graphs/browser_thr.gif')

root = Tk()
my_gui = ProductionTestBrowser(root)

root.mainloop()


