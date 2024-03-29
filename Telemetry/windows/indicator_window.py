import PySimpleGUI as sg
from Telemetry.globals import *
from Telemetry.windows.base_window import BaseWindow, img_to_64, min_max_popup, plot_sources_popup
from Telemetry import usb_receiver


class IndicatorWindow(BaseWindow):
    data = {key: [0, 0, 0] for key in AVAILABLE_PLOTS}  # key: [val, min, max]
    last_update = 0
    initial_update = True

    # TODO init from config file
    def __init__(self, **kwargs):
        self.selected_layout = kwargs.get("layout", PLOT_LAYOUT_TYPES[0])
        self.selected_data_source = kwargs.get("source", DATA_SOURCES[0])

    # ===========================================================================
    # functions that returns layout fragments
    # ===========================================================================
    def indicators_columns(self, values):
        name_col = [[sg.Text("Name:")]] + [[sg.Text(key, key=f"-{key}_name-")] for key in values]
        val_col = [[sg.Text("Value:")]] + [[sg.Text("0.0", key=f"-{key}_val-")] for key in values]
        min_col = [[sg.Text("Min:")]] + [[sg.Text("0.0", key=f"-{key}_min-")] for key in values]
        max_col = [[sg.Text("Max:")]] + [[sg.Text("0.0", key=f"-{key}_max-")] for key in values]
        return sg.Column(name_col), sg.Column(val_col), sg.Column(min_col), sg.Column(max_col)

    def indicators_layout(self):
        layout = [[sg.Text("Last update: "), sg.Text("0", key="-last_update-")]]
        sub_layout = []
        i = 0
        for _ in range(INDICATORS_GRID[1]):
            if i + INDICATORS_GRID[0] > len(AVAILABLE_PLOTS):
                sub_layout.extend(self.indicators_columns(AVAILABLE_PLOTS[i:]))
                break
            else:
                sub_layout.extend(self.indicators_columns(AVAILABLE_PLOTS[i:i + INDICATORS_GRID[0]]))
            i += INDICATORS_GRID[0]
            sub_layout.append(sg.VerticalSeparator())
        layout.append(sub_layout)
        return layout

    # ===========================================================================
    # functions for managing gui
    # ===========================================================================
    def create_window(self):
        sg.theme(GUI_THEME)

        # create whole layout and window
        whole_layout = [[sg.Column(self.top_menu_layout(), expand_x=True, key="-top_menu-", size=(0, TOP_MENU_SIZE),
                                   vertical_alignment="center")],
                        [sg.HorizontalSeparator()],
                        [sg.Column(self.side_menu_layout(), vertical_alignment="top", key="-side_menu-",
                                   size=(SIDE_MENU_WIDTH, 1), expand_y=True),
                         sg.VerticalSeparator(),
                         sg.Column(self.indicators_layout(), key="-plots-")]
                        ]

        self.window = sg.Window(WINDOW_TITLE, layout=whole_layout, finalize=True, resizable=True,
                                icon=img_to_64(ICON_PATH))
        # self.window.maximize()  # really slows down startup

    # ======================== Event loop =======================================
    def read_window(self):
        event, values = self.window.read(timeout=20)
        if event == sg.WINDOW_CLOSED or event is None:
            return "closed"

        elif event == "Settings":
            min_max_popup()

        elif event == "Reset":
            for group in DATA_PARAMETERS:
                for num in range(DATA_PARAMETERS[group][1]):
                    self.window[f"-{group} {num}_min-"].update(self.window[f"-{group} {num}_val-"].DisplayText)
                    self.window[f"-{group} {num}_max-"].update(self.window[f"-{group} {num}_val-"].DisplayText)

        elif event == "Export":
            self.save_config(CONFIG_PATH)

        elif event == "Import":
            self.load_config()

        elif event == "Connect":
            if not self.connected:
                resp = usb_receiver.connect_to_port(self.selected_port)
                if resp is not True:
                    sg.popup_ok(resp)
                    self.connected = False
                else:
                    self.connected = True

        elif event == "-layout_type-":
            # saving parameters that may changed and cleaning flags
            self.selected_layout = values["-layout_type-"]
            self.selected_data_source = values["-data_source-"]
            self.connected = False
            # restarting window
            self.window.close()
            return "layout"

        elif event == "-data_source-":
            if values[event] == "USB":
                self.window["-usb_settings-"].update(visible=True)
                self.selected_port = values["-selected_com-"]
            else:
                self.window["-usb_settings-"].update(visible=False)

        # connect to com port picked from list
        elif event == "-selected_com-":
            usb_receiver.connect_to_port(values["-selected_com-"])

        # refresh com ports list
        elif event == "-refresh_com-":
            if usb_receiver.available_ports():
                if usb_receiver.ser.is_open:
                    com_port = usb_receiver.ser.name
                else:
                    com_port = None
                self.window['-selected_com-'].update(value=com_port, values=usb_receiver.available_ports(),
                                                     disabled=False)
            else:
                self.window['-selected_com-'].update(value="Unavailable", disabled=True)
        return None

    # ====================== Data processing ====================================
    def update_data(self, data):
        self.last_update = data["time"]
        for key in data:
            if self.data.get(key) is not None:
                self.data[key][0] = data[key]
                # min
                if data[key] < self.data[key][1] or self.initial_update:
                    self.data[key][1] = data[key]
                # max
                if data[key] > self.data[key][2] or self.initial_update:
                    self.data[key][2] = data[key]

        self.initial_update = False
        self.refresh_values()
        self.validate()

    def refresh_values(self):
        for key in self.data:
            self.window[f"-{key}_val-"].update(self.data[key][0])
            self.window[f"-{key}_min-"].update(self.data[key][1])
            self.window[f"-{key}_max-"].update(self.data[key][2])

        self.window["-last_update-"].update(f"{self.last_update:.2f}")

    def validate(self):
        for group in DATA_PARAMETERS:
            for num in range(DATA_PARAMETERS[group][1]):
                for val, typ in zip(self.data[f"{group} {num}"], ("val", "min", "max")):
                    if not (DATA_PARAMETERS[group][2][2] < val < DATA_PARAMETERS[group][2][1]):
                        if not (DATA_PARAMETERS[group][2][3] < val < DATA_PARAMETERS[group][2][0]):
                            self.window[f"-{group} {num}_{typ}-"].update(background_color=COLORS["Error"],
                                                                         text_color="#ffffff")
                        else:
                            self.window[f"-{group} {num}_{typ}-"].update(background_color=COLORS["Warning"],
                                                                         text_color="#000000")
                    else:
                        self.window[f"-{group} {num}_{typ}-"].update(background_color=sg.theme_background_color(),
                                                                     text_color="#ffffff")
