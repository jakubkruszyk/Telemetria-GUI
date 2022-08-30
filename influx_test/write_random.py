from datetime import datetime
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import random
import time
from Telemetry.globals import DATA_PARAMETERS

token = "xX_L0QKGV2wp2T0kKTHWHIWCAIvP7eNG0514PvT6wuACfwTOSVso_EZCtDA7t3nmRZ5rLTAJrD0wvy41XGivjQ=="
org = "Test"
bucket = "Pomiary"
url = "192.168.1.29:8086"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

data = dict()

print(client.ping())


def gen():
    global data
    for key in DATA_PARAMETERS:
        n = DATA_PARAMETERS[key][1]
        min = DATA_PARAMETERS[key][-1][-1]
        max = DATA_PARAMETERS[key][-1][0]
        for i in range(n):
            data[f"{key} {i}"] = round(random.uniform(0.9*min, 1.1*max), 2)


while True:
    gen()
    point = [{
        "measurement": "Klara",
        "tags": {"session": "test3"},
        "fields": data,
        "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    }]

    write_api.write(bucket, org, point)
    print(f"Cell voltage 0: {data['Cell voltage 0']}")
    time.sleep(1)
