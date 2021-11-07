# =====================================================================================================================================
# generates random data for testing purposes
# =====================================================================================================================================
from Telemetry.globals import *
import random
import serial
import serial.tools.list_ports as port_list
import logging


class Generator:
    time = 0
    ser = serial.Serial()
    dataFromUSB = {"Battery voltage": -1, "Battery temperature": -1}  # przechowuje dane odczytane z USB

    def __init__(self, seed):
        random.seed(seed)
        if not self.connectToPort():
            logging.error("Can't find any available ports :(")

    def connectToPort(self): # metoda nawiązuje połączenie z portem COM
        ports = list(port_list.comports())  # zwraca wszystkie dostępne porty COM
        if not ports:
            return False
        print("Available ports:")
        for p in ports:
            print(p)
        self.ser.port = ports[0][0]  # używa pierwszego portu COM na liście
        self.ser.baudrate = 9600
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_EVEN
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 0.01
        try:
            self.ser.open()
        except:
            logging.error("Can't open port " + self.ser.name)  # ten błąd czasami wywala jak się odepnie USB w trakcie działania programu
        print("Data from port: " + self.ser.name)
        return True

    def getDataFromUSB(self):  # metoda aktualizuje słownik dataFromUSB w oparciu o dane otrzymane po USB
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
                        print('.', end='') # występuje jeśli informacja nie zostanie przesłana w całości, czyli prawie zawsze tuż po uruchomieniu programu
        else:
            self.connectToPort()

    def get(self):
        data = {"time": self.time}
        self.getDataFromUSB()
        for key in AVAILABLE_PLOTS:
            if key == "Only 1":
                data[key] = 1
            elif key == "Random":
                data[key] = random.randrange(-20, 20)
            elif key == "Battery voltage" or key == "Battery temperature":
                data[key] = self.dataFromUSB[key]
            else:
                data[key] = 0
        self.time += TIME_STEP
        return data

