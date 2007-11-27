# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_chunks.py - enforce rules on chunks containing changed PAM atoms

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_updater_globals import get_changes_and_clear
from dna_updater_globals import ignore_new_changes

from dna_updater_utils import remove_killed_atoms

##from constants import noop as STUB_FUNCTION # FIX all uses

from dna_updater_constants import DEBUG_DNA_UPDATER

# ==

def update_PAM_chunks(changed_atoms):
    """
    Update chunks containing changed PAM atoms, ensuring that
    PAM atoms remain divided into AxisChunks and StrandSegmentChunks
    in the right way.

    @param changed_atoms: an atom.key -> atom dict of all changed atoms
                          that this update function needs to consider,
                          which includes no killed atoms. WE ASSUME
                          OWNERSHIP OF THIS DICT and modify it in
                          arbitrary ways.

    @return: None (??)
    """

    # Sort changed atoms into types we consider differently.

    axis_atoms = {}
    strand_atoms = {}

    def classify(atom):
        "put a live real atom into axis_atoms or strand_atoms, or discard it"
        # REVIEW: should we use atom classes or per-class methods here?
        # REVIEW: need to worry about atoms with too few bonds?
        element = atom.element
        role = element.role # 'axis' or 'strand' or None
        pam = element.pam # 'PAM3' or 'PAM5' or None
        if role == 'axis':
            axis_atoms[atom.key] = atom
            assert pam in ('PAM3', 'PAM5') # REVIEW: separate these too?
        elif role == 'strand':
            strand_atoms[atom.key] = atom
            assert pam in ('PAM3', 'PAM5') # REVIEW: separate these too?
        else:
            pass # ignore all other atoms
        return

    for atom in changed_atoms.itervalues():
        if atom.killed():
            print "bug: update_PAM_chunks: %r is killed (ignoring)", atom
        elif atom.is_singlet():
            # classify the real neighbor instead
            # (Note: I'm not sure if this is needed, but I'll do it to be safe.
            #  A possible need-case to review is when an earlier update step
            #  broke a bond.)
            classify(atom.singlet_neighbor())
        else:
            classify(atom)
        continue

    if not axis_atoms and not strand_atoms:
        return # optimization

    if DEBUG_DNA_UPDATER:
        print "dna updater: %d axis atoms, %d strand atoms" % (len(axis_atoms), len(strand_atoms))

    # Separate connected sets of axis atoms into AxisChunks, reusing existing
    # AxisChunks whereever possible.
    # [REVIEW: also label the atoms with positional hints?]
    # (If any improper branching is found, complain, and let it break up
    #  the chunks so that each one is properly structured.)

    def atom_ok_in_axis(atom): # REVIEW: pass in the first atom as well?
        "is an atom bonded to an atom in axis_atoms ok in the same AxisChunk?"
        assert not atom.killed()
        return atom.element.role == 'axis' # implies atom is not a bondpoint

    axis_analyzer = axis_bond_chain_analyzer()
    
    axis_chains = axis_analyzer.find_chains_or_rings( axis_atoms )
        # NOTE: this takes ownership of axis_atoms and trashes it.
        # NOTE: this only finds chains or rings which contain at least one
        # atom in axis_atoms, but they often contain other axis atoms too
        # (which were not in axis_atoms since they were not recently changed).
        #
        # Result is a list of objects returned by the make_ methods in
        # analyzer (for doc, see abstract_bond_chain_analyzer, unless we
        # override them in axis_bond_chain_analyzer).

    assert not axis_atoms ### REMOVE WHEN WORKS

    ## del axis_atoms
    ##     SyntaxError: can not delete variable 'axis_atoms' referenced in nested scope
    axis_atoms = None # not a dict, bug if used

    if DEBUG_DNA_UPDATER:
        print "dna updater: found %d axis chains or rings" % len(axis_chains)
    
    # ...
    # just for debug:
    strand_analyzer = strand_bond_chain_analyzer()
    strand_chains = strand_analyzer.find_chains_or_rings( strand_atoms )
    assert not strand_atoms ### REMOVE WHEN WORKS
    strand_atoms = None # not a dict, bug if used
    if DEBUG_DNA_UPDATER:
        print "dna updater: found %d strand chains or rings" % len(strand_chains)

    return # from update_PAM_chunks

# == scratch area


        # divide atoms into chunks of the right classes, in the right way

        # some bond classes can't be internal bonds... some must be...

# == for a new file? if short, can stay here

from bond_chains import abstract_bond_chain_analyzer

class axis_bond_chain_analyzer(abstract_bond_chain_analyzer): #e also new make_ methods?
    def atom_ok(self, atom):
        return atom.element.role == 'axis'
    pass

class strand_bond_chain_analyzer(abstract_bond_chain_analyzer):
    def atom_ok(self, atom):
        return atom.element.role == 'strand'
    pass

