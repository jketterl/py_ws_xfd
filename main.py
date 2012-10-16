# -*- coding: utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient
import RPi.GPIO as GPIO
import threading, time

class JenkinsClient(WebSocketClient):
    def opened(self):
	print "Connection opened"

    def closed(self, code, reason):
        print "Closed down", code, reason

    def received_message(self, m):
        print "=> %d %s" % (len(m), str(m))

if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)
    GPIO.output(11, GPIO.LOW)
    GPIO.setup(12, GPIO.OUT)
    GPIO.output(12, GPIO.LOW)
    GPIO.setup(13, GPIO.OUT)
    GPIO.output(13, GPIO.LOW)

    try:
        ws = JenkinsClient('ws://dev-build.pocci.cxo.name:8000/jenkins', protocols=['http-only', 'chat'])
        ws.connect()
	while threading.active_count() > 0 :
		time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
	print "shutting down"
	GPIO.cleanup()
        ws.close()
