#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Python Data Collection Module

"""
Created on Tue May 9 12:13:27 2017

@author: Hyun-seok

IMPORTANT: REQUIRES ROOT ACCESS TO RUN.

Reads and interprets data from an ADXL 345 triaxial accelerometer and uses
a Adafruit 24 pixel neopixel ring to determine payload status.

Examples:
Run with the following lines on the command prompt:
    $ sudo python gnd.py

Run with this command to write to a .txt file:
    $ sudo nice -20 python gnd.py > logGND.txt

Wiring Details:

    Connect neopixel to ground, 5v, and physical pin 12 (gpio pin 18) (0)
    #(not needed) Connect neopixel to ground, 5v, and physical pin 33 (gpio pin 13) (1)

    GPIO 1 setup: ADXL - Pi (0x53)

    GND, SDO - GND
    VCC, CS - 3V3
    SDA - SDA (GPIO 2)
    SCL - SCL (GPIO 3)

    GPIO 2 setup: ADXL - Pi (0x1D)

    GND - GND
    VCC, CS, SDO - 3V3
    SDA - SDA
    SCL - SCL
"""

import sys
import collections
from os import path
import raspi_accel_lib
import settings as st

if __name__ == '__main__':
    # init global variables
    CIRCULAR_BUFF = collections.deque(maxlen=st.MAXLEN)
    AVG_BUFF = collections.deque(maxlen=st.ACCEL_RESPONSE)
    RESTING = 0

    # Define accelerometers (named after rivers)
    INDUS = raspi_accel_lib.ADXL345(0x53)

    # Define Neopixels (named after swords)
    # KATANA = neopxl.Adafruit_NeoPixel(st.LED_COUNT_1, st.LED_PIN_1, st.LED_FREQ_HZ_1,
    #                                  st.LED_DMA_1, st.LED_INVERT_1, st.LED_BRIGHTNESS_1, 0)

    # Startup Neopixel
    # KATANA.neopixel_startup(st.BLUE, st.GREEN, st.RED)

    # Startup Accelerometer
    INDUS.accel_startup(st.GFORCE)

    #Initalize .txt file by writing headers
    print('#Time,X,Y,Z')
    sys.stdout.flush()

    # Store up data in circular buffer on launch pad and
    # flush when launched.
    while True:
        CIRCULAR_BUFF.append(INDUS.string_output())
        if INDUS.accel_magnitude(True) > st.TAKEOFF_THRESHOLD:
            BUFFER_DATA = list(CIRCULAR_BUFF)
            print('\n'.join(BUFFER_DATA))
            sys.stdout.flush()
            break

    # Record Data until vehicle is deemed to be "landed"
    while True:
        print(INDUS.string_output(st.GFORCE))
        sys.stdout.flush()

        if INDUS.accel_magnitude(True) < st.LANDING_THRESHOLD:
            RESTING += 1
        elif st.LANDING_SENSE < 0:
            RESTING = 0
        else:
            RESTING -= st.LANDING_SENSE

        if RESTING <= 0:
            RESTING = 0

        if RESTING >= st.RESTING_THRESHOLD:
            print("#Landed")
            sys.stdout.flush()
            break

        if path.getsize('loggnd.txt') > st.MEM_MAX:
            print('# Memory Stop')
            break
