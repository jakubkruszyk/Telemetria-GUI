from Telemetry import main_window, container, PlotWindow, IndicatorWindow, usb_receiver
from Telemetry.data_generator import Generator
from Telemetry.globals import *

main_window.create_window()
generator = Generator(2)

while True:
    event = main_window.read_window()
    if event == "closed":
        break

    elif event == "layout":
        new_layout = main_window.selected_layout
        if new_layout == PLOT_LAYOUT_TYPES[0]:
            main_window = IndicatorWindow()
        else:
            main_window = PlotWindow(layout=new_layout)
        main_window.create_window()

    # container.update(generator.get())
    container.update(usb_receiver.get())
    main_window.update_data(container.read_last())
