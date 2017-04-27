############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################



# Slow control:
# Syntax:   'Time' Write 'Reg(name of subregister)' 'Value/Increment(if in a repeat)(dec)'
#           'Time' Write 'Reg(dec number of register)' 'Value(bin)'
#           'Time' Read 'Address' 
# FCC:
# Syntax:
#           'Time' Send 'Command' 
#           'Time' Send_Repeat 'Command' '# times to repeat' 'interval' 
# Repeat: 
# Syntax: 
#           'Time' Repeat '# times to repeat' 
#           'Time' End_Repeat 





import time
import  os
from instruction_object import *


def generator(scan_name):
    modified_scan_name = scan_name.replace(" ", "_")
    input_file = "./routines/%s/instruction_list.txt" % modified_scan_name
    repeat_flag = 0
    repeat_times = 1
    generation_output_list = []
    generation_error_list = []
    instruction_list = instruction_object(modified_scan_name)
    start = time.time()
    with open(input_file, 'rU') as f:
        for line in f:
            if line[0] == "#":
                continue
            elif line == "\n":
                continue
            else:
                line = line.rstrip('\n')
                text = "LINE: %s" % line
                generation_output_list.append(text)
                split_line = line.split()
                try:
                    BCd = int(split_line[0])
                except ValueError:
                    text =  "-IGNORED: Invalid BCd value: %s" % split_line[0]
                    generation_output_list.append(text)
                    generation_error_list.append(text)
                    continue

                ######### Write to Slow Control
                if split_line[1] == "Write":
                    # Check the given parameters.
                    try:
                        value = int(split_line[3])
                    except ValueError:
                        text = "-IGNORED: Invalid value: %s" % split_line[3]
                        generation_output_list.append(text)
                        generation_error_list.append(text)
                        continue
                    reg = split_line[2]

                    if repeat_flag == 1:
                        text =  "-Write to Slow Control. Register: %s, Increment: %s" % (split_line[2], split_line[3])
                        generation_output_list.append(text)
                        instruction_list.add("WRITE_REPEAT", BCd, reg, value)
                    else:
                        text = "-Write to Slow Control. Register: %s, Data: %s" % (split_line[2], split_line[3])
                        generation_output_list.append(text)
                        instruction_list.clear()
                        instruction_list.add("WRITE", BCd, reg, value)
                        instruction_list.write_to_file()
                        instruction_list.clear()

                ######### Read from slow Control.
                elif split_line[1] == "Read":
                    text = "-Read from Slow Control. Address: %s" % split_line[2]
                    generation_output_list.append(text)
                    # Check the given parameters.
                    try:
                        addr = int(split_line[2])
                    except ValueError:
                        text = "-IGNORED: Invalid value for Address: %s" % split_line[2]
                        generation_output_list.append(text)
                        generation_error_list.append(text)
                        continue

                    # Add a new instruction and write if not in repeat -mode.
                    if repeat_flag == 1:
                        instruction_list.add("READ", BCd, addr, 0)
                    else:
                        instruction_list.clear()
                        instruction_list.add("READ", BCd, addr, 0)
                        instruction_list.write_to_file()
                        instruction_list.clear()

               ######### write default values to the register.
                elif split_line[1] == "Write_defaults":
                        instruction_list.write_register_defaults()

                ######### Send a single FCC command.
                elif split_line[1] == "Send":
                    text = "-Send a Fast Control Command: %s" % split_line[2]
                    generation_output_list.append(text)
                    command = split_line[2]

                    if repeat_flag == 1:
                        instruction_list.add("FCC", BCd, command, 0)
                    else:
                        instruction_list.clear()
                        instruction_list.add("FCC", BCd, command, 0)
                        instruction_list.write_to_file()
                        instruction_list.clear()

                ##### Start a repeat loop.
                elif split_line[1] == "Repeat":
                    text = "Starting repeat"
                    generation_output_list.append(text)
                    try:
                        repeat_times = int(split_line[2])
                    except ValueError:
                        text = "-IGNORED: Invalid value for repeat: %s" % split_line[2]
                        generation_output_list.append(text)
                        generation_error_list.append(text)                        
                        continue
                    repeat_flag = 1

                # End a repeat loop.
                elif split_line[1] == "End_Repeat":
                    repeat_flag = 0
                    for i in xrange(repeat_times):
                        instruction_list.write_to_file()
                    instruction_list.clear()
                    repeat_times = 0
                    text = "Ending repeat"
                    generation_output_list.append(text)
             
                # Send repatedly a FCC with a fixed interval
                elif split_line[1] == "Send_Repeat":
                    command = split_line[2]
                    try:
                        repeat = int(split_line[3])
                    except ValueError:
                        text = "-IGNORED: Invalid value for repeat: %s" % split_line[3]
                        generation_output_list.append(text)
                        generation_error_list.append(text) 
                        continue
                    try:
                        interval = int(split_line[4])
                    except ValueError:
                        text = "-IGNORED: Invalid value for interval: %s" % split_line[4]
                        generation_output_list.append(text)
                        generation_error_list.append(text) 
                        continue

                    text = "-Send a Fast Control Command. Command: %s, Repeat: %s, Interval: %s" % (command,repeat,interval)
                    generation_output_list.append(text)                    

                    if repeat_flag == 1:
                        instruction_list.add("FCC", BCd, command, 0)
                        for i in xrange(repeat-1):
    			        instruction_list.add("FCC", interval, command, 0)
                    else:
                        instruction_list.clear()
                        instruction_list.add("FCC", BCd, command, 0)
                        for i in xrange(repeat-1):
    			        instruction_list.add("FCC", interval, command, 0)
                        instruction_list.write_to_file()
                        instruction_list.clear()

                else:
                    text = "-Line ignored: %s" % line
                    generation_output_list.append(text)

    # Generation of the statistics.

    num_lines = sum(1 for line in open('./data/FPGA_instruction_list.dat'))
    b = os.path.getsize("./data/FPGA_instruction_list.dat")
    size = b/1000
    size = (num_lines*16)/1000
    time_ns = instruction_list.BCcounter*25
    # print time_ns
    time_us = time_ns/1000.0
    # print time_us
    time_ms = time_us/1000.0

    specs = [num_lines,size,instruction_list.BCcounter,time_ms]
    events = instruction_list.get_events()
    stop = time.time()
    print("Generation time (minutes):")
    print(stop - start)/60
    return [generation_output_list, generation_error_list, specs, events]






