import serial
import time
from os import listdir
from os.path import islink

class os1327dInterface:
    def __init__(self):
        serial_id_list = listdir('/dev/serial/by-id')
        for serial_id in serial_id_list:
            print serial_id
            if "Prolific" in serial_id:
                print "Found: %s" % serial_id
                if islink('/dev/serial/by-id/%s' % serial_id):
                    print "Hellurei"
        self.open_connection()
        self.close_connection()

    def open_connection(self):
        self.ser = serial.Serial(
            port='/dev/ttyUSB1',
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=10)

        print("connected to: " + self.ser.portstr)

    def read_value(self):
        self.open_connection()
        encoding_flag = 0
        received_bytes = []
        run_flag = 1
        while run_flag == 1:
            for c in self.ser.read():
                input_byte = c.encode('hex')
                # print input_byte
                received_bytes.append(input_byte)
                if encoding_flag >= 1:
                    encoding_flag += 1
                if input_byte == "02" and encoding_flag == 0:
                    # print "Start of packet."
                    encoding_flag = 1
                    received_bytes = []
                if encoding_flag == 11 and input_byte == "03":
                    # print "End of Packet"
                    encoding_flag = 0
                    infrared_temp = int(received_bytes[0]+received_bytes[1], 16)/10.0
                    k_type_temp = int(received_bytes[2]+received_bytes[3], 16)/100.0
                    emissivity = int(received_bytes[4], 16)/100.0
                    timestamp = time.strftime("%H:%M:%S")
                    print "%s Infrared temperature: %s C, K-type: %s C" % (timestamp, infrared_temp, k_type_temp)
                    # outF = open(self.output_file, "a")
                    # outF.write("%s %s\n" % (timestamp, infrared_temp))
                    # outF.close()
                    run_flag = 0
        self.close_connection()
        return infrared_temp

    def close_connection(self):
            self.ser.close()


if __name__ == "__main__":   # This code is executed if the file is run as standalone.
    interface = os1327dInterface()
    while True:
        interface.read_value()
        time.sleep(1)

