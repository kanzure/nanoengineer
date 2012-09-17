# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
dna_updater_main.py - enforce rules on newly changed DNA-related model objects,
including DnaGroups, AxisChunks, PAM atoms, etc.

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna.updater.dna_updater_globals import get_changes_and_clear
from dna.updater.dna_updater_globals import ignore_new_changes
from dna.updater.dna_updater_globals import clear_updater_run_globals
from dna.updater.dna_updater_globals import _f_invalid_dna_ladders
from dna.updater.dna_updater_globals import restore_dnaladder_inval_policy
from dna.updater.dna_updater_globals import DNALADDER_INVAL_IS_OK

from utilities import debug_flags

from dna.updater.dna_updater_utils import remove_killed_atoms
from dna.updater.dna_updater_utils import remove_closed_or_disabled_assy_atoms

from dna.updater.dna_updater_atoms import update_PAM_atoms_and_bonds

from dna.updater.dna_updater_chunks import update_PAM_chunks

from dna.updater.dna_updater_groups import update_DNA_groups

from dna.updater.dna_updater_debug import debug_prints_as_dna_updater_starts
from dna.updater.dna_updater_debug import debug_prints_as_dna_updater_ends

from dna.model.DnaMarker import _f_are_there_any_homeless_dna_markers
from dna.model.DnaMarker import _f_get_homeless_dna_markers

# ==

_runcount = 0 # for debugging [bruce 080227]

def full_dna_update():
    """
    [meant to be called from _master_model_updater]

    Enforce rules on all newly changed DNA-related model objects,
    including DnaGroups, AxisChunks, PAM atoms, etc.

    @warning: external calls to any smaller parts of the dna updater
              would probably have bugs, due to the lack of beginning
              and ending calls to clear_updater_run_globals, and possibly
              for many other reasons. In fact, external calls to this function
              rather than to update_parts (which calls it) are risky, since it's
              not reviewed how much this function depends on things that
              update_parts has normally done by the time it calls this.

    @note: The newly changed objects are not necessarily
           all in the same assy (class assembly).
           E.g. there might be some from an open mmp file
           and some from a just-opened part library part.

    @return: None
    """
    global _runcount
    _runcount += 1
    clear_updater_run_globals()
    try:
        _full_dna_update_0( _runcount) # includes debug_prints_as_dna_updater_starts
    finally:
        debug_prints_as_dna_updater_ends( _runcount)
        clear_updater_run_globals()
    return

