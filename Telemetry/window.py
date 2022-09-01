import base64
import PySimpleGUI as sg
import globals as gb
import usb
import influx

# ======================================================================================================================
# Data
# ======================================================================================================================
window = sg.Window(title="empty")  # empty window created mostly for spell checking

selected_data_source = gb.DATA_SOURCES[0]

data = {key: [0, 0, 0] for key in gb.AVAILABLE_VARS}  # { key: [val, min, max] }
last_update = 0  # keep datetime object of last query
initial_update = True  # needed for initial write to min and max values


# ======================================================================================================================
# Methods
# ======================================================================================================================

# neccessary for displaing icons in pysimplegui
def img_to_64(path):
    with open(path, "rb") as file:
        icon = file.read()
        return base64.encodebytes(icon)


# creates main window from separate layouts functions
def create_window():
    sg.theme(gb.GUI_THEME)

    # create whole layout and window
    whole_layout = [[sg.Column(top_menu_layout(), expand_x=True, key="-top_menu-", size=(0, gb.TOP_MENU_SIZE),
                               vertical_alignment="center")],
                    [sg.HorizontalSeparator()],
                    [sg.Column(side_menu_layout(), vertical_alignment="top", key="-side_menu-",
                               size=(gb.SIDE_MENU_WIDTH, 1), expand_y=True),
                     sg.VerticalSeparator(),
                     sg.Column(indicators_layout(), key="-plots-", vertical_alignment="top")]
                    ]

    return sg.Window(gb.WINDOW_TITLE, layout=whole_layout, finalize=True, resizable=True,
                     icon=img_to_64(gb.ICON_PATH))


# ======================================================================================================================
# Popups
# ======================================================================================================================

# popup for changing error and warning thresholds for given signals
# noinspection PyTypeChecker
def min_max_popup():
    name_col = [[sg.Text('Signal')]] + [[sg.Text(name)] for name in gb.DATA_PARAMETERS]
    max_err = [[sg.Text('Max err')]] + [[sg.Input(val[-1][0], key=f"-{key}_max_err-", size=7)]
                                        for key, val in gb.DATA_PARAMETERS.items()]
    max_war = [[sg.Text('Max war')]] + [[sg.Input(val[-1][1], key=f"-{key}_max_war-", size=7)]
                                        for key, val in gb.DATA_PARAMETERS.items()]
    min_war = [[sg.Text('Min war')]] + [[sg.Input(val[-1][2], key=f"-{key}_min_war-", size=7)]
                                        for key, val in gb.DATA_PARAMETERS.items()]
    min_err = [[sg.Text('Min err')]] + [[sg.Input(val[-1][3], key=f"-{key}_min_err-", size=7)]
                                        for key, val in gb.DATA_PARAMETERS.items()]
    layout = [[sg.Column(name_col), sg.Column(max_err), sg.Column(max_war), sg.Column(min_war), sg.Column(min_err)],
              [sg.Button("Save")]]
    min_max_window = sg.Window("Settings", layout, modal=True)
    event, values = min_max_window.read(close=True)
    if event == sg.WINDOW_CLOSED or event is None:
        return
    if event == "Save":
        for key in gb.DATA_PARAMETERS:
            for idx, err in enumerate(('max_err', 'max_war', 'min_war', 'min_err')):
                gb.DATA_PARAMETERS[key][-1][idx] = float(values[f"-{key}_{err}-"].replace(",", "."))


# ======================================================================================================================
# Layouts
# ======================================================================================================================
def indicators_columns(values):
    name_col = [[sg.Text("Name:")]] + [[sg.Text(key, key=f"-{key}_name-")] for key in values]
    val_col = [[sg.Text("Value:")]] + [[sg.Text("0.0", key=f"-{key}_val-")] for key in values]
    min_col = [[sg.Text("Min:")]] + [[sg.Text("0.0", key=f"-{key}_min-")] for key in values]
    max_col = [[sg.Text("Max:")]] + [[sg.Text("0.0", key=f"-{key}_max-")] for key in values]
    return sg.Column(name_col, vertical_alignment='top'), sg.Column(val_col, vertical_alignment='top'), \
        sg.Column(min_col, vertical_alignment='top'), sg.Column(max_col, vertical_alignment='top')


def indicators_layout():
    layout = [[sg.Text("Last update: "), sg.Text("0", key="-last_update-")]]
    sub_layout = []
    i = 0
    for _ in range(gb.INDICATORS_GRID[1]):
        if i + gb.INDICATORS_GRID[0] > len(gb.AVAILABLE_VARS):
            sub_layout.extend(indicators_columns(gb.AVAILABLE_VARS[i:]))
            break
        else:
            sub_layout.extend(indicators_columns(gb.AVAILABLE_VARS[i:i + gb.INDICATORS_GRID[0]]))
        i += gb.INDICATORS_GRID[0]
        sub_layout.append(sg.VerticalSeparator())
    layout.append(sub_layout)
    return layout


