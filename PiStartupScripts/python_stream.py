import os
import sys
import time
import subprocess
import shutil
import signal
import threading
from datetime import datetime
import json
import logging
import sensors
import RPi.GPIO as GPIO
import psutil

#Setup button input (on 6 mic array)
array_mic_button = 26


"""
Runs ODAS to stream localisation data to python program (connected via ethernet)
"""


def safe_shutdown():
    """
    Safely powers down the device (without corruption)
    ...even when threads are running (it will halt these first)
    -h stands for 'halt'
    """
    shutdown_cmd = "sudo shutdown -h now"
    subprocess.call(shutdown_cmd, shell=True)
    

# On button press, safely shutdown the pi...
def interrupt_button_callback(channel):
    logging.info('\nButton press detected. Safely shutting down.\n')
    safe_shutdown()


if __name__ == "__main__":
    
    # Setting up the button (on the top of the 6 mic array)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(array_mic_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    GPIO.add_event_detect(array_mic_button, GPIO.FALLING,
                          callback=interrupt_button_callback, bouncetime=100)
    
    # start streaming the data from the pi...
    stream_cmd = "../odas/build/bin/odaslive -c ./respeaker_6_mic_array.cfg"
    subprocess.call(stream_cmd, shell=True)

    while True:
        time.sleep(1)
    
