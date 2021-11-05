from Telemetry.globals import *
import PySimpleGUI as sg


class BaseWindow:
    window = None
    selected_data_source = DATA_SOURCES[0]
    selected_layout = "Indicator"
    connected = False

    # =====================================================================================================================================
    # layouts for gui sections
    # =====================================================================================================================================
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

    def top_menu_layout(self):
        return [[sg.Button("Connect"), sg.Button("Import"), sg.Button("Export")]]

    # =====================================================================================================================================
    # layouts for gui sections
    # =====================================================================================================================================
    def connect(self):
        pass

    def handle_menus_events(self, event, values):
        if event == "Import":
            pass
        elif event == "Export":
            pass
