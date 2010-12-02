# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
__Symbols__.py -- support for "from __Symbols__ import xxx", from within the exprs module.

NOTE: This module replaces its entry in sys.modules with a FakeModule object, which probably doesn't support reload.

$Id$

"""
__author__ = "bruce" # (but I took the idea of FakeModule from Pmw == Python Megawidgets) 

from Exprs import Symbol
    # no point in supporting reload of that, since this module doesn't support reload

class FakeModule:
    #e [obs comment?] when working stably, i could make it stable across reloads -- if Symbol (passed in) is also stable; so option should decide
    # make sure all of our private attrs or methods start with '__' (name-mangling is ok, so they needn't end with '__')
    def __init__(self, name, getattr_func):
        self.__name__ = name #k ok? not yet needed, anyway; done just in case some IDE wants every module to have it
        # note: self.__file__ can be assigned by caller, if it wants
        self.__path__ = "fakepath/" + name #k ok? maybe not, it might be some sort of dotted import path -- better look it up ####@@@@
        #e __file__?
        self.__getattr_func = getattr_func
    def __getattr__(self, attr): # in class FakeModule
        if attr.startswith('_'):
            ## too common, e.g. _self: print "fyi: fakemodule getattr warns about initial underscores:",attr # e.g. __path__
            if attr.startswith('__'):
                raise AttributeError, attr
            pass # let single-underscore names work normally as symbols, even though we [used to] warn about them for now
        # print "fyi: fakemodule getattr will make Symbol for",attr # this works
        res = self.__getattr_func(attr)
        setattr(self, attr, res) # don't ask me about this attr again!
        return res
    pass

import sys


## print "__name__ of exprs.__Symbols__ is %r" % (__name__,) # 'exprs.__Symbols__'
## print dir() # ['FakeModule', 'Symbol', '__author__', '__builtins__', '__doc__', '__file__', '__name__', 'sys']


sys.modules[__name__] = fakemodule = FakeModule(__name__, Symbol)

fakemodule.__file__ = __file__
fakemodule.__doc__ = __doc__


##print "dir(fakemodule)"
##print dir(fakemodule)
####dir(fakemodule)
####fyi: fakemodule getattr got __members__
####fyi: fakemodule getattr got __methods__
####['_FakeModule__getattr_func', '__doc__', '__file__', '__getattr__', '__init__', '__module__', '__name__', '__path__']

# end
