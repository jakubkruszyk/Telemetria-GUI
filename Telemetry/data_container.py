from Telemetry.globals import *


class DataContainer:
    data = {k: [] for k in AVAILABLE_PLOTS}
    new_ready = False

    def update(self, values):
        for dat, val in zip(self.data, values):
            self.data[dat].append(val)
        self.new_ready = True

    def read(self):
        self.new_ready = False
        return self.data
