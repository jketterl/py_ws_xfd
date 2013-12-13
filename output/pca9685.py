from output import Output
import sys, time
sys.path.append('../Adafruit-Raspberry-Pi-Python-Code/Adafruit_PWM_Servo_Driver')
from Adafruit_PWM_Servo_Driver import PWM

class Pca9685(Output):
	def __init__(self):
		self.pwm = PWM(0x40, False)
		self.pwm.setPWMFreq(600)
		for i in range(0, 10):
			for k in range(0, 4095, 256):
				self.pwm.setPWM(i, 0, k)
				time.sleep(.02)
			self.pwm.setPWM(i, 0, 0)
		super(Pca9685, self).__init__()

	def setState(self, states):
		channels = []
		for state in states:
			if state == 'SUCCESS':
				channels.append(2)
			elif state == 'UNSTABLE':
				channels.append(1)
			elif state == 'FAILURE':
				channels.append(0)
		for i in range(3):
			self.pwm.setPWM(i, 0, 4095 if i in channels else 0) 
