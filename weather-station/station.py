import sqlite3
import argparse
import logging
import time

VERSION = 0.1
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
LOGGER = logging.getLogger('weather')


def setup_db(conn):
    cursor = conn.cursor()
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
    conn.commit()


# HELPERS


def get_location(conn):
    return 1


def store_temp(conn, temp):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO temp (location, temp, created_at) VALUES(?, ?, datetime('now'))",
                   (get_location(conn), temp))
    conn.commit()


def get_last_temp(conn, location):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM temp WHERE location=? ORDER BY created_at LIMIT 1", (location, ))
    return cursor.fetchone()


# ACTIONS


def report(conn):
    import pprint
    pprint.pprint(get_last_temp(conn, get_location(conn)))
    pass


def run(conn):
    store_temp(conn, 20)
    # while True:
    #     time.sleep(1)
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Weather station", description="My pretty lil weather station")
    parser.add_argument('--version', action="version", version="%(prog)s {ver} ".format(ver=VERSION))
    parser.add_argument('--db', '-d', type=str, default="weather.db", nargs="?",
                        help="Database file path")
    parser.add_argument('-v', action="store_true", help="verbose output")
    parser.add_argument('command', choices=['report', 'run'], default="run", nargs="?",
                        help="action")
    args = parser.parse_args()

    if args.v:
        LOGGER.setLevel(logging.DEBUG)

    conn = sqlite3.connect(args.db)
    setup_db(conn)

    commands = {
        'run': run,
        'report': report,
    }

    LOGGER.debug("Executing action: {command}".format(command=args.command))
    try:
        commands.get(args.command)(conn)
    except KeyboardInterrupt as e:
        LOGGER.info("Keyboard interruption detected")

    conn.close()
