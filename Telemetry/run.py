import PySimpleGUI as sg
import globals as gb
import window
import influx
import usb
import json
import time

# TODO config import
window.window = window.create_window()
selected_source = gb.DATA_SOURCES[0]

last_update = 0


# ======================================================================================================================
# reused methods
# ======================================================================================================================
def get_update_buckets(new_bucket=None):
    if new_bucket is None:
        buckets = influx.list_buckets()
        gb.BUCKET = buckets[0]
        window.window[f"-selected_bucket-"].update(value=gb.BUCKET, values=buckets, disabled=False)
    else:
        gb.BUCKET = new_bucket

    measurements = influx.list_measurements()
    influx.measurement = measurements[0]
    sessions = influx.list_sessions()
    influx.session = sessions[0]
    window.window[f"-selected_measurement-"].update(value=influx.measurement, values=measurements, disabled=False)
    window.window[f"-selected_session-"].update(value=influx.session, values=sessions, disabled=False)

    if influx.error is not None:
        window.window["Connect"].update(text="Disconnected")
        sg.popup_no_wait(influx.error, keep_on_top=True)


def get_update_ports():
    usb.disconnect()
    window.window["Connect"].update(text="Disconnected")
    com_ports = usb.available_ports()
    usb.port = com_ports[0] if com_ports else "None"
    window.window['-selected_com-'].update(value=usb.port, values=com_ports, disabled=False)


# ======================================================================================================================
# Event loop
# ======================================================================================================================
while True:
    # ========== Get new data ==========================================================================================
    if (time.time() - last_update) >= gb.QUERY_RATE:
        window.update_data(influx.query())
        last_update = time.time()

    # ==================================================================================================================
    event, values = window.window.read(timeout=20)

    if event == sg.WINDOW_CLOSED or event is None:
        usb.disconnect()
        influx.disconnect()
        break

    # ========== Top menu events =======================================================================================
    elif event == "Settings":
        window.min_max_popup()

    elif event == "Reset":
        for var in gb.AVAILABLE_VARS:
            window.window[f"-{var}_min-"].update(window.window[f"-{var}_val-"].DisplayText)
            window.window[f"-{var}_max-"].update(window.window[f"-{var}_val-"].DisplayText)
        window.data = {key: [v[0], v[0], v[0]] for key, v in window.data.items()}

    elif event == "Export":
        try:
            with open(gb.CONFIG_PATH, 'w') as file:
                configs = {"data": window.selected_data_source,
                           "port": usb.port,
                           "bucket": gb.BUCKET,
                           "measurement": influx.measurement,
                           "session": influx.session,
                           "min_max": {}}
                for key, val in gb.DATA_PARAMETERS.items():
                    configs["min_max"][key] = val[-1]
                json.dump(configs, file, indent=4)
        except FileNotFoundError:
            sg.popup_no_wait("Invalid file path", keep_on_top=True)

    elif event == "Import":
        path = sg.popup_get_file("popup_get_file", file_types=(("JSON", ".json"), ("All", ".*"),))
        if path is not None:
            with open(path, 'r') as file:
                configs = json.load(file)
                try:
                    window.data_source = configs["data"]
                    usb.port = configs["port"]
                    gb.BUCKET = configs["bucket"]
                    influx.measurement = configs["measurement"]
                    influx.session = configs["session"]
                    for key, val in configs["min_max"].items():
                        gb.DATA_PARAMETERS[key][-1] = val
                except KeyError:
                    sg.popup_no_wait("Config file is invalid", keep_on_top=True)

    elif event == "Connect":
        if window.window[f"-data_source-"] == "Cloud":
            usb.disconnect()
            influx.session = window.window["-selected_session-"]
            # try to connect
            error = influx.connect()
        else:
            influx.disconnect()
            error = usb.connect()

        if error is None:
            window.window["Connect"].update(text="Connected")
        else:
            sg.popup_no_wait(error, keep_on_top=True)

    # ========== Side menu events ======================================================================================
    elif event == "-data_source-":
        window.window["Connect"].update(text="Disconnected")
        if values[event] == "USB":
            influx.disconnect()
            window.window["-usb_settings-"].update(visible=True)
            window.window["-influx_settings-"].update(visible=False)
            get_update_ports()

        elif values[event] == "Cloud":
            usb.disconnect()
            window.window["-usb_settings-"].update(visible=False)
            window.window["-influx_settings-"].update(visible=True)

            if influx.client.ping():
                get_update_buckets()
            else:
                sg.popup_no_wait("Cannot connect to server", keep_on_top=True)

    # usb settings
    elif event == "-selected_com-":
        usb.disconnect()
        window.window["Connect"].update(text="Disconnected")
        usb.port = values[event]

    elif event == "-refresh_com-":
        usb.disconnect()
        window.window["Connect"].update(text="Disconnected")
        get_update_ports()

    # influx settings
    elif event == "-selected_bucket-":
        get_update_buckets(values["-selected_bucket-"])
        influx.update_query()
        if influx.error is not None:
            window.window["Connect"].update(text="Disconnected")
            sg.popup_no_wait(influx.error, keep_on_top=True)

    elif event == "-selected_measurement-":
        influx.measurement = values[event]
        sessions = influx.list_sessions()
        influx.session = sessions[0]
        window.window[f"-selected_session-"].update(value=influx.session, values=sessions, disabled=False)
        influx.update_query()
        if influx.error is not None:
            window.window["Connect"].update(text="Disconnected")
            sg.popup_no_wait(influx.error, keep_on_top=True)

    elif event == "-selected_session-":
        influx.session = values[event]
        influx.update_query()
        if influx.error is not None:
            window.window["Connect"].update(text="Disconnected")
            sg.popup_no_wait(influx.error, keep_on_top=True)

    elif event == "-refresh_influx-":
        get_update_buckets()
        if influx.error is not None:
            window.window["Connect"].update(text="Disconnected")
            sg.popup_no_wait(influx.error, keep_on_top=True)
