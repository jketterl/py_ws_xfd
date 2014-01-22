from output import Output
import sys, time, threading, re
sys.path.append('../Adafruit-Raspberry-Pi-Python-Code/Adafruit_PWM_Servo_Driver')
from Adafruit_PWM_Servo_Driver import PWM

pwm = PWM(0x40, False)
pwm.setPWMFreq(600)

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

    def run(self):
        while(self.doRun):
            for i in range(0, 4095, 256):
                self.setOutputs(i)
                time.sleep(.05)
            for i in range(4095, 0, -256):
                self.setOutputs(i)
                time.sleep(.05)

    def stop(self):
        self.doRun = False
        Blinker._instance = None

    def setOutputs(self, value):
        for output in self.channels:
            pwm.setPWM(output, 0, value)

    def _addChannel(self, channel):
        self.channels.append(channel)

    def _removeChannel(self, channel):
        if not channel in self.channels: return
        self.channels.remove(channel)
        if len(self.channels) == 0: self.stop()

class Pca9685(Output):
    def __init__(self, offset, leds, *args, **kwargs):
        self.offset = offset
        self.leds = leds
        self.states = {}

        for i in range(0, len(self.leds)):
            for k in range(0, 4095, 256):
                pwm.setPWM(self.offset + i, 0, k)
                time.sleep(.02)
            pwm.setPWM(self.offset + i, 0, 0)
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
            if not led in self.leds: continue
            if match.group(2) == "_BLINK":
                out[self.leds[led]] = 'BLINK'
            else:
                out[self.leds[led]] = 'ON'
        for index, value in enumerate(out):
            Blinker.removeChannel(self.offset + index)
            if value == "ON":
                pwm.setPWM(self.offset + index, 0, 4095) 
            elif value == "BLINK":
                Blinker.addChannel(self.offset + index)
            else:
                pwm.setPWM(self.offset + index, 0, 0)

    def shutdown(self):
        for i in range(len(self.leds)):
            Blinker.removeChannel(self.offset + i)
            pwm.setPWM(self.offset + i, 0, 0)
