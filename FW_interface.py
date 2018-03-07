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

    def execute_req(self, message):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)
        print "Send:"
        print message
        self.sock.sendall(bytearray(message))
        try:
            self.sock.settimeout(5.0)
            data = self.sock.recv(2000)
            # MSGLEN = 5
            # chunks = []
            # bytes_recd = 0
            # while bytes_recd < MSGLEN:
            #     chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            #     print chunk
            #     if chunk == b'':
            #         raise RuntimeError("socket connection broken")
            #     chunks.append(chunk)
            #     bytes_recd = bytes_recd + len(chunk)
            # data = b''.join(chunks)
            hex_data = []
            for i in data:
                hex_text = hex(ord(i))
                hex_data.append(hex_text)
            print "Reply:"
            print hex_data
        finally:
            self.sock.close()
        return hex_data

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
        #print "Register address: %s" % address_hex
        address_3 = address_hex[2:4]
        address_2 = address_hex[4:6]
        address_1 = address_hex[6:8]
        address_0 = address_hex[8:10]

        # Data from bit-string to hex bytes
        #print "writing register value:"
        #print value
        data_0 = value[8:16]
        data_1 = value[0:8]
        #data_0.reverse()
        #data_1.reverse()
        data_0 = ''.join(str(e) for e in data_0)
        data_1 = ''.join(str(e) for e in data_1)
        #print "data0, bin: %s, hex: %x, dec:%i" % (data_0, int(data_0, 2), int(data_0, 2))
        #print "data1, bin: %s, hex: %x, dec:%i" % (data_1, int(data_1, 2), int(data_1, 2))
        message = [0xca, 0x00, 0x01]
        message.append(0x01)  # R/W-byte
        message.extend([int(address_3, 16), int(address_2, 16), int(address_1, 16), int(address_0, 16)])
        message.extend([0,0, int(data_1, 2), int(data_0, 2)])
        #print message
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
        print output
        return output

    def adjust_iref(self):
        message = [0xca, 0x00, 0x05]
        output = self.execute_req(message)
        print output
        return output

    def int_adc_calibration(self):
        message = [0xca, 0x00, 0x06]
        output = self.execute_req(message)
        print output

    def cal_dac_calibration(self):
        message = [0xca, 0x00, 0x07]
        output = self.execute_req(message)
        print output

    def run_scurve(self):
        message = [0xca, 0x00, 0x08]
        output = self.execute_req(message)
        print output


