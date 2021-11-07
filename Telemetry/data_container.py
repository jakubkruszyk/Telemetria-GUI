from Telemetry.globals import *
import numpy as np


# test 
class DataContainer:
    data = {k: [0 for _ in range(PLOTS_POINTS)] for k in AVAILABLE_PLOTS}
    data["time"] = np.arange(-1 * PLOTS_DEFAULT_RANGES[0], 0.1, TIME_STEP).tolist()
    new_ready = False

    def update(self, values):  # values should be a dict
        for key in values:
            self.data[key].append(values[key])
        self.new_ready = True

    def read_range(self):
        self.new_ready = False
        data_range = {k: self.data[k][(-1 * PLOTS_POINTS - 1):-1] for k in self.data}
        return data_range

    def read_last(self):
        last_data = {k: self.data[k][-1] for k in self.data}
        return last_data
# test comment