############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################

from SC_encode import *
import time


def decode_scurve_data(data_list, channel, nr_triggers=100, nr_dac_values=20):

    datapacket_status = "IDLE"
    datapacket_byte_counter = 0

    HDR_1 = "00011110"  # Basic Data Packet
    HDR_1W = "01011110"  # Basic Data Packet, With FIFO half full -warning

    BC_size = 2
    data_size = 16
    crc_size = 2
    hit_counter = 0
    data_packet_counter = 0
    hit_list = []
    data_packet_data = ""
    data_packet_crc = ""
    data_packet_crc_calc = ""
    if data_list is None:
        pass
    elif any(data_list):
        for i in data_list:
            if i == 0:
                pass
            else:
                line = bin(i)
                line = line.replace('b', '0')
                if data_packet_counter >= nr_triggers:
                    hit_list.append(hit_counter)
                    data_packet_counter = 0
                    hit_counter = 0


                input_value = line[-8:]

                if datapacket_status != "IDLE":
                    data_packet_crc_calc += input_value

                if (input_value == HDR_1 or input_value == HDR_1W) and datapacket_status == "IDLE":  # See if the read line is Header 1.
                    data_packet_crc_calc += input_value
                    datapacket_status = "EC"  # If EC counter size is not zero, we change the status to EC
                    datapacket_byte_counter = 0  # Set byte counter to zero. This is used to count the number of bytes to be read in different stages.

                elif datapacket_status == "EC":  # Enter the EC to collect the bytes for EC.e
                    datapacket_status = "BC"

                elif datapacket_status == "BC":  # Enter the BC to collect the bytes for BC.
                    datapacket_byte_counter += 1  # Byte counter is incremented by one to count the amount of BC bytes.
                    if datapacket_byte_counter >= BC_size:  # If byte counter is >= than size of BC we have all BC bytes and we can move to next state.
                        datapacket_status = "DATA"  # Set state to DATA
                        datapacket_byte_counter = 0  # Set the byte counter to 0 for the next state.

                elif datapacket_status == "DATA":  # Enter the DATA state to collect the bytes for DATA.
                    data_packet_data += input_value  # Input value is added to the data.
                    datapacket_byte_counter += 1  # Byte counter is incremented by one to count the amount of data bytes.
                    if datapacket_byte_counter >= data_size:  # If byte counter is >= than data_size we have all data bytes and we can move to next state.
                        data_packet_data = data_packet_data[::-1]
                        if data_packet_data[channel] == "1":
                            hit_counter += 1
                        datapacket_status = "CRC"  # Set state to CRC.
                        datapacket_byte_counter = 0  # Set the byte counter to 0 for the next state.
                        data_packet_data = ""

                elif datapacket_status == "CRC":  # Enter the DATA state to collect the bytes for DATA.
                    data_packet_crc += input_value  # Input value is added to the data.
                    datapacket_byte_counter += 1  # Byte counter is incremented by one to count the amount of data bytes.
                    if datapacket_byte_counter >= crc_size:  # If byte counter is >= than data_size we have all data bytes and we can move to next state.
                        data_packet_counter += 1
                        datapacket_status = "IDLE"  # Set state to IDLE.
                        datapacket_byte_counter = 0  # Set the byte counter to 0 for the next state.
                        received_crc_int = int(data_packet_crc, 2)
                        calculated_crc = crc_remainder(list(data_packet_crc_calc[:-16]))

                        if received_crc_int != calculated_crc:
                            print("!-> data packet CRC error.")
                        else:
                            pass
                        data_packet_crc = ""
                        data_packet_crc_calc = ""

    return hit_list
