# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
api_enforcement.py - utilities for API enforcement (experimental).

Provides def or class privateMethod, etc.

@author: Will
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.

History:

Experimental code by Will. May have worked, but never extensively used.

Bruce 071107 split it from debug.py into this scratch file.
"""

# REVIEW: might require some imports from debug.py

import sys, os, time, types, traceback
from utilities.constants import noop
import foundation.env as env
from utilities import debug_flags

# ==

API_ENFORCEMENT = False   # for performance, commit this only as False

class APIViolation(Exception):
    pass

# We compare class names to find out whether calls to private methods
# are originating from within the same class (or one of its friends). This
# could give false negatives, if two classes defined in two different places
# have the same name. A work-around would be to use classes as members of
# the "friends" tuple instead of strings. But then we need to do extra
# imports, and that seems to be not only inefficient, but to sometimes
# cause exceptions to be raised.

def _getClassName(frame):
    """
    Given a frame (as returned by sys._getframe(int)), dig into
    the list of local variables' names in this stack frame. If the
    frame represents a method call in an instance of a class, then the
    first local variable name will be "self" or whatever was used instead
    of "self". Use that to index the local variables for the frame and
    get the instance that owns that method. Return the class name of
    the instance.
    See http://docs.python.org/ref/types.html for more details.
    """
    varnames = frame.f_code.co_varnames
    selfname = varnames[0]
    methodOwner = frame.f_locals[selfname]
    return methodOwner.__class__.__name__

def _privateMethod(friends=()):
    """
    Verify that the call made to this method came either from within its
    own class, or from a friendly class which has been granted access. This
    is done by digging around in the Python call stack. The "friends" argument
    should be a tuple of strings, the names of the classes that are considered
    friendly. If no list of friends is given, then any calls from any other
    classes will be flagged as API violations.

    CAVEAT: Detection of API violations is done by comparing only the name of
    the class. (This is due to some messiness I encountered while trying to
    use the actual class object itself, apparently a complication of importing.)
    This means that some violations may not be detected, if we're ever careless
    enough to give two classes the same name.

    ADDITIONAL CAVEAT: Calls from global functions will usually be flagged as API
    violations, and should always be flagged. But this approach will not catch
    all such cases. If the first argument to the function happens to be an
    instance whose class name is the same as the class wherein the private
    method is defined, it won't be caught.
    """
    f1 = sys._getframe(1)
    f2 = sys._getframe(2)
    called = _getClassName(f1)
    caller = _getClassName(f2)
    if caller == called or caller in friends:
        # These kinds of calls are okay.
        return
    # Uh oh, an API violation. Print information that will
    # make it easy to track it down.
    import inspect
    f1 = inspect.getframeinfo(f1)
    f2 = inspect.getframeinfo(f2)
    lineno, meth = f1[1], f1[2]
    lineno2, meth2 = f2[1], f2[2]
    print
    print (called + "." + meth +
           " (line " + repr(lineno) + ")" +
           " is a private method called by")
    print (caller + "." + meth2 +
           " (line " + repr(lineno2) + ")" +
           " in file " + f2[0])
    raise APIViolation

if API_ENFORCEMENT:
    privateMethod = _privateMethod
else:
    # If we're not checking API violations, be as low-impact as possible.
    # In this case 'friends' is ignored.
    def privateMethod(friends = None):
        return

# end
