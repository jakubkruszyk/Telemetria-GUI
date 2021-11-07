# =====================================================================================================================================
# generates random data for testing purposes
# =====================================================================================================================================
from Telemetry.globals import *
import random


class Generator:
    time = 0

    def __init__(self, seed):
        random.seed(seed)

    def get(self):
        data = {"time": self.time}
        for key in AVAILABLE_PLOTS:
            if key == "Only 1":
                data[key] = 1
            else:
                data[key] = random.randrange(-20, 20)
        self.time += TIME_STEP
        return data
# test comment