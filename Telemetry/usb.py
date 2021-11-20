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
            return ports[0]
        else:
            return False

    def connect_to_port(self, port):  # method opens connection with USB port
        self.ser = serial.Serial(port, BAUDRATE, BYTESIZE, PARITY, STOPBITS, TIMEOUT)

    def get_data_from_usb(self):  # method updates values in data dictionary
        try:
            if self.ser.is_open:
                id = self.ser.read(1).decode('utf-8')  # read first byte
                for key in ID:
                    if id == ID[key]:  # check if first byte is an ID
                        line = self.ser.readline().decode('utf-8')  # read message up to \n char
                        values = line[1:-3].split(";")
                        # self.data[key] = list(map(float, values))  # inserts list of received data, to data dictionary
                        self.data[key] = list(map(float, values))[0]  # inserts first value from list of received data, to data dictionary
        except serial.SerialException:
            self.ser.close()
            return "Disconnected from USB port :/"

    def get(self):
        self.data["time"] = self.time
        self.get_data_from_usb()
        self.time += TIME_STEP
        return self.data
