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
    
    chain = None # will be a DnaChain in finished instances #k needed? probably...

    wholechain = None # will be a WholeChain once dna_updater is done --
        # set by update_PAM_chunks in the updater run that made self,
        # and again in each updater run that made a new wholechain
        # running through self
    
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

    def set_wholechain(self, wholechain):
        """
        [to be called by dna updater]
        """
        # note: self.wholechain might or might not be None when this is called
        # (it's None for new chunks, but not for old ones now on new wholechains)
        self.wholechain = wholechain
        
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

class DnaAxisChunk(DnaLadderRailChunk):
    """
    Chunk for holding part of a Dna Segment Axis (the part in a single DnaLadder).

    Internal model object; same comments as in DnaStrandChunk docstring apply.
    """
    pass

# ==

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
    def _grab_atoms_from_chain(self, chain): # misnamed, doesn't take them out of chain
        """
        [extends superclass version]
        """
        DnaLadderRailChunk._grab_atoms_from_chain(self, chain)
        for atom in chain.baseatoms:
            # pull in Pls too (if they prefer this Ss to their other one)
            # and also directly bonded unpaired base atoms (which should
            # never be bonded to more than one Ss)
            ### review: can't these atoms be in an older chunk of the same class
            # from a prior step?? I think yes... so always pull them in,
            # regardless of class of their current chunk.
            for atom2 in atom.neighbors():
                grab_atom2 = False # might be changed to True below
                is_Pl = atom2.element.symbol.startswith('Pl') # KLUGE
                if is_Pl:
                    # does it prefer to stick with atom (over its other Ss neighbors, if any)?
                    if atom is atom2.Pl_preferred_Ss_neighbor(): # an Ss or None
                        grab_atom2 = True
                elif atom2.element.role == 'unpaired-base':
                    grab_atom2 = True
                if grab_atom2:
                    if atom2.molecule is self:
                        print "dna updater: should not happen: %r is already in %r" % \
                              (atom2, self)
                        # since self is new, just now being made,
                        # and since we think only one Ss can want to pull in atom2
                    else:
                        atom2.hopmol(self)
                            # review: does this harm the chunk losing it if it too is new? @@@
                            # (guess: yes; since we overrode delatom to panic... not sure about Pl etc)
                            # academic for now, since it can't be new, afaik
                            # (unless some unpaired-base atom is bonded to two Ss atoms,
                            #  which we ought to prevent in the earlier bond-checker @@@@ NIM)
                            # (or except for inconsistent bond directions, ditto)
                        pass
                    pass
                continue
            continue
        return # from _grab_atoms_from_chain
    pass # end of class DnaStrandChunk

# end
