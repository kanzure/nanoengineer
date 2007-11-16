# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
master_model_updater.py - do the post-event (or pre-checkpoint) updates
necessary for all of NE1's model types, in an appropriate order (which may
involve recursively running some lower-level updates to completion after
higher-level ones change things).

See also: update_parts method

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

def _master_model_updater( warn_if_needed = False ):
    """
    This should be called at the end of every user event which might have
    changed anything in any loaded model which defers some updates to this
    function.

    This can also be called at the beginning of user events, such as redraws
    or saves, which want to protect themselves from event-processors which
    should have called this at the end, but forgot to. Those callers should
    pass warn_if_needed = True, to cause a debug-only warning to be emitted
    if the call was necessary. (This function is designed
    to be very fast when called more times than necessary.)

    This should also be called before taking Undo checkpoints, to make sure
    they correspond to legal structures, and so this function's side effects
    (and the effect of assy.changed, done by this function as of 060126(?))
    are treated as part of the same undoable operation as the changes that
    required them to be made. As of 060127 this is done by those checkpoints
    calling update_parts, which indirectly calls this function.

    In practice, as of 071115, we have not yet tried to put in calls
    to this function at the end of user event handlers, so we rely on the
    other calls mentioned above, and none of them pass warn_if_needed.
    """    
    if not (changed_structure_atoms or changed_bond_types):
        # Note: this will be generalized to:
        # if no changes of any kind, since the last call
        return
    
    # some changes occurred, so this function needed to be called
    # (even if they turn out to be trivial)
    if warn_if_needed and env.debug():
        # whichever user event handler made these changes forgot to call
        # this function when it was done!
        # [as of 071115 warn_if_needed is never true; see docstring]
        print "atom_debug: _master_model_updater should have been called " \
              "before this call (since the most recent model changes), " \
              "but wasn't!" #e use print_compact_stack??
        pass # (other than printing this, we handle unreported changes normally)
    
    # handle and clear all changes since the last call
    # (in the proper order, when there might be more than one kind of change)

    # Note: reloading this module won't work, the way this code is currently
    # structured. If reloading is needed, this routine needs to be
    # unregistered prior to the reload, and reregistered afterwards.
    # Also, note that the module might be reloading itself, so be careful.

    if changed_structure_atoms:
        update_bonds_after_each_event( changed_structure_atoms)
            #bruce 060315 revised following comments:
            # Note: this can modify changed_bond_types (from bond-inference,
            # if we implement that in the future, or from correcting
            # illegal bond types, in the present code).
            # SOMEDAY: I'm not sure if that routine will need to use or change
            # other similar globals in this module; if it does, passing just
            # that one might be a bit silly (so we could pass none, or all
            # affected ones)
        changed_structure_atoms.clear()
    
    if changed_bond_types:
        # WARNING: this dict may have been modified by the above loop
        # which processes changed_structure_atoms...
        process_changed_bond_types( changed_bond_types)
            # REVIEW: our interface to that function needs review if it can
            # recursively add bonds to this dict -- if so, it should .clear,
            # not us!
        changed_bond_types.clear()
    
    return # from _master_model_updater

# ==

def initialize():
    """
    Register one or more related post_event_model_updaters
    (in the order in which they should run). These will be
    run by env.do_post_event_updates().
    """
    env.register_post_event_model_updater( _master_model_updater)
    return

# end
