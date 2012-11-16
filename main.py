#!/usr/bin/python
# -*- coding: utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient
from output import Ampel
#from output import Console
import threading, time, json, urllib2, base64, ConfigParser, socket, logging

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

class JenkinsClient(object):
	def __init__(self, output, host, httpPort, wsPort, projects, user, token):
		self.output = output
		self.host = host
		self.httpPort = httpPort
		self.wsPort = wsPort
		self.projects = projects
		self.user = user
		self.token = token
		self.socket = None
		self.shouldBeOnline = False
		self.states = dict(zip(self.projects,  ['UNSTABLE'] * len(projects)))

	def start(self):
		self.readCurrentState()
		self.shouldBeOnline = True
		self.getSocket()

	def getSocket(self):
		if self.socket is None:
			self.socket = JenkinsSocket('ws://' + self.host + ':' + str(self.wsPort) + '/jenkins', self);
			self.socket.start()
		return self.socket

	def onClose(self, origin):
		if origin is not self.socket: return
		self.socket = None
		if not self.shouldBeOnline: return
		self.getSocket()

	def onMessage(self, message, origin):
		if origin is not self.socket: return
		self.update(message)

	def update(self, message):
		if 'project' in message and message['project'] not in self.projects: return
		self.states[message['project']] = message['result']
		self.output.setState(list(set(self.states.values())))

	def readCurrentState(self):
		logging.info('getting initial states')
		auth = base64.encodestring('%s:%s' % (self.user, self.token)).replace('\n', '')
		for project in self.projects:
			req = urllib2.Request('http://' + self.host + ':' + str(self.httpPort) + '/job/' + project + '/lastBuild/api/json')
			req.add_header('Authorization', 'Basic: %s' % auth)
			res = urllib2.urlopen(req)
			message = json.loads(res.read())
			message['project'] = project
			self.update(message)

	def ping(self):
		ping = self.getSocket().stream.ping('some_data')
		self.getSocket().sender(ping);

	def close(self):
		self.shouldBeOnline = False
		if self.socket is None: return
		self.socket.close()

class JenkinsSocket(WebSocketClient):
	def __init__(self, url, target):
		self.target = target
		super(JenkinsSocket, self).__init__(url)

	def opened(self):
		logging.info("Websocket connection opened")

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
				logging.info('Attempting websocket connection...')
				self.connect()
				connected = True
			except socket.error as e:
				logging.warn('Websocket connection failed')
				logging.warn(str(e))
				time.sleep(10);

if __name__ == '__main__':

	config = ConfigParser.ConfigParser()
	config.read('config.ini')
	
	output = Ampel()
	#output = Console()

	try:
		ws = JenkinsClient(output,
				   config.get('jenkins', 'host'),
				   config.get('jenkins', 'httpPort'),
				   config.get('jenkins', 'wsPort'),
				   config.get('project', 'name').split(','),
				   config.get('jenkins', 'user'),
				   config.get('jenkins', 'token'));
		ws.start()
		while threading.active_count() > 0 :
			time.sleep(20)
			ws.ping()

	except (KeyboardInterrupt, SystemExit):
		logging.info("shutting down")
		output.shutdown()
		ws.close()
