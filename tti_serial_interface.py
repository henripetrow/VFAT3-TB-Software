import serial
import serial.tools.list_ports
import sys
import glob
import time


class TtiSerialInterface:

    def __init__(self, baudrate=9600):

        # Instrument specific commands.
        self.ch1_voltage_req = "V1O?"
        self.ch2_voltage_req = "V2O?"
        self.ch1_voltage_set = "V1"
        self.ch2_voltage_set = "V2"
        self.ch1_current_req = "I1O?"
        self.ch2_current_req = "I2O?"
        self.ch1_current_set = "I1"
        self.ch2_current_set = "I2"
        self.turn_off_outputs = "OPALL 0"
        self.turn_on_outputs = "OPALL 1"
        self.req_ch1_state = "OP1?"
        self.req_ch2_state = "OP2?"
        self.instrument_identification = "*IDN?"

        self.psu_found = 0

        # test which port is the right one by requesting ID.
        print "Looking for connected PSU."
        ports = glob.glob('/dev/ttyACM*')
        if len(ports) == 1:
            self.serial_port = ports[0]
            self.ser = serial.Serial(self.serial_port, baudrate=baudrate, timeout=0.01)
            for i in range(1, 10):
                time.sleep(2)
                self.device_ID = self.req_device_id()
                if "THURLBY" in self.device_ID:
                    self.psu_found = 1
                    print "Found PSU: %s" % self.device_ID
                    print "From port: %s" % ports[0]
                    break
                else:
                    self.psu_found = 0
                print "PSU port found, waiting for response. %s" % i
        else:
            for port in ports:
                self.serial_port = port
                self.ser = serial.Serial(self.serial_port, baudrate=baudrate, timeout=0.01)
                self.device_ID = self.req_device_id()
                if "THURLBY" in self.device_ID:
                    self.psu_found = 1
                    print "Found PSU: %s" % self.device_ID
                    print "From port: %s" % port
                    break
                else:
                    self.psu_found = 0

    # Functions

    def execute(self, data):
        self.ser.write(data)
        self.ser.write("\x0A")
        data = self.ser.read(100)  # Read up to 100 bytes
        data = data.rstrip()
        return data

    def read_float(self, command):
        output_data = self.execute(command)
        return_data = float(output_data[:-1])
        return return_data

    def read_int(self, command):
        return int(self.execute(command))

    def req_ch1_current(self):
        return self.read_float(self.ch1_current_req)

    def req_ch2_current(self):
        return self.read_float(self.ch2_current_req)

    def set_ch1_current_limit(self, current):
        command = self.ch1_current_set + " %f" % current
        return self.execute(command)

    def set_ch2_current_limit(self, current):
        command = self.ch2_current_set + " %f" % current
        return self.execute(command)

    def req_ch1_voltage(self):
        return self.read_float(self.ch1_voltage_req)

    def set_ch1_voltage(self, voltage):
        command = self.ch1_voltage_set + " %f" % voltage
        return self.execute(command)

    def req_ch2_voltage(self):
        return self.read_float(self.ch2_voltage_req)

    def set_ch2_voltage(self, voltage):
        command = self.ch2_voltage_set + " %f" % voltage
        return self.execute(command)

    def req_device_id(self):
        return self.execute(self.instrument_identification)

    def set_outputs_off(self):
        return self.execute(self.turn_off_outputs)

    def set_outputs_on(self):
        return self.execute(self.turn_on_outputs)

    def req_output_states(self):
        states = [0, 0]
        states[0] = self.read_int(self.req_ch1_state)
        states[1] = self.read_int(self.req_ch2_state)
        return states



if __name__ == "__main__":   # This code is executed if the file is run as standalone.
    import time
    tti_if = TtiSerialInterface()
    print "Device ID:"
    print tti_if.req_device_id()
    tti_if.set_outputs_on()
    time.sleep(3)
    print "Channel 1 voltage: %.4f" % tti_if.req_ch1_voltage()
    print "Channel 1 current: %.4f" % tti_if.req_ch1_current()
    print "Channel 2 voltage: %.4f" % tti_if.req_ch2_voltage()
    print "Channel 2 current: %.4f" % tti_if.req_ch2_current()
    tti_if.set_outputs_off()
