from control import Controllable, Storable, List, Readonly
from ws4py.client.threadedclient import WebSocketClient
from ws4py.exc import WebSocketException
import json, uuid, urllib2, logging, socket, time, threading
from output import Output

class Server(Storable, Controllable):
    fields = [ "id", "name", "host", "port", "urlPrefix", "wsPort", "https", "user", "token", "uuid" ]
    def __init__(self, *args, **kwargs):
        if not "uuid" in kwargs or kwargs["uuid"] == "": kwargs["uuid"] = str(uuid.uuid4())
        self.projectListeners = {}
        super(Server, self).__init__(*args, **kwargs)
    def getId(self):
        return self.uuid
    def read(self, **kwargs):
        url = self.getBaseUrl() + "api/json"
        return json.loads(urllib2.urlopen(url).read())

    def getBaseUrl(self):
        return "http" + ("s" if self.https else "") + "://" + self.host + ":" + str(self.port) + "/" + self.urlPrefix + "/"

    def addProjectListener(self, project, listener):
        if not project.name in self.projectListeners: self.projectListeners[project.name] = []
        self.projectListeners[project.name].append(listener)
        listener.receiveState(self.loadCurrentState(project))
    def loadCurrentState(self, project):
        url = self.getBaseUrl() + "job/" + project.name + "/lastBuild/api/json"
        res = json.loads(urllib2.urlopen(url).read())
        if res['result'] != None: return res['result']

        # if the result of the latest build is null, we assume the build to be currently in progress.
        # download the build before to get the last known result
        url = self.getBaseUrl() + "job/" + project.name + "/" + str(res['number'] - 1) + "/api/json"
        res = json.loads(urllib2.urlopen(url).read())
        return res['result'] + "_BLINK"
    def apply(self, *args, **kwargs):
        logging.debug('apply called')
        super(Server, self).apply(*args, **kwargs)
        self.ws = JenkinsClient(self.host, self.wsPort)
        self.ws.start()
        logging.debug('apply leaving')

class Job(Storable):
    fields = [ "id", "name", "server_id", "output_id" ]
    def wire(self, server, output):
        self.output = output
        server.addProjectListener(self, self)
    def receiveState(self, state):
        logging.info("project " + self.name + " received state " + state)
        self.output.setState(self.id, state)

class ServerList(List):
    constructor = Server
    def getId(self):
        return "serverList"

class JobList(List):
    constructor = Job
    def __init__(self, file, serverList, outputList):
        self.serverList = serverList
        self.outputList = outputList
        super(JobList, self).__init__(file)
    def getId(self):
        return "jobList"
    def addObject(self, job):
        super(JobList, self).addObject(job)
        server = self.serverList.findById(job.server_id)
        output = self.outputList.findById(job.output_id)
        job.wire(server, output)

class OutputList(List, Readonly):
    def constructor(self, **kwargs):
        type = kwargs['type']
        del kwargs['type']
        return Output.factory(type, **kwargs)
    def getId(self):
        return "outputList"

class JenkinsClient(threading.Thread):
    user = None
    token = None
    def __init__(self, host, wsPort):
        self.host = host
        self.wsPort = wsPort
        self.socket = None
        self.shouldBeOnline = False
        super(JenkinsClient, self).__init__()

    def setAuthentication(self, user, token):
        self.user = user
        self.token = token

    def run(self):
        retries = 0
        self.shouldBeOnline = True
        while (retries < 5):
            try:
                self.getSocket()
                # reset retry counter on success
                retries = 0
            except WebSocketException as wse:
                self.socket = None
                retries += 1
                logging.error("websocket connection failed (%d retries)", retries)
                #logging.exception(wse)
                time.sleep(10)

        logging.info("falling back to polling")

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
        print message
        '''
        if 'project' in message and message['project'] not in self.projects: return
        if not 'result' in message: return logging.warn("Invalid message on websocket")
        self.states[message['project']] = message['result']
        self.output.setState(list(set(self.states.values())))
        '''

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
