# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
globals.py

Place for various global and/or "dynamic" variables.
(Some of these might need to be thread-specific if we ever have threads.)

Also, certain basic routines for using/allocating some of these globals.


$Id$


Usage:

import globals

   ... use globals.xxx as needed ...     # (it should be called "global.py" but "global" is a Python keyword!)
   # Don't say "from globals import xxx" since globals.xxx might be reassigned dynamically.
   # Variables that never change (and are importable when the program is starting up)
   # can be put into constants.py


Purpose and future plans:

Soon we should move some more variables here from platform, assy, win, and/or globalParms,
especially win.history (as a place to record things, of which there is one at a time,
even if we someday have more than one widget to view it, and change it dynamically to record
object-specific histories -- well, in that case an object-attr might be appropriate,
but not an assy or win attr like now!).

We might also put some "dynamic variables" here, like the current Part --
this is not yet decided.

Generators used to allocate things also might belong here, whether or not
we have global dicts of allocated things. (E.g. the one for atom keys.)

The main test of whether something might belong here is whether there will always be at most one
of them per process (or per active thread), even when we support multiple open files,
multiple main windows, multiple glpanes and model trees, etc.


History:

bruce 050610 made this since we've needed it for awhile.
'''

__author__ = 'bruce'

from constants import *

_last_glselect_name = 0

obj_with_glselect_name = {} # public for lookup ###e this needs to be made weak-valued ASAP! #######@@@@@@@

def new_glselect_name():
    "Return a session-unique 32-bit unsigned int for use as a GL_SELECT name."
    #e We could recycle these for dead objects (and revise docstring),
    # but that's a pain, and unneeded (I think), since it's very unlikely
    # we'll create more than 4 billion objects in one session.
    global _last_glselect_name
    _last_glselect_name += 1
    return _last_glselect_name

def alloc_my_glselect_name(obj):
    "Register obj as the owner of a new GL_SELECT name, and return that name."
    name = new_glselect_name()
    obj_with_glselect_name[name] = obj
    return name

# end
