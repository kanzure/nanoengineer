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

### REVIEW: should a DnaChain contain any undoable state? (it doesn't now) (guess: no)




class DnaChain_minimal(object):
    """
    just has baseatoms, index_direction record [doc more]
    """
    # default values of instance variables:
    
    baseatoms = None # subclass-specific __init__ must set this
    
    index_direction = 1 # might be set to 1 or -1 in instances -- OR we might replace this with a .reverse() method ### REVIEW/IMPLEM
        # note: not the same as bond direction for strands (which is not even defined for axis bonds).

        # current plan: this is public; might be moved to bare chain object;
        # a reverse method negates this and also reverses the lists.
        # so this's purpose is just to record whether that's been done
        # so direction info relative to our direction can continue to make sense
        # w/o needing update. @@@ REVIEW ### DOIT

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
        baseatoms = self.baseatoms
##        if self.index_direction < 0: ### IMPLEM, -1 or 1... better if we can get chain to reverse the list when it's made ###
##            baseatoms = reversed_list(baseatoms)
        return zip(baseatoms, range(len(baseatoms))) # assumes no bondpoint-like termination atoms! review for PAM5.

    def start_baseindex(self):
        return 0
    
    def baselength(self):
        return len(self.baseatoms)

    def end_baseatoms(self):
        return (self.baseatoms[0], self.baseatoms[-1]) # might be same atom

    pass

# ==

class DnaChainFragment(DnaChain_minimal): #e does it need to know ringQ? axis vs strand?
    def __init__(self, atom_list, index_direction):
        self.baseatoms = atom_list
        self.index_direction = index_direction
            # not sure this is correct,
            # as opposed to always storing (or caller always passing) 1 @@@
    pass

# ==

class DnaChain_AtomChainWrapper(DnaChain_minimal):
    #e inherit ChainAPI? (we're passed to a DnaAtomMarker as its chain -- no, more likely, as an element of a list which is that@@@)
    """
    Abstract class, superclass of AxisChain and StrandChain.

    Owns and delegates to an AtomChainOrRing, providing DNA-specific
    navigation and indexing.

    Used internally for base indexing in strands and segments,
    mainly while updating associations between the user-visible
    nodes for those and the pseudoatoms comprising them.

    Note: this base indexing is for purposes of moving origin markers
    for user convenience when editing several associated chains
    (e.g. the axis and two strand of a duplex). By default it
    is likely to be assigned as a "base pair index", which means
    that on the "2nd strand" it will go backwards compared to
    the actual "physical" base index within that strand. So it
    should not be confused with that. Further, on rings it
    may jump in value at a different point than whatever user-
    visible index is desired. If in doubt, consider it
    an internal thing, not to be user-exposed without using
    markers, relative directions, offsets, and ring-origins
    to interpret it.

    Note: some of the atoms in our chain_or_ring might be killed;
    we never remove atoms or modify our atom list after creation
    (except perhaps to reverse or reorder it). Instead, client code
    makes new chain objects.
    """
    # default values of instance variables:

    controlling_marker = None

    # REVIEW: need to delegate ringQ, or any other vars or methods, to self.chain_or_ring?
    
    def __init__(self, chain_or_ring):
        
        self.chain_or_ring = chain_or_ring
        
        #e possible optim: can we discard the bonds stored in chain_or_ring, and keep only the atomlist,
        # maybe not even in that object?
        # (but we do need ringQ, and might need future chain_or_ring methods that differ for it.)
        # decision 071203: yes, and even more, discard non-base atoms, optimize base scanning. [nim @@@]
        # make sure we can iterate over all atoms incl bos and Pls, sometime, for some purposes.
        # use a method name that makes that explicit.
        # For now, just store a separate list of baseatoms (in each subclass __init__ method).
        return
    
    def iteratoms(self): # REVIEW: different if self.index_direction < 0?
        """
        # get doc from calling method
        """
        return self.chain_or_ring.iteratoms()
    
    _chain_id = None
    def chain_id(self): #k this is used, but as of 071203 i'm not sure the use will survive, so review later whether it's needed
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
    
