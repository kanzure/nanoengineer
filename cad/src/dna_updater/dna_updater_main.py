# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_main.py - enforce rules on newly changed DNA-related model objects,
including DnaGroups, AxisChunks, PAM atoms, etc.

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_updater_globals import get_changes_and_clear

from dna_updater_constants import DEBUG_DNA_UPDATER

from dna_updater_utils import remove_killed_atoms

from dna_updater_atoms import update_PAM_atoms_and_bonds

from dna_updater_chunks import update_PAM_chunks

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

    remove_killed_atoms( changed_atoms) # only affects this dict, not the atoms

    if not changed_atoms:
        return
    
    update_PAM_atoms_and_bonds( changed_atoms)
    
    if not changed_atoms:
        # (unlikely, but no harm)
        return

    update_PAM_chunks( changed_atoms)
        # ... return value?

    # now do groups .... TODO
    
    # ....
    
    return

# end
