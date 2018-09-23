import logging
import subprocess
import threading
import time

import RPi.GPIO as GPIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
LOGGER = logging.getLogger('weather')

MODE = ""
REQUESTED_MODE = "clock"

BOTTOM_LEFT = 17
BOTTOM = 27
DOT = 22
BOTTOM_RIGHT = 10
MIDDLE = 9
DIGIT_4 = 11
TOP_RIGHT = 18
DIGIT_3 = 23
DIGIT_2 = 24
TOP = 25
TOP_LEFT = 8
DIGIT_1 = 7

GPIO.setmode(GPIO.BCM)

SEGMENTS = (TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, BOTTOM, BOTTOM_LEFT, TOP, MIDDLE, DOT)
DIGITS = (DIGIT_1, DIGIT_2, DIGIT_3, DIGIT_4)

GPIO.setup(SEGMENTS, GPIO.OUT)
GPIO.setup(DIGITS, GPIO.OUT)

GPIO.output(SEGMENTS, GPIO.LOW)
GPIO.output(DIGITS, GPIO.HIGH)

layouts = {
    '1': (False, True, True, False, False, False, False, False),
    '2': (True, True, False, True, True, False, True, False),
    '3': (True, True, True, True, False, False, True, False),
    '4': (False, True, True, False, False, True, True, False),
    '5': (True, False, True, True, False, True, True, False),
    '6': (True, False, True, True, True, True, True, False),
    '7': (True, True, True, False, False, False, False, False),
    '8': (True, True, True, True, True, True, True, False),
    '9': (True, True, True, True, False, True, True, False),
    '0': (True, True, True, True, True, True, False, False),
    'A': (True, True, True, False, True, True, True, False),
    'B': (False, False, True, True, True, True, True, False),
    'C': (True, False, False, True, True, True, False, False),
    'D': (False, True, True, True, True, False, True, False),
    'E': (True, False, False, True, True, True, True, False),
    'F': (True, False, False, False, True, True, True, False),
    'G': (True, False, True, True, True, True, False, False),
    'H': (False, True, True, False, True, True, True, False),
    'I': (False, False, False, False, True, True, False, False),
    'J': (False, True, True, True, True, False, False, False),
    'K': (True, False, True, False, True, True, True, False),
    'L': (False, False, False, True, True, True, False, False),
    'M': (True, False, True, False, True, False, False, False),
    'N': (True, True, True, False, True, True, False, False),
    'O': (True, True, True, True, True, True, False, False),
    'P': (True, True, False, False, True, True, True, False),
    'Q': (True, True, False, True, False, True, True, False),
    'R': (True, True, False, False, True, True, False, False),
    'S': (True, False, True, True, False, True, True, False),
    'T': (False, False, False, True, True, True, True, False),
    'U': (False, False, True, True, True, False, False, False),
    'V': (False, True, True, True, True, True, False, False),
    'W': (False, True, False, True, False, True, False, False),
    'X': (False, True, True, False, True, True, True, False),
    'Y': (False, True, True, True, False, True, True, False),
    'Z': (True, True, False, True, True, False, True, False),
    '-': (False, False, False, False, False, False, True, False),
    ' ': (False, False, False, False, False, False, False, False),
    '=': (False, False, False, True, False, False, True),
    '*': (True, True, False, False, False, True, True, False),
    '.': (False, False, False, False, False, False, False, True),
}


def show_clock():
    LOGGER.info("MODE = clock")
    global MODE
    prev_second = time.strftime("%S")
    blink_dot = True
    while MODE == "clock":
        normalized_time = time.strftime("%H%M")
        current_second = time.strftime("%S")
        if prev_second != current_second:
            blink_dot = not blink_dot
            prev_second = current_second
        for digit in range(4):
            GPIO.output(SEGMENTS, layouts[normalized_time[digit]])
            if digit == 1:
                GPIO.output(DOT, blink_dot)
            GPIO.output(DIGITS[digit], 0)
            time.sleep(0.001)
            GPIO.output(DIGITS[digit], 1)


TEMP = "----"


def _get_temp(stop_event):
    global TEMP
    iteration = 30
    while not stop_event.isSet():
        if iteration == 30:  # this shit is needed to be more responsive to termination. Daemon did not work
            temp = subprocess.check_output(['bash', '/etc/init.d/station.sh', 'report-temperature'],
                                           shell=False).strip()
            TEMP = temp[0:2] + "*C"
            LOGGER.info("Got temperature from station: " + TEMP)
            iteration = 0
        else:
            time.sleep(2)
            iteration += 1


def show_temp():
    LOGGER.info("MODE = temp")
    global TEMP, MODE
    stop_event = threading.Event()
    thread = threading.Thread(target=_get_temp, args=(stop_event,))
    try:
        thread.start()
        while MODE == "temp":
            for digit in range(4):
                GPIO.output(SEGMENTS, layouts[TEMP[digit]])
                GPIO.output(DIGITS[digit], 0)
                time.sleep(0.001)
                GPIO.output(DIGITS[digit], 1)
    finally:
        stop_event.set()


HUMIDITY = "----"


def _get_humidity(stop_event):
    global HUMIDITY
    iteration = 30
    while not stop_event.isSet():
        if iteration == 30:  # this shit is needed to be more responsive to termination. Daemon did not work
            HUMIDITY = subprocess.check_output(['bash', '/etc/init.d/station.sh', 'report-humidity'],
                                               shell=False).strip()
            LOGGER.info("Got humidity from station: " + HUMIDITY)
            iteration = 0
        else:
            time.sleep(2)
            iteration += 1


def show_humidity():
    LOGGER.info("MODE = humidity")
    global HUMIDITY, MODE
    stop_event = threading.Event()
    thread = threading.Thread(target=_get_humidity, args=(stop_event,))
    try:
        thread.start()
        while MODE == "humidity":
            for digit in range(4):
                GPIO.output(SEGMENTS, layouts[HUMIDITY[digit]])
                GPIO.output(DIGITS[digit], 0)
                time.sleep(0.001)
                GPIO.output(DIGITS[digit], 1)
    finally:
        stop_event.set()


modes = {
    "temp": show_temp,
    "humidity": show_humidity,
    "clock": show_clock
}

rotate_modes_timer = 30
iteration = 0

try:
    while True:
        if REQUESTED_MODE != MODE:
            MODE = REQUESTED_MODE
            threading.Thread(target=modes[MODE]).start()
        time.sleep(1)
        iteration += 1
        if iteration > rotate_modes_timer:
            iteration = 0
            if MODE == "temp":
                REQUESTED_MODE = "humidity"
            elif MODE == "humidity":
                REQUESTED_MODE = "clock"
            else:
                REQUESTED_MODE = "temp"
            LOGGER.info("Switching MODE to " + REQUESTED_MODE)
except KeyboardInterrupt:
    MODE = ""
    LOGGER.info("Caught ^C, quitting")
    time.sleep(1)  # time for threads to terminate cleanly
finally:
    GPIO.cleanup()
