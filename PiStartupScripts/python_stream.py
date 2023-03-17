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
import RPi.GPIO as GPIO
import psutil

#Setup button input (on 6 mic array)
array_mic_button = 26

button_press_count = 0

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
    

# On button press...
def interrupt_button_callback(channel):
    """
    We wait for the button press before we start streaming over ethernet.
    This allows the ethernet connection to be established, and gives time to start the server (on the laptop)
    """

    # On first button press
    if button_press_count == 0:
        # start streaming the data from the pi...
        stream_cmd = "../../odas/build/bin/odaslive -c ./respeaker_6_mic_array.cfg"
        subprocess.call(stream_cmd, shell=True)
        button_press_count += 1
    # Otherwise, shutdown the pi
    else:
        logging.info('\nButton press detected. Safely shutting down.\n')
        print("2nd button press detected - shutting down")
        safe_shutdown()


if __name__ == "__main__":
    
    # Setting up the button (on the top of the 6 mic array)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(array_mic_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    GPIO.add_event_detect(array_mic_button, GPIO.FALLING,
                          callback=interrupt_button_callback, bouncetime=100)
    
    print("Waiting for button press, to begin streaming")

    while True:
        time.sleep(1)
    
