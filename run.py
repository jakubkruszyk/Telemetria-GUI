from Telemetry.globals import *
from Telemetry import main_window, usb_receiver
import random
import time

main_window.create_window()

data_gen = {"time": 0}


# simple random data generator
def gen():
    global data_gen
    data_gen["time"] += 1
    for key in DATA_PARAMETERS:
        n = DATA_PARAMETERS[key][1]
        min = DATA_PARAMETERS[key][-1][-1]
        max = DATA_PARAMETERS[key][-1][0]
        for i in range(n):
            data_gen[f"{key} {i}"] = round(random.uniform(0.9*min, 1.1*max), 2)


gen()  # generate initial data


while True:
    event = main_window.read_window()
    if event == "closed":
        break

    # elif event == "layout":
    #     new_layout = main_window.selected_layout
    #     if new_layout == PLOT_LAYOUT_TYPES[0]:
    #         main_window = IndicatorWindow()
    #     else:
    #         main_window = PlotWindow(layout=new_layout)
    #     main_window.create_window()

    # container.update(usb_receiver.get())
    # main_window.update_data(container.read_last())

    main_window.update_data(data_gen)
    gen()
    # time.sleep(1)
