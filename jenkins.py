from control import Controllable
import json

class Server(object):
    fields = [ "name", "host", "port", "wsPort", "https", "user", "token" ]
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
    def __init__(self, serverFile):
        self.serverFile = serverFile
        f = open(self.serverFile, "r")
        input = json.loads(f.read())
        for rec in input: self.objects.append(Server(**rec)) 
        super(List, self).__init__()
    def _json(self):
        out = []
        for object in self.objects: out.append(object._json())
        return out
    def _write(self):
        f = open(self.serverFile, "w")
        f.write(json.dumps(self._json()))
        f.close()
    def read(self, **kwargs):
        return self._json()

class ServerList(List):
    def getId(self):
        return "serverList"
    def add(self, *args, **kwargs):
        server = Server(**kwargs)
        self.objects.append(server)
        self._write()
        return server._json()
