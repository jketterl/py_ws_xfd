from control import Controllable

class ServerList(Controllable):
    def getId(self):
        return "serverList"
    def add(self, *args, **kwargs):
        print kwargs
