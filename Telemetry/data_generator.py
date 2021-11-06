# =====================================================================================================================================
# generates random data for testing purposes
# =====================================================================================================================================
from Telemetry.globals import *
from random import seed, randrange

seed(2)
time = 0


def generate():
    global time
    temp = [time]
    for _ in AVAILABLE_PLOTS:
        temp.append(randrange(-20, 20))
    time += 0.1
    return temp
        