from Telemetry.data_container import DataContainer
from Telemetry.usb import USBReceiver

usb_receiver = USBReceiver()
# container = DataContainer()

# from Telemetry.windows.plot_window import PlotWindow
from Telemetry.windows.indicator_window import IndicatorWindow
from Telemetry.windows.plot_window import PlotWindow

main_window = IndicatorWindow()

