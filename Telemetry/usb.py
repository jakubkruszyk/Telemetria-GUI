from Telemetry.globals import *
import serial
import serial.tools.list_ports as port_list


class USBReceiver:
    time = 0
    ser = serial.Serial()
    data = {}  # stores data received from USB port

    def __init__(self):
        port = self.available_ports()
        if port:
            self.connect_to_port(port[0])  # connect to first port on list by default

    def available_ports(self):  # returns list of available ports. Returns false if no ports are available
        ports = list(port_list.comports())
        if ports:
            for idx, val in enumerate(ports):
                ports[idx] = val[0]
            return ports
        else:
            return False

    def connect_to_port(self, port):  # method opens connection with USB port
        self.ser.close()
        try:
            self.ser = serial.Serial(port, BAUDRATE, BYTESIZE, PARITY, STOPBITS, TIMEOUT)
        except serial.SerialException:
            return "Can't connect to " + port + " port :/"

    def get_data_from_usb(self):  # method updates values in data dictionary
        try:
            if self.ser.is_open:
                id = self.ser.read(1).decode('utf-8')  # read first byte
                for key in DATA_PARAMETERS:
                    if id == DATA_PARAMETERS[key][0]:  # check if first byte is an ID
                        line = self.ser.readline().decode('utf-8')  # read message up to \n char
                        values = line[1:-3].split(";")
                        if len(values) > 1:
                            for i in range(len(values)):
                                self.data[key + " " + str(i)] = list(map(float, values))[i]  # inserts value from list of received data, to data dictionary
                        else:
                            self.data[key] = list(map(float, values))[0]
        except serial.SerialException:
            self.ser.close()
            return "Disconnected from USB port :/"

    def get(self):
        self.data["time"] = self.time
        self.get_data_from_usb()
        self.time += TIME_STEP
        return self.data
