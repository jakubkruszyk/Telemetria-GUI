from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import random

token = "6fnNpVRmGquD2M8NijeqMXVrDmaSt2z9myhG1FUBY1E3juFmiEucEgVeAkYiYR9qpIph6Xjl6J-YCj6B1rwv4w=="
org = "Test"
bucket = "Pomiary"
url = "192.168.1.29:8086"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

point = [{
    "measurement": "Klara",
    "tags": {"session": "test1"},
    "fields": {
        "Cell voltage 0": round(random.uniform(3.5, 4.4), 2),
        "Cell voltage 1": round(random.uniform(3.5, 4.4), 2),
        "Cell temp": round(random.uniform(18, 50), 2),
        "SoC": round(random.uniform(80, 99), 2)
    },
    "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
}]

write_api.write(bucket, org, point)

query = 'from(bucket: "Pomiary") |> range(start: -1h) ' \
        '|> filter(fn: (r) => r["_measurement"] == "Klara") ' \
        '|> filter(fn: (r) => r["session"] == "test1")'

tables = query_api.query(query)

query_result = dict()
for table in tables:
    name = table.records[0]["_field"]
    query_result[name] = [(record["_time"], record["_value"]) for record in table.records]

print(query_result)

client.close()
