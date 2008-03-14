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

from utilities import debug_flags

from dna.updater.dna_updater_utils import remove_killed_atoms
from dna.updater.dna_updater_utils import remove_closed_or_disabled_assy_atoms

from dna.updater.dna_updater_atoms import update_PAM_atoms_and_bonds

from dna.updater.dna_updater_chunks import update_PAM_chunks

from dna.updater.dna_updater_groups import update_DNA_groups

from dna.updater.dna_updater_debug import debug_prints_as_dna_updater_starts
from dna.updater.dna_updater_debug import debug_prints_as_dna_updater_ends

# ==

_runcount = 0 # for debugging [bruce 080227]

def full_dna_update():
    """
    [meant to be called from _master_model_updater]

    Enforce rules on all newly changed DNA-related model objects,
    including DnaGroups, AxisChunks, PAM atoms, etc.

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
    changed_atoms = get_changes_and_clear()

    debug_prints_as_dna_updater_starts( _runcount, changed_atoms)
        # note: this function should not modify changed_atoms.
        # note: the corresponding _ends call is in our caller.
    
    if not changed_atoms:
        return # optimization (might not be redundant with caller)

    if debug_flags.DEBUG_DNA_UPDATER_MINIMAL:
        print "\ndna updater: %d changed atoms to scan" % len(changed_atoms)
    if debug_flags.DEBUG_DNA_UPDATER: # should be _VERBOSE, but has been useful enough to keep seeing for awhile
        items = changed_atoms.items()
        items.sort()
        atoms = [item[1] for item in items]
        NUMBER_TO_PRINT = 10
        if debug_flags.DEBUG_DNA_UPDATER_VERBOSE or len(atoms) <= NUMBER_TO_PRINT:
            print " they are: %r" % atoms
        else:
            print " the first %d of them are: %r ..." % \
                  (NUMBER_TO_PRINT, atoms[:NUMBER_TO_PRINT])

    remove_killed_atoms( changed_atoms) # only affects this dict, not the atoms

    remove_closed_or_disabled_assy_atoms( changed_atoms)
        # This should remove all remaining atoms from closed files.
        # Note: only allowed when no killed atoms are present in changed_atoms;
        # raises exceptions otherwise.
        
    if not changed_atoms:
        return
    
    update_PAM_atoms_and_bonds( changed_atoms)
    
    if not changed_atoms:
        # (unlikely, but no harm)
        return

    new_chunks, new_wholechains = update_PAM_chunks( changed_atoms)

    # review: if not new_chunks, return? wait and see if there are also new_markers, etc...
    
    update_DNA_groups( new_chunks, new_wholechains)
        # review:
        # args? a list of nodes, old and new, whose parents should be ok? or just find them all, scanning MT?
        # the underlying nodes we need to place are just chunks and jigs. we can ignore old ones...
        # so we need a list of new or moved ones... chunks got made in update_PAM_chunks; jigs, in update_PAM_atoms_and_bonds...
        # maybe pass some dicts into these for them to add things to?

    ignore_new_changes("as full_dna_update returns", changes_ok = False )

    return # from _full_dna_update_0

# end
