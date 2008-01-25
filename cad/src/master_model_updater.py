# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
master_model_updater.py - do the post-event (or pre-checkpoint) updates
necessary for all of NE1's model types, in an appropriate order (which may
involve recursively running some lower-level updates to completion after
higher-level ones change things).

See also: update_parts method

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.


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

from debug import print_compact_stack, print_compact_traceback

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

    if 1:
        # KLUGE; the changedicts and updater should really be per-assy...
        # this is a temporary scheme for detecting the unanticipated
        # running of this in the middle of loading an mmp file, and for
        # preventing errors from that,
        # but it only works for the main assy -- not e.g. for a partlib
        # assy. I don't yet know if this is needed. [bruce 080117]    
        assy = env.mainwindow().assy
        if not assy.assy_valid:
            msg = "deferring _master_model_updater(warn_if_needed = %r) " \
                  "since not %r.assy_valid" % (warn_if_needed, assy)
            print_compact_stack(msg + ": ") # soon change to print...
            return
        pass
    
    # TODO: check some dicts first, to optimize this call when not needed?
    # TODO: zap the temporary function calls here
    if debug_pref_use_dna_updater(): # soon will be if 1
        if debug_pref_reload_dna_updater(): # for release, always false
            _reload_dna_updater() # also reinits it if needed
        _ensure_ok_to_call_dna_updater() # soon will not be needed here
        from dna_updater.dna_updater_main import full_dna_update
            # soon will be toplevel import
        try:
            full_dna_update()
        except:
            msg = "\n*** exception from dna updater; will attempt to continue"
            print_compact_traceback(msg + ": ")
        pass

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

# temporary code for use while developing dna_updater

def debug_pref_use_dna_updater():
    from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
    res = debug_pref("DNA: use dna_updater.py?",
                     Choice_boolean_False,
                     ## SOON: Choice_boolean_True,
                     non_debug = True,
                     prefs_key = True)
    return res

def debug_pref_reload_dna_updater():
    import EndUser
    if not EndUser.enableDeveloperFeatures():
        return False
    from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
    res = debug_pref("DNA: auto-reload dna_updater.py?",
                     Choice_boolean_False,
                     ## SOON: Choice_boolean_True,
                     non_debug = True,
                     prefs_key = True)
    return res
    
_initialized_dna_updater_yet = False

def _ensure_ok_to_call_dna_updater():
    global _initialized_dna_updater_yet
    if not _initialized_dna_updater_yet:
        from dna_updater import dna_updater_init
        dna_updater_init.initialize()
        _initialized_dna_updater_yet = True
    return

def _reload_dna_updater():
    from dna_updater import dna_updater_atoms
    reload(dna_updater_atoms)
    #e could add more modules to that list, in order;
    # no need to reinit
    return

def initialize():
    """
    Register one or more related post_event_model_updaters
    (in the order in which they should run). These will be
    run by env.do_post_event_updates().
    """
    if debug_pref_use_dna_updater():
##        from dna_updater import dna_updater_init
##        dna_updater_init.initialize()
        _ensure_ok_to_call_dna_updater() # TODO: replace with the commented out 2 lines above

    env.register_post_event_model_updater( _master_model_updater)
    return

# end
