from Telemetry.globals import *
import PySimpleGUI as sg
import base64
from Telemetry import usb_receiver


# convert png/jpg to base64, most portable way because .ico works only on Windows
def img_to_64(path):
    with open(path, "rb") as file:
        icon = file.read()
        return base64.encodebytes(icon)


class BaseWindow:
    window = None
    selected_data_source = DATA_SOURCES[0]
    selected_layout = PLOT_LAYOUT_TYPES[0]
    connected = False

    # =====================================================================================================================================
    # layouts for gui sections
    # =====================================================================================================================================
    def side_menu_layout(self):
        return [[sg.Text("Layout Type")],
                [sg.Combo(values=PLOT_LAYOUT_TYPES, default_value=self.selected_layout, key="-layout_type-",
                          enable_events=True, readonly=True)],
                [sg.Text("Data source")],
                [sg.Combo(values=DATA_SOURCES, default_value=self.selected_data_source, key="-data_source-",
                          enable_events=True, readonly=True)],
                [sg.pin(sg.Column(self.usb_settings_layout(), key="-usb_settings-", visible=False, pad=0))],
                [sg.Button("Create new window")],
                [sg.Button("Close all")]
                ]

    def usb_settings_layout(self):
        bcg = sg.theme_background_color()
        available_ports = usb_receiver.available_ports()
        no_ports = False
        if not available_ports:
            available_ports = ['-']
            no_ports = True

        return [[sg.Text("COM Port:")],
                [sg.Combo(values=available_ports, default_value=available_ports[0], key="-selected_com-",
                          enable_events=True, readonly=True, size=7, disabled=no_ports),
                 sg.Button("", key="-refresh_com-", image_data=img_to_64(DATA_REFRESH_ICON_PATH), image_size=(32, 32), border_width=0,
                           button_color=(bcg, bcg))]
                ]

    def top_menu_layout(self):
        return [[sg.Button("Connect"), sg.Button("Import"), sg.Button("Export")]]

    # =====================================================================================================================================
    # gui event routines
    # =====================================================================================================================================
