import globals as gb
import serial
import serial.tools.list_ports as port_list

port = "COM1"
ser = serial.Serial()
connected = False


def connect():
    global ser, connected
    ser.close()
    try:
        ser = serial.Serial(port, gb.BAUDRATE, gb.BYTESIZE, gb.PARITY, gb.STOPBITS, gb.TIMEOUT)
        connected = True
        return None
    except serial.SerialException:
        return "Can't connect to " + port + " port :/"


def disconnect():
    global connected
    if connected:
        ser.close()
        connected = False


def available_ports():
    if not connected:
        return ["None"]

    ports = list(port_list.comports())
    if ports:
        for idx, val in enumerate(ports):
            ports[idx] = val[0]
        return ports
    else:
        return None


# TODO debugging
def get_data():
    if not connected:
        return None

    usb_data = dict()
    try:
        if ser.is_open:
            signal_id = ser.read(1).decode('utf-8')  # read first byte
            line = ser.readline().decode('utf-8')  # read message up to \n char
            for key in gb.DATA_PARAMETERS:
                if signal_id == gb.DATA_PARAMETERS[key][0]:  # check if first byte is an ID
                    values = line[1:-3].split(";")
                    if len(values) > 1:
                        for i in range(len(values)):
                            # inserts value from list of received data, to data dictionary
                            usb_data[key + " " + str(i)] = list(map(float, values))[i]
                    else:
                        usb_data[key] = list(map(float, values))[0]
            return usb_data
        else:
            return None

    except serial.SerialException:
        return None
