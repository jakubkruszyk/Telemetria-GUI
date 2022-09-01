import serial
# main window parameters
WINDOW_TITLE = "Wacław - Telemetria"
GUI_THEME = "DarkGrey5"

# in pixels
SIDE_MENU_WIDTH = 150
TOP_MENU_SIZE = 40


# paths are relative to run.py file
ICON_PATH = r"img\\logo.png"
CONFIG_PATH = r"configs.json"
DATA_REFRESH_ICON_PATH = r"img\\refresh_icon.png"

DATA_SOURCES = ("Cloud", "USB")

# how often app will query for new data (in seconds)
QUERY_RATE = 1

# indicators window parameters
# (rows, columns)
INDICATORS_GRID = (15, 4)
COLORS = {"Warning": "#fcca03", "Error": "#ff0000"}

# Influx parameters
TOKEN = "xX_L0QKGV2wp2T0kKTHWHIWCAIvP7eNG0514PvT6wuACfwTOSVso_EZCtDA7t3nmRZ5rLTAJrD0wvy41XGivjQ=="
ORG = "Test"
BUCKET = "Pomiary"
URL = "192.168.1.29:8086"

# UART connection parameters
BAUDRATE = 115200
BYTESIZE = serial.EIGHTBITS
PARITY = serial.PARITY_NONE
STOPBITS = serial.STOPBITS_ONE
TIMEOUT = 0.05  # time which readline() method wait for \n symbol.
# Value should be grater than bytes_in_the_longest_frame * 10 / baudrate
WAIT_FOR_ALL = False

# Tracked values parameters -> { Name: [ ID, how_many, [max_err, max_war, min_war, min_err] ] }
# ID is only used for usb connection
# error and warning values can be also changed from popup menu (Settings)
DATA_PARAMETERS = {"Cell voltage": ['V', 28, [4.3, 4.2, 3.6, 3.4]], "Battery voltage": ['B', 1, [74, 72, 68, 66]],
                   "Battery temp": ['T', 12, [60, 50, 10, 0]], "SoC": ['S', 1, [110, 105, 30, 15]]}

# ======================================================================================================================
# Do not change anything below
# ======================================================================================================================

# Create AVAILABLE_VARS based on values parameters - shortcut for accessing window elements
AVAILABLE_VARS = list()
for data in DATA_PARAMETERS:
    n = DATA_PARAMETERS[data][1]
    for i in range(n):
        AVAILABLE_VARS.append(data + " " + str(i))
