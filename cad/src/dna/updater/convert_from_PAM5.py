# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
convert_from_PAM5.py - detect PAM5 atoms and convert (some of) them to PAM3+5

WARNING: THIS MODULE IS PROBABLY OBSOLETE, and is no longer called as of 080408.
Newer code does this in later stages of the dna updater after ladders are made.
However, it might be partly revived (see comment near the commented-out call)
and some code within it will be useful in those later stages,
so don't remove it yet.

@author: Bruce (but model and conversion function is by Eric D)
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from model.elements import Pl5, Singlet

from utilities import debug_flags
from utilities.constants import MODEL_PAM5

from dna.updater.dna_updater_prefs import pref_dna_updater_convert_to_PAM3plus5

import foundation.env as env
from utilities.Log import orangemsg, redmsg, graymsg

from model.bond_constants import find_bond

# ==

def convert_from_PAM5( changed_atoms): # might be misnamed, if it turns out it does only some of the conversion ###
    """
    scan for PAM5 elements that should be converted, and convert them
    as well as can be done per-atom.

    @note: this replaces Pl5 with direct bonds, and may do more (undecided),
           but some conversion must be done later after ladders are constructed.
    """

    convert = pref_dna_updater_convert_to_PAM3plus5()
        # note: in future this is likely to be a finer-grained setting

    if not convert:
        return

    pam5_atoms = [] #k needed? not yet used, might not be useful until we have ladders... ###

    for atom in changed_atoms.itervalues():
        chunk = atom.molecule
        if chunk is None or atom.key not in chunk.atoms:
            continue # don't touch nonlive atoms
        if chunk.display_as_pam == MODEL_PAM5:
            continue # this atom doesn't want to be converted
        if atom.element is Pl5:
            _convert_Pl5(atom) # and save others to convert later?? see _save_Pl_info ...
        else:
            pam = atom.element.pam
            if pam == MODEL_PAM5:
                pam5_atoms += [atom] # note: slow and not yet used
        continue

    return # from convert_from_PAM5

# ==

