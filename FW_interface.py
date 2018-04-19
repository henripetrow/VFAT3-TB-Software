############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################

import socket
import sys
import time
from test_system_functions import *

class FW_interface:
    def __init__(self, mode):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        self.server_address = ('192.168.1.10', 7)

    def execute_req(self, message, no_packets=1, timeout=2, scurve="no"):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)
        self.sock.sendall(bytearray(message))
        if scurve == "yes":
            channels = range(message[3], message[4]+1, message[5])
        #print message
        try:
            self.sock.settimeout(timeout)
            int_data = []
            hex_data = []
            multi_line_data = []
            for k in range(0, no_packets):
                output = self.sock.recv(3000)
                if scurve == "yes":
                    for i in output:
                        hex_value = hex(ord(i))
                        hex_data.append(hex_value)
                    value_flag = 0
                    for value in hex_data:
                        if value_flag == 0:
                            value_lsb = value[2:]
                            if len(value_lsb) == 1:
                                value_lsb = "0" + value_lsb
                            value_flag = 1
                        elif value_flag == 1:
                            ivalue = value + value_lsb
                            ivalue_dec = int(ivalue, 16)
                            ivalue_dec = 100*ivalue_dec/float(message[12])
                            int_data.append(ivalue_dec)
                            value_flag = 0
                    int_data.reverse()
                    print "Channel %i:" % channels[k]
                    print int_data
                    multi_line_data.append(int_data)
                    output = multi_line_data
                    int_data = []
                    hex_data = []
                else:
                    for i in output:
                        hex_text = hex(ord(i))
                        hex_data.append(hex_text)
                    output = hex_data
                    #print output
        except socket.timeout:
            output = ['Error']
            print "No response"
        finally:
            self.sock.close()
        # print output
        #print "output length: %i" % len(output)
        return output

    def send_fcc(self, fcc_bin, file=""):   # fcc_hex can be given as a list also.
        message = [0xca, 0x00, 0x00]
        if file != "":
            fcc_data = []
            length = 0
            with open(file, 'r') as f:
                for line in f:
                    length += 1
                    fcc = line.strip('\n')

                    fcc_data.append(int(fcc,2))
            address_hex = '0x%0*x' % (4, length)
            message.extend([int(address_hex[2:4], 16), int(address_hex[4:6], 16)])
            message.extend(fcc_data)
            #print message
            output = self.execute_req(message)
        else:
            if isinstance(fcc_bin, list):
                command_list_len = len(fcc_bin)
                address_hex = '0x%0*x' % (4, command_list_len)
                message.extend([int(address_hex[2:4], 16), int(address_hex[4:6], 16)])
                fcc_list_int = [int(i, 2) for i in fcc_bin]
                message.extend(fcc_list_int)
            else:
                message.extend([0, 1])
                message.extend([int(fcc_bin, 2)])
            output = self.execute_req(message)
        return output

    def write_register(self, address, value):
        # Dec address to hex bytes
        address_hex = '0x%0*x' % (8, address)
        address_3 = address_hex[2:4]
        address_2 = address_hex[4:6]
        address_1 = address_hex[6:8]
        address_0 = address_hex[8:10]

        # Data from bit-string to hex bytes
        data_0 = value[8:16]
        data_1 = value[0:8]
        data_0 = ''.join(str(e) for e in data_0)
        data_1 = ''.join(str(e) for e in data_1)
        message = [0xca, 0x00, 0x01]
        message.append(0x01)  # R/W-byte
        message.extend([int(address_3, 16), int(address_2, 16), int(address_1, 16), int(address_0, 16)])
        message.extend([0, 0, int(data_1, 2), int(data_0, 2)])
        output = self.execute_req(message)
        return output

    def read_register(self, address): # Address in dec
        address_hex = '0x%0*x' % (8, address)
        #print "Register address: %s" % address_hex
        #print "Reading register."
        address_3 = address_hex[2:4]
        address_2 = address_hex[4:6]
        address_1 = address_hex[6:8]
        address_0 = address_hex[8:10]
        message = [0xca, 0x00, 0x01]
        message.append(0x00)  # R/W-byte
        message.extend([int(address_3, 16), int(address_2, 16), int(address_1, 16), int(address_0, 16)])
        output = self.execute_req(message)
        output_bin = []
        output_bin.extend(dec_to_bin_with_stuffing(int(output[3], 16), 8))
        output_bin.extend(dec_to_bin_with_stuffing(int(output[2], 16), 8))
        output_bin.extend(dec_to_bin_with_stuffing(int(output[1], 16), 8))
        output_bin.extend(dec_to_bin_with_stuffing(int(output[0], 16), 8))
        #print output_bin
        return output_bin

    def send_sync(self):
        message = [0xca, 0x00, 0x02]
        output = self.execute_req(message)
        return output

    def adjust_iref(self):
        message = [0xca, 0x00, 0x05]
        output = self.execute_req(message)
        return output

    def int_adc_calibration(self, start, step, stop):
        message = [0xca, 0x00, 0x06, start, step, stop]
        output = self.execute_req(message, timeout=30, no_packets=2)
        return output

    def cal_dac_calibration(self, start, stop, step):
        message = [0xca, 0x00, 0x07, start, step, stop]
        output = self.execute_req(message, no_packets=2, timeout=30)
        return output

    def run_scurve(self, start_ch, stop_ch, step_ch, cal_dac_start, cal_dac_stop, delay, arm_dac, triggers=100):
        message = [0xca, 0x00, 0x08, start_ch, stop_ch, step_ch, cal_dac_start, cal_dac_stop, 1, 0x0, 0x0, 0, triggers, arm_dac, 8, 0, delay, 0x01, 0xf4]
        nr_channels = stop_ch - start_ch + 1
        output = self.execute_req(message, no_packets=nr_channels,  timeout=30, scurve="yes")
        return output

    def run_dac_scan(self, start, step, stop, mon_sel):
        message = [0xca, 0x00, 0x09, start, step, stop, 0, 0, 0, mon_sel]
        output = self.execute_req(message,  timeout=30)
        return output

    def read_ext_adc(self):
        message = [0xca, 0x00, 0x03]
        output = self.execute_req(message,  timeout=30)
        return output

    def run_bist(self):
        message = [0xca, 0x00, 0x0a]
        output = self.execute_req(message, timeout=30)
        return output