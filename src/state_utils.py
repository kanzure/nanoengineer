# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
state_utils.py

General state-related utilities.

$Id$
'''
__all__ = ['copy_val'] # __all__ must be the first symbol defined in the module.

    #e was the old name (copy_obj) better than copy_val??

__author__ = 'bruce'

# == public definitions

def copy_val(obj):
    """Copy obj, leaving no shared mutable components between copy and original,
    assuming (and verifying) that obj is a type we consider (in nE-1) to be a
    "standard data-like type", and using our standard copy semantics for such types.
    (These standards are not presently documented except in the code of this module.)
       #e In the future, additional args will define our actions on non-data-like Python objects
    (e.g. Atom, Bond, Node), and we might even merge the behaviors of this function
    and the ops_copy.Copier class; for now, all unrecognized types or classes are errors
    if encountered in our recursive scan of obj (at any depth).
       We don't handle or check for self-reference in obj -- that would always be an error;
    it would always cause infinite recursion in the present implem of this function.
       We don't optimize for shared subobjects within obj. Each reference to one of those
    is copied separately, whether it's mutable or immutable. This could be easily fixed if desired.
    """
    return copy_run().copy_val(obj) # let's hope the helper gets deleted automatically if it saves any state (it doesn't now)

# == helper code

from Numeric import array, PyObject

numeric_array_type = type(array(range(2)))

class copy_run: # might have called it Copier, but that conflicts with the ops_copy.py class; rename it again if it becomes public
    "one instance exists to handle one copy-operation of some python value, of the kind we use in copyable attributes"
    #e the reason it's an object is so it can store options given to the function copy_val, when we define those.
    #e such options would affect what this does for python objects it doesn't always copy.
    atomic_types = tuple( map(type, (1, 1.0, "x", u"x", None, True)) ) #e also complex (a python builtin type)?
    def __init__(self):
        ##e might need args for how to map pyobjs, or use subclass for that...
        #e ideal might be a func to copy them, which takes our own copy_val method...
        pass ## not needed: self.memo = {} # maps id(obj) to obj for objs that might contain self-refs
    def copy_val(self, obj):
        t = type(obj)
        if t in self.atomic_types:
            return obj
        #e memo check? not yet needed. if it is, see copy module (python library) source code for some subtleties.
        copy = self.copy_val
        if t is type([]):
            return map( copy, obj )
        if t is type(()):
            #e note: we don't yet bother to optimize by avoiding the copy when the components are immutable,
            # like copy.deepcopy does.
            return tuple( map( copy, obj ) )
        if t is type({}):
            res = {}
            for key, val in obj.iteritems():
                key = copy(key) # might not be needed or even desirable; ok for now
                val = copy(val)
                res[key] = val #e want to detect overlaps as errors? to be efficient, could just compare lengths.
            assert len(res) == len(obj) # for now
            return res
        #e Numeric array
        if t is numeric_array_type:
            if obj.typecode() == PyObject:
                return array( map( copy, obj) )
                # we don't know whether the copy typecode should be PyObject (eg if they get encoded),
                # so let it be inferred for now... fix this when we see how this needs to be used,
                # by requiring it to be declared, since it relates to the mapping of objects...
                # or by some other means.
            return obj.copy() # use Numeric's copy method for Character and number arrays ###@@@ verify ok from doc of this method...
        # Handle data-like objects which declare themselves as such.
        # Note: we have to use our own method name and API, since its API can't be made compatible
        # with the __deepcopy__ method used by the copy module (since that doesn't call back to our own
        # supplied copy function for copying parts, only to copy.deepcopy).
        #e We might need to revise the method name, if we split the issues of how vs whether to deepcopy an object.
        try:
            method = obj._s_deepcopy
            # This should be defined in any object which should *always* be treated as fully copied data.
            # Presently this includes VQT.Q (quats), and maybe class gamessParms.
        except AttributeError:
            pass
        else:
            return method( self.copy_val)
        # Special case for QColor; if this set gets extended we can use some sort of table and registration mechanism.
        # We do it by name so this code doesn't need to import QColor.
        if obj.__class__.__name__ == 'qt.QColor':
            return _copy_QColor(obj) # extra arg for copyfunc is not needed
        #e future: if we let clients customize handling of classes like Atom, Bond, Node,
        # they might want to encode them, wrap them, copy them, or leave them as unchanged refs.
        #
        # Unknown or unexpected pyobjs will always be errors
        # (whether or not they define copy methods of some other kind),
        # though we might decide to make them print a warning rather than assertfailing,
        # once this system has been working for long enough to catch the main bugs.
        assert 0, "uncopyable by copy_val: %r" % (obj,)
    pass

def _copy_QColor(obj):
    from qt import QColor
    assert obj.__class__ is QColor
    return QColor(obj)

# == test code

def _test():
    print "testing some simple cases of copy_val"
    map( _test1, [2,
                  3,
                  "string",
                  [4,5],
                  (6.0,),
                  {7:8,9:10},
                  array([2,3]),
                  None] )
    print "done"

def _test1(obj): #e perhaps only works for non-pyobj types for now
    if obj != copy_val(obj):
        print "failed for %r" % (obj,)

if __name__ == '__main__':
    _test()

# end
