class Output(object):
    def shutdown(self):
        pass
    
    def setState(self, state):
        pass
    
    @staticmethod
    def factory(classname):
        mod = __import__("output.%s" % classname.lower(), fromlist=[classname.capitalize()])
        cls = getattr(mod, classname.capitalize())
        return cls()