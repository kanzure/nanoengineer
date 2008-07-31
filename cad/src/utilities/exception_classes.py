# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
exception_classes.py -- exception classes for general use

@author: Will
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

Note:

This module can't be called exceptions.py, since that confuses
some other modules which try to import the Python builtin module
of the same name.

History:

Will wrote these in GeneratorBaseClass.py for its own use.
Since then they have become used by unrelated code,
so Bruce 080730 moved them into their own file.
"""

# REVIEW: AbstractMethod should ideally be merged with the other
# 2 or 3 variants of this idea, or replaced with the exception built into
# Python for this purpose.
# [070724 code review]

class AbstractMethod(Exception):
    def __init__(self):
        Exception.__init__(self, "Abstract method - must be overloaded")

# REVIEW:
# The following should be taught to help print messages about themselves,
# so that handlePluginExceptions (in GeneratorBaseClass) doesn't need to
# catch each one individually. This should be revisited after our overall
# error handling code is revised.
# [070724 code review]
#
# REVIEW: I suspect these exceptions are not handled in the best way, and in
# particular, I am not sure it's useful to have a CadBug exception class,
# given that any unexpected exception (of any class) also counts as a "bug
# in the cad code".
# [bruce 070719 comments]
#
# The docstrings are also not good enough (all the same).

class CadBug(Exception):
    """
    Useful for distinguishing between an exception from subclass
    code which is a bug in the cad, a report of an error in the
    plugin, or a report of a user error.
    """
    def __init__(self, arg = None):
        if arg is not None:
            Exception.__init__(self, arg)
        else:
            Exception.__init__(self)
    pass

class PluginBug(Exception):
    """
    Useful for distinguishing between an exception from subclass
    code which is a bug in the cad, a report of an error in the
    plugin, or a report of a user error.
    """
    def __init__(self, arg = None):
        if arg is not None:
            Exception.__init__(self, arg)
        else:
            Exception.__init__(self)
    pass

class UserError(Exception):
    """
    Useful for distinguishing between an exception from subclass
    code which is a bug in the cad, a report of an error in the
    plugin, or a report of a user error.
    """
    def __init__(self, arg = None):
        if arg is not None:
            Exception.__init__(self, arg)
        else:
            Exception.__init__(self)
    pass

# end
