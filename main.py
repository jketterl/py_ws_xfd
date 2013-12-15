#!/usr/bin/python
# -*- coding: utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient
from output import Output
import threading, time, json, urllib2, base64, ConfigParser, socket, logging, control

import jenkins

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

class JenkinsClient(object):
    user = None
    token = None
    def __init__(self, output, host, httpPort, wsPort, projects):
        self.output = output
        self.host = host
        self.httpPort = httpPort
        self.wsPort = wsPort
        self.projects = projects
        self.socket = None
        self.shouldBeOnline = False
        self.states = dict(zip(self.projects,  ['UNSTABLE'] * len(projects)))

    def setAuthentication(self, user, token):
        self.user = user
        self.token = token

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
        if not 'result' in message: return logging.warn("Invalid message on websocket")
        self.states[message['project']] = message['result']
        self.output.setState(list(set(self.states.values())))

    def readCurrentState(self):
        logging.info('getting initial states')
        if self.user is not None and self.token is not None:
            auth = base64.encodestring('%s:%s' % (self.user, self.token)).replace('\n', '')
        else:
            auth = None
        for project in self.projects:
            req = urllib2.Request('http://' + self.host + ':' + str(self.httpPort) + '/job/' + project + '/lastBuild/api/json')
            if auth is not None: req.add_header('Authorization', 'Basic: %s' % auth)
            res = urllib2.urlopen(req)
            message = json.loads(res.read())
            message['project'] = project
            self.update(message)

    def close(self):
        self.shouldBeOnline = False
        if self.socket is None: return
        self.socket.close()

class JenkinsSocket(WebSocketClient):
    def __init__(self, url, target):
        self.target = target
        super(JenkinsSocket, self).__init__(url, heartbeat_freq = 20)

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

    serverList = jenkins.ServerList("servers.json")
    
    output = Output.factory(config.get('output', 'type'))

    try:
        ws = JenkinsClient(output,
                   config.get('jenkins', 'host'),
                   config.get('jenkins', 'httpPort'),
                   config.get('jenkins', 'wsPort'),
                   config.get('project', 'name').split(','));
        try:
            ws.setAuthentication(config.get('jenkins', 'user'), config.get('jenkins', 'token'))
        except (ConfigParser.NoOptionError):
            pass
        ws.start()
        while threading.active_count() > 0 :
            time.sleep(20)

    except (KeyboardInterrupt, SystemExit):
        logging.info("shutting down")
        output.shutdown()
        control.ControlServer.getInstance().shutdown()
        ws.close()
