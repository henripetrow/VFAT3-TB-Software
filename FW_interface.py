############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################

#import serial
import sys, os
#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/python_scripts_thomas/kernel")
#from ipbus import *

from test_system_functions import *
from output_decoder import *
import time

class FW_interface:

    def __init__(self, mode):
        self.simulation_mode = mode
        if self.simulation_mode == 0: #Normal mode
            print "Entering normal mode"
            #using pychips
            self.glib = GLIB()
        if self.simulation_mode == 1: #Simulation mode
            with open("./data/FPGA_statusfile.dat", "w") as myfile:
                print "Entering Simulation mode."
                myfile.write("0")
        if self.simulation_mode == 2: #Aamir mode
            print "Entering Aamir mode."

        self.FCC_LUT_L = {
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





    def write_control(self,input_value):
        print "Writing control register: %d" % input_value
        #using pychips
        self.glib.set("control_register",input_value)

    def read_control(self): 
        print "Reading control register."
        #using pychips
        value = self.glib.get("control_register")
        print value
        return value

    def write_fifo(self):
        with open("./data/FPGA_instruction_list.dat", 'r') as f:
            for line in f:
                line = line.rstrip('\n')
                data_line = line + "0000000000000000"
                #using pychips
                self.glib.set("test_fifo",int(data_line,2))
                print "Writing command to fifo:"
                print data_line
                print int(data_line,2)
                data_line = ""

    def read_fifo(self):
        open("./data/FPGA_output.dat", 'w').close()
        while (False):
            line = self.glib.get("test_fifo")
            line = dec_to_bin_with_stuffing(line, 32)
            if line == 0:
                break
            else:
                with open("./data/FPGA_output.dat", "a") as myfile:
                    myfile.write("%s" % line)

    def launch(self,register,file_name,serial_port):
        timeout = 0
        print "Chosen COM port: %s" % serial_port
        ########### NORMAL MODE ##########
        if self.simulation_mode == 0:
            self.write_fifo()
            self.write_control(1)
            counter = 0
            while True:
                counter += 1
                status = self.read_control()
                if counter == 20:
                    print "Timeout, no response from the firmware."
                    timeout = 1
                    break
                if status == 3:
                    break
                time.sleep(1)
            self.read_fifo()

        ############# SIMULATION MODE ##########
        if self.simulation_mode == 1:
            with open("./data/FPGA_statusfile.dat", "w") as myfile:
                myfile.write("1")
            counter = 0
            while(True):
                counter += 1
                if counter == 60:
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



        ############### Aamir mode #####################333
        if self.simulation_mode == 2:
            ser = serial.Serial(serial_port, baudrate=115200, writeTimeout=0)
            # ser.baudrate =9600
            ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
            ser.parity = serial.PARITY_NONE  # set parity check: no parity
            ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
            # ser.timeout = None          #block read
            # ser.timeout = 1  # non-block read
            ser.timeout = 10  # timeout block read
            ser.xonxoff = True  # disable software flow control
            ser.rtscts = False  # disable hardware (RTS/CTS) flow control
            ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
            # ser.writeTimeout = 100  # timeout for write

            data = "\xca"
            ser.write(data)
            #data = "\x00"
            #ser.write(data)


            output_byte_list = []
            with open(file_name, 'r') as f0:
                for i, l in enumerate(f0):
                    pass
            f0.close()
            size = i + 1

            c, f= divmod(size, 1<<8)        # split the size to 8 bit lsb and msb
            output_byte_list.append(c)
            output_byte_list.append(f)

            with open(file_name, 'r') as f:
                for line in f:
                    line = line.rstrip('\n')
                    data_line = line[-4:]
                    data_line = self.FCC_LUT_L[data_line]
                    data_line = int(data_line, 2)
                    output_byte_list.append(data_line)



            ser.write(bytearray(output_byte_list))

            open("./data/FPGA_output_list.dat", 'w').close()
            for i in range(0,1024):
                data = ser.read()
                data = ord(data)
                data = dec_to_bin_with_stuffing(data, 8)
                data = ''.join(str(e) for e in data)
                data = "000000000001,%s\n" % data
                with open("./data/FPGA_output_list.dat", "a") as myfile:
                    myfile.write(data)
            timeout = 0

        if not timeout:
            output_data = decode_output_data('./data/FPGA_output_list.dat',register)
            open("./data/FPGA_output_list.dat", 'w').close()
        else:
            output_data = ['Error','Timeout, no response from the firmware.']
        return output_data
