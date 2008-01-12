# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaLadderRailChunk.py - 

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from chunk import Chunk

from constants import gensym

# see also:
## from dna_model.DnaLadder import _rail_end_atom_to_ladder
# (below, perhaps in a cycle)

# ==

class DnaLadderRailChunk(Chunk):
    """
    """

    # initial values of instance variables:
    
    chain = None # will be a DnaChain in finished instances
    
    ladder = None # will be a DnaLadder in finished instances
    
    ###e todo: undo, copy for those attrs?

    # == init methods

    def __init__(self, assy, chain_or_something_else):
        # TODO: check if this arg signature is ok re undo, copy, etc;
        # and if ok for rest of Node API if that matters for this kind of chunk;
        # for now just assume chain_or_something_else is a DnaChain
        chain = chain_or_something_else
        # name should not be seen, but it is for now...
        name = gensym(self.__class__.__name__.split('.')[-1]) + ' (internal)'
        Chunk.__init__(self, assy, name)
        self.chain = chain
        # add atoms before setting self.ladder, so adding them doesn't invalidate it
        self._grab_atoms_from_chain(chain) #e we might change when this is done, if we implem copy for this class
        # following import is a KLUGE to avoid recursive import
        # (still has import cycle, ought to ### FIX -- should refile that func somehow)
        from dna_model.DnaLadder import _rail_end_atom_to_ladder
            # todo: make not private... or get by without it here (another init arg??)
            # review: make this import toplevel? right now it's probably in a cycle.
        self.ladder = _rail_end_atom_to_ladder( chain.baseatoms[0] )
        return

    def _grab_atoms_from_chain(self, chain):
        """
        Assume we're empty of atoms;
        pull in all baseatoms from the given DnaChain,
        plus whatever bondpoints or Pl atoms are attached to them
        (but only Pl atoms which are not already in other DnaLadderRailChunks).
        """
        # common code -- just pull in baseatoms and their bondpoints.
        # subclass must extend as needed.
        for atom in chain.baseatoms:
            atom.hopmol(self)
                # note: hopmol immediately kills old chunk if it becomes empty
        return

    # == invalidation-related methods
    
    def invalidate_ladder(self): #bruce 071203
        """
        [overrides Chunk method]
        [only legal after init, not during it, thus not in self.addatom]
        """
        self.ladder.invalidate()
        return

    def in_a_valid_ladder(self): #bruce 071203
        """
        Is this chunk a rail of a valid DnaLadder?
        [overrides Chunk method]
        """
        return self.ladder.valid

    # == override Chunk methods related to invalidation

    def addatom(self, atom):
        Chunk.addatom(self, atom)
        if self.ladder and self.ladder.valid:
            # this happens for bondpoints (presumably when they're added since
            # we broke a bond); I doubt it happens for anything else,
            # but let's find out (in a very safe way, tho a bit unclear):
            if atom.element.eltnum != 0:
                print "dna updater, fyi: %r.addatom %r invals %r" % (self, atom, self.ladder)
            self.ladder.invalidate()
        return

    def delatom(self, atom):
        Chunk.delatom(self, atom)
        if self.ladder.valid:
            self.ladder.invalidate()
        return
    
    # == other methods
    
    #e draw method?
    
    pass

# == these subclasses might be moved to separate files, if they get long

class DnaStrandChunk(DnaLadderRailChunk):
    """
    Chunk for holding part of a Dna Strand (the part in a single DnaLadder).

    Internal model object -- won't be directly user-visible (for MT, selection, etc)
    when dna updater is complete. But it's a normal member of the internal model tree for
    purposes of copy, undo, mmp file, internal selection, draw.
    (Whether copy implem makes another chunk of this class, or relies on dna
    updater to make one, is not yet decided. Likewise, whether self.draw is
    normally called is not yet decided.)
    """
    def _grab_atoms_from_chain(self, chain):
        """
        [extends superclass version]
        """
        DnaLadderRailChunk._grab_atoms_from_chain(self, chain)
        for atom in chain.baseatoms:
            # pull in unowned Pls too
            for atom2 in atom.neighbors():
                if atom2.element.symbol.startswith('Pl'): # KLUGE
                    mol2 = atom2.molecule
                    if not isinstance(mol2, DnaLadderRailChunk):
                        # also covers whether mol2 is self
                        # WARNING: correctness of this condition
                        # assumes that we don't change chunk classes,
                        # but only make new chunks, when we want chunks
                        # to have the subclasses defined in this module.
                        atom2.hopmol(self)
        return
    pass

class DnaAxisChunk(DnaLadderRailChunk):
    """
    Chunk for holding part of a Dna Segment Axis (the part in a single DnaLadder).

    Internal model object; same comments as in DnaStrandChunk docstring apply.
    """
    pass
                        
# end