##    def baseatom_index_pairs(self):
##        assert 0, "subclass must implement"
##        
##    def start_baseindex(self):
##        assert 0, "subclass must implement"
##        
##    def baselength(self):
##        assert 0, "subclass must implement"

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
        
        # NOTE/TODO: if useful, this might record a list of all live markers
        # found on that chain in the chain, as well as whatever marker
        # is chosen or made to control it. (But note that markers might
        # get removed or made independently without the chain itself
        # changing. If so, some invalidation of those chain attributes
        # might be needed)
        
        print "%r._f_own_atoms() is a stub - always makes a new marker" % self #####FIX
        chain = self.chain_or_ring
        # stub -- just make a new marker! we'll need code for this anyway...
        # but it's WRONG to do it when an old one could take over, so this is not a correct stub, just one that might run.
        atom = chain.atom_list[0]
        assy = atom.molecule.assy
        marker = DnaAtomMarker(assy, [atom], chain = self)
            # note: chain has to be self, not self.chain
            # (the marker calls some methods that are only on self).
        self.controlling_marker = marker
        marker.set_whether_controlling(True)
        ## and call that with False for the other markers, so they die if needed -- ### IMPLEM
        #e For a chosen old marker, we get advice from it about chain direction,
        # then call a direction reverser if needed; see comments around index_direction.

    def virtual_fragment(self, start_baseindex, baselength, direction):
        """
        """
        # STUB - assume dir is 1, always return real fragment,
        # but assume it doesn't need most methods of the main api here...
        # so refactor this class... but for now, be quicker:
        assert direction == 1
        baseindex = start_baseindex - self.start_baseindex()
        subchain = self.baseatoms[baseindex : baseindex + baselength]
        return DnaChainFragment(subchain, self.index_direction) #e more args? does it know original indices? (i doubt it)
        
    pass # end of class DnaChain_AtomChainWrapper

# ==

class AxisChain(DnaChain_AtomChainWrapper):
    """
    A kind of DnaChain for just-found axis chains or rings.
    """
    def __init__(self, chain_or_ring):
        DnaChain_AtomChainWrapper.__init__(self, chain_or_ring)
        self.baseatoms = chain_or_ring.atom_list
        return
##    def baseatom_index_pairs(self):
##        chain = self.chain_or_ring
##        atom_list = chain.atom_list
####        if self.index_direction < 0: ### IMPLEM, -1 or 1... better if we can get chain to reverse the list when it's made ###
####            atom_list = reversed_list(atom_list)
##        return zip(atom_list, range(len(atom_list))) # assumes no bondpoint-like termination atoms! review for PAM5.
##    def start_baseindex(self):
##        return 0
##    def baselength(self):
##        return len(self.chain_or_ring.atom_list)
    pass

# ==

class StrandChain(DnaChain_AtomChainWrapper):
    """
    A kind of DnaChain for just-found strand chains or rings.
    
    Knows to skip Pl atoms when indexing or iterating over "base atoms"
    (but covers them in iteratoms).
    """
    def __init__(self, chain_or_ring):
        DnaChain_AtomChainWrapper.__init__(self, chain_or_ring)
        baseatoms = filter( lambda atom:
                              not atom.element.symbol.startswith('P') ,
                                # KLUGE, should use an element attribute, whether it's base-indexed
                            chain_or_ring.atom_list )
        self.baseatoms = baseatoms # in order of rungindex (called baseindex in methods)
            # note: baseatoms affects methods with "base" in their name,
            # but not e.g. iteratoms (which must cover Pl)
        return
    
##    def baseatom_index_pairs(self):
##        chain = self.chain_or_ring
##        atom_list = chain.atom_list
####        if self.index_direction < 0: ### IMPLEM, -1 or 1... better if we can get chain to reverse the list when it's made ###
####            # do this now, so our baseindex counter is in the right order
####            atom_list = reversed_list(atom_list)
##
####        res = []
####        baseindex = 0 # incremented for base atoms during loop; found indices will start at 1
####        for atom in atom_list: # in order for chain (arb direction), or ring (arbitrary origin & direction)
####            if not atom.element.symbol.startswith('P'): # KLUGE, should use an element attribute, whether it's base-indexed
####                baseindex += 1
####                res.append((atom, baseindex))
####        return res
##    def start_baseindex(self):
##        return 1
##    def baselength(self):
##        return len(self.baseatom_index_pairs()) # STUB, correct but SLOW, needs optim (cache the value) #####
    pass

# end
