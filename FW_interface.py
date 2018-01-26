############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################

import serial
import sys
import os
from output_decoder import *
from scurve_decoder import *
import time
import shutil

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/python_scripts_thomas/kernel")
from ipbus import *

class FW_interface:

    def __init__(self, mode):
        self.connection_mode = mode
        if self.connection_mode == 0:  # IPbus/pyChips mode
            self.glib = GLIB()
            #print "Entering normal mode"
        if self.connection_mode == 1:  # Simulation mode
            with open("./data/FPGA_statusfile.dat", "w") as myfile:
                print "Entering Simulation mode."
                myfile.write("0")
        if self.connection_mode == 2:  # Serial mode
            print "Entering Aamir mode."

        if self.connection_mode == 3: # IPbus/uHal mode
            #self.glib = GLIB()
            #self.glib.get("ext_adc")
            import uhal

            manager = uhal.ConnectionManager("file://connections.xml")
            self.hw = manager.getDevice("VFAT3_TB")
            self.hw.setTimeoutPeriod(5000)

            #self.hw.getNode("STATE").write(1)
            #self.hw.dispatch()

            reg = self.hw.getNode("STATE").read()
            self.hw.dispatch()
            print reg


        self.FCC_LUT_L = {
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

    def reset_vfat3(self):
        if self.connection_mode == 0:
            self.glib.set("reset", 1)

    def reset_ipbus(self):
        if self.connection_mode == 0:
            self.glib.set("reset_ipbus", 1)

    def ext_adc(self):
        counter = 0
        self.start_ext_adc()
        time.sleep(0.1)
        while True:
            if counter == 10:
                print "No answer from ADC."
                print "Are ADC inputs connected?"
                rvalue = "Error"
                break
            if self.connection_mode == 0:
                value = self.glib.get("ext_adc")
            if value != 0:
                rvalue = value * 0.0625  # ext ADC LSB is 62.5 uV
                break
            # print "counter is %i"%counter
            print "ADC returned 0, trying again."
            counter += 1
        self.stop_ext_adc()
        return rvalue

    def start_ext_adc(self):
        if self.connection_mode == 0:
            self.glib.set("ext_adc_on", 1)

    def stop_ext_adc(self):
        if self.connection_mode == 0:
            self.glib.set("ext_adc_on", 0)

    def write_control(self, input_value):
        self.glib.set("state_fw", input_value)

    def read_control(self):
        value = self.glib.get("state_fw")
        return value

    def write_fifo(self):
        f = open("./data/FPGA_instruction_list.dat", 'r')
        x = f.read().splitlines()
        x = [int(i, 2) for i in x]

        self.glib.fifoWrite("test_fifo", x)

    def empty_fifo(self):
        while True:
            line = self.glib.get("test_fifo")
            if line == 0 or line is None:
                break

    def empty_full_fifo(self):
        self.glib.fifoRead("test_fifo", 131000)

    def read_fifo(self):
        open("./data/FPGA_output.dat", 'w').close()
        data_list = []
        while True:
            line = self.glib.get("test_fifo")
            if line == 0 or line is None:
                break
            if len(data_list) > 132000:
                    break
            else:
                data_list.append(line)
        return data_list

    def read_routine_fifo(self):
        data_list = self.glib.fifoRead("test_fifo", 250074)
        return data_list

    # def read_routine_fifo(self):
    #     data_list = self.glib.fifoRead("test_fifo", 300074)
    #     open("./data/FPGA_output_list.dat", 'w').close()
    #     with open("./data/FPGA_output_list.dat", "a") as myfile:
    #         if data_list is None:
    #             pass
    #         elif any(data_list):
    #             for i in data_list:
    #                 line = dec_to_bin_with_stuffing(i, 32)
    #                 # print "routine: %s" % line
    #                 line1 = ''.join(str(e) for e in line[0:24])
    #                 line2 = ''.join(str(e) for e in line[-8:])
    #                 line = "%s,%s \n" % (int(line1, 2), line2)
    #                 myfile.write(line)
    #         else:
    #             print "!-> read_routine_fifo received a value: None."
    #     return data_list

    def read_sync_fifo(self):
        data_list = self.glib.fifoRead("test_fifo", 130)
        return data_list

    def launch(self, register, file_name, serial_port, routine=0, save_data=0, obj=0, scurve_ch="j"):

        open("./data/FPGA_output_list.dat", 'w').close()
        if file_name != "./data/FPGA_instruction_list.dat":
            shutil.copy2(file_name, "./data/FPGA_instruction_list.dat")
        timeout = 0
        # ########## NORMAL MODE ##########
        if self.connection_mode == 0 or self.connection_mode == 3:
            if routine == 2:
                self.empty_full_fifo()
            elif routine == 1:
                pass
            else:
                self.empty_fifo()
            #time.sleep(0.01)
            self.write_control(0)
            #time.sleep(0.01)
            self.write_fifo()
            #time.sleep(0.001)
            self.write_control(1)
            if scurve_ch != "j":
                time.sleep(0.035)
                #time.sleep(0.2)
            #else:
            #    #time.sleep(0.03)
            #    pass
            if routine == 1:
                received_data = self.read_routine_fifo()
            elif routine == 2:
                received_data = self.read_sync_fifo()
            else:
                #received_data = self.read_fifo()
                received_data = self.read_sync_fifo()
        # ############ SIMULATION MODE ##########
        if self.connection_mode == 1:

            with open("./data/FPGA_statusfile.dat", "w") as myfile:
                myfile.write("1")
            counter = 0
            while(True):
                counter += 1
                if counter == 100:
                    print "Timeout, no response from the firmware."
                    timeout = 1
                    break
                with open('./data/FPGA_statusfile.dat', 'r') as f:
                    first_line = f.readline()
                    first_line.strip()
                    first_line = int(first_line)
                time.sleep(1)
                print "Waiting. Control register value: %s" % first_line
                if first_line == 3:
                    with open("./data/FPGA_statusfile.dat", "w") as myfile:
                        myfile.write("0")
                    break

        if save_data != 0:
            timestamp = time.strftime("%Y%m%d_%H%M%s")
            FPGA_output = "./data/FPGA_output_list.dat"
            dump_file = "%s/concecutive_tiggers/data_dump/%s_concecutive_trigger_data_dump.dat" % (obj.data_folder, timestamp)
            if not os.path.exists(os.path.dirname(dump_file)):
                try:
                    os.makedirs(os.path.dirname(dump_file))
                except OSError as exc:  # Guard against race condition
                    print "Unable to create directory"
            shutil.copy2(FPGA_output, dump_file)

        if not timeout:
            transaction_stop = time.time()
            analysis_start = time.time()
            if scurve_ch == "j":
                output_data = decode_output_data(received_data, register)
            else:
                output_data = decode_scurve_data(received_data, scurve_ch)

        else:
            print "not Decoding output data."
            output_data = ['Error', 'Timeout, no response from the firmware.']
        return output_data








