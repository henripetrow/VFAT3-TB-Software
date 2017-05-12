############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################

import csv

from SC_encode import *
from VFAT3_registers import *
from test_system_functions import *




class instruction_object:

    def __init__(self,modified_scan_name):
        self.BCcounter = 0
        self.instruction_list = []
        self.even_output_file =  "./routines/%s/output_events.csv" % modified_scan_name
        self.output_file =       "./routines/%s/FPGA_instruction_list.txt" % modified_scan_name
        open(self.output_file, 'w').close()
        self.SC_encoder = SC_encode()
        self.registers = register
        self.CalPulse_list = []
        self.FCC_list = []
        self.Register_change_list = []
        self.Register_read_list = []
        self.event_list = []
        self.instruction_write_list = []

    def get_events(self):
        self.event_list = [self.CalPulse_list,self.FCC_list,self.Register_change_list,self.Register_read_list]
        with open(self.even_output_file, "wb") as f:
            writer = csv.writer(f)
            writer.writerows(self.event_list)
        return self.event_list

    def add(self, command_type, BCd, command_addr_register, increment):
        new_instruction = [command_type, BCd, command_addr_register, increment]
        self.instruction_list.append(new_instruction)

    def clear(self):
        self.instruction_list = []

    def add_instruction(self,input_file, BCd, command, erase):
        self.instruction_write_list.append([BCd,command])

    def write_register_defaults():
        write_register_default_values("SCAN")

    def write_to_file(self,write_BCd_as_fillers):
        for line in self.instruction_list:
            command_type = line[0]
            BCd = line[1]
            idle_flag = 0
            if write_BCd_as_fillers:
                for x in range(1, BCd):
                    if idle_flag == 0:     
                        self.add_instruction(self.output_file, 1, "PPPP",0)
                        idle_flag = 1
                    else:
                        self.add_instruction(self.output_file, 1, "AAAA",0)
                        idle_flag = 0

            # FCC
            if command_type == "FCC":
                command = line[2]
                command_bin = FCC_LUT[command]  # Add error checks.  # BCd comes reversed?
                self.add_instruction(self.output_file, BCd, command_bin, 0)
                self.BCcounter = self.BCcounter + BCd


                # ###### Information collection
                if command == "CalPulse":
                    channel_list = []
                    for i in range(0, 129):
                        if not register[i].mask:             
                            if register[i].cal:
                                channel_list.append(i)
                    self.CalPulse_list.append([self.BCcounter,channel_list])
                else:
                    self.FCC_list.append([self.BCcounter,command])

            # READ
            elif command_type == "READ":
                data = 0
                addr = line[2]

                self.BCcounter = self.BCcounter + BCd
                output = self.SC_encoder.create_SC_packet(addr, data, "READ", self.BCcounter)
                paketti = output[0]
                self.add_instruction(self.output_file, BCd, FCC_LUT[paketti[0]], 0)
                for x in range(1, len(paketti)):
                    self.add_instruction(self.output_file, 1, FCC_LUT[paketti[x]], 0)
                    self.BCcounter = self.BCcounter + 1

                self.Register_read_list.append([self.BCcounter,addr])

            # WRITE
            elif command_type == "WRITE" or command_type == "WRITE_REPEAT":   			# ######### Need a read repeat.

                reg = line[2]
                str_reg = reg
                if isinstance(reg, (int, long)):
                    data = line[3]
                    addr = key[0]
                else:
                    try:
                        key = LUT[reg]
                    except ValueError:  # Muuta
                        print "-IGNORED: Invalid value for Register: %s" % reg
                        continue

                    addr = key[0]
                    variable = key[1]

                    current_value = register[addr].reg_array[variable][0]
                    size = register[addr].reg_array[variable][1]

                    if command_type == "WRITE_REPEAT":
                        increment = line[3]
                        new_value = current_value + increment

                    if command_type == "WRITE":
                        new_value = line[3]

                    if new_value < 0 or new_value > 2**(size)-1:
                        print "-IGNORED: Value out of the range of the register: %d" % new_value
                        continue
                    print new_value
                    register[addr].reg_array[variable][0] = new_value
                    
                    data = []
                    data_intermediate = []
                    for x in register[addr].reg_array:
                        data_intermediate = dec_to_bin_with_stuffing(x[0], x[1])
                        data_intermediate.reverse()
                        data.extend(data_intermediate)

                data.reverse()

                self.BCcounter = self.BCcounter + BCd
                output = self.SC_encoder.create_SC_packet(addr, data, "WRITE", self.BCcounter)
                paketti = output[0]
                trans_id = output[1]
                # Snapshots of register changes for the decoding of the outputdata.
                self.Register_change_list.append([self.BCcounter, str_reg, new_value, trans_id])
 
                # Write instructions
                self.add_instruction(self.output_file, BCd, FCC_LUT[paketti[0]], 0)  # To get the right starting BCd
                for x in range(1,len(paketti)):
                    self.add_instruction(self.output_file, 1, FCC_LUT[paketti[x]], 0)  # To get the right starting BCd
                    self.BCcounter = self.BCcounter + 1

        write_instruction_list(self.output_file, self.instruction_write_list)







