# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_find_chains.py - helper for dna_updater_chunks

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_updater_constants import DEBUG_DNA_UPDATER

from bond_chains import abstract_bond_chain_analyzer

from dna_model.AtomChainOrRing import AtomChain, AtomRing

from dna_model.DnaChain import AxisChain, StrandChain
from dna_model.DnaChain import DnaChain_AtomChainWrapper # for isinstance

# ==

# helper classes (will probably turn out to be private, or perhaps
#  even local to find_axis_and_strand_chains_or_rings)

class dna_bond_chain_analyzer(abstract_bond_chain_analyzer):
    """
    [private abstract helper class]
    For DNA, we like our found atom/bond chains or rings to be instances
    of one of AtomChainOrRing's subclasses, AtomChain or AtomRing.
    """
    _wrapper = None # a per-subclass constant, to wrap an AtomChainOrRing
    def make_chain(self, listb, lista):
        # also used for lone atoms
        return self._wrap( AtomChain(listb, lista))
    def make_ring(self, listb, lista):
        return self._wrap( AtomRing(listb, lista))
    def _wrap(self, chain_or_ring):
        if chain_or_ring is None:
            return None
        res = self._wrapper(chain_or_ring)
        # check effect of wrapper:
        assert isinstance( res, DnaChain_AtomChainWrapper) #e remove when works?
        return res
    def found_object_iteratoms(self, chain_or_ring):
        if chain_or_ring is None:
            return ()
        # check effect of wrapper:
        assert isinstance( chain_or_ring, DnaChain_AtomChainWrapper) #e remove when works?
        return chain_or_ring.iteratoms()
            # note: it's essential to include Pl atoms in this value,
            # for sake of find_chain_or_ring's dict.pop.
    pass
    
class axis_bond_chain_analyzer(dna_bond_chain_analyzer):
    _wrapper = AxisChain
    def atom_ok(self, atom):
        return atom.element.role == 'axis' and not atom.molecule.in_a_valid_ladder()
    pass

class strand_bond_chain_analyzer(dna_bond_chain_analyzer):
    _wrapper = StrandChain
    def atom_ok(self, atom):
        # note: this can include Pl atoms in PAM5,
        # but the wrapper class filters them out of
        # the atom list it stores.
        return atom.element.role == 'strand' and not atom.molecule.in_a_valid_ladder()
    pass

# singleton objects
# (todo: could be local to the main using function,
#  if they returned instances so axis_analyzer.found_object_iteratoms etc
#  was not needed by other functions here; now they do, so REVIEW whether they can be local ###)

axis_analyzer = axis_bond_chain_analyzer()

strand_analyzer = strand_bond_chain_analyzer()

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

    @return: (axis_chains, strand_chains), which are sequences of
    objects representing changed chains or rings (or lone atoms)
    of the specified element roles (axis or strand respectively).
    (They should be both tuples or both lists, so the caller can
    concatenate them using +.)
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
        """
        [local helper function]
        put a live real atom into axis_atoms or strand_atoms, or discard it
        """
        # REVIEW: should we use atom classes or per-class methods here?
        # REVIEW: need to worry about atoms with too few bonds?
        element = atom.element
        role = element.role # 'axis' or 'strand' or None # @@@@@@
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
            print "bug: update_PAM_chunks: %r is killed (ignoring)" % atom
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
        return (), () # optimization

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

    return axis_chains, strand_chains # from find_axis_and_strand_chains_or_rings

# end
