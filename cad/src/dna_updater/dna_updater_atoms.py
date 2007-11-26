# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_atoms.py - enforce rules on newly changed PAM atoms and bonds

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_updater_globals import get_changes_and_clear
from dna_updater_globals import ignore_new_changes

from dna_updater_utils import remove_killed_atoms

from constants import noop as STUB_FUNCTION # FIX all uses

from fix_atom_classes import fix_atom_classes

fix_bond_classes = STUB_FUNCTION

from fix_deprecated_elements import fix_deprecated_elements

delete_bare_atoms = STUB_FUNCTION

# ==

def update_PAM_atoms_and_bonds(changed_atoms):
    """
    Update PAM atoms and bonds.

    @param changed_atoms: an atom.key -> atom dict of all changed atoms
                          that this update function needs to consider,
                          which includes no killed atoms. THIS WILL BE
                          MODIFIED to include all atoms changed herein,
                          and to remove any newly killed atoms.

    @return: None
    """
    # ==

    # fix atom & bond classes, and break illegal bonds

    # (Note that we never record changed bonds directly -- we just look at
    #  all bonds on all atoms we record as having changes.)
    
    fix_atom_classes( changed_atoms)
    
    fix_bond_classes( changed_atoms)
        # Fixes (or breaks if illegal) all bonds of those atoms.
        # NOTE: new bondpoints must be given correct classes by bond.bust,
        # since we don't fix them ourselves! (Can this be done incrementally? ### REVIEW)
        # IMPLEM THAT ###

    # depending on implem, fixing classes might record more atom changes;
    # if so, those functions also fixed the changed_atoms dict we passed in,
    # and we can ignore whatever additional changes were recorded:

    ignore_new_changes( "from fixing atom & bond classes")

    # ==
    
    # fix deprecated elements, and the classes of any new objects this creates
    # (covering all new atoms, and all their bonds)

    # (note: we might also extend this to do PAM 3/3+5/5 conversions. not sure.)
    
    fix_deprecated_elements( changed_atoms) # changes more atoms;
        # implem is allowed to depend on atom & bond classes being correct

    # NOTE: this may kill some atoms that remain in changed_atoms
    # or get added to it below. Subroutines must tolerate killed atoms
    # until we remove them again.

    # Grab new atoms the prior step made, to include in subsequent steps.
    # (Note also that atoms already in changed_atoms might have been killed
    #  and/or transmuted during the prior step.)

    new_atoms = get_changes_and_clear()

    if new_atoms:
    
        fix_atom_classes( new_atoms)
            # must tolerate killed atoms
        fix_bond_classes( new_atoms)
            # sufficient, since any changed bonds (if alive) must be new bonds.

        # Note: do changed_atoms.update only after fixing classes on new_atoms,
        # so any new atoms that replace old ones in new_atoms also make it
        # into changed_atoms. Note that this effectively replaces all old atoms
        # in changed_atoms. (Note that this only works because new atoms have
        # the same keys as old ones. Also note that none of this matters as of
        # 071120, since fixing classes doesn't make new objects in the present
        # implem.)
        
        changed_atoms.update( new_atoms )
        
        ignore_new_changes( "from fixing classes after fixing deprecated elements")

    # ==

    # delete bare atoms (axis atoms without strand atoms, or vice versa).

    delete_bare_atoms( changed_atoms)
        # must tolerate killed atoms; can kill more atoms and break bonds,
        # but we can ignore those changes
    ignore_new_changes( "from delete_bare_atoms")

    remove_killed_atoms( changed_atoms)

    return # from update_PAM_atoms_and_bonds

# end
