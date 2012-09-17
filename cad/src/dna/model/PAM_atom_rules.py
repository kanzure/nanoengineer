# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
PAM_atom_rules.py - functions that define rules for permissible PAM structure

(note: not all such code is in this module; some of it is implicit
or hardcoded in other files)

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from model.elements import Singlet

from dna.updater.dna_updater_globals import _f_anyatom_wants_pam

from model.bonds import find_bond

# ==

def PAM_atoms_allowed_in_same_ladder(a1, a2): #bruce 080401
    # has known bugs, see comment; in future may apply only within rails
    """
    Are a1 and a2 both PAM atoms or bondpoints which are allowed in the same
    DnaLadder, during either formation or merging of ladders?

    If not, this might be for any reason we want, including cosmetic
    (e.g. chunk colors differ), but if different atoms in one base pair
    use different criteria, problems might ensue if the dna updater does not
    explicitly handle that somehow when forming ladders (since currently
    it requires all atoms in one full or partial basepair to be in one ladder).

    Presently, we allow bondpoints to go with anything; other than that,
    we require both atoms to have the same PAM model, and to be in chunks
    with the same PAM-related properties (display_as_pam, save_as_pam).
    """
    # BUG: the following will be wrong, if the atoms in one full or partial
    # basepair disagree about this data. To fix, find the basepair here
    # (if too big, mark atoms as error, use default results), and combine
    # the properties to make a joint effective property on each atom,
    # before comparing. Not trivial to do that efficiently. Or, actually
    # modify the atoms in a basepair to agree, or mark them as errors so
    # they are excluded from chains, at earlier updater stages. ### TODO
    #
    # I'm ignoring this for now, though it means some operation bugs could
    # lead to updater exceptions. (And correct operations must change these
    # properties in sync across base pairs.) It may even mean the user can
    # cause those errors by piecing together base pairs from different
    # DnaLadders using direct bond formation. (Maybe make rung-bond-former
    # detect and fix those?)
    #
    # Review: how to treat atoms with dna_updater_errors?

    explain_false_when_printed = True

    explain_false_always = False # do not commit with true --
        # too verbose if user makes mixed PAM models on purpose

    explain_false = explain_false_when_printed or explain_false_always
        # revised all explain_false logic, bruce 080413

    print0 = [""]

    def doit():
        if a1.element is Singlet or a2.element is Singlet:
            return True
        if a1.element.pam != a2.element.pam:
            # different pam models, or one has no pam model (non-PAM element)
            if explain_false:
                print0[0] = "different pam models: %s, %s" % (a1.element.pam, a2.element.pam)
            return False
        # we don't need to check for "both non-PAM", since we're not called
        # for such atoms (and if we were, we might as well allow them together)

        # compare manual pam conversion requests
        if _f_anyatom_wants_pam(a1) != _f_anyatom_wants_pam(a2):
            if explain_false:
                print0[0] = "different requested manual pam conversion: %s, %s" % \
                      ( _f_anyatom_wants_pam(a1),
                        _f_anyatom_wants_pam(a2) )
            return False

        # compare pam-related properties of chunks
        chunk1 = a1.molecule
        chunk2 = a2.molecule
        # assume atoms not killed, so these are real chunks
        if chunk1 is chunk2:
            # optimize common case
            return True
        if (chunk1.display_as_pam or None) != (chunk2.display_as_pam or None): # "or None" is kluge bug workaround [080407 late]
            if explain_false:
                print0[0] = "different display_as_pam: %r != %r" % ( chunk1.display_as_pam, chunk2.display_as_pam)
            return False
        if (chunk1.save_as_pam or None) != (chunk2.save_as_pam or None):
            if explain_false:
                print0[0] = "different save_as_pam: %r != %r" % ( chunk1.save_as_pam, chunk2.save_as_pam)
            return False
        return True
    res = doit()
    if not res:
        # should we print this as a possible bug, and/or explain why it's false?
        bond = find_bond(a1, a2)
        weird = False
        if bond is None: # can this happen, re find_bond semantics? I think so;
            # should not happen re how we are called, tho..
            # oops, it's routine, since ladder merge is filtered by checking
            # this for arbitrary baseatoms, so nevermind. [bruce 080413 230pm]
            pass ## weird = "not bonded"
        elif bond.is_rung_bond():
            weird = "rung bond"
        if weird:
            print "might cause bugs: %r and %r not allowed in same ladder, but %s" % (a1, a2, weird)
            if explain_false:
                print " reason not allowed: ", print0[0]
        elif explain_false_always:
            print "debug fyi: PAM_atoms_allowed_in_same_ladder(%r, %r) -> %r" % (a1, a2, res)
            print " reason not allowed: ", print0[0]
    return res

# end
