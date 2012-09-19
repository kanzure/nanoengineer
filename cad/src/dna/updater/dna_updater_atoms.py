# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
dna_updater_atoms.py - enforce rules on newly changed PAM atoms and bonds

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from utilities.constants import noop as STUB_FUNCTION # FIX all uses

from dna.updater.dna_updater_globals import get_changes_and_clear
from dna.updater.dna_updater_globals import ignore_new_changes

from dna.updater.dna_updater_utils import remove_killed_atoms
from dna.updater.dna_updater_utils import remove_error_atoms

from utilities import debug_flags

from dna.updater.fix_atom_classes import fix_atom_classes

fix_bond_classes = STUB_FUNCTION

from dna.updater.fix_deprecated_elements import fix_deprecated_elements

from dna.updater.delete_bare_atoms import delete_bare_atoms
from dna.updater.dna_updater_prefs import pref_permit_bare_axis_atoms

from dna.updater.fix_bond_directions import fix_local_bond_directions

##from dna.updater.convert_from_PAM5 import convert_from_PAM5

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

    # fix atom & bond classes, and break locally-illegal bonds

    # (Note that the dna updater only records changed bonds
    #  by recording both their atoms as changed -- it has no
    #  list of "changed bonds" themselves.)

    # note: these fix_ functions are called again below, on new atoms.

    fix_atom_classes( changed_atoms)

    fix_bond_classes( changed_atoms)
        # Fixes (or breaks if locally-illegal) all bonds of those atoms.
        # ("Locally" means "just considering that bond and its two atoms,
        #  not worrying about other bonds on those atoms. ### REVIEW: true now? desired?)

        # NOTE: new bondpoints must be given correct classes by bond.bust,
        # since we don't fix them in this outer method!
        # (Can this be done incrementally? ### REVIEW)
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

            # @@@@ did that break illegal bonds, or do we do that somewhere else? [080117 Q]

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

    if not pref_permit_bare_axis_atoms():
        delete_bare_atoms( changed_atoms)
        # must tolerate killed atoms; can kill more atoms and break bonds,
        # but we can ignore those changes; BUT it can change neighbor atom
        # structure, and those changes are needed by subsequent steps
        # (though no need to fix their classes or look for bareness again,
        #  as explained inside that function)

        # Grab newly changed atoms from that step (neighbors of deleted atoms),
        # to include in subsequent steps. (But no need to fix their classes
        # or again call delete_bare_atoms, as explained inside that function.)
        # (Note also that atoms already in changed_atoms might have been killed
        #  during that step.)

        new_atoms = get_changes_and_clear()

        if new_atoms:
            if debug_flags.DEBUG_DNA_UPDATER:
                print "dna_updater: will scan %d new changes from delete_bare_atoms" % len(new_atoms)
            changed_atoms.update( new_atoms )

    # ==

    # Fix local directional bond issues:
    # - directional bond chain branches (illegal)
    # - missing bond directions (when fixable locally -- most are not)
    # - inconsistent bond directions
    #
    # The changes caused by these fixes include only:
    # - setting atom._dna_updater__error to a constant error code string on some atoms
    # - setting or unsetting bond direction on open bonds (changes from this could be ignored here)

    # Tentative conclusion: no need to do anything to new changed atoms
    # except scan them later; need to ignore atoms with _dna_updater__error set
    # when encountered in changed_atoms (remove them now? or in that function?)
    # and to stop on them when finding chains or rings.

    # [Note: geometric warnings (left-handed DNA, major groove on wrong side)
    # are not yet implemented. REVIEW whether they belong here or elsewhere --
    # guess: later, once chains and ladders are known. @@@@]

    fix_local_bond_directions( changed_atoms)

    new_atoms = get_changes_and_clear()

    if new_atoms:
        if debug_flags.DEBUG_DNA_UPDATER:
            print "dna_updater: will scan %d new changes from fix_local_bond_directions" % len(new_atoms)
        changed_atoms.update( new_atoms )

    # ==

    remove_killed_atoms( changed_atoms)

    remove_error_atoms( changed_atoms)

    # replaced with code at a later stage [bruce 080408];
    # we might revive this to detect Pl5 atoms that are bridging Ss3 atoms
    # (an error to fix early to prevent bugs)
    # or to make a note of ladders that need automatic conversion
    # due to displaying PAM5 in PAM35 form by default
    #
##    # ==
##
##    # Convert from PAM5 to PAM3+5, per-atom part. [080312, unfinished]
##
##    # Potential optimization (not known whether it'd be significant):
##    # only do this after operations that might introduce new PAM5 atoms
##    # (like mmp read, mmp insert, or perhaps Dna Generator)
##    # or that change any setting that causes them to become convertable.
##    # This is not practical now, since errors or non-whole base pairs prevent
##    # conversion, and almost any operation can remove those errors or make the
##    # base pairs whole.
##
##    convert_from_PAM5( changed_atoms)
##        # note: this replaces Pl5 with direct bonds, and may do more (undecided),
##        # but some conversion might be done later after ladders are constructed.
##        # So it might be misnamed. ###
##
##    ignore_new_changes( "from converting PAM5 to PAM3+5")
##
##    remove_killed_atoms( changed_atoms)

    return # from update_PAM_atoms_and_bonds

# end
