"""Version information for nanoENGINEER,
and other stuff like author list, program name, release info, etc.

Example usage:
from version import Version
v = Version()
print v, v.product, v.authors
"""

# Alphabetical by last name
__author__ = """Josh Hall
Eric Messick
Huaicai Mo
Ninad Sathaye
Mark Sims
Bruce Smith
Will Ware"""

class Version:
    # Every instance of Version will share the same state
    __shared_state = {
        "major": 0,
        "minor": 0,
        "tiny": 6,
        "teensy": 9,   # the teensy attribute is optional
        "releaseType": "Alpha",
        "releaseDate": "March 2, 2006",
        "product": "nanoENGINEER-1",
        "copyright": "Copyright (C) 2004-2005, Nanorex, Inc.",
        "authors": __author__
        }
    def __init__(self):
        # Use Alex Martelli's singleton recipe
        # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531
        self.__dict__ = self.__shared_state
    def __setattr__(self, attr, value):  # attributes write-protected
        raise AttributeError, attr
    def __repr__(self):
        major = self.__shared_state["major"]
        minor = self.__shared_state["minor"]
        tiny = self.__shared_state["tiny"]
        str = "v%d.%d.%d" % (major, minor, tiny)
        if self.__shared_state.has_key("teensy"):
            teensy = self.__shared_state["teensy"]
            str += ".%d" % teensy
        return str

###############################

if __name__ == "__main__":
    v = Version()
    print v
    for x in dir(v):
        print x + ":", getattr(v, x)
        print
    # test write protection
    try:
        v.foo = "bar"
        print "WRITE PROTECTION IS BROKEN"
    except AttributeError:
        pass