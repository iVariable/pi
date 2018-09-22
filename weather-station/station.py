import argparse
import logging
import sqlite3
import time

import Adafruit_DHT
from google.cloud import monitoring_v3

INPUT_PIN = 4

VERSION = 0.1
GCP_METRIC_TYPE = "weatherstation"
MEASURE_INTERVAL = 60

VERBOSE = False
DB = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
LOGGER = logging.getLogger('weather')

GCP_CLIENT = monitoring_v3.MetricServiceClient.from_service_account_file('gcp_key.json')


def setup_db():
    cursor = DB.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS location ("
                   "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                   "name TEXT"
                   ");")
    cursor.execute("CREATE TABLE IF NOT EXISTS temp ("
                   "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                   "location INTEGER,"
                   "temp REAL,"
                   "created_at TEXT"
                   ");")
    cursor.execute("CREATE INDEX IF NOT EXISTS temp_location_created_at ON temp(location, created_at);")
    cursor.execute("CREATE TABLE IF NOT EXISTS humidity ("
                   "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                   "location INTEGER,"
                   "humidity REAL,"
                   "created_at TEXT"
                   ");")
    cursor.execute("CREATE INDEX IF NOT EXISTS humidity_location_created_at ON temp(location, created_at);")
    DB.commit()


# HELPERS

def store_metric_in_gcp(type, location, value):
    series = monitoring_v3.types.TimeSeries()
    series.metric.type = 'custom.googleapis.com/' + GCP_METRIC_TYPE + '/' + type + '/' + str(location)
    series.resource.type = 'global'
    point = series.points.add()
    point.value.double_value = value
    now = time.time()
    point.interval.end_time.seconds = int(now)
    GCP_CLIENT.create_time_series(GCP_CLIENT.project_path('zayavpn'), [series])


def get_location():
    return 1


def store_temp(temp):
    cursor = DB.cursor()
    cursor.execute("INSERT INTO temp (location, temp, created_at) VALUES(?, ?, datetime('now'))",
                   (get_location(), temp))
    DB.commit()
    store_metric_in_gcp("temperature", get_location(), temp)


def get_last_temp(location):
    cursor = DB.cursor()
    cursor.execute("SELECT temp, location, created_at FROM temp WHERE location=? ORDER BY created_at DESC LIMIT 1",
                   (location,))
    return cursor.fetchone()


def store_humidity(humidity):
    cursor = DB.cursor()
    cursor.execute("INSERT INTO humidity (location, humidity, created_at) VALUES(?, ?, datetime('now'))",
                   (get_location(), humidity))
    DB.commit()
    store_metric_in_gcp("humidity", get_location(), humidity)


def get_last_humidity(location):
    cursor = DB.cursor()
    cursor.execute(
        "SELECT humidity, location, created_at FROM humidity WHERE location=? ORDER BY created_at DESC LIMIT 1",
        (location,))
    return cursor.fetchone()


# ACTIONS


def report(type=None):
    temperature, _, temp_time = get_last_temp(get_location())
    humidity, _, humidity_time = get_last_humidity(get_location())
    if type == "temp":
        print(temperature)
    elif type == "humidity":
        print(humidity)
    else:
        LOGGER.info('Temp at {temp_time}: {temp:0.1f} C  Humidity at {humidity_time}: {humidity:0.1f} %'.format(
            temp=temperature, humidity=humidity, temp_time=temp_time, humidity_time=humidity_time
        ))


def run():
    next_time = time.time()
    while True:
        time.sleep(max(0, next_time - time.time()))
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, INPUT_PIN)
        store_temp(temperature)
        store_humidity(humidity)
        if VERBOSE:
            LOGGER.info('Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity))
        next_time += (time.time() - next_time) // MEASURE_INTERVAL * MEASURE_INTERVAL + MEASURE_INTERVAL


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Weather station", description="My pretty lil weather station")
    parser.add_argument('--version', action="version", version="%(prog)s {ver} ".format(ver=VERSION))
    parser.add_argument('--db', '-d', type=str, default="weather.db", nargs="?",
                        help="Database file path")
    parser.add_argument('-v', action="store_true", help="verbose output")
    parser.add_argument('command', choices=['report', 'run', 'report-temperature', 'report-humidity'], default="run",
                        nargs="?", help="action")
    args = parser.parse_args()

    VERBOSE = args.v

    if VERBOSE:
        LOGGER.setLevel(logging.DEBUG)

    DB = sqlite3.connect(args.db)
    setup_db()

    commands = {
        'run': run,
        'report': report,
        'report-temperature': lambda: report("temp"),
        'report-humidity': lambda: report("humidity"),
    }

    LOGGER.debug("Executing action: {command}".format(command=args.command))
    try:
        commands.get(args.command)()
    except KeyboardInterrupt as e:
        LOGGER.info("Keyboard interruption detected")

    DB.close()
