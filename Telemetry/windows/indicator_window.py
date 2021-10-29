import PySimpleGUI as sg
from Telemetry.globals import *


class IndicatorWindow:
    window = None
    # TODO change name of AVAILABLE_PLOTS to DATA_ORDER
    data = [[0, 0, 0] for _ in range(AVAILABLE_PLOTS)]
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
                [sg.Text("Value:"), sg.Text("Min:"), sg.Text("Max:")],
                [sg.Text("", key=f"-{key}_val-"), sg.Text("", key=f"-{key}_min"), sg.Text("", key=f"-{key}_max-")]
                ]

    # TODO write layout
    def indicators_layout(self):
        return [[sg.Text("For future")]]

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
        while True:
            event, values = self.window.read(timeout=20)
            if event == sg.WINDOW_CLOSED or event is None:
                return sg.WINDOW_CLOSED
            elif event == "Close all":
                return "Close all"

    def refresh_values(self, data):
        if len(data) == len(self.data):
            for i, dat in self.data:
                dat[0] = data[i]
                # min
                if dat[1] > data[i]:
                    dat[1] = data[i]
                # max
                if dat[2] < data[i]:
                    dat[2] = data[i]
                # TODO update gui
        else:
            print(f"Data packet size is wrong. Received: {len(data)}, expected: {len(self.data)}")

    def connect(self):
        pass
