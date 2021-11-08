from Telemetry.globals import *
import serial
import serial.tools.list_ports as port_list
import logging


# TODO zmienić logging na return z komunikatem -> będziemy to wyświetlać w oknie albo popupie
class USBReceiver:
    time = 0
    ser = serial.Serial()
    dataFromUSB = {k: -1 for k in AVAILABLE_PLOTS}  # przechowuje dane odczytane z USB

    def __init__(self):
        if not self.connect_to_port():
            logging.error("Can't find any available ports :(")

    # TODO dodać odpowiednie błędy do except:
    def connect_to_port(self):  # metoda nawiązuje połączenie z portem COM
        ports = list(port_list.comports())  # zwraca wszystkie dostępne porty COM
        if not ports:
            return False
        print("Available ports:")
        for p in ports:
            print(p)
        self.ser.port = ports[0][0]  # używa pierwszego portu COM na liście
        self.ser.baudrate = BAUDRATE
        self.ser.bytesize = BYTESIZE
        self.ser.parity = PARITY
        self.ser.stopbits = STOPBITS
        self.ser.timeout = TIMEOUT
        try:
            self.ser.open()
        except:
            logging.error("Can't open port " + self.ser.name)  # ten błąd czasami wywala jak się odepnie USB w trakcie działania programu
        print("Data from port: " + self.ser.name)
        return True

    # TODO usunąć auto-connect, dodać odpowiednie błędy do except:,
    def get_data_from_usb(self):  # metoda aktualizuje słownik dataFromUSB w oparciu o dane otrzymane po USB
        if self.ser.is_open:
            try:
                line = self.ser.readline().decode('utf-8')
            except:
                self.ser.close()
                logging.error("Disconnected from USB port :/")
            else:
                if line != "":  # przy uruchamianiu programu, odzczytywane jest dużo pustych znaków nwm czemu
                    try:
                        if '\t' in line and '\n' in line:
                            line = line[1:-1].split(":")
                            self.dataFromUSB[line[0]] = int(line[1])
                        else:
                            raise Exception()
                    except:
                        # występuje jeśli informacja nie zostanie przesłana w całości,
                        # czyli prawie zawsze tuż po uruchomieniu programu
                        print('.', end='')
        else:
            self.connect_to_port()

    def get(self):
        data = {"time": self.time}
        self.get_data_from_usb()
        for key in AVAILABLE_PLOTS:
            data[key] = self.dataFromUSB.get(key, 0)  # 0 is default value when key is not found in dict
        self.time += TIME_STEP
        return data
