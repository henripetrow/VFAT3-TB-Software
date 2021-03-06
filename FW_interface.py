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
        self.connection_error = 0

    def execute_req(self, message, no_packets=1, timeout=2, scurve="no", receive=2000):
        # Create a TCP/IP socket
        self.connection_error = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)
        self.sock.sendall(bytearray(message))
        if scurve == "yes":
            channels = range(message[3], message[4]+1, message[5])
            print "Triggers:"
            triggers = message[11] << 8
            triggers += message[12]
            print triggers
        # print message
        try:
            self.sock.settimeout(timeout)
            int_data = []
            hex_data = []
            multi_line_data = []
            for k in range(0, no_packets):
                output = self.sock.recv(receive)
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
                            ivalue_dec = 100*ivalue_dec/float(triggers)
                            int_data.append(ivalue_dec)
                            value_flag = 0
                    int_data.reverse()
                    print_data = [int(i) for i in int_data]
                    print "Channel %i:" % channels[k]
                    print print_data
                    # print int_data
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
            self.connection_error = 1
        except socket.error:
            print "Problems connecting to the system."
            output = ['Error']
            self.connection_error = 1
        finally:
            self.sock.close()
        # print output
        # print "output length: %i" % len(output)
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
            # print message
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
        # print "\nWriting register: %s Value: %s" % (hex(address), ''.join(str(e) for e in value))
        # Data from bit-string to hex bytes
        # print value
        if len(value) == 16:
            data_0 = value[8:16]
            data_1 = value[0:8]
            data_2 = [0]
            data_3 = [0]
        elif len(value) == 32:
            data_0 = value[24:32]
            data_1 = value[16:24]
            data_2 = value[8:16]
            data_3 = value[0:8]
        else:
            print "Invalid write -data."
        data_0 = ''.join(str(e) for e in data_0)
        data_1 = ''.join(str(e) for e in data_1)
        data_2 = ''.join(str(e) for e in data_2)
        data_3 = ''.join(str(e) for e in data_3)
        message = [0xca, 0x00, 0x01]
        message.append(0x01)  # R/W-byte
        message.extend([int(address_3, 16), int(address_2, 16), int(address_1, 16), int(address_0, 16)])
        message.extend([int(data_3, 2), int(data_2, 2), int(data_1, 2), int(data_0, 2)])
        output = self.execute_req(message, receive=10)
        # print "Reply: %s" % output
        return output

    def read_register(self, address):  # Address in dec
        address_hex = '0x%0*x' % (8, address)
        # print "Register address: %s" % address_hex
        # print "Reading register."
        address_3 = address_hex[2:4]
        address_2 = address_hex[4:6]
        address_1 = address_hex[6:8]
        address_0 = address_hex[8:10]
        message = [0xca, 0x00, 0x01]
        message.append(0x00)  # R/W-byte
        message.extend([int(address_3, 16), int(address_2, 16), int(address_1, 16), int(address_0, 16)])
        output = self.execute_req(message, receive=20)
        # print output
        output_bin = []
        output_bin.extend(dec_to_bin_with_stuffing(int(output[3], 16), 8))
        output_bin.extend(dec_to_bin_with_stuffing(int(output[2], 16), 8))
        output_bin.extend(dec_to_bin_with_stuffing(int(output[1], 16), 8))
        output_bin.extend(dec_to_bin_with_stuffing(int(output[0], 16), 8))

        ipbus_header = output[7]+output[6]+output[5]+output[4]

        crc_r1 = int(output[9], 16) << 8
        crc_r0 = int(output[8], 16)
        crc_received = crc_r1 + crc_r0

        crc_c1 = int(output[11], 16) << 8
        crc_c0 = int(output[10], 16)
        crc_calculated = crc_c1 + crc_c0

        # print ipbus_header
        # print crc_received
        # print crc_calculated
        # print output_bin
        return output_bin

    def send_sync(self):
        message = [0xca, 0x00, 0x02]
        output = self.execute_req(message)
        return output

    def send_ext_reset(self):
        message = [0xca, 0xdd, 0x02]
        output = self.execute_req(message)
        return output

    def adjust_iref(self):
        message = [0xca, 0x00, 0x05]
        output = self.execute_req(message)
        return output

    def int_adc_calibration(self, start, step, stop):
        message = [0xca, 0x00, 0x06, start, step, stop]
        output = self.execute_req(message, timeout=30, no_packets=1)
        return output

    def cal_dac_calibration(self, start, stop, step):
        message = [0xca, 0x00, 0x07, start, step, stop]
        output = self.execute_req(message, no_packets=2, timeout=30)
        return output

    def run_scurve(self, start_ch, stop_ch, step_ch, cal_dac_start, cal_dac_stop, arm_dac, triggers, latency, obj):
        delay = 1
        d1 = obj.d1
        d2 = obj.d2

        cal_dac_array = range(cal_dac_start, cal_dac_stop+1, 1)

        message = [0xca, 0xff, 0x08, start_ch, stop_ch, step_ch, 0, 0, 0, latency >> 8, latency & 0xFF, triggers >> 8,
                   triggers & 0xFF, arm_dac, delay, d1 >> 8, d1 & 0xFF, d2 >> 8, d2 & 0xFF, 1, len(cal_dac_array)]
        print message
        for value in cal_dac_array:
            message.append(value)
        nr_channels = stop_ch - start_ch + 1
        output = self.execute_req(message, no_packets=nr_channels,  timeout=30, scurve="yes")

        # Re-run S-curve for specified channels

        for re_channel in obj.rerun_scurve_channel_list:
            message = [0xca, 0, 0x08, re_channel, re_channel, step_ch, obj.cal_dac_start_rerun, obj.cal_dac_stop_rerun, 1, latency >> 8,
                       latency & 0xFF,
                       triggers >> 8, triggers & 0xFF, arm_dac, delay, d1 >> 8, d1 & 0xFF, d2 >> 8, d2 & 0xFF]
            out = self.execute_req(message, no_packets=1, timeout=30, scurve="yes")
            time.sleep(0.5)
            output[re_channel] = out

        dead_channel_list = []
        for i, data in enumerate(output):
            if all(v == 0 for v in data):
                dead_channel_list.append(i)

        if len(dead_channel_list) < 100:
            for i, in dead_channel_list:
                print "Detected zero output in channel %s." % i
                print "Trying to re-run s-curve for it."
                for k in range(0, 3):
                    obj.register[i].mask[0] = 0
                    obj.write_register(i)
                    time.sleep(1)
                    message = [0xca, 0, 0x08, i, i, step_ch, cal_dac_start, cal_dac_stop, 1, latency >> 8, latency & 0xFF,
                               triggers >> 8, triggers & 0xFF, arm_dac, delay, d1 >> 8, d1 & 0xFF, d2 >> 8, d2 & 0xFF]
                    out = self.execute_req(message, no_packets=1, timeout=30, scurve="yes")
                    if not all(v == 0 for v in out):
                        break
                    time.sleep(0.5)
                output.pop(i)
                output.insert(i, out)

        return output

    def run_dac_scan(self, start, step, stop, mon_sel):
        message = [0xca, 0x00, 0x09, start, step, stop, 0, 0, 0, mon_sel]
        output = self.execute_req(message,  timeout=30)
        return output

    def read_ext_adc_imon(self):
        message = [0xca, 0x00, 0x03, 0x49, 0x01]
        output = self.execute_req(message,  timeout=30, receive=20)
        return output

    def read_ext_adc_vmon(self):
        message = [0xca, 0x00, 0x03, 0x49, 0x00]
        output = self.execute_req(message,  timeout=10, receive=20)
        return output

    def read_ext_adc_vbgr(self):
        message = [0xca, 0x00, 0x03, 0x49, 0x02]
        output = self.execute_req(message,  timeout=10, receive=20)
        return output

    def run_bist(self):
        message = [0xca, 0x00, 0x0a]
        output = self.execute_req(message, timeout=10)
        return output

    def read_avdd_power(self):
        message = [0xca, 0x00, 0x03, 0x48, 0x00]
        output = self.execute_req(message,  timeout=10, receive=20)
        if output[0] != 'Error':
            msb = int(output[1], 16) << 8
            lsb = int(output[0], 16)
            avdd_value_int = msb + lsb
            avdd_value_mv = avdd_value_int * 0.0625
            # print "AVDD voltage: %f" % avdd_value_mv
            avdd_value_current = avdd_value_mv * 0.2346 - 4.17
            avdd_power = avdd_value_current * 1.2
            print "Power AVDD: %f" % avdd_power
            return avdd_power
        else:
            return 'Error'

    def read_dvdd_power(self):
        message = [0xca, 0x00, 0x03, 0x48, 0x01]
        output = self.execute_req(message,  timeout=10, receive=20)
        if output[0] != 'Error':
            msb = int(output[1], 16) << 8
            lsb = int(output[0], 16)
            dvdd_value_int = msb + lsb
            dvdd_value_mv = dvdd_value_int * 0.0625
            dvdd_value_current = dvdd_value_mv * 0.2346 - 4.17
            dvdd_power = dvdd_value_current * 1.2
            # print "DVDD voltage: %f" % dvdd_value_mv
            print "Power DVDD: %f" % dvdd_power
            return dvdd_power
        else:
            return 'Error'

    def read_iovdd_power(self):
        message = [0xca, 0x00, 0x03, 0x48, 0x02]
        output = self.execute_req(message,  timeout=10, receive=20)
        if output[0] != 'Error':
            msb = int(output[1], 16) << 8
            lsb = int(output[0], 16)
            iovdd_value_int = msb + lsb
            iovdd_value_mv = iovdd_value_int * 0.0625
            iovdd_value_current = iovdd_value_mv * 0.2346 - 4.17
            iovdd_power = iovdd_value_current * 2.5
            # print "IOVDD voltage: %f" % iovdd_value_mv
            print "Power IOVDD: %f" % iovdd_power
            return iovdd_power
        else:
            return 'Error'

    def test_trigger_bits(self, message, ch):
        error = [0, 0]
        print "\nTesting TU_TX%s." % ch
        # print "\nSending:"
        # print message
        # print "Reply:"
        output0 = self.execute_req(message,  timeout=30)
        # print output0
        nr_packets = (len(output0)-4)/8
        if not output0[-4]:
            print "ERROR: SoT signal is broken."
            error[0] = 1
            error[1] = 1

        temp_list = [0]*8
        for i in range(0, nr_packets):
            # print "Packet nr: %s" % i
            output = output0[i*8:i*8+8]
            sorted_output = [int(output[4], 16), int(output[5], 16), int(output[6], 16), int(output[7], 16), int(output[0], 16), int(output[1], 16), int(output[2], 16), int(output[3], 16)]
            # print sorted_output
            fired_channels = dec_to_bin_with_stuffing(sorted_output[ch], 8)
            # print "Trigger output"
            # print fired_channels
            # print ""
            temp_list[0] += fired_channels[0]
            temp_list[1] += fired_channels[1]
            temp_list[2] += fired_channels[2]
            temp_list[3] += fired_channels[3]
            temp_list[4] += fired_channels[4]
            temp_list[5] += fired_channels[5]
            temp_list[6] += fired_channels[6]
            temp_list[7] += fired_channels[7]
            #print temp_list
        print temp_list
        sum1 = temp_list[0] + temp_list[2] + temp_list[4] + temp_list[6]
        sum2 = temp_list[1] + temp_list[3] + temp_list[5] + temp_list[7]
        if sum1 > 11 and sum2 == 0:
            print "TU_TX%s working.\n" % ch
        else:
            print "ERROR: TU_TX%s not working.\n" % ch
            error[1] = 1

        return error

    def sbit_phase_alingment(self):
        error = 0
        message = [0xca, 0xdd, 0x09]
        # print "Trigger bit phase alignment."
        # print "Sending:"
        # print message
        output = self.execute_req(message,  timeout=10, receive=20)
        # print "Received:"
        # print output
        if len(output) != 4:
            print output
            error = 1
        return error

