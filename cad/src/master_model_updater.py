# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
master_model_updater.py - do the post-event (or pre-checkpoint) updates
necessary for all of NE1's model types, in an appropriate order (which may
involve recursively running some lower-level updates to completion after
higher-level ones change things).


@author: Bruce
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.


TODO:

Once the general structure stabilizes, refactor this so that the model-type-
specific updaters can register themselves, rather than being hardcoded here
as they are now.

The unclear part of doing that is how the higher-level ones can recursively/
repeatedly run lower-level ones, given that they're all only in a partial
order; and also, the general degree of interdependence in the rules for what
gets in each changedict, which related fields are derived from other ones,
etc.

For now, this means all the updaters have to be co-developed and called (in
a hardcoded way) by one master function, which is the one in this module.

(But this master updater can and does register itself with
env.register_post_event_model_updater, so the env function via which these
get called can remain in the model-type-independent part of the core.)


History:

bruce 050627 started this as part of supporting higher-order bonds.

bruce 071108 split this out of bond_updater.py, in preparation for adding
DNA-specific code in other specific updater modules, for this to also call.
"""

from global_model_changedicts import changed_structure_atoms
from global_model_changedicts import changed_bond_types

import env

from bond_updater import update_bonds_after_each_event
from bond_updater import process_changed_bond_types

# ==

# the beginnings of a general change-handling scheme [bruce 050627]

def _master_model_updater( warn_if_needed = False ):
    """
    This should be called at the end of every user event which might have changed
    anything in any loaded model which defers some updates to this function.

    This can also be called at the beginning of user events, such as redraws or saves,
    which want to protect themselves from event-processors which should have called this
    at the end, but forgot to. Those callers should pass warn_if_needed = True, to cause
    a debug-only warning to be emitted if the call was necessary. (This function is designed
    to be very fast when called more times than necessary.)
    """
    #bruce 060127: Note: as of long before now, nothing actually calls this with warn_if_needed = True;
    # the only calls are from GLPane.paintGL and assembly.update_parts.
    # FYI: As of 060127 I'll be calling update_parts (which always calls this method)
    # before every undo checkpoint (begin and end both), so that all resulting changes
    # from both of them (and the effect of calling assy.changed, now often done by this method as of yesterday)
    # get into the same undo diff.) [similar comment is in update_parts]
    #
    #obs? ####@@@@ call this from lots of places, not just update_parts like now; #doc is obs
    #
    #bruce 051011: some older experimental undo code I probably won't use:
##    for class1, classmethodname in _change_recording_classes:
##        try:
##            method = getattr(class1, classmethodname)
##            method() # this can update the global dicts here...
##                #e how that works will be revised later... e.g. we might pass an object to revise
##        except:
##            print "can't yet handle an exception in %r.%r, just reraising it" % (class1, classmethodname)
##            raise
##        pass
    if not (changed_structure_atoms or changed_bond_types):
        #e this will be generalized to: if no changes of any kind, since the last call
        return
    # some changes occurred, so this function needed to be called (even if they turn out to be trivial)
    if warn_if_needed and env.debug():
        # whichever user event handler made these changes forgot to call this function when it was done!
        print "atom_debug: do_post_event_updates should have been called before, but wasn't!" #e use print_compact_stack??
        pass # (other than printing this, we handle unreported changes normally)
    # handle and clear all changes since the last call
    # (in the proper order, when there might be more than one kind of change #nim)

    # NOTE: reloading won't work the way this code is currently
    # structured.  If reloading is needed, this routine needs to be
    # unregistered prior to the reload, and reregistered afterwards.
    # Also, note that the module would be reloading itself, so be
    # careful.
    #if changed_structure_atoms or changed_bond_types:
        #if 0 and platform.atom_debug: #bruce 060315 disabled this automatic reload (not needed at the moment)
            # during development, reload this module every time it's used
            # (Huaicai says this should not be done by default in the released version,
            #  due to potential problems if reloading from a zip file. He commented it
            #  out completely (7/14/05), and I then replaced it with this debug-only reload.
            #  [bruce 050715])
            #import bond_updater
            #reload(bond_updater)

    if changed_structure_atoms:
        update_bonds_after_each_event( changed_structure_atoms)
            #bruce 060315 revised following comments:
            # this can modify changed_bond_types (from bond-inference in the future, or from correcting illegal bond types now).
            #e not sure if that routine will need to use or change other similar globals in this module;
            # if it does, passing just that one might be a bit silly (so we could pass none, or all affected ones)
        changed_structure_atoms.clear()
    if changed_bond_types: # warning: this can be modified by above loop which processes changed_structure_atoms...
        process_changed_bond_types( changed_bond_types)
            ###k our interface to that function needs review if it can recursively
            # add bonds to this dict -- if so, it should .clear, not us!
        changed_bond_types.clear()
    return # from _master_model_updater

# ==

def initialize():
    """
    Register one or more related post_event_model_updaters
    (in the order in which they should run).
    """
    env.register_post_event_model_updater( _master_model_updater)
    return

# end
