# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_main.py - enforce rules on newly changed DNA-related model objects,
including DnaGroups, AxisChunks, PAM atoms, etc.

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_updater_globals import get_changes_and_clear
from dna_updater_globals import ignore_new_changes

from dna_updater_constants import DEBUG_DNA_UPDATER

from dna_updater_utils import remove_killed_atoms

from dna_updater_atoms import update_PAM_atoms_and_bonds

from dna_updater_chunks import update_PAM_chunks

from dna_updater_groups import update_DNA_groups

# ==

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
    changed_atoms = get_changes_and_clear()
    
    if not changed_atoms:
        return # optimization (might not be redundant with caller)

    if DEBUG_DNA_UPDATER:
        print "\ndna updater: %d changed atoms to scan" % len(changed_atoms)
    if DEBUG_DNA_UPDATER: # should be _VERBOSE, but has been useful enough to keep seeing for awhile
        items = changed_atoms.items()
        items.sort()
        atoms = [item[1] for item in items]
        print " they are: %r" % atoms

    remove_killed_atoms( changed_atoms) # only affects this dict, not the atoms
        # TODO: also remove atoms from assys that have been destroyed
        # (i.e. closed files) @@@

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

    return

# end
