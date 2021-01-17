"""
Created on Nov 12, 2012

@author: jketterl
"""

from output import Output
import RPi.GPIO as GPIO
import time


class GPIO(Output):
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11, GPIO.OUT)
        GPIO.output(11, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(11, GPIO.LOW)
        GPIO.setup(12, GPIO.OUT)
        GPIO.output(12, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(12, GPIO.LOW)
        GPIO.setup(13, GPIO.OUT)
        GPIO.output(13, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(13, GPIO.LOW)
        super(GPIO, self).__init__()
        
    def setState(self, states):
        # turn all LEDs off
        GPIO.output(11, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        # turn on only the one that reflects our status
        for state in states:
            if state == 'SUCCESS':
                GPIO.output(13, GPIO.HIGH)
            elif state == 'UNSTABLE':
                GPIO.output(12, GPIO.HIGH)
            elif state == 'FAILURE':
                GPIO.output(11, GPIO.HIGH)
