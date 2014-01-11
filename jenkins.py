from control import Controllable, Storable, List, Readonly
import json, uuid, urllib2
from output import Output

class Server(Storable, Controllable):
    fields = [ "id", "name", "host", "port", "wsPort", "https", "user", "token", "uuid" ]
    def __init__(self, *args, **kwargs):
        if not "uuid" in kwargs or kwargs["uuid"] == "": kwargs["uuid"] = str(uuid.uuid4())
        super(Server, self).__init__(*args, **kwargs)
    def getId(self):
        return self.uuid
    def read(self, **kwargs):
        url = "http" + ("s" if self.https else "") + "://" + self.host + ":" + str(self.port) + "/api/json"
        return json.loads(urllib2.urlopen(url).read())

class Job(Storable):
    fields = [ "id", "name", "server_id", "output_id" ]

class ServerList(List):
    constructor = Server
    def getId(self):
        return "serverList"

class JobList(List):
    constructor = Job
    def getId(self):
        return "jobList"

class OutputList(List, Readonly):
    def constructor(self, **kwargs):
        type = kwargs['type']
        del kwargs['type']
        return Output.factory(type, **kwargs)
    def getId(self):
        return "outputList"

