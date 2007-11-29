# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaChain.py - Dna-aware AtomChainOrRing subclasses, AxisChain and StrandChain

Used internally for base indexing in strands and segments; perhaps used in the
future to mark subsequence endpoints for relations or display styles.

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_model.DnaAtomMarker import DnaAtomMarker

# ==

try:
    _chain_id_counter
except NameError:
    _chain_id_counter = 0

class DnaChain(object):
    """
    Abstract class, superclass of AxisChain and StrandChain.

    Owns and delegates to an AtomChainOrRing, providing DNA-specific
    navigation and indexing.

    Used internally for base indexing in strands and segments.
    """
    # default values of instance variables (DNA-specific):
    index_direction = 1 # might be set to 1 or -1 in instances -- OR we might replace this with a .reverse() method ### REVIEW/IMPLEM
        # note: not the same as bond direction for strands (which is not even defined for axis bonds).
    controlling_marker = None

    # REVIEW: need to delegate ringQ, or any other vars or methods, to self.chain_or_ring?
    
    def __init__(self, chain_or_ring):
        self.chain_or_ring = chain_or_ring
        #e possible optim: can we discard the bonds stored in chain_or_ring, and keep only the atomlist,
        # maybe not even in that object?
        # (but we do need ringQ, and might need future chain_or_ring methods that differ for it.)
        return
    def iteratoms(self): # REVIEW: different if self.index_direction < 0?
        """
        # get doc from calling method
        """
        return self.chain_or_ring.iteratoms()
    _chain_id = None
    def chain_id(self):
        """
        Return a unique, non-reusable id (with a boolean value of true)
        for "this chain" (details need review and redoc).
        """
        #e revise/refile (object_id_mixin?);
        # REVIEW whether on self or self.chain_or_ring (related: which is stored in the marker?)
        if not self._chain_id:
            global _chain_id_counter
            _chain_id_counter += 1
            self._chain_id = _chain_id_counter
        return self._chain_id
    def baseatom_index_pairs(self):
        """
        Return a list of pairs (baseatom, baseindex) for every pseudoatom
        in self.chain_or_ring which corresponds to a base or basepair,
        using an arbitrary origin for baseindex, and a direction corresponding
        to how we store the atoms, which is arbitrary until something corrects it;
        ###REVIEW whether to correct it by list reversal or setting index_direction,
        and whether to also store a base_offset for use by this function.
        
        (This skips PAM5 Pl atoms in strands, and would skip any bondpoint-like
        termination atoms if we still had them. [###REVIEW -- do we, in PAM5? nim if so?])
        """
        # doc - iterator or just return a list? for now, return list, for simplicity & robustness
        assert 0, "subclass must implement"
    def _f_own_atoms(self):
        """
        Own our atoms, for chain purposes.
        This does not presently store anything on the atoms, even indirectly,
        but we do take over the markers and decide between competing ones
        and tell them their status, and record the list of markers (needs update??)
        and the controlling marker for our chain identity (needs update??).
        This info about markers might be DNA-specific ...
        and it might be only valid during the dna updater run, before
        more model changes are made. [#todo: update docstring when known]
        """
        print "%r._f_own_atoms() is a stub - always makes a new marker" % self #####FIX
        chain = self.chain_or_ring
        # stub -- just make a new marker! we'll need code for this anyway...
        # but it's WRONG to do it when an old one could take over, so this is not a correct stub, just one that might run.
        atom = chain.atom_list[0]
        # hmm, this is getting dna specific, but we already have a chain vs ring subclass distinction,
        # which might affect general methods, so ignore that for now...
        assy = atom.molecule.assy
        marker = DnaAtomMarker(assy, [atom], chain = self) ### REVIEW: chain = self or chain? what's it for, anyway? ### @@@
        self.controlling_marker = marker
        marker.set_whether_controlling(True)
        ## and call that with False for the other markers, so they die if needed -- ### IMPLEM
    pass

# ==

class AxisChain(DnaChain):
    """
    Subclass of DnaChain for axis chains or rings.
    """
    def baseatom_index_pairs(self):
        chain = self.chain_or_ring
        atom_list = chain.atom_list
        if self.index_direction < 0: ### IMPLEM, -1 or 1... better if we can get chain to reverse the list when it's made ###
            atom_list = reversed_list(atom_list)
        return zip(atom_list, range(len(atom_list))) # assumes no bondpoint-like termination atoms! review for PAM5.
    pass

# ==

class StrandChain(DnaChain):
    """
    Subclass of DnaChain for strand chains or rings.
    
    Knows to skip Pl atoms when indexing or iterating over "base atoms".
    """
    def baseatom_index_pairs(self):
        chain = self.chain_or_ring
        atom_list = chain.atom_list
        if self.index_direction < 0: ### IMPLEM, -1 or 1... better if we can get chain to reverse the list when it's made ###
            # do this now, so our baseindex counter is in the right order
            atom_list = reversed_list(atom_list)
        res = []
        baseindex = 0 # incremented for base atoms during loop; found indices will start at 1
        for atom in atom_list: # in order for chain (arb direction), or ring (arbitrary origin & direction)
            if not atom.element.symbol.startswith('P'): # KLUGE, should use an element attribute, whether it's base-indexed
                baseindex += 1
                res.append((atom, baseindex))
        return res
    pass

# end
