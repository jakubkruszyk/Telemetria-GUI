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
        data = [self.time]
        for _ in AVAILABLE_PLOTS:
            data.append(random.randrange(-20, 20))
        self.time += 0.1
        return data
