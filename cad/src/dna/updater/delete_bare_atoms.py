# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
delete_bare_atoms.py - delete atoms lacking required neighbors

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna.updater.dna_updater_prefs import pref_fix_bare_PAM3_atoms
from dna.updater.dna_updater_prefs import pref_fix_bare_PAM5_atoms

from model.elements import Pl5

# ==

def delete_bare_atoms( changed_atoms):
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

    delete_these = []
    
    for atom in changed_atoms.itervalues():
        pam = atom.element.pam
        if pam: # optimization
            if (pam == 'PAM3' and fix_PAM3) or \
               (pam == 'PAM5' and fix_PAM5):
                if not atom.killed():
                    if atom_is_bare(atom):
                        delete_these.append(atom)

    for atom in delete_these:
        atom.kill()

    return

def atom_is_bare(atom): # fyi: only used in this file as of 080312
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
