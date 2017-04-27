############################################
# Created by Henri Petrow 2017
# Lappeenranta University of Technology
###########################################

def write_instruction(input_file, BCd, command, erase):
    if erase == 1:
        open(input_file, 'w').close() 
    BCd = dec_to_bin_with_stuffing(BCd,12)
    BCd = ''.join(str(e) for e in BCd)
    with open(input_file, "a") as myfile:
        myfile.write("%s%s\n" % (BCd,command))

def write_register_default_values(value):
    data = []
    with open('data/register_default_values.dat', 'rU') as f:
        for line in f:
            line = line.rstrip('\n')
            split_line = line.split()
            data.append(split_line[1])

    if value == "INTERACTIVE":
        open("./data/FPGA_instruction_list.dat", 'w').close()

    BCd = 1
    addr = 0
    transaction_ID = 1         #Function to handle this.
        
    ipbus = IPbus14_package(addr,data,147,0,transaction_ID)
    paketti = HDLC_package(ipbus)
    paketti = binary_to_sc(paketti)

    BCvalue = dec_to_bin_with_stuffing(BCd,12)
    BCvalue = ''.join(str(e) for e in BCvalue)
    data = "%s%s\n" % (BCvalue,FCC_LUT[paketti[0]]) # To get the right starting BCd
    with open("./data/FPGA_instruction_list.dat", "a") as myfile:
        myfile.write("%s" % data)
    for x in range(1,len(paketti)):
        data = "%s%s\n" % (BCvalue,FCC_LUT[paketti[x]])    # Rest instructions will be written with increment 1
        with open("./data/FPGA_instruction_list.dat", "a") as myfile:
            myfile.write("%s" % data)


def dec_to_bin_with_stuffing(inn, size):
    out = [int(x) for x in bin(inn)[2:]]
    for x in range(len(out), size):
        out.insert(0,0)
    return out

def data_packet_bit_stuffing(data):
    out = []
    SC1_counter = 0
    for x in range(0,len(data)):
        if data[x] == 1:
            SC1_counter += 1
            out.extend([1])
            if SC1_counter == 5:
                out.extend([0])
                SC1_counter = 0
        elif data[x] == 0:
            out.extend([0])
            SC1_counter = 0
    return out

def crc_remainder(input_package):
    polynomial_bitstring = 4129
    crc = 65535

    input_package_len = len(input_package)/8

    for j in range(0,input_package_len):
        input_bitstring = input_package[(j*8):((j+1)*8)]
        input_bitstring.reverse()
        input_bitstring = ''.join(str(e) for e in input_bitstring)





        for i in range(7,-1,-1):

            crc_bin = bin(crc)				# Convert CRC dec to bin.
            crc_bin = crc_bin[2:]			#
            crc_len = len(crc_bin)			#
            crc_bin = (16-crc_len)*'0' + crc_bin	#

            if int(input_bitstring[i],2)^int(crc_bin[0],2) == 1:

                crc_bin = crc_bin[1:]+'0'
                crc = int(crc_bin,2)
                crc =crc^polynomial_bitstring
            else:
                crc_bin = crc_bin[1:]+'0'
                crc = int(crc_bin,2)
    return crc

