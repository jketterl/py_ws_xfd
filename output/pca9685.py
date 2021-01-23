from output import Output
import time
import threading
import re
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685


class Blinker(threading.Thread):
    _instance = None

    @staticmethod
    def getInstance():
        if Blinker._instance is None:
            Blinker._instance = Blinker()
            Blinker._instance.start()
        return Blinker._instance

    @staticmethod
    def addChannel(channel):
        return Blinker.getInstance()._addChannel(channel)

    @staticmethod
    def removeChannel(channel):
        if Blinker._instance == None: return
        return Blinker.getInstance()._removeChannel(channel)

    def __init__(self):
        super(Blinker, self).__init__()
        self.channels = []
        self.doRun = True

        # alpha filter
        self.filterTable = [0] * 16
        for i in range(16):
            self.filterTable[i] = round(max_brightness * (i / 15.0) ** 2.2)

    def run(self):
        while(self.doRun):
            for i in range(0, 16):
                self.setOutputs(self.filterTable[i])
                time.sleep(.05)
            for i in range(15, -1, -1):
                self.setOutputs(self.filterTable[i])
                time.sleep(.05)

    def stop(self):
        self.doRun = False
        Blinker._instance = None

    def setOutputs(self, value):
        for output in self.channels:
            pwm.channels[output].duty_cycle = value

    def _addChannel(self, channel):
        self.channels.append(channel)

    def _removeChannel(self, channel):
        if not channel in self.channels: return
        self.channels.remove(channel)
        if len(self.channels) == 0: self.stop()


pwm = PCA9685(busio.I2C(SCL, SDA))
pwm.frequency = 600

max_brightness = 5000


class Pca9685(Output):
    def __init__(self, offset, leds, *args, **kwargs):
        self.offset = offset
        self.leds = leds
        self.states = {}

        for i in range(0, len(self.leds)):
            for k in range(0, 16):
                pwm.channels[self.offset + i].duty_cycle = round((k / 16) * max_brightness)
                time.sleep(.02)
            pwm.channels[self.offset + i].duty_cycle =  0
        super(Pca9685, self).__init__(*args, **kwargs)

    def setState(self, projectId, state):
        self.states[projectId] = state
        self._setState(self.getUniqueStates())

    def getUniqueStates(self):
        out = []
        for id in self.states:
            state = self.states[id]
            if state in out: continue
            out.append(state)
        return out

    def _setState(self, states):
        out = [0] * len(self.leds)
        pattern = re.compile('^([A-Z]+)(_BLINK)?$')
        for state in states:
            match = pattern.match(state)
            if not match: continue
            led = match.group(1)
            if not led in self.leds: led = 'FAILURE'
            if match.group(2) == "_BLINK":
                out[self.leds[led]] = 'BLINK'
            else:
                out[self.leds[led]] = 'ON'
        for index, value in enumerate(out):
            Blinker.removeChannel(self.offset + index)
            if value == "ON":
                pwm.channels[self.offset + index].duty_cycle = max_brightness
            elif value == "BLINK":
                Blinker.addChannel(self.offset + index)
            else:
                pwm.channels[self.offset + index].duty_cycle = 0

    def shutdown(self):
        for i in range(len(self.leds)):
            Blinker.removeChannel(self.offset + i)
            pwm.channels[self.offset + i].duty_cycle = 0
