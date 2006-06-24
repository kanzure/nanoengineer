"""Version information for NanoEngineer-1,
including author list, program name, release info, etc.
"""

__copyright__ = "Copyright (C) 2004-2006, Nanorex, Inc."

# Alphabetical by last name
__author__ = """Damian Allis
K. Eric Drexler
Josh Hall
Eric Messick
Huaicai Mo
Ninad Sathaye
Mark Sims
Bruce Smith
Will Ware"""

class Version:
    """Example usage:
    from version import Version
    v = Version()
    print v, v.product, v.authors
    """
    # Every instance of Version will share the same state
    __shared_state = {
        "major": 0,
        "minor": 7,
        "tiny": 1,     # tiny and teeny are optional
        # "teensy": 0,   # you can have both, or just tiny, or neither
        "releaseType": "Alpha",
        "releaseDate": "June 23, 2006",
        "product": "NanoEngineer-1",
        "copyright": __copyright__,
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
        str = "v%d.%d" % (major, minor)
        if self.__shared_state.has_key("tiny"):
            teensy = self.__shared_state["tiny"]
            str += ".%d" % teensy
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