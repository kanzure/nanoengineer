# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
env.py

A place for global variables treated as "part of the environment".

$Id$

This module is for various global or "dynamic" variables,
which can be considered to be part of the environment of the code
that asks for them (thus the module name "env"). This is for variables
which are used by lots of code, but which would be inconvenient to pass
as arguments (since many routines would need to pass these through
without using them), and which some code might want to change dynamically
to provide a modified environment for some of the code it calls.

(Many of these variables will need to be thread-specific if we ever have threads.)

Also, certain basic routines for using/allocating some of these global variables.


Usage:

import env

   ... use env.xxx as needed ...
   # Don't say "from env import xxx" since env.xxx might be reassigned dynamically.
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

bruce 050610 made this module (since we've needed it for awhile), under the name "globals.py"
(since "global" is a Python keyword).

bruce 050627 renamed this module to "env.py", since "globals" is a Python builtin function.

bruce 050803 new features to help with graphics updates when preferences are changed 
'''

__author__ = 'bruce'

# This module defines stub functions which are replaced with different implementations
# by the changes module when it's imported.
# So this module should not import the changes module, directly or indirectly.
# But in case it does, by accident or if in future it needs to,
# we'll define those stub functions as early as possible.
# (One motivation for this (not yet made use of as of 050908)
#  is to enable stripped-down code to call these functions
#  even if the functionality of the changes module is never needed.
#  The immediate motivation is to allow them to be called arbitrarily early during init.)

def track(thing): #bruce 050804
    "Default implementation -- will be replaced at runtime as soon as changes.py module is imported (if it ever is)"
    import platform
    if platform.atom_debug:
        print "atom_debug: fyi (from env module): something asked to be tracked, but nothing is tracking: ", thing
        # if this happens and is not an error, then we'll zap the message.
    return

#bruce 050908 stubs for Undo  ####@@@@

def begin_op(*args):
    "Default implementation -- will be replaced at runtime as soon as changes.py module is imported (if it ever is)"
    return "fake begin" #k needed?

def end_op(*args):
    "Default implementation -- will be replaced at runtime as soon as changes.py module is imported (if it ever is)"
    pass

in_op = begin_op
after_op = end_op
begin_recursive_event_processing = begin_op
end_recursive_event_processing = end_op

# end of stubs to be replaced by changes module

def call_qApp_processEvents(*args): #bruce 050908
    "No other code should directly call qApp.processEvents -- always call it via this function."
    from qt import qApp #k ??
    mc = begin_recursive_event_processing()
    try:
        res = qApp.processEvents(*args)
    finally:
        end_recursive_event_processing(mc)
    return res
    
# ==

# most imports should occur here

from constants import *
import platform

class pre_init_fake_history_widget: #bruce 050901 moved this here from MWsemantics.py
    too_early = 1
        # defined so insiders can detect that it's too early (using hasattr)
        # and not call us at all (as they could have using hasattr on win.history
        #  before this "safety net" for early messages was added)
    def message(self, msg, **options):
        """This exists to handle messages sent to win.history or env.history during
        win.__init__, before the history widget has been created!
        Someday it might save them up and print them when that becomes possible.
        """
        if platform.atom_debug:
            print "fyi: too early for this status msg:", msg
        pass # too early
    pass

history = pre_init_fake_history_widget() # this will be changed by MWsemantics.__init__ [bruce 050727]

redraw_counter = 0 #bruce 050825

# ==

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

# ==

# dict for atoms or singets whose element, atomtype, or set of bonds (or neighbors) gets changed [bruce 050627]
#e (doesn't yet include all killed atoms or singlets, but maybe it ought to)
_changed_structure_atoms = {} # maps id(atom) to atom, for atoms or singlets

_changed_bond_types = {} # dict for bonds whose bond-type gets changed (need not include newly created bonds) ###k might not be used

# the beginnings of a general change-handling scheme [bruce 050627]

def post_event_updates( warn_if_needed = False ): #####@@@@@ call this from lots of places, not just update_parts like now
    """[public function]
       This should be called at the end of every user event which might have changed
    anything in any loaded model which defers some updates to this function.
    (Someday there will be a general way for models to register their updaters here,
    so that they are called in the proper order. For now, that's hardcoded.)
       This can also be called at the beginning of user events, such as redraws or saves,
    which want to protect themselves from event-processors which should have called this
    at the end, but forgot to. Those callers should pass warn_if_needed = True, to cause
    a debug-only warning to be emitted if the call was necessary. (This function is designed
    to be very fast when called more times than necessary.)
    """
    if not (_changed_structure_atoms or _changed_bond_types):
        #e this will be generalized to: if no changes of any kind, since the last call
        return
    # some changes occurred, so this function needed to be called (even if they turn out to be trivial)
    if warn_if_needed and platform.atom_debug:
        # whichever user event handler made these changes forgot to call this function when it was done!
        print "atom_debug: post_event_updates should have been called before, but wasn't!" #e use print_compact_stack??
        pass # (other than printing this, we handle unreported changes normally)
    # handle and clear all changes since the last call
    # (in the proper order, when there might be more than one kind of change #nim)
    if _changed_structure_atoms or _changed_bond_types:
        if platform.atom_debug:
            # during development, reload this module every time it's used
            # (Huaicai says this should not be done by default in the released version,
            #  due to potential problems if reloading from a zip file. He commented it
            #  out completely (7/14/05), and I then replaced it with this debug-only reload.
            #  [bruce 050715])
            import bond_updater
            reload(bond_updater)
    if _changed_structure_atoms:
        from bond_updater import update_bonds_after_each_event
        update_bonds_after_each_event( _changed_structure_atoms) # this might modify _changed_bond_types when it does bond-inference
            #e not sure if that routine will need to use or change other similar globals in this module;
            # if it does, passing just that one might be a bit silly (so we could pass none, or all affected ones)
        _changed_structure_atoms.clear()
    if _changed_bond_types:
        from bond_updater import process_changed_bond_types
        process_changed_bond_types( _changed_bond_types)
            ###k our interface to that function needs review if it can recursively add bonds to this dict -- if so, it should .clear
        _changed_bond_types.clear()
    return

# ==

# end
