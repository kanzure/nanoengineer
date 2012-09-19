# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
delete_bare_atoms.py - delete atoms lacking required neighbors

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna.updater.dna_updater_prefs import pref_fix_bare_PAM3_atoms
from dna.updater.dna_updater_prefs import pref_fix_bare_PAM5_atoms

from dna.model.PAM_atom_rules import PAM_atoms_allowed_in_same_ladder

from model.elements import Pl5

from utilities.constants import MODEL_PAM3, MODEL_PAM5

import foundation.env as env
from utilities.Log import orangemsg

# ==

def delete_bare_atoms( changed_atoms): # rename; also make not delete, just error (### need to review error propogation system)
    """
    Delete excessively-bare atoms (defined as axis atoms without strand atoms,
     or any other PAM atoms that are not allowed to exist with as few neighbors
     as they have -- note that the rules for strand atoms are in flux as of
     080117 since the representation of single-stranded DNA is as well).

    [must tolerate killed atoms; can kill more atoms and break bonds;
     can record more changes to neighbors of deleted atoms]
    """
    # Q. Which changes recorded by our side effects are needed in subsequent
    # dna updater steps?
    # A. The changed neighbor atoms are needed, in case they're the only
    # indicator of a change to the chain they're on (especially if the killed
    # atom was in a different dna ladder). But their classes needn't be changed,
    # and their deletion can't cause any more atoms to become bare (due to
    # the current meaning of bare), so no earlier updater steps need to be
    # repeated.

    # Note: if these debug prefs are not both True, errors might occur in the
    # dna updater. The goal is for these errors to be harmless (just debug
    # prints). As of 071205 the defaults are True, False, respectively.
    # TODO: revise following code to debug-print when these prefs make it
    # refrain from killing a bare atom (giving a count, per PAM model).
    fix_PAM3 = pref_fix_bare_PAM3_atoms()
    fix_PAM5 = pref_fix_bare_PAM5_atoms()

    delete_these_atoms = [] # change to mark them as errors

    fix_these_bonds = {} # id(bond) -> bond

    for atom in changed_atoms.itervalues():
        pam = atom.element.pam
        if pam: # optimization
            if (pam == MODEL_PAM3 and fix_PAM3) or \
               (pam == MODEL_PAM5 and fix_PAM5):
                if not atom.killed():
                    if atom_is_bare(atom):
                        delete_these_atoms.append(atom)
                    else:
                        # Do something about rung bonds between mismatched PAM atoms
                        # (in pam model or pam3+5 properties)
                        # [bruce 080405 new feature, for PAM3+5 safety]
                        # Note: if this kills bonds, we'd need to do that first,
                        # then recheck atom_is_bare (or always check it later).
                        # But it doesn't.
                        #
                        #update 080407: maybe this is not necessary:
                        # - we could permit these mismatches until DnaLadders
                        #   are formed, then fix them much more easily;
                        # - or we could even permit them then
                        #   (each rail would be uniform within itself),
                        #   with a little extra complexity in PAM conversion,
                        #   but it might even be useful to display "one strand
                        #   in PAM5", for example.
                        # So for now, I won't finish this code here, though I'll
                        # leave it in for long enough to see if it prints
                        # anything; then it should be removed, in case it's
                        # slow. ##### @@@@@
                        for bond in atom.bonds:
                            if bond.is_rung_bond():
                                if not PAM_atoms_allowed_in_same_ladder(bond.atom1, bond.atom2):
                                    fix_these_bonds[id(bond)] = bond

    for bond in fix_these_bonds.values():
        # REVIEW: can one of its atoms be in delete_these_atoms?
        # (probably doesn't matter even if it is)
        print "*** need to fix this bad rung bond (nim, so bugs will ensue): %r" % bond #####
        # pam model mismatch: mark them as errors, so not in any chains or ladders
        # pam option mismatch: reset options to default on all chunks connected by rung bonds (or could mark as errors)
        # other (if possible) (eg display styles, if that matters) --
        #  those differences would be ok here, only matters along axis
        #  (we'll make the func distinguish this if it ever looks at those)
        #
        # no need to be fast, this only happens for rare errors
        a1, a2 = bond.atom1, bond.atom2
        if a1.element.pam != a2.element.pam:
            # since it's a rung bond, we know the pams are both set
            print " nim: mark as errors", a1, a2 ## NIM here, look up how other code does it before propogation
        elif a1.molecule.display_as_pam != a2.molecule.display_as_pam or \
             a1.molecule.save_as_pam != a2.molecule.save_as_pam:
            # transclose to find chunks connected by rung bonds, put in a dict, reset pam props below
            print " nim: reset pam props starting at", a1, a2
        continue

    for atom in delete_these_atoms:
        #bruce 080515: always emit a deferred_summary_message,
        # since it can seem like a bug otherwise
        # (review this, if it happens routinely)
        summary_format = \
            "Warning: dna updater deleted [N] \"bare\" %s pseudoatom(s)" % \
            ( atom.element.symbol, )
        env.history.deferred_summary_message( orangemsg(summary_format) )
        atom.kill()

    return

def atom_is_bare(atom): # fyi: only used in this file as of 080312; ### REVIEW [080320]: better to mark as errors, not delete?
    """
    Is atom an axis atom with no axis-strand bonds,
    or (IF this is not allowed -- as of 080117 it *is* allowed)
    a strand base atom with no strand-axis bonds,
    or any other PAM atom with illegally-few neighbor atoms
    of the types it needs?
    (Note that a strand non-base atom, like Pl, can never be
     considered bare by this code.)
    """
    if atom.element.role == 'axis':
        strand_neighbors = filter(lambda other: other.element.role == 'strand', atom.neighbors())
        return not strand_neighbors
    elif atom.element.role == 'strand' and not atom.element is Pl5:
        return False # bruce 080117 revision, might be temporary --
            # but more likely, we'll replace it with some "bigger fix"
            # like adding Ub (or we might just do that manually later
            # and allow this with no change in old files)
##        axis_neighbors = filter(lambda other: other.element.role == 'axis', atom.neighbors())
##        return not axis_neighbors
    elif atom.element.role == 'unpaired-base':
        # guess, bruce 080117
        strand_neighbors = filter(lambda other: other.element.role == 'strand', atom.neighbors())
        return not strand_neighbors
    else:
        return False
    pass

# end
