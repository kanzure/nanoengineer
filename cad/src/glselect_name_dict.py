# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
glselect_name_dict.py - allocate GL_SELECT names and record their owners.

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

bruce 080219 split this out of env.py so we can make it per-assy.
"""

# UNFINISHED VERSION, just to show the code right after it got split out,
# before we change it from globals & functions into a class.

_last_glselect_name = 0

def new_glselect_name():
    """
    Return a session-unique 32-bit unsigned int for use as a GL_SELECT name.
    """
    #e We could recycle these for dead objects (and revise docstring),
    # but that's a pain, and unneeded (I think), since it's very unlikely
    # we'll create more than 4 billion objects in one session.
    global _last_glselect_name
    _last_glselect_name += 1
    return _last_glselect_name

obj_with_glselect_name = {} # public for lookup
    ###e this needs to be made weak-valued ASAP! (or, call destroy methods to dealloc) ###@@@


def alloc_my_glselect_name(obj):
    """
    Register obj as the owner of a new GL_SELECT name, and return that name.

    @see: Selobj_API
    """
    name = new_glselect_name()
    obj_with_glselect_name[name] = obj
    return name

def dealloc_my_glselect_name(obj, name):
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
    obj1 = obj_with_glselect_name.get(name)
    if obj1 is obj:
        del obj_with_glselect_name[name]
##    elif obj1 is None:
##        pass # repeated destroy should be legal, and might call this (unlikely, since obj would not know name -- hmm... ok, zap it)
    else:
        print "bug: dealloc_my_glselect_name(obj, name) mismatch for name %r: real owner is %r, not" % (name, obj1), obj
            # print obj separately in case of exceptions in its repr
    return

# end
