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

from bond_chains import abstract_bond_chain_analyzer

# ==

class axis_bond_chain_analyzer(abstract_bond_chain_analyzer): #e also new make_ methods?
    def atom_ok(self, atom):
        return atom.element.role == 'axis'
    pass

class strand_bond_chain_analyzer(abstract_bond_chain_analyzer):
    def atom_ok(self, atom):
        return atom.element.role == 'strand'
    pass

# singleton objects
# (todo: could be local to the main using function,
#  if they returned instances so axis_analyzer.found_object_iteratoms etc
#  was not needed by other functions here)

axis_analyzer = axis_bond_chain_analyzer()

strand_analyzer = strand_bond_chain_analyzer()

# ==

def update_PAM_chunks( changed_atoms):
    """
    Update chunks containing changed PAM atoms, ensuring that
    PAM atoms remain divided into AxisChunks and StrandSegmentChunks
    in the right way.

    @param changed_atoms: an atom.key -> atom dict of all changed atoms
                          that this update function needs to consider,
                          which includes no killed atoms. WE ASSUME
                          OWNERSHIP OF THIS DICT and modify it in
                          arbitrary ways.
                          Note: in present calling code [071127]
                          this dict might include atoms from closed files.

    @return: None (??)
    """

    # see scratch file for comments to revise and bring back here...
    # also notesfile about dna markers, for how to maintain base index origin and identity.
    
    axis_chains, strand_chains = find_axis_and_strand_chains_or_rings( changed_atoms)

    #e move the chain markers whose atoms got killed

    #e use them (or make new) to determine id & index for each chain

    # revise indices & chunking

    # markers are really on base-pairs... even though on certain atoms too. indices are for base pairs...
    # so we need to find sections of axis whose strands have no nicks, and number these, and assign these to larger things.
    # one alg: assign new id & indices to every changed chain, effectively a jiglike thing on that chain just to index it...
    # maybe the returned objects above could even be these things. a quick check lets you see if the atom already has one;
    # only reuse it if every atom has same one and atom count matches (ie if its membership needn't change).
    # the atom class can have a field & method for this thing, even if it's also in jigs list... it's a chain id & index...
    # so it can be identical for both axis and strand chains. those atoms can be ChainAtoms.
    # (What about PAM5? i think we'd index only Ss and reuse same index on Pl...)

    # optim: sort bonds in atom classes, and sort atoms in bond classes, in special ways.
    
    return # from update_PAM_chunks

# ==

def find_axis_and_strand_chains_or_rings( changed_atoms):
    """
    Find and return the lists (axis_chains, strand_chains)
    of connected sets of axis and strand atoms respectively,
    in the representation described below.

    @param changed_atoms: an atom.key -> atom dict of all changed atoms
                          that this function needs to consider,
                          which includes no killed atoms. WE ASSUME
                          OWNERSHIP OF THIS DICT and modify it in
                          arbitrary ways.
                          Note: in present calling code [071127]
                          this dict might include atoms from closed files.

    @return: (axis_chains, strand_chains), which are lists of
    objects representing changed chains or rings (or lone atoms)
    of the specified element roles (axis or strand respectively).
    The chain or ring format is as returned by the make_* methods
    of the singleton objects axis_analyzer and strand_analyzer,
    which have methods for further use of those objects (in case
    they are just python data rather than class instances),
    e.g. for iterating over their atoms.
    Exception: None is never an element of the returned lists,
    since we remove it.
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
    
    # 
    strand_chains = strand_analyzer.find_chains_or_rings( strand_atoms )
    assert not strand_atoms ### REMOVE WHEN WORKS
    strand_atoms = None # not a dict, bug if used
    if DEBUG_DNA_UPDATER:
        print "dna updater: found %d strand chains or rings" % len(strand_chains)

    return axis_chains, strand_chains # from ...

# end

