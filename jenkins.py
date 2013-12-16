from control import Controllable
import json

class Storable(object):
    def __init__(self, **kwargs):
        self.apply(**kwargs)
    def _json(self):
        result = {}
        for key in self.fields:
            if hasattr(self, key): result[key] = getattr(self, key)
        return result
    def apply(self, **kwargs):
        for key in self.fields:
            if key in kwargs: setattr(self, key, kwargs[key])

class Server(Storable):
    fields = [ "id", "name", "host", "port", "wsPort", "https", "user", "token" ]

class Job(Storable):
    fields = [ "id", "name", "server_id" ]

class List(Controllable):
    def __init__(self, serverFile):
        self.objects = []
        self.idSequence = 0
        self.serverFile = serverFile
        try:
            f = open(self.serverFile, "r")
            input = json.loads(f.read())
            for rec in input:
                if "id" in rec and rec["id"] > self.idSequence: self.idSequence = rec["id"]
            for rec in input:
                if not "id" in rec:
                    rec["id"] = self.getNextSequence()
                self.objects.append(Server(**rec)) 
        except IOError:
            pass
        super(List, self).__init__()
    def _json(self):
        out = []
        for object in self.objects: out.append(object._json())
        return out
    def _write(self):
        f = open(self.serverFile, "w")
        f.write(json.dumps(self._json()))
        f.close()
    def getNextSequence(self):
        self.idSequence += 1;
        return self.idSequence
    def findById(self, id):
        for candidate in self.objects:
            if candidate.id == id: return candidate
        raise Exception("id not found")
    def read(self, **kwargs):
        return self._json()
    def write(self, **kwargs):
        if not "id" in kwargs: raise Exception("record could not be identified")
        object = self.findById(kwargs["id"])
        object.apply(**kwargs)
        self._write()
        return object._json()
    def delete(self, **kwargs):
        if not "id" in kwargs: raise Exception("record could not be identified")
        object = self.findById(kwargs["id"])
        self.objects.remove(object)
        self._write()
    def add(self, *args, **kwargs):
        kwargs["id"] = self.getNextSequence()
        server = self.constructor(**kwargs)
        self.objects.append(server)
        self._write()
        return server._json()

class ServerList(List):
    constructor = Server
    def getId(self):
        return "serverList"

class JobList(List):
    constructor = Job
    def getId(self):
        return "jobList"
