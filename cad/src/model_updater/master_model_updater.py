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

bruce 080305 added _autodelete_empty_groups.
"""

from model.global_model_changedicts import changed_structure_atoms
from model.global_model_changedicts import changed_bond_types

from model.global_model_changedicts import LAST_RUN_DIDNT_HAPPEN
from model.global_model_changedicts import LAST_RUN_IS_ONGOING
from model.global_model_changedicts import LAST_RUN_FAILED
from model.global_model_changedicts import LAST_RUN_SUCCEEDED

import model.global_model_changedicts as global_model_changedicts # for setting flags in it

import foundation.env as env

from utilities.Log import redmsg
from utilities.GlobalPreferences import dna_updater_is_enabled
from utilities.debug import print_compact_stack, print_compact_traceback

from model_updater.bond_updater import update_bonds_after_each_event
from model_updater.bond_updater import process_changed_bond_types

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

    # 0. Don't run while mmp file is being read [###FIX, use one global flag]
    if 1:
        # KLUGE; the changedicts and updater should really be per-assy...
        # this is a temporary scheme for detecting the unanticipated
        # running of this in the middle of loading an mmp file, and for
        # preventing errors from that,
        # but it only works for the main assy -- not e.g. for a partlib
        # assy. I don't yet know if this is needed. [bruce 080117]
        #update 080319: just in case, I'm fixing the mmpread code
        # to also use the global assy to store this.
        kluge_main_assy = env.mainwindow().assy
        if not kluge_main_assy.assy_valid:
            global_model_changedicts.status_of_last_dna_updater_run = LAST_RUN_DIDNT_HAPPEN
            msg = "deferring _master_model_updater(warn_if_needed = %r) " \
                  "since not %r.assy_valid" % (warn_if_needed, kluge_main_assy)
            print_compact_stack(msg + ": ") # soon change to print...
            return
        pass

    env.history.emit_all_deferred_summary_messages() #bruce 080212 (3 places)

    _run_dna_updater()

    env.history.emit_all_deferred_summary_messages()

    _run_bond_updater( warn_if_needed = warn_if_needed)

    env.history.emit_all_deferred_summary_messages()

    _autodelete_empty_groups(kluge_main_assy)

    env.history.emit_all_deferred_summary_messages()

    return # from _master_model_updater

# ==

def _run_dna_updater(): #bruce 080210 split this out
    # TODO: check some dicts first, to optimize this call when not needed?
    # TODO: zap the temporary function calls here
    #bruce 080319 added sets of status_of_last_dna_updater_run
    if dna_updater_is_enabled():
        # never implemented sufficiently: if ...: _reload_dna_updater()
        _ensure_ok_to_call_dna_updater() # soon will not be needed here
        from dna.updater.dna_updater_main import full_dna_update
            # soon will be toplevel import
        global_model_changedicts.status_of_last_dna_updater_run = LAST_RUN_IS_ONGOING
        try:
            full_dna_update()
        except:
            global_model_changedicts.status_of_last_dna_updater_run = LAST_RUN_FAILED
            msg = "\n*** exception in dna updater; will attempt to continue"
            print_compact_traceback(msg + ": ")
            msg2 = "Error: exception in dna updater (see console for details); will attempt to continue"
            env.history.message(redmsg(msg2))
        else:
            global_model_changedicts.status_of_last_dna_updater_run = LAST_RUN_SUCCEEDED
        pass
    else:
        global_model_changedicts.status_of_last_dna_updater_run = LAST_RUN_DIDNT_HAPPEN
    return

# ==

def _run_bond_updater(warn_if_needed = False): #bruce 080210 split this out

    if not (changed_structure_atoms or changed_bond_types):
        # Note: this will be generalized to:
        # if no changes of any kind, since the last call
        # Note: the dna updater processes changes in other dicts,
        # but we don't need to check those in this function.
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

    return # from _run_bond_updater

# ==

def _autodelete_empty_groups(assy): #bruce 080305
    """
    Safely call currentCommand.autodelete_empty_groups( part.topnode)
    (if a debug_pref permits) for currentCommand and current part found via assy
    """
    if debug_pref_autodelete_empty_groups():
        try:
            part = assy.part
            currentCommand = assy.w.currentCommand
            if part:
                currentCommand.autodelete_empty_groups( part.topnode)
        except:
            msg = "\n*** exception in _autodelete_empty_groups; will attempt to continue"
            print_compact_traceback(msg + ": ")
            msg2 = "Error: exception in _autodelete_empty_groups (see console for details); will attempt to continue"
            env.history.message(redmsg(msg2))
            pass
        pass
    return

# ==

# temporary code for use while developing dna_updater

def debug_pref_autodelete_empty_groups():
    from utilities.debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
    res = debug_pref("autodelete empty Dna-related groups?", #bruce 080317 revised text
                     ##Choice_boolean_False,
                     #autodelete empty groups by default. This looks safe so far
                     #and soon, we will make it mainstream (not just a debug
                     #option) -- Ninad 2008-03-07
                     Choice_boolean_True,
                     ## non_debug = True, #bruce 080317 disabled
                     prefs_key = True
                     )
    return res


_initialized_dna_updater_yet = False

def _ensure_ok_to_call_dna_updater():
    global _initialized_dna_updater_yet
    if not _initialized_dna_updater_yet:
        from dna.updater import dna_updater_init
        dna_updater_init.initialize()
        _initialized_dna_updater_yet = True
    return

# ==

def initialize():
    """
    Register one or more related post_event_model_updaters
    (in the order in which they should run). These will be
    run by env.do_post_event_updates().
    """
    if dna_updater_is_enabled():
        ## from dna_updater import dna_updater_init
        ## dna_updater_init.initialize()
        _ensure_ok_to_call_dna_updater() # TODO: replace with the commented out 2 lines above

    env.register_post_event_model_updater( _master_model_updater)
    return

# end
