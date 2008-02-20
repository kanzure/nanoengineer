# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
glselect_name_dict.py - allocate GL_SELECT names and record their owners.

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

bruce 080219 split this out of env.py so we can make it per-assy.
"""

_last_glselect_name = 0

def _new_glselect_name():
    """
    Return a session-unique 32-bit unsigned int (not 0) for use as a GL_SELECT name.

    @note: these are unique even between instances of class glselect_name_dict.
    """
    #e We could recycle these for dead objects (and revise docstring),
    # but that's a pain, and unneeded (I think), since it's very unlikely
    # we'll create more than 4 billion objects in one session.
    global _last_glselect_name
    _last_glselect_name += 1
    return _last_glselect_name

class glselect_name_dict(object):
    """
    Allocate OpenGL GL_SELECT names for use when drawing one model (e.g. an assembly),
    and record their owners.

    @note: The allocated names are session-unique 32-bit unsigned ints (not 0).
           They are unique even between instances of this class.

    @note: Callers are free to share one instance of this class over multiple
           models, or (with suitable changes in current code in GLPane) to use
           more than one instance for objects drawn together in the same frame.

    @note: The allocated names can be used in OpenGL display lists, provided
           their owning objects remain alive as long as those display lists
           remain in use.
    """
    def __init__(self):
        self.obj_with_glselect_name = {} # public for lookup
            ###e this needs to be made weak-valued ASAP! (or, call destroy methods to dealloc) ###@@@
    
    def alloc_my_glselect_name(self, obj):
        """
        Allocate and return a new GL_SELECT name, recording obj as its owner.
        Obj should provide the Selobj_API so it can handle GLPane callbacks during
        hit-testing.
        
        @see: Selobj_API
        """
        name = _new_glselect_name()
        self.obj_with_glselect_name[name] = obj
        return name

    # Maybe todo: add methods for temporarily removing name from dict (without deallocating it)
    # and for restoring it, so killed objects needn't have names in the dict.
    # This would mean we needn't remove the name when destroying a killed object,
    # thus, needn't find the object at all. But when this class is per-assy, there
    # won't be a need for that when destroying an entire assy, so it might not be
    # needed at all.
    
    def dealloc_my_glselect_name(self, obj, name):
        """
        #doc

        @see: Selobj_API
        """
        # objs have to pass the name, since we don't know where they keep it and don't want to have to keep a reverse dict;
        # but we make sure they own it before zapping it!
        #e this function could be dispensed with if our dict was weak, but maybe it's useful for other reasons too, who knows
        if not name:
            # make repeated destroy methods easier to implement; ok since we never allocate a name of 0
            return
        obj1 = self.obj_with_glselect_name.get(name)
        if obj1 is obj:
            del self.obj_with_glselect_name[name]
    ##    elif obj1 is None:
    ##        pass # repeated destroy should be legal, and might call this (unlikely, since obj would not know name -- hmm... ok, zap it)
        else:
            print "bug: dealloc_my_glselect_name(obj, name) mismatch for name %r: real owner is %r, not" % (name, obj1), obj
                # print obj separately in case of exceptions in its repr
        return

    pass # end of class

# end
