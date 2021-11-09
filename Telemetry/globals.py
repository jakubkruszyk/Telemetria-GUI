# main window parameters
WINDOW_TITLE = "Wacław - Telemetria"
SIDE_MENU_WIDTH = 150
TOP_MENU_SIZE = 40
GUI_THEME = "DarkGrey5"
ICON_PATH = r"Docs\\img\\logo.png"

PLOT_LAYOUT_TYPES = ("Indicators", "1x1", "2x1", "2x2")
DATA_SOURCES = ("Auto", "USB", "Cloud")
DATA_REFRESH_ICON_PATH = r"Docs\\img\\refresh_icon.png"
AVAILABLE_PLOTS = ("None", "Random", "Only 1", "Battery voltage", "Battery temperature")

# plot window parameters
PLOTS_PADDING = 10
PLOTS_Y_OFFSET = 50
PLOTS_MARGINS = 0.05
PLOTS_DEFAULT_RANGES = (20, 20)
PLOTS_POINTS = 150

# DataContainer parameters
AUTO_LOG = False
AUTO_LOG_COUNT = 100
TIME_STEP = 20/150


# UART connection parameters
import serial
BAUDRATE = 9600
BYTESIZE = serial.EIGHTBITS
PARITY = serial.PARITY_EVEN
STOPBITS = serial.STOPBITS_ONE
TIMEOUT = 0.01
