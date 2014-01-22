from control import Controllable, Storable, List, Readonly
import json, uuid, urllib2
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
        if not project in self.projectListeners: self.projectListeners[project] = []
        self.projectListeners[project] = listener
        listener.receiveState(self.loadCurrentState(project))
    def loadCurrentState(self, project):
        url = self.getBaseUrl() + "job/" + project + "/lastBuild/api/json"
        res = json.loads(urllib2.urlopen(url).read())
        return res['result']

class Job(Storable):
    fields = [ "id", "name", "server_id", "output_id" ]
    def wire(self, server, output):
        self.output = output
        server.addProjectListener(self.name, self)
    def receiveState(self, state):
        self.output.setState([state])

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

