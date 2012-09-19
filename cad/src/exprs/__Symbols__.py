# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
__Symbols__.py -- support for "from __Symbols__ import xxx",
to make a shared Symbol object within the exprs module.

$Id$

NOTE: This module replaces its entry in sys.modules with a
_FakeModule_for_Symbols object. That object probably doesn't support reload.
So this module is effectively not reloadable.

TODO: it might be possible to make this reloadable
by passing in a new version of getattr_func,
or if the reload would occur in here, passing in a
source for new getattr_funcs. The Python 2.3 new import hooks
might also help with this. Details not yet analyzed.
"""
__author__ = "bruce" # (but I took the idea of _FakeModule_for_Symbols
    # from Pmw == Python Megawidgets)

from exprs.Exprs import Symbol
    ### TODO: remove this import cycle, here or (preferably?) in Exprs

class _FakeModule_for_Symbols:
    """
    An object which can take the place of a real module
    in sys.modules, for some purposes. Used as a singleton.
    Comments and messages assume it's used to create "Symbols".
    """
    # make sure all of our private attrs or methods start with '__'
    __getattr_func = None # initial value of instance variable
    def __init__(self, name, getattr_func = None):
        self.__name__ = name
        # note: self.__file__ can be assigned by caller, if it wants
        self.__path__ = "fakepath/" + name
            #k ok? maybe not, it might be some sort of dotted import path --
            # better look it up ####@@@@
        self.__set_getattr_func(getattr_func) # might be None
    def __repr__(self): # only used in bug messages; UNTESTED
        return "<%s(%r) at %#x>" % (self.__class__.__name__, self.__name__, id(self))
    def __set_getattr_func(self, getattr_func):
        assert self.__getattr_func is None
        self.__getattr_func = getattr_func
    def __clear_getattr_func(self):
        # not yet used
        self.__set_getattr_func(None)
    def __getattr__(self, attr): # in class _FakeModule_for_Symbols
        if attr.startswith('__'):
            raise AttributeError, attr
        assert self.__getattr_func, "bug: symbol source not yet set in %r" % (self,)
        res = self.__getattr_func(attr)
        setattr(self, attr, res) # cache the value of this attr for reuse
        return res
    pass

import sys


## print "__name__ of exprs.__Symbols__ is %r" % (__name__,) # 'exprs.__Symbols__'
## print dir() # ['_FakeModule_for_Symbols', 'Symbol', '__author__', '__builtins__',
##   # '__doc__', '__file__', '__name__', 'sys']


sys.modules[__name__] = fakemodule = _FakeModule_for_Symbols(__name__, Symbol)

fakemodule.__file__ = __file__
    # REVIEW: does __file__ work in a Windows release build?
    # Guess: yes, since this is also assumed in canon_image_filename (exprs/images.py)
    # which I think is always run due to confirmation corner.
    # It doesn't exist in __main__ (or didn't at one time anyway)
    # but I guess that's a special case. It would be good to confirm all this.
    # [bruce 080111 comment]
fakemodule.__doc__ = __doc__
# note: __name__ and __path__ are set inside _FakeModule_for_Symbols.__init__

"""
>>> print dir(fakemodule)
fyi: fakemodule getattr got __members__
fyi: fakemodule getattr got __methods__
['_FakeModule__getattr_func', '__doc__', '__file__', '__getattr__', '__init__', '__module__', '__name__', '__path__']
"""

# end
