"""
Created on Nov 19, 2012

@author: jketterl
"""

from tornado import ioloop, web, websocket
import threading
import json
import traceback


class ControlSocket(websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(ControlSocket, self).__init__(*args, **kwargs)
        self.listeners = []

    def open(self):
        pass

    def on_message(self, message):
        message = json.loads(message)
        if 'module' not in message:
            controllable = ControlServer.getInstance()
        else:
            controllable = ControlServer.getInstance().getControllable(message['module'])

        if controllable is None:
            self.write_message(json.dumps({'status': 'EXCEPTION', 'message': 'controllable not found'}))
            return
        if 'command' not in message:
            return
        params = {}
        if 'params' in message:
            params = message['params']
        params['socket'] = self

        try:
            response = {'status': 'OK', 'data': controllable.executeCommand(message['command'], **params)}
        except Exception as e:
            traceback.print_exc()
            response = {'status': 'EXCEPTION', 'message': str(e)}

        if 'sequence' in message:
            response['sequence'] = message['sequence']
        self.write_message(json.dumps(response))

    def on_close(self):
        for listener in self.listeners:
            listener.onClose(self)

    def addListener(self, listener):
        self.listeners.append(listener)

    def check_origin(self, origin):
        return True


class Controllable(object):
    def __init__(self, *args, **kwargs):
        ControlServer.getInstance().registerControllable(self)
        self.listeners = []

        # try to call the super constructor. this might fail if python mro gives us object as super, but there's no way
        # to know before actually calling it...
        try:
            super(Controllable, self).__init__(*args, **kwargs)
        except TypeError:
            pass

    def executeCommand(self, command, **kwargs):
        return getattr(self, command)(**kwargs)

    def emit(self, data):
        for listener in self.listeners:
            listener.write_message(json.dumps({'source': self.getId(), 'data': data}))

    def listen(self, socket=None):
        socket.addListener(self)
        self.listeners.append(socket)

    def onClose(self, socket):
        self.listeners.remove(socket)

    def unregister(self):
        ControlServer.getInstance().unregisterControllable(self)


class ControlServer(Controllable):
    _instance = None

    @staticmethod
    def getInstance():
        if ControlServer._instance is None:
            ControlServer._instance = ControlServer()
        return ControlServer._instance

    def __init__(self, *args, **kwargs):
        self.app = web.Application([
            (r"/socket", ControlSocket),
            (r"/(.*)", web.StaticFileHandler, {"path": "ws"}),
        ])
        self.app.listen(8000)
        threading.Thread(target=ioloop.IOLoop.instance().start).start()

        self.controllables = {}

        # instead of the super constructor call
        self.listeners = []
        self.registerControllable(self)

    def shutdown(self):
        ioloop.IOLoop.instance().stop()

    def registerControllable(self, controllable):
        cid = controllable.getId()
        self.controllables[cid] = controllable
        self.emit({'add': {'id': cid, 'type': controllable.__class__.__name__}})

    def unregisterControllable(self, controllable):
        cid = controllable.getId()
        self.emit({'remove': {'id': cid}})
        del self.controllables[cid]

    def getControllable(self, id):
        try:
            return self.controllables[id]
        except KeyError:
            return None

    def getControllables(self):
        result = []
        for key in self.controllables:
            controllable = self.controllables[key]
            result.append({'id': controllable.getId(), 'type': controllable.__class__.__name__})
        return result

    def getId(self):
        return 'controlserver'


class Storable(object):
    def __init__(self, *args, **kwargs):
        self.apply(**kwargs)

        # try to call the super constructor. this might fail if python mro gives us object as super, but there's no way
        # to know before actually calling it...
        try:
            super(Storable, self).__init__(*args, **kwargs)
        except TypeError:
            pass

    def _json(self):
        result = {}
        for key in self.fields:
            if hasattr(self, key):
                result[key] = getattr(self, key)
        return result

    def apply(self, **kwargs):
        for key in self.fields:
            if key in kwargs:
                setattr(self, key, kwargs[key])


class List(Controllable):
    def __init__(self, storageFile):
        self.objects = []
        self.idSequence = 0
        self.storageFile = storageFile
        try:
            f = open(self.storageFile, "r")
            jinput = json.loads(f.read())
            for rec in jinput:
                if "id" in rec and rec["id"] > self.idSequence:
                    self.idSequence = rec["id"]
            for rec in jinput:
                if "id" not in rec:
                    rec["id"] = self.getNextSequence()
                self.addObject(self.constructor(**rec))
        except IOError:
            traceback.print_exc()
            pass
        super(List, self).__init__()

    def _json(self):
        return [o._json() for o in self.objects]

    def _write(self):
        f = open(self.storageFile, "w")
        f.write(json.dumps(self._json()))
        f.close()

    def all(self):
        return self.objects

    def getNextSequence(self):
        self.idSequence += 1
        return self.idSequence

    def findById(self, id):
        for candidate in self.objects:
            if candidate.id == id:
                return candidate
        raise Exception("id not found")

    def read(self, **kwargs):
        return self._json()

    def write(self, **kwargs):
        if "id" not in kwargs:
            raise Exception("record could not be identified")
        object = self.findById(kwargs["id"])
        self.updateObject(object, **kwargs)
        self._write()
        return object._json()

    def delete(self, **kwargs):
        if "id" not in kwargs:
            raise Exception("record could not be identified")
        object = self.findById(kwargs["id"])
        self.removeObject(object)
        self._write()

    def add(self, *args, **kwargs):
        kwargs["id"] = self.getNextSequence()
        ob = self.constructor(**kwargs)
        self.addObject(ob)
        self._write()
        return ob._json()

    def addObject(self, obj):
        self.objects.append(obj)

    def updateObject(self, obj, **kwargs):
        obj.apply(**kwargs)

    def removeObject(self, obj):
        self.objects.remove(obj)


class Readonly(object):
    def write(self, **kwargs):
        pass

    def add(self, *args, **kwargs):
        pass

    def delete(self, **kwargs):
        pass