def _convert_Pl5(atom):
    """
    If atom's neighbors have the necessary structure
    (Ss-Pl-Ss or X-Pl-Ss, with fully set and consistent bond_directions),
    save atom's coordinates on its Ss neighbors,
    arrange for them to postprocess that info later,
    and then kill atom, replacing its bonds with a direct bond
    between its neighbors (same bond_direction).

    Summarize results (ok or error) to history.
    """

    ### NOTE: the code starting from here has been copied and modified
    #### into a new function in pam3plus5_ops.py by bruce 080408.

    assert atom.element is Pl5 # remove when works

    # could also assert no dna updater error

    # Note: we optimize for the common case (nothing wrong, conversion happens)

    bonds = atom.bonds

    # change these during the loop
    bad = False
    saw_plus = saw_minus = False
    num_bondpoints = 0
    neighbors = []
    direction = None # KLUGE: set this during loop, but use it afterwards too

    for bond in bonds:
        other = bond.other(atom)
        neighbors += [other]
        element = other.element
        direction = bond.bond_direction_from(atom)

        if direction == 1:
            saw_plus = True
        elif direction == -1:
            saw_minus = True

        if element is Singlet:
            num_bondpoints += 1
        elif element.symbol in ('Ss3', 'Ss5'):
            pass
        else:
            bad = True
        continue

    if not (len(bonds) == 2 and saw_minus and saw_plus and num_bondpoints < 2):
        bad = True

    if bad:
        summary_format = \
            "Warning: dna updater left [N] Pl5 pseudoatom(s) unconverted"
        env.history.deferred_summary_message( orangemsg(summary_format) )
        return

    del saw_plus, saw_minus, num_bondpoints, bad

    # Now we know it is either Ss-Pl-Ss or X-Pl-Ss,
    # with fully set and consistent bond_directions.

    # But we'd better make sure the neighbors are not already bonded!
    #
    # (This is weird enough to get its own summary message, which is red.
    #  Mild bug: we're not also counting it in the above message.)
    #
    # (Note: there is potentially slow debug code in rebond which is
    #  redundant with this. It does a few other things too that we don't
    #  need, so if it shows up in a profile, just write a custom version
    #  for this use. ### OPTIM)

    n0, n1 = neighbors
    del neighbors

    b0, b1 = bonds
    del bonds # it might be mutable and we're changing it below,
        # so be sure not to use it again

    if find_bond(n0, n1):
        summary_format = \
            "Error: dna updater noticed [N] Pl5 pseudoatom(s) whose neighbors are directly bonded"
        env.history.deferred_summary_message( redmsg(summary_format) )
        return

    # Pull out the Pl5 and directly bond its neighbors,
    # reusing one of the bonds for efficiency.
    # (This doesn't preserve its bond_direction, so set that again.)

    # Kluge: the following code only works for n1 not a bondpoint
    # (since bond.bust on an open bond kills the bondpoint),
    # and fixing that would require inlining and modifying a
    # few Atom methods,
    # so to avoid this case, reverse everything if needed.
    if n1.element is Singlet:
        direction = - direction
        n0, n1 = n1, n0
        b0, b1 = b1, b0
        # Note: bonds.reverse() might modify atom.bonds itself,
        # so we shouldn't do it even if we didn't del bonds above.
        # (Even though no known harm comes from changing an atom's
        #  order of its bonds. It's not reviewed as a problematic
        #  change for an undo snapshot, though. Which is moot here
        #  since we're about to remove them all. But it still seems
        #  safer not to do it.)
        pass

    # save atom_posn before modifying atom (not known to be needed),
    # and set atom.atomtype to avoid bugs in reguess_atomtype during atom.kill
    # (need to do that when it still has the right number of bonds, I think)
    atom_posn = atom.posn()
    atom.atomtype # side effect: set atomtype

    old_nbonds_neighbor1 = len(n1.bonds) # for assert
    old_nbonds_neighbor0 = len(n0.bonds) # for assert

    b1.bust(make_bondpoints = False) # n1 is now missing one bond; so is atom
    b0.rebond(atom, n1) # now n1 has enough bonds again; atom is missing both bonds

    assert len(atom.bonds) == 0, "Pl %r should have no bonds but has %r" % (atom, atom.bonds)
    assert not atom.killed()

    assert len(n1.bonds) == old_nbonds_neighbor1
    assert len(n0.bonds) == old_nbonds_neighbor0

    # KLUGE: we know direction is still set to the direction of b1 from atom
    # (since b1 was processed last by the for loop above),
    # which is the overall direction from n0 thru b0 to atom thru b1 to n1,
    # so use this to optimize recording the Pl info below.
    # (Of course we really ought to just rewrite this whole conversion in Pyrex.)

    ## assert direction == b1.bond_direction_from(atom) # too slow to enable by default

    # not needed, rebond preserves it:
    ## b0.set_bond_direction_from(n0, direction)
    ## assert b0.bond_direction_from(n0) == direction # too slow to enable by default

    # now save the info we'll need later (this uses direction left over from for-loop)

    if n0.element is not Singlet:
        _save_Pl_info( n0, direction, atom_posn)

    if n1.element is not Singlet:
        _save_Pl_info( n1, - direction, atom_posn) # note the sign on direction

    # get the Pl atom out of the way

    atom.kill()
        # (let's hope this happened before an Undo checkpoint ever saw it --
        #  sometime verify that, and optimize if it's not true)

    # summarize our success -- we'll remove this when it becomes the default,
    # or condition it on a DEBUG_DNA_UPDATER flag ###

    debug_flags.DEBUG_DNA_UPDATER # for use later

    summary_format = \
        "Note: dna updater converted [N] Pl5 pseudoatom(s)"
    env.history.deferred_summary_message( graymsg(summary_format) )

    return

# ==

def _save_Pl_info( sugar, direction_to_Pl, Pl_posn ):
    print "_save_Pl_info is nim: %r" % ((sugar, direction_to_Pl, Pl_posn),)


# end
