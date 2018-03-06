############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################

import socket
import sys
import time


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
        self.sock.sendall(bytearray(message))
        try:
            data = self.sock.recv(600)
            hex_data = []
            for i in data:
                hex_text = hex(ord(i))
                hex_data.append(hex_text[-2:])
            print hex_data
        finally:
            self.sock.close()
        return hex_data

    def send_fcc(self, fcc_hex):   # fcc_hex can be given as a list also.
        message = [0xca, 0x00, 0x00]
        message.extend(fcc_hex)
        output = self.execute_req(message)
        return output

    def write_register(self, address_lsb, value):
        message = [0xca, 0x00, 0x01]
        message.append(0x01)  # R/W-byte
        message.extend([0x00, 0x00, 0x00, address_lsb])
        message.extend(value)
        output = self.execute_req(message)
        return output

    def read_register(self, address_lsb):
        message = [0xca, 0x00, 0x01]
        message.append(0x01)  # R/W-byte
        message.extend([0x00, 0x00, 0x00, address_lsb])
        output = self.execute_req(message)
        return output

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


