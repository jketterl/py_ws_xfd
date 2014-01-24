from control import Controllable, Storable, List, Readonly
from ws4py.client.threadedclient import WebSocketClient
from ws4py.exc import WebSocketException
import json, uuid, urllib2, logging, socket, time, threading, re
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

    def getProjects(self):
        return self.projectListeners.keys()
    def addProjectListener(self, project, listener):
        if not project.name in self.projectListeners: self.projectListeners[project.name] = []
        self.projectListeners[project.name].append(listener)
        self.ws.loadCurrentState(project.name)
    def removeProjectListener(self, project, listener):
        if not project.name in self.projectListeners: return
        self.projectListeners[project.name].remove(listener)
    def apply(self, *args, **kwargs):
        if hasattr(self, "ws"): self.ws.stop()
        super(Server, self).apply(*args, **kwargs)
        self.ws = JenkinsClient(self)
        self.ws.start()
    def pushResult(self, projectName, result):
        if not projectName in self.projectListeners:
            logging.error("%s is not a registered project", projectName)
            return
        for listener in self.projectListeners[projectName]:
            listener.receiveState(result)

class Job(Storable):
    fields = [ "id", "name", "server_id", "output_id" ]
    def __init__(self, *args, **kwargs):
        self.state = 'UNKNOWN'
        super(Job, self).__init__(*args, **kwargs)
    def wire(self, server, output):
        self.unwire()
        self.output = output
        self.server = server
        server.addProjectListener(self, self)
    def unwire(self):
        if hasattr(self, "server"): self.server.removeProjectListener(self, self)
        self.output = None
    def receiveState(self, state):
        if (state == 'BLINK'):
            state = self.state + '_BLINK'

        pattern = re.compile('^([A-Z]+)(_BLINK)?$')
        match = pattern.match(state)
        if not match: return
        self.state = match.group(1)

        logging.info("project " + self.name + " received state " + state)
        if self.output is None: return
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
    def rewireJob(self, job):
        server = self.serverList.findById(job.server_id)
        output = self.outputList.findById(job.output_id)
        job.wire(server, output)
    def addObject(self, job):
        super(JobList, self).addObject(job)
        self.rewireJob(job)
    def updateObject(self, job, **kwargs):
        super(JobList, self).updateObject(job, **kwargs)
        self.rewireJob(job)
    def removeObject(self, job):
        super(JobList, self).removeObject(job)
        job.unwire()

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
    def __init__(self, server):
        self.server = server
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

        while (self.shouldBeOnline):
            logging.debug("starting refresh cycle on %s", self.server.name)
            for projectName in self.server.getProjects():
                self.loadCurrentState(projectName)
            logging.debug("refresh cycle on %s finished", self.server.name)
            time.sleep(30)

    def loadCurrentState(self, projectName):
        try:
            url = self.server.getBaseUrl() + "job/" + projectName + "/lastBuild/api/json"
            res = json.loads(urllib2.urlopen(url).read())
            if res['result'] != None: return self.server.pushResult(projectName, res['result'])

            # if the result of the latest build is null, we assume the build to be currently in progress.
            # download the build before to get the last known result
            url = self.server.getBaseUrl() + "job/" + projectName + "/" + str(res['number'] - 1) + "/api/json"
            res = json.loads(urllib2.urlopen(url).read())
            self.server.pushResult(projectName, res['result'] + "_BLINK")
        except urllib2.HTTPError as e:
            logging.error("HTTP error occured while trying to refresh project %s", projectName)
            logging.exception(e)

    def getSocket(self):
        if self.socket is None:
            self.socket = JenkinsSocket('ws://' + self.server.host + ':' + str(self.server.wsPort) + '/jenkins', self);
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
        if not 'project' in message: return
        if 'result' in message:
            self.server.pushResult(message['project'], message['result'])
        else:
            self.server.pushResult(message['project'], 'BLINK')

    def stop(self):
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