def _full_dna_update_0( _runcount):
    """
    [private helper for full_dna_update -- do all the work]
    """

    # TODO: process _f_baseatom_wants_pam: (or maybe a bit later, after delete bare, and error finding?)
    # - extend to well-structured basepairs; drop structure error atoms (as whole basepairs)
    # - these and their baseatom neighbors in our changed atoms, maybe even real .changed_structure

    changed_atoms = get_changes_and_clear()

    debug_prints_as_dna_updater_starts( _runcount, changed_atoms)
        # note: this function should not modify changed_atoms.
        # note: the corresponding _ends call is in our caller.

    if not changed_atoms and not _f_are_there_any_homeless_dna_markers():
        # maybe: also check _f_baseatom_wants_pam, invalid ladders, here and elsewhere
        # (or it might be more efficient to officially require _changed_structure on representative atoms,
        #  which we're already doing now as a kluge workaround for the lack of testing those here)
        # [bruce 080413 comment]
        #
        # note: adding marker check (2 places) fixed bug 2673 [bruce 080317]
        return # optimization (might not be redundant with caller)

    # print debug info about the set of changed_atoms (and markers needing update)
    if debug_flags.DEBUG_DNA_UPDATER_MINIMAL:
        print "\ndna updater: %d changed atoms to scan%s" % \
              ( len(changed_atoms),
                _f_are_there_any_homeless_dna_markers() and " (and some DnaMarkers)" or ""
              )
    if debug_flags.DEBUG_DNA_UPDATER and changed_atoms:
        # someday: should be _VERBOSE, but has been useful enough to keep seeing for awhile
        items = changed_atoms.items()
        items.sort()
        atoms = [item[1] for item in items]
        NUMBER_TO_PRINT = 10
        if debug_flags.DEBUG_DNA_UPDATER_VERBOSE or len(atoms) <= NUMBER_TO_PRINT:
            print " they are: %r" % atoms
        else:
            print " the first %d of them are: %r ..." % \
                  (NUMBER_TO_PRINT, atoms[:NUMBER_TO_PRINT])

    if changed_atoms:
        remove_killed_atoms( changed_atoms) # only affects this dict, not the atoms

    if changed_atoms:
        remove_closed_or_disabled_assy_atoms( changed_atoms)
            # This should remove all remaining atoms from closed files.
            # Note: only allowed when no killed atoms are present in changed_atoms;
            # raises exceptions otherwise.

    if changed_atoms:
        update_PAM_atoms_and_bonds( changed_atoms)
            # this can invalidate DnaLadders as it changes various things
            # which call atom._changed_structure -- that's necessary to allow,
            # so we don't change dnaladder_inval_policy until below,
            # inside update_PAM_chunks [bruce 080413 comment]
            # (REVIEW: atom._changed_structure does not directly invalidate
            #  dna ladders, so I'm not sure if this comment is just wrong,
            #  or if it meant something not exactly what it said, like,
            #  this can cause more ladders to be invalidated than otherwise
            #  in an upcoming step -- though if it meant that, it seems
            #  wrong too, since the existence of that upcoming step
            #  might be enough reason to not be able to change the policy yet.
            #  [bruce 080529 addendum/Q])

    if not changed_atoms and not _f_are_there_any_homeless_dna_markers() and not _f_invalid_dna_ladders:
        return # optimization

    homeless_markers = _f_get_homeless_dna_markers() #e rename, homeless is an obs misleading term ####
        # this includes markers whose atoms got killed (which calls marker.remove_atom)
        # or got changed in structure (which calls marker.changed_structure)
        # so it should not be necessary to also add to this all markers noticed
        # on changed_atoms, even though that might include more markers than
        # we have so far (especially after we add atoms from invalid ladders below).
        #
        # NOTE: it can include fewer markers than are noticed by _f_are_there_any_homeless_dna_markers
        # since that does not check whether they are truly homeless.
    assert not _f_are_there_any_homeless_dna_markers() # since getting them cleared them

    new_chunks, new_wholechains = update_PAM_chunks( changed_atoms, homeless_markers)
        # note: at the right time during this or a subroutine, it sets
        # dnaladder_inval_policy to DNALADDER_INVAL_IS_ERROR

    # review: if not new_chunks, return? wait and see if there are also new_markers, etc...

    update_DNA_groups( new_chunks, new_wholechains)
        # review:
        # args? a list of nodes, old and new, whose parents should be ok? or just find them all, scanning MT?
        # the underlying nodes we need to place are just chunks and jigs. we can ignore old ones...
        # so we need a list of new or moved ones... chunks got made in update_PAM_chunks; jigs, in update_PAM_atoms_and_bonds...
        # maybe pass some dicts into these for them to add things to?

    ignore_new_changes("as full_dna_update returns", changes_ok = False )

    if debug_flags.DEBUG_DNA_UPDATER_MINIMAL:
        if _f_are_there_any_homeless_dna_markers():
            print "dna updater fyi: as updater returns, some DnaMarkers await processing by next run"
                # might be normal...don't know. find out, by printing it even
                # in minimal debug output. [bruce 080317]

    if _f_invalid_dna_ladders: #bruce 080413
        print "\n*** likely bug: some invalid ladders are recorded, as dna updater returns:", _f_invalid_dna_ladders
        # but don't clear them, in case this was sometimes routine and we were
        # working around bugs (unknowingly) by invalidating them next time around

    restore_dnaladder_inval_policy( DNALADDER_INVAL_IS_OK)

    return # from _full_dna_update_0

# end
