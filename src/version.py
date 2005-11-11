"""Version information for nanoENGINEER,
and other stuff like author list, program name, release info, etc.

Example usage:
from version import Version
v = Version()
print v
print v.product
print v.authors
"""

# Use Alex Martelli's singleton recipe
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531

class Version:
    # Every instance of Version will share the same state
    __shared_state = {}
    def __init__(self, major=None, minor=None,
                 tiny=None, teensy=None):
        self.__dict__ = self.__shared_state
        if major != None:
            self.__shared_state["major"] = major
            self.__shared_state["minor"] = minor
            self.__shared_state["tiny"] = tiny
            if teensy != None:
                self.__shared_state["teensy"] = teensy
    def __setattr__(self, attr, value):
        # attributes can be write-protected
        if self.__shared_state.has_key("write_protect"):
            raise AttributeError, attr
        self.__shared_state[attr] = value
    def writeProtect(self):
        self.__shared_state["write_protect"] = True
    def __repr__(self):
        major = self.__shared_state["major"]
        minor = self.__shared_state["minor"]
        tiny = self.__shared_state["tiny"]
        str = "v%d.%d.%d" % (major, minor, tiny)
        if self.__shared_state.has_key("teensy"):
            teensy = self.__shared_state["teensy"]
            str += ".%d" % teensy
        return str

v = Version(0, 0, 6, 7)
v.releaseType = "Alpha"
v.releaseDate = "January 1, 2025"

v.product = "nanoENGINEER-1"
v.copyright = "Copyright (C) 2004-2005, Nanorex, Inc."

# Last names in alphabetical order
v.authors = """Josh Hall
Eric Messick
Huaicai Mo
Ninad Sathaye
Mark Sims
Bruce Smith
Will Ware"""

#v.writeProtect()
v.write_protect = True
del v   # leave the namespace uncluttered

###############################

if __name__ == "__main__":
    v = Version()
    for x in dir(v):
        print x + ":", getattr(v, x)
        print
    # test write protection
    try:
        v.foo = "bar"
        print "WRITE PROTECTION IS BROKEN"
    except AttributeError:
        pass
