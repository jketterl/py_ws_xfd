from control import Storable


class Output(Storable):
    fields = ['id', 'name']

    def shutdown(self):
        pass
    
    def setState(self, projectId, state):
        pass
    
    @staticmethod
    def factory(classname, *args, **kwargs):
        mod = __import__("output.%s" % classname.lower(), fromlist=[classname.capitalize()])
        cls = getattr(mod, classname.capitalize())
        return cls(*args, **kwargs)
