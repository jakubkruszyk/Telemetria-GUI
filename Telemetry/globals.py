# main window parameters
WINDOW_TITLE = "Wacław - Telemetria"
SIDE_MENU_WIDTH = 150
TOP_MENU_SIZE = 40
GUI_THEME = "DarkGrey5"
ICON_PATH = r"Docs\\img\\logo.png"

PLOT_LAYOUT_TYPES = ("Indicators", "1x1", "2x1", "2x2")
DATA_SOURCES = ("Auto", "USB", "Cloud")
DATA_REFRESH_ICON_PATH = r"Docs\\img\\refresh_icon.png"
AVAILABLE_PLOTS = ["None"]

# plot window parameters
PLOTS_PADDING = 10
PLOTS_Y_OFFSET = 50
PLOTS_MARGINS = 0.05
PLOTS_DEFAULT_RANGES = (20, 20)
PLOTS_POINTS = 150

# indicators window parameters
INDICATORS_GRID = (8, 7)

# DataContainer parameters
AUTO_LOG = False
AUTO_LOG_COUNT = 100
TIME_STEP = 20/150

# UART connection parameters
import serial
BAUDRATE = 115200
BYTESIZE = serial.EIGHTBITS
PARITY = serial.PARITY_NONE
STOPBITS = serial.STOPBITS_ONE
TIMEOUT = 0.05  # time which readline() method wait for \n symbol. Value should be grater than bytes_in_the_longest_frame * 10 / baudrate

# UART values parameters
DATA_PARAMETERS = {"Battery packages voltage": ('V', 28), "Battery voltage": ('B', 1), "Battery temperatures": ('T', 12), "State of charge": ('S', 1)}

# Create AVAILABLE_PLOTS based on UART values parameters
for data in DATA_PARAMETERS:
    n = DATA_PARAMETERS[data][1]
    if n > 1:
        for i in range(n):
            AVAILABLE_PLOTS.append(data + " " + str(i))
    else:
        AVAILABLE_PLOTS.append(data)