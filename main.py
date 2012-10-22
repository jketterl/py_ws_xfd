#!/usr/bin/python
# -*- coding: utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient
import RPi.GPIO as GPIO
import threading, time, json, urllib2, base64, ConfigParser, socket

class JenkinsClient(WebSocketClient):
	def __init__(self, host, httpPort, wsPort, project, user, token):
		self.host = host
		self.httpPort = httpPort
		self.wsPort = wsPort
		self.project = project
		self.user = user
		self.token = token
		super(JenkinsClient, self).__init__('ws://' + self.host + ':' + str(self.wsPort) + '/jenkins')
		#super(JenkinsClient, self).__init__('ws://jketterl-n0:8080/')

	def opened(self):
		print "Connection opened"

	def closed(self, code, reason):
		print "Closed down", code, reason
		self.close()
		self.start()

	def received_message(self, m):
		print "=> %d %s" % (len(m), str(m))
		message = json.loads(str(m));
		self.update(message)

	def start(self):
		connected = False
		while not connected:
			try:
				print 'attempting connection...'
				self.connect()
				connected = True
			except socket.error as e:
				print 'failed'
				print e
				time.sleep(10);
		self.readCurrentState()

	def update(self, message):
		if 'project' in message and message['project'] != self.project: return
		# turn all LEDs off
		GPIO.output(11, GPIO.LOW)
		GPIO.output(12, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
		# turn on only the one that reflects our status
		if message['result'] == 'SUCCESS':
			GPIO.output(13, GPIO.HIGH)
		elif message['result'] == 'UNSTABLE':
			GPIO.output(12, GPIO.HIGH)
		elif message['result'] == 'FAILURE':
			GPIO.output(11, GPIO.HIGH)

	def readCurrentState(self):
		auth = base64.encodestring('%s:%s' % (self.user, self.token)).replace('\n', '')
		req = urllib2.Request('http://' + self.host + ':' + str(self.httpPort) + '/job/' + self.project + '/lastBuild/api/json')
		req.add_header('Authorization', 'Basic: %s' % auth)
		res = urllib2.urlopen(req)
		message = json.loads(res.read())
		self.update(message)

	def ponged(self):
		print 'ponged'

if __name__ == '__main__':
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(11, GPIO.OUT)
	GPIO.output(11, GPIO.LOW)
	GPIO.setup(12, GPIO.OUT)
	GPIO.output(12, GPIO.LOW)
	GPIO.setup(13, GPIO.OUT)
	GPIO.output(13, GPIO.LOW)

	config = ConfigParser.ConfigParser()
	config.read('config.ini')

	try:
		ws = JenkinsClient(config.get('jenkins', 'host'),
				   config.get('jenkins', 'httpPort'),
				   config.get('jenkins', 'wsPort'),
				   config.get('project', 'name'),
				   config.get('jenkins', 'user'),
				   config.get('jenkins', 'token'));
		ws.start()
		while threading.active_count() > 0 :
			time.sleep(10)
			ws.sender(ws.stream.ping('some_data'));

	except (KeyboardInterrupt, SystemExit):
		print "shutting down"
		GPIO.cleanup()
        	ws.close()
