from influxdb_client import InfluxDBClient
import globals as gb
import itertools
from urllib3.exceptions import ConnectTimeoutError

client = InfluxDBClient(url=gb.URL, token=gb.TOKEN, org=gb.ORG, timeout=2000)
query_api = client.query_api()
error = None if client.ping() else "Cannot connect to server"
connected = True if error is None else False
query_last = 'from(bucket: "Pomiary") |> range(start: -7d) ' \
             '|> filter(fn: (r) => r["_measurement"] == "Klara") ' \
             '|> filter(fn: (r) => r["session"] == "test3")' \
             '|> last()'
measurement = "None"
session = ""


def param_check():
    if measurement == "None" or gb.BUCKET == "None":
        return False
    else:
        return True


def connect():
    global client, query_api, connected
    if client is not None:
        client.close()

    client = InfluxDBClient(url=gb.URL, token=gb.TOKEN, org=gb.ORG)
    query_api = client.query_api()

    if not client.ping():
        connected = False
        return "Cannot connect to server"
    else:
        connected = True
        return None


def disconnect():
    global connected
    if connected:
        client.close()
        connected = False


def query():
    if not connected or not param_check():
        return None

    global error
    tables = query_api.query(query_last)
    if len(tables) == 0:
        error = "Cant get values"
        return None

    values = tables.to_values(columns=['_field', '_value', '_time'])
    query_data = {value[0]: value[1] for value in values}
    query_data["time"] = values[0][2]
    return query_data


def list_buckets():
    global error

    if not connected:
        return ["None"]

    error = None
    try:
        buckets_api = client.buckets_api()
        buckets = buckets_api.find_buckets().buckets
        buckets_list = [bucket.name for bucket in buckets if not bucket.name[0] == "_"]
        return buckets_list if buckets_list else ["None"]

    except ConnectTimeoutError:
        disconnect()
        error = "Lost connection to server"
        return ["None"]


def list_measurements():
    global error

    if not connected or gb.BUCKET == "None":
        return ["None"]

    error = None
    try:
        q = f'import "influxdata/influxdb/schema"\n\nschema.measurements(bucket: "{gb.BUCKET}")'
        tables = query_api.query(q)
        measurements = tables.to_values(columns=['_value'])
        measurements = list(itertools.chain.from_iterable(measurements))
        return measurements if measurements else ["None"]

    except ConnectTimeoutError:
        disconnect()
        error = "Lost connection to server"
        return ["None"]


def list_sessions():
    global error

    if not connected or not param_check():
        return ["None"]

    try:
        q = f'import "influxdata/influxdb/schema"\n\nschema.measurementTagValues(bucket: "{gb.BUCKET}",' \
            f'tag: "session",measurement: "{measurement}")'
        tables = query_api.query(q)
        sessions = tables.to_values(columns=['_value'])
        sessions = list(itertools.chain.from_iterable(sessions))
        return sessions if sessions else ["None"]

    except ConnectTimeoutError:
        disconnect()
        error = "Lost connection to server"
        return ["None"]


def update_query():
    global query_last
    if session == "":
        query_last = f'from(bucket: "Pomiary") |> range(start: -7d) ' \
                     f'|> filter(fn: (r) => r["_measurement"] == "{measurement}") ' \
                     f'|> last()'
    else:
        query_last = f'from(bucket: "Pomiary") |> range(start: -7d) ' \
                     f'|> filter(fn: (r) => r["_measurement"] == "{measurement}") ' \
                     f'|> filter(fn: (r) => r["session"] == "{session}")' \
                     f'|> last()'
