import sqlite3
import argparse
import logging
import time
import Adafruit_DHT

VERBOSE = False
DB = None
INPUT_PIN = 4
VERSION = 0.1

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
LOGGER = logging.getLogger('weather')


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


def get_location():
    return 1


def store_temp(temp):
    cursor = DB.cursor()
    cursor.execute("INSERT INTO temp (location, temp, created_at) VALUES(?, ?, datetime('now'))",
                   (get_location(), temp))
    DB.commit()


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


def get_last_humidity(location):
    cursor = DB.cursor()
    cursor.execute(
        "SELECT humidity, location, created_at FROM humidity WHERE location=? ORDER BY created_at DESC LIMIT 1",
        (location,))
    return cursor.fetchone()


# ACTIONS


def report():
    temperature, _, temp_time = get_last_temp(get_location())
    humidity, _, humidity_time = get_last_humidity(get_location())
    LOGGER.info('Temp at {temp_time}: {temp:0.1f} C  Humidity at {humidity_time}: {humidity:0.1f} %'.format(
        temp=temperature, humidity=humidity, temp_time=temp_time, humidity_time=humidity_time
    ))


def run():
    delay = 60
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, INPUT_PIN)
        store_temp(temperature)
        store_humidity(humidity)
        if VERBOSE:
            LOGGER.info('Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity))
        next_time += (time.time() - next_time) // delay * delay + delay
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Weather station", description="My pretty lil weather station")
    parser.add_argument('--version', action="version", version="%(prog)s {ver} ".format(ver=VERSION))
    parser.add_argument('--db', '-d', type=str, default="weather.db", nargs="?",
                        help="Database file path")
    parser.add_argument('-v', action="store_true", help="verbose output")
    parser.add_argument('command', choices=['report', 'run'], default="run", nargs="?",
                        help="action")
    args = parser.parse_args()

    VERBOSE = args.v

    if VERBOSE:
        LOGGER.setLevel(logging.DEBUG)

    DB = sqlite3.connect(args.db)
    setup_db()

    commands = {
        'run': run,
        'report': report,
    }

    LOGGER.debug("Executing action: {command}".format(command=args.command))
    try:
        commands.get(args.command)()
    except KeyboardInterrupt as e:
        LOGGER.info("Keyboard interruption detected")

    DB.close()
