# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
glselect_name_dict.py - allocate GL_SELECT names and record their owners.

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

Module classification:  [bruce 080223]

It imports nothing, but the code that needs to use it is OpenGL drawing code
or a framework that supports it, so it seems more natural as graphics/drawing.
(It's really an "opengl drawing utility".)

History:

bruce 080220 split this out of env.py so we can make it per-assy.
"""

_last_glselect_name = 0

def _new_glselect_name():
    """
    Return a session-unique 32-bit unsigned int (not 0) for use as a GL_SELECT
    name.

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
    Allocate OpenGL GL_SELECT names for use when drawing one model (e.g. an
    assembly), and record their owners.

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
            # [Note: we might make this private
            #  when access from env.py is no longer needed]
            # TODO: clear this when destroying the assy which owns self

    def alloc_my_glselect_name(self, obj):
        """
        Allocate and return a new GL_SELECT name, recording obj as its owner.
        Obj should provide the Selobj_API so it can handle GLPane callbacks
        during hit-testing.

        @see: Selobj_API
        """
        glname = _new_glselect_name()
        self.obj_with_glselect_name[glname] = obj
        return glname

    def object_for_glselect_name(self, glname):
        """
        #doc [todo: get material from docstring of same method in assembly.py]
        """
        return self.obj_with_glselect_name.get( glname)

    # Todo: add a variant of object_for_glselect_name to which the entire
    # name stack should be passed. Current code (as of 080220) passes the last
    # (innermost) element of the name stack.

    # Maybe todo: add methods for temporarily removing glname from dict (without
    # deallocating it) and for restoring it, so killed objects needn't have
    # names in the dict.  This would mean we needn't remove the name when
    # destroying a killed object, thus, needn't find the object at all. But when
    # this class is per-assy, there won't be a need for that when destroying an
    # entire assy, so it might not be needed at all.

    def dealloc_my_glselect_name(self, obj, glname):
        """
        #doc [todo: get material from docstring of same method in assembly.py]

        @note: the glname arg is permitted to be 0 or None, in which case we
               do nothing, to make it easier for callers to implement repeatable
               destroy methods which forget their glname, or work if they never
               allocated one yet. (Note that this is only ok because we never
               allocate a glname of 0.)

        @see: Selobj_API
        """
        # objs have to pass the glname, since we don't know where they keep it
        # and don't want to have to keep a reverse dict; but we make sure they
        # own it before zapping it!
        #e This function could be dispensed with if our dict was weak, but maybe
        #  it's useful for other reasons too, who knows.
        if not glname:
            return
        obj1 = self.obj_with_glselect_name.get(glname)
        if obj1 is obj:
            del self.obj_with_glselect_name[glname]
    ##    elif obj1 is None:
    ##        # Repeated destroy should be legal, and might call this (unlikely,
    ##        # since obj would not know glname -- hmm... ok, zap it.)
    ##        pass
        else:
            print ("bug: %s %r: real owner is %r, not" %
                ("dealloc_my_glselect_name(obj, glname) mismatch for glname",
                 glname, obj1)), obj
                # Print obj separately in case of exceptions in its repr.
        return

    pass # end of class

# end
