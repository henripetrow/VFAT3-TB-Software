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

    def execute_req(self, message, no_packets=1, timeout=15, scurve="no"):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)
        print message
        self.sock.sendall(bytearray(message))
        try:
            self.sock.settimeout(timeout)
            hex_data = []
            multi_line_data = []
            for k in range(0, no_packets):
                output = self.sock.recv(2000)
                if scurve == "yes":
                    for i in output:
                        hex_text = int(ord(i))
                        hex_data.append(hex_text)
                    hex_data.reverse()
                    print hex_data
                    multi_line_data.append(hex_data)
                    output = multi_line_data
                    hex_data = []
                else:
                    for i in output:
                        hex_text = hex(ord(i))
                        hex_data.append(hex_text)
                    output = hex_data
        finally:
            self.sock.close()
        print output
        print len(output)
        return output

    def send_fcc(self, fcc_bin):   # fcc_hex can be given as a list also.
        message = [0xca, 0x00, 0x00]
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
        print "Register address: %s" % address_hex
        print "Reading register."
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
        print output_bin
        return output_bin

    def send_sync(self):
        message = [0xca, 0x00, 0x02]
        output = self.execute_req(message)
        return output

    def adjust_iref(self):
        message = [0xca, 0x00, 0x05]
        output = self.execute_req(message)
        return output

    def int_adc_calibration(self):
        message = [0xca, 0x00, 0x06]
        output = self.execute_req(message)
        output = [int(i, 16) for i in output]
        return output

    def cal_dac_calibration(self, start, stop, step):
        message = [0xca, 0x00, 0x07, start, step, stop]
        output = self.execute_req(message, no_packets=2)
        return output

    def run_scurve(self, start_ch, stop_ch, cal_dac_start, cal_dac_stop):
        message = [0xca, 0x00, 0x08, start_ch, stop_ch, 1, cal_dac_start, cal_dac_stop, 1, 0x01, 0x2c, 0, 0x64]
        nr_channels = stop_ch - start_ch + 1
        output = self.execute_req(message, no_packets=nr_channels,  timeout=30, scurve="yes")
        return output

    def run_dac_scan(self, start, step, stop, mon_sel):
        message = [0xca, 0x00, 0x09, start, step, stop, 0, 0, 1, mon_sel]
        output = self.execute_req(message,  timeout=30)
        return output
