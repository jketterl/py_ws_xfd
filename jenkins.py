from control import Controllable
import json

class Server(object):
    fields = [ "id", "name", "host", "port", "wsPort", "https", "user", "token" ]
    host = ""
    port = 8080
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

class List(Controllable):
    objects = []
    idSequence = 0
    def __init__(self, serverFile):
        self.serverFile = serverFile
        f = open(self.serverFile, "r")
        input = json.loads(f.read())
        for rec in input:
            if "id" in rec and rec["id"] > self.idSequence: self.idSequence = rec["id"]
        for rec in input:
            if not "id" in rec:
                rec["id"] = self.getNextSequence()
            self.objects.append(Server(**rec)) 
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

class ServerList(List):
    def getId(self):
        return "serverList"
    def add(self, *args, **kwargs):
        kwargs["id"] = self.getNextSequence()
        server = Server(**kwargs)
        self.objects.append(server)
        self._write()
        return server._json()
