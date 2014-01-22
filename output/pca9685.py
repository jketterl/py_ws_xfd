from output import Output
import sys, time
sys.path.append('../Adafruit-Raspberry-Pi-Python-Code/Adafruit_PWM_Servo_Driver')
from Adafruit_PWM_Servo_Driver import PWM

class Pca9685(Output):
    def __init__(self, offset, leds, *args, **kwargs):
        self.offset = offset
        self.leds = leds

        self.pwm = PWM(0x40, False)
        self.pwm.setPWMFreq(600)
        for i in range(0, len(self.leds)):
            for k in range(0, 4095, 256):
                self.pwm.setPWM(self.offset + i, 0, k)
                time.sleep(.02)
            self.pwm.setPWM(self.offset + i, 0, 0)
        super(Pca9685, self).__init__(*args, **kwargs)

    def setState(self, states):
        out = [0] * len(self.leds)
        for state in states:
            if not state in self.leds: continue
            out[self.leds[state]] = 4095
        for index, value in enumerate(out):
            self.pwm.setPWM(self.offset + index, 0, value) 

    def shutdown(self):
        for i in range(10):
            self.pwm.setPWM(self.offset + i, 0, 0)
