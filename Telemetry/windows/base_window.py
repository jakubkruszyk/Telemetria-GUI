from Telemetry.globals import *
import PySimpleGUI as sg
import base64
from Telemetry import usb_receiver
import json


# convert png/jpg to base64, most portable way because .ico works only on Windows
def img_to_64(path):
    with open(path, "rb") as file:
        icon = file.read()
        return base64.encodebytes(icon)


# noinspection PyTypeChecker
def min_max_popup():
    name_col = [[sg.Text('Signal')]] + [[sg.Text(name)] for name in DATA_PARAMETERS]
    max_err = [[sg.Text('Max err')]] + [[sg.Input(val[-1][0], key=f"-{key}_max_err-", size=7)]
                                        for key, val in DATA_PARAMETERS.items()]
    max_war = [[sg.Text('Max war')]] + [[sg.Input(val[-1][1], key=f"-{key}_max_war-", size=7)]
                                        for key, val in DATA_PARAMETERS.items()]
    min_war = [[sg.Text('Min war')]] + [[sg.Input(val[-1][2], key=f"-{key}_min_war-", size=7)]
                                        for key, val in DATA_PARAMETERS.items()]
    min_err = [[sg.Text('Min err')]] + [[sg.Input(val[-1][3], key=f"-{key}_min_err-", size=7)]
                                        for key, val in DATA_PARAMETERS.items()]
    layout = [[sg.Column(name_col), sg.Column(max_err), sg.Column(max_war), sg.Column(min_war), sg.Column(min_err)],
              [sg.Button("Save")]]
    window = sg.Window("Settings", layout, modal=True)
    event, values = window.read(close=True)
    if event == sg.WINDOW_CLOSED or event is None:
        return
    if event == "Save":
        for key in DATA_PARAMETERS:
            for idx, err in enumerate(('max_err', 'max_war', 'min_war', 'min_err')):
                DATA_PARAMETERS[key][-1][idx] = float(values[f"-{key}_{err}-"].replace(",", "."))


# noinspection PyTypeChecker
def plot_sources_popup():
    step = 5
    i = step
    layout = []
    while i < len(AVAILABLE_PLOTS):
        sub_layout = [sg.Checkbox(sig, key=f"-{sig}-") for sig in AVAILABLE_PLOTS[i-step: i]]
        layout.append(sub_layout)
        i += step
    layout.append([sg.Checkbox(sig, key=f"-{sig}-") for sig in AVAILABLE_PLOTS[i-step:]])
    layout.append([sg.Button("Save")])
    window = sg.Window("Settings", layout, modal=True)
    event, values = window.read(close=True)
    if event == sg.WINDOW_CLOSED or event is None:
        return
    if event == "Save":
        lines = [key for key, value in values if value]
        return lines


class BaseWindow:
    window = None
    selected_data_source = DATA_SOURCES[0]
    selected_layout = PLOT_LAYOUT_TYPES[0]
    selected_port = None
    connected = False

    # =====================================================================================================================================
    # layouts for gui sections
    # =====================================================================================================================================
    def side_menu_layout(self):
        # return [[sg.Text("Layout Type")],
        #         [sg.Combo(values=PLOT_LAYOUT_TYPES, default_value=self.selected_layout, key="-layout_type-",
        #                   enable_events=True, readonly=True)],
        #         [sg.Text("Data source")],
        #         [sg.Combo(values=DATA_SOURCES, default_value=self.selected_data_source, key="-data_source-",
        #                   enable_events=True, readonly=True)],
        #         [sg.pin(sg.Column(self.usb_settings_layout(), key="-usb_settings-", visible=False, pad=0))],
        #         [sg.Button("Create new window")],
        #         [sg.Button("Close all")]
        #         ]
        return [[sg.Text("Data source")],
                [sg.Combo(values=DATA_SOURCES, default_value=self.selected_data_source, key="-data_source-",
                          enable_events=True, readonly=True)],
                [sg.pin(sg.Column(self.usb_settings_layout(), key="-usb_settings-", visible=False, pad=0))],
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
                 sg.Button("", key="-refresh_com-", image_data=img_to_64(DATA_REFRESH_ICON_PATH), image_size=(32, 32),
                           border_width=0, button_color=(bcg, bcg))]
                ]

    def top_menu_layout(self):
        return [[sg.Button("Connect"), sg.Button("Import"), sg.Button("Export"), sg.Button("Reset"),
                 sg.Button("Settings")]]

    def save_config(self, path):
        with open(path, 'w') as file:
            configs = {"data": self.selected_data_source, "layout": self.selected_layout, "port": self.selected_port,
                       "min_max": {}}
            for key, val in DATA_PARAMETERS.items():
                configs["min_max"][key] = val[-1]
            json.dump(configs, file)

    def load_config(self, path=None):
        if path is None:
            path = sg.popup_get_file("popup_get_file", file_types=(("JSON", ".json"), ("All", ".*"),))
        if path is None:
            return
        with open(path, 'r') as file:
            configs = json.load(file)
            self.selected_data_source = configs["data"]
            self.selected_layout = configs["layout"]
            self.selected_port = configs["port"]
            for key, val in configs["min_max"].items():
                DATA_PARAMETERS[key][-1] = val
