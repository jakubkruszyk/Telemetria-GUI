from Telemetry.globals import *


class DataContainer:
    data = {k: [0 for _ in range(PLOTS_DEFAULT_RANGES[0])] for k in AVAILABLE_PLOTS}
    data["time"] = [0 for _ in range(PLOTS_DEFAULT_RANGES[0])]
    new_ready = False

    def update(self, values):  # values should be a dict
        for key in values:
            self.data[key].append(values[key])
        self.new_ready = True

    def read_range(self):
        self.new_ready = False
        data_range = {k: self.data[k][(-PLOTS_DEFAULT_RANGES[0] - 1):-1] for k in self.data}
        return data_range

    def read_last(self):
        last_data = {k: self.data[k][-1] for k in self.data}
        return last_data


if __name__ == "__main__":
    d = DataContainer()
    test_dict = {"time": 0, "None": 1, "Random": 17}
    d.update(test_dict)
    d.update(test_dict)
    print(d.data)
    # print(d.read_last())
