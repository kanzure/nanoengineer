# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_main.py - enforce rules on newly changed DNA-related model objects,
including DnaGroups, AxisChunks, PAM atoms, etc.

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_updater_atoms import update_PAM_atoms_and_bonds

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
    changed_atoms = update_PAM_atoms_and_bonds()
    
    if not changed_atoms:
        return # optimization (might not be redundant with caller)

    # now do chunks, groups .... TODO

        # ==
    
    # divide atoms into chunks of the right classes, in the right way

    # look at element fields:
    # pam = 'PAM3' or 'PAM5' or None
    # role = 'axis' or 'strand' or None

    
    # ....
    
    return

# end
