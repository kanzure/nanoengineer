class _fakemethod_class(object):
    def __init__(self, name):
        self.name = name
    def fakemethod(self, *args):
        return self.name, args
    pass

class Description_Making_Methods(object): #e rename; also let it assertfail if attr not recognized
    "#doc"
    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError, attr
        #e assert attr in some list, perhaps generated from filtering dir(some subclass of HighlightGraphics)
        fakemethod = _fakemethod_class(name = attr).fakemethod
            # note: using a local function didn't seem to work re storing name --
            # e.g. the arg signature (*args, _name = attr) was not allowed.
        setattr(self, attr, fakemethod) # cache it for efficiency
        return fakemethod
    pass

def description_maker_for_methods_in_class( cls):
    del cls
    return Description_Making_Methods() # kluge: use dir(cls) as in comment above

