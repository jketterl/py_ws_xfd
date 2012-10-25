#!/usr/bin/python
# -*- coding: utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient
import RPi.GPIO as GPIO
import threading, time, json, urllib2, base64, ConfigParser, socket, logging

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

class JenkinsClient:
	def __init__(self, host, httpPort, wsPort, project, user, token):
		self.host = host
		self.httpPort = httpPort
		self.wsPort = wsPort
		self.project = project
		self.user = user
		self.token = token
		self.socket = None

	def start(self):
		self.readCurrentState()
		self.getSocket()

	def getSocket(self):
		if self.socket is None:
			self.socket = JenkinsSocket('ws://' + self.host + ':' + str(self.wsPort) + '/jenkins', self);
			self.socket.start()
		return self.socket

	def onClose(self, origin):
		if origin is not self.socket: return
		self.socket = None
		self.getSocket()

	def onMessage(self, message, origin):
		if origin is not self.socket: return
		self.update(message)

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

	def ping(self):
		ping = self.getSocket().stream.ping('some_data')
		self.getSocket().sender(ping);

	def close(self):
		if self.socket is None: return
		self.socket.close()

class JenkinsSocket(WebSocketClient):
	def __init__(self, url, target):
		self.target = target
		super(JenkinsSocket, self).__init__(url)

	def opened(self):
		logging.info("Connection opened")

	def closed(self, code, reason):
		logging.info("Closed down: %i %s", code, reason)
		self.close()
		self.target.onClose(self)

	def received_message(self, m):
		#print "=> %d %s" % (len(m), str(m))
		message = json.loads(str(m));
		self.target.onMessage(message, self)

	def start(self):
		connected = False
		while not connected:
			try:
				logging.info('attempting connection...')
				self.connect()
				connected = True
			except socket.error as e:
				logging.warn('failed')
				logging.warn(str(e))
				time.sleep(10);

	def ponged(self, pong):
		logging.debug('ponged: ' + pong)
		super(JenkinsClient, self).ponged()

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
			ws.ping()

	except (KeyboardInterrupt, SystemExit):
		logging.info("shutting down")
		GPIO.cleanup()
        	ws.close()