def side_menu_layout():
    return [[sg.Text("Data source")],
            [sg.Combo(values=gb.DATA_SOURCES, default_value=selected_data_source, key="-data_source-",
                      enable_events=True, readonly=True)],
            [sg.pin(sg.Column(usb_settings_layout(), key="-usb_settings-", visible=False, pad=0))],
            [sg.pin(sg.Column(influx_settings_layout(), key="-influx_settings-", visible=True, pad=0))],
            ]


def usb_settings_layout():
    bcg = sg.theme_background_color()
    available_ports = usb.available_ports()
    no_ports = False
    if not available_ports:
        available_ports = ['-']
        no_ports = True

    return [[sg.Text("COM Port:")],
            [sg.Combo(values=available_ports, default_value=available_ports[0], key="-selected_com-",
                      enable_events=True, readonly=True, size=7, disabled=no_ports),
             sg.Button("", key="-refresh_com-", image_data=img_to_64(gb.DATA_REFRESH_ICON_PATH), image_size=(20, 20),
                       border_width=0, button_color=(bcg, bcg))]
            ]


def influx_settings_layout():
    bcg = sg.theme_background_color()

    available_buckets = influx.list_buckets()
    available_measurements = influx.list_measurements()
    gb.BUCKET = available_buckets[0]
    influx.measurement = available_measurements[0]

    available_sessions = influx.list_sessions()
    influx.session = available_sessions[0]

    if influx.error is not None:
        sg.popup_no_wait("Cannot connect to server", keep_on_top=True)

    return [[sg.Text("Bucket:")],
            [sg.Combo(values=available_buckets, default_value=gb.BUCKET, key="-selected_bucket-",
                      enable_events=True, readonly=True, size=7),
             sg.Button("", key="-refresh_influx-", image_data=img_to_64(gb.DATA_REFRESH_ICON_PATH), image_size=(20, 20),
                       border_width=0, button_color=(bcg, bcg))],
            [sg.Text("Measurement:")],
            [sg.Combo(values=available_measurements, default_value=influx.measurement, key="-selected_measurement-",
                      enable_events=True, readonly=True, size=7)],
            [sg.Text("Session:")],
            [sg.Combo(values=available_sessions, default_value=influx.session, key="-selected_session-",
                      enable_events=True, readonly=True, size=7)]
            ]


def top_menu_layout():
    return [[sg.Button("Disconnected", key="Connect"), sg.Button("Import"), sg.Button("Export"), sg.Button("Reset"),
             sg.Button("Settings")]]


# ======================================================================================================================
# Data update methods
# ======================================================================================================================

# update data dictonary, check for new min and max values
def update_data(new_data):
    global last_update, initial_update

    if new_data is None:
        return

    last_update = new_data["time"]
    for key, value in new_data.items():
        if data.get(key) is not None:
            data[key][0] = value
            # min
            if value < data[key][1] or initial_update:
                data[key][1] = value
            # max
            if value > data[key][2] or initial_update:
                data[key][2] = value

    initial_update = False
    refresh_values()
    validate()


# refresh values displayed in window
def refresh_values():
    for key in data:
        window[f"-{key}_val-"].update(data[key][0])
        window[f"-{key}_min-"].update(data[key][1])
        window[f"-{key}_max-"].update(data[key][2])

    window["-last_update-"].update(f"{last_update}")


# check if current values are outside specified boundaries and set background color to error / warning
def validate():
    for group in gb.DATA_PARAMETERS:
        for num in range(gb.DATA_PARAMETERS[group][1]):
            for val, typ in zip(data[f"{group} {num}"], ("val", "min", "max")):
                if not (gb.DATA_PARAMETERS[group][2][2] < val < gb.DATA_PARAMETERS[group][2][1]):
                    if not (gb.DATA_PARAMETERS[group][2][3] < val < gb.DATA_PARAMETERS[group][2][0]):
                        window[f"-{group} {num}_{typ}-"].update(background_color=gb.COLORS["Error"],
                                                                text_color="#ffffff")
                    else:
                        window[f"-{group} {num}_{typ}-"].update(background_color=gb.COLORS["Warning"],
                                                                text_color="#000000")
                else:
                    window[f"-{group} {num}_{typ}-"].update(background_color=sg.theme_background_color(),
                                                            text_color="#ffffff")
