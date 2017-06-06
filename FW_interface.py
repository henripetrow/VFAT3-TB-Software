############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################

import serial
import sys
import os
from output_decoder import *
import time
import shutil

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/python_scripts_thomas/kernel")
from ipbus import *

class FW_interface:

    def __init__(self, mode):
        self.connection_mode = mode
        if self.connection_mode == 0:  # IPbus mode
            print "Entering normal mode"
            self.glib = GLIB()
        if self.connection_mode == 1:  # Simulation mode
            with open("./data/FPGA_statusfile.dat", "w") as myfile:
                print "Entering Simulation mode."
                myfile.write("0")
        if self.connection_mode == 2:  # Serial mode
            print "Entering Aamir mode."

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
        self.glib.set("reset", 1)

    def write_control(self, input_value):
        self.glib.set("state_fw", input_value)

    def read_control(self):
        value = self.glib.get("state_fw")
        return value

    def write_fifo(self):
        with open("./data/FPGA_instruction_list.dat", 'r') as f:
            for line in f:
                line = line.rstrip('\n')
                data_line = "0000000000000000" + line
                self.glib.set("test_fifo", int(data_line, 2))

    def empty_fifo(self):
        while True:
            line = self.glib.get("test_fifo")
            if line == 0 or line is None:
                break

    def empty_full_fifo(self):
        print "Emptying FIFO"
        self.glib.fifoRead("test_fifo", 131000)
        print "FIFO empty"

    def read_fifo(self):
        open("./data/FPGA_output.dat", 'w').close()
        data_list = []
        while True:
            line = self.glib.get("test_fifo")
            if line == 0 or line is None:
                break
            else:
                line = dec_to_bin_with_stuffing(line, 32)
                line1 = ''.join(str(e) for e in line[0:24])
                line2 = ''.join(str(e) for e in line[-8:])
                line = "%s,%s \n" % (int(line1, 2), line2)
                data_list.append(line)
        open("./data/FPGA_output_list.dat", 'w').close()
        with open("./data/FPGA_output_list.dat", "a") as myfile:
            for i in data_list:
                myfile.write(i)

    def read_routine_fifo(self):
        open("./data/FPGA_output.dat", 'w').close()
        data_list = self.glib.fifoRead("test_fifo", 130074)

        open("./data/FPGA_output_list.dat", 'w').close()
        with open("./data/FPGA_output_list.dat", "a") as myfile:
            for i in data_list:
                line = dec_to_bin_with_stuffing(i, 32)
                line1 = ''.join(str(e) for e in line[0:24])
                line2 = ''.join(str(e) for e in line[-8:])
                line = "%s,%s \n" % (int(line1, 2), line2)
                myfile.write(line)

    def launch(self, register, file_name, serial_port, routine=0):
        open("./data/FPGA_output_list.dat", 'w').close()
        if file_name != "./data/FPGA_instruction_list.dat":
            shutil.copy2(file_name, "./data/FPGA_instruction_list.dat")
        timeout = 0

        # ########## NORMAL MODE ##########
        if self.connection_mode == 0:
            if routine == 2:
                self.empty_full_fifo()
            else:
                self.empty_fifo()
            self.write_control(0)
            self.write_fifo()
            self.write_control(1)
            time.sleep(0.1)
            if routine == 1:
                self.read_routine_fifo()
            else:
                self.read_fifo()

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

        # ############## Aamir mode #####################333
        if self.connection_mode == 2:
            ser = serial.Serial(serial_port, baudrate=115200, writeTimeout=0)
            ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
            ser.parity = serial.PARITY_NONE  # set parity check: no parity
            ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
            ser.timeout = 10  # timeout block read
            ser.xonxoff = True  # disable software flow control
            ser.rtscts = False  # disable hardware (RTS/CTS) flow control
            ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
            data = "\xca"
            ser.write(data)
            output_byte_list = []
            with open(file_name, 'r') as f0:
                for i, l in enumerate(f0):
                    pass
            f0.close()
            size = i + 1
            c, f = divmod(size, 1 << 8)        # split the size to 8 bit lsb and msb
            output_byte_list.append(c)
            output_byte_list.append(f)

            with open(file_name, 'r') as f:
                for line in f:
                    line = line.rstrip('\n')
                    data_line = line[-4:]
                    data_line = self.FCC_LUT_L[data_line]
                    data_line = int(data_line, 2)
                    print data_line
                    output_byte_list.append(data_line)

            ser.write(bytearray(output_byte_list))
            data_list = []
            for i in range(0,700):
                data = ser.read()
                data = ord(data)
                data = dec_to_bin_with_stuffing(data, 8)
                data = ''.join(str(e) for e in data)
                data = "000000000001,%s\n" % data
                data_list.append(data)

            open("./data/FPGA_output_list.dat", 'w').close()
            with open("./data/FPGA_output_list.dat", "a") as myfile:
                for i in data_list:
                    myfile.write(i)
            timeout = 0

        if not timeout:
            output_data = decode_output_data('./data/FPGA_output_list.dat', register)
        else:
            print "not Decoding output data."
            output_data = ['Error', 'Timeout, no response from the firmware.']
        return output_data








