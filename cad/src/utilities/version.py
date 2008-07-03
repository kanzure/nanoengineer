# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
version.py -- provide version information for NanoEngineer-1,
including author list, program name, release info, etc.

@author: Will, Mark
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

NOTE: this is copied and imported by autoBuild.py in a directory
which contains no other files, so it needs to be completely self-contained.
(I.e. it should not import anything else in its source directory,
only builtin Python modules.)

Module classification, and refactoring needed:

This should be given a less generic name, and also split into a
high-level module (since it would differ for different applications
built from the same code base) and low-level global access to the
"currently running app's name and version info"
(perhaps implemented similarly to EndUser)
for uses like printing version info into output files
(as in our caller in files_pdb).

In the meantime, to avoid package import cycles, we pretend this is
entirely low-level and classify it as either utilities or constants.
[bruce 071215]
"""

import NE1_Build_Constants

# Note: __copyright__ and __author__ below are about NE1 as a whole,
# not about this specific file. (In some source files, __author__
# is defined and is about that specific file. That usage of
# __author__ is deprecated, superceded by an @author line in the
# module docstring. [bruce 071215 comment])

__copyright__ = "Copyright 2004-2008, Nanorex, Inc."

# Alphabetical by last name
__author__ = """
Damian Allis
K. Eric Drexler
Russ Fish
Josh Hall
Brian Helfrich
Eric Messick
Huaicai Mo
Tom Moore
Piotr Rotkiewicz
Ninad Sathaye
Mark Sims
Bruce Smith
Will Ware
"""

class Version:
    """
    Example usage:
    from utilities.version import Version
    v = Version()
    print v, v.product, v.authors
    """
    # Every instance of Version will share the same state
    tmpary = NE1_Build_Constants.NE1_RELEASE_VERSION.split(".")
    __shared_state = {
        "major": int(tmpary[0]),
        "minor": int(tmpary[1]),
        "releaseType": "",
        "releaseDate": NE1_Build_Constants.NE1_RELEASE_DATE,
        "product": "NanoEngineer-1",
        "copyright": __copyright__,
        "authors": __author__
        }
    if len(tmpary) >= 3:  #tiny and teensy are both not required in version
        __shared_state["tiny"] = int(tmpary[2])
        if len(tmpary) == 4:
            __shared_state["teensy"] = int(tmpary[3])
    def __init__(self):
        # Use Alex Martelli's singleton recipe
        # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531
        self.__dict__ = self.__shared_state
    def __setattr__(self, attr, value):  # attributes write-protected
        raise AttributeError, attr
    def __repr__(self):
        major = self.__shared_state["major"]
        minor = self.__shared_state["minor"]
        str = "%d.%d" % (major, minor)
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
