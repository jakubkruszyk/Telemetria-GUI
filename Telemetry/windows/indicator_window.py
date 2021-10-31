import PySimpleGUI as sg
from Telemetry.globals import *


class IndicatorWindow:
    window = None
    # TODO change name of AVAILABLE_PLOTS to DATA_ORDER
    data = {key: [0, 0, 0] for key in AVAILABLE_PLOTS}  # key: [val, min, max]
    last_update = 0

    selected_data_source = DATA_SOURCES[0]
    selected_layout = "Indicator"
    connected = False

    # TODO init from config file
    def __init__(self):
        pass

    # ===========================================================================
    # functions that returns layout fragments
    # ===========================================================================
    def single_indicator_layout(self, key):
        return [[sg.Text(key)],
                [sg.Column([[sg.Text("Value:")], [sg.Text("0.0", key=f"-{key}_val-")]]),
                 sg.Column([[sg.Text("Min:")], [sg.Text("0.0", key=f"-{key}_min-")]]),
                 sg.Column([[sg.Text("Max:")], [sg.Text("0.0", key=f"-{key}_max-")]])]
                ]

    # TODO write layout
    def indicators_layout(self):
        return [[sg.Text("Last update: "), sg.Text("0", key="-last_update-")],
                [sg.Frame("", self.single_indicator_layout("None")), sg.Frame("", self.single_indicator_layout("Random"))],
                [sg.Frame("", self.single_indicator_layout("Only 1")), sg.Frame("", self.single_indicator_layout(3))]
                ]

    # TODO throw to separate file
    def side_menu_layout(self):
        return [[sg.Text("Layout Type")],
                [sg.Combo(values=PLOT_LAYOUT_TYPES, default_value=self.selected_layout, key="-layout_type-",
                          enable_events=True)],
                [sg.Text("Data source")],
                [sg.Combo(values=DATA_SOURCES, default_value=self.selected_data_source, key="-data_source-",
                          enable_events=True)],
                [sg.Button("Create new window")],
                [sg.Button("Close all")]
                ]

    # TODO throw to separete file
    def top_menu_layout(self):
        return [[sg.Button("Connect"), sg.Button("Import"), sg.Button("Export")]]

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
        self.window = sg.Window(WINDOW_TITLE, layout=whole_layout, finalize=True, resizable=True)
        self.window.maximize()
        # TODO ! for future ! elements scaling like plots

    def read_window(self):
        event, values = self.window.read(timeout=20)
        if event == sg.WINDOW_CLOSED or event is None:
            return "closed"

        elif event == "Connect":
            if not self.connected:
                self.connected = True
                self.connect()

        return None

    def update_data(self, data):
        self.last_update = data.pop("time")
        for key in data:
            self.data[key][0] = data[key]
            # min
            if data[key] < self.data[key][1]:
                self.data[key][1] = data[key]
            # max
            if data[key] > self.data[key][2]:
                self.data[key][2] = data[key]

        self.refresh_values()

    def refresh_values(self):
        for key in self.data:
            self.window[f"-{key}_val-"].update(self.data[key][0])
            self.window[f"-{key}_min-"].update(self.data[key][1])
            self.window[f"-{key}_max-"].update(self.data[key][2])

        self.window["-last_update-"].update(f"{self.last_update:.2f}")

    def connect(self):
        pass
