# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaAtomMarker.py - marked positions on atom chains, moving to live atoms as needed

Used internally for base indexing in strands and segments; perhaps used in the
future to mark subsequence endpoints for relations or display styles.

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from ChainAtomMarker import ChainAtomMarker

# ==

# constants

_CONTROLLING_UNKNOWN = True # represents an unknown value of self.controlling
    # note: this value of True is not strictly correct, but simplifies the code
    #e rename?

# ==

# globals and accessors

_homeless_dna_markers = {}

def _f_get_homeless_dna_markers():
    """
    Return the homeless dna markers,
    and clear the list so they won't be returned again
    (unless they are newly made homeless).

    Friend function for dna updater. Other calls
    would cause it to miss newly homeless markers,
    causing serious bugs.
    """
    res = _homeless_dna_markers.values()
    _homeless_dna_markers.clear()
    res = filter( lambda marker: marker.is_homeless(), res ) # probably not needed
    return res

# ==

#e refile these utilities

def reversed_list(list1):
    """
    Return a reversed copy of list1 (of the same class as list1),
    which can be a Python list, or any object obeying the same API.
    """
    list1 = list1[:]
    list1.reverse()
    return list1

# ==

class DnaAtomMarker( ChainAtomMarker):
    """
    A ChainAtomMarker specialized for DNA axis or strand atoms
    (base atoms only, not Pl atoms).
    """

    # default values of instance variables:
    
    # Jig API variables
    sym = "DnaAtomMarker" # ?? maybe used only on subclasses for SegmentMarker & StrandMarker? maybe never visible?
        # TODO: not sure if this gets into mmp file, but i suppose it does... and it gets copied, and has undoable properties...
        # and in theory it could appear in MT, though in practice, probably only in some PM listwidget, but still,
        # doing the same things a "visible node" can do is good for that.

    copyable_attrs = ChainAtomMarker.copyable_attrs + ()
        # todo: add some -- namely the settings about how it moves, whether it lives, etc
    
    # other variables

    controlling = _CONTROLLING_UNKNOWN

    _advise_new_chain_direction = 0
        # temporarily set to 0 or -1 or 1 for use when moving self and setting a new chain

    # == Jig API methods (overridden or extended):
    
    def remove_atom(self, atom):
        "[extends superclass method]"
        ChainAtomMarker.remove_atom(self, atom)
        _homeless_dna_markers[id(self)] = self # TODO: also do this when copied? not sure it's needed.
        return

    #e also add a method [nim in api] for influencing how we draw the atom?
    # guess: no -- might be sufficient (and is better, in case old markers lie around)
    # to just use the Jig.draw method, and draw the marker explicitly. Then it can draw
    # other graphics too, be passed style info from its DnaGroup/Strand/Segment, etc.

    # == ChainAtomMarker API methods (overridden or extended):
    
    def set_chain(self, chain):
        """
        A new AtomChainOrRing object is taking us over (but we'll stay on the same atom).
        (Also called during superclass __init__ to set our initial chain.)

        @param chain: the atom chain or ring which we now reside on (can't be None)
        @type chain: AtomChainOrRing instance
        """
        ChainAtomMarker.set_chain(self, chain)
        self.controlling = _CONTROLLING_UNKNOWN

    # == other methods
    
    def set_whether_controlling(self, controlling):
        """
        our new chain tells us whether we control its atom indexing, etc, or not
        [depending on our settings, we might die or behave differently if we're not]
        """
        self.controlling = controlling
        if not controlling:
            self.kill() # stub -- in future, depends on user-settable properties and/or on subclass
        return
    
    def _f_move_to_live_atom_step1(self): #e todo: split docstring
        """
        [friend method, called from dna_updater]
        Our atom died; see if there is a live atom on our old chain which we want to move to;
        if so, move to the best one (updating all our properties accordingly) and return True;
        if not, die and return False.
        """
            # IMPLEM - just find the nearest live atom in the right direction; return "still alive"
            # do this by scanning old atom lists in chain objs known to markers, so no need for per-atom stored info.
            # [alt: do by sorting new atoms for best new home - bad since requires storing that info on atoms, or lots of lookup.]

        assert self.is_homeless()
        
        old_chain = self._chain # @@@ needs revision so this is a FullChain (list of chain frags), not just one chain frag like now
        old_atom = self._get_marker_atom()
        
        assert not self.atoms
        assert old_atom.killed() #e or we could just return if these are false, if we want to be callable then

        # Find the first and last live atoms in the atom list (and their indices),
        # both before and after our atom, whose index we also find.
        # From this info we can simulate searching in either direction on a chain or ring,
        # and also compute the index offset of the move.
        # (To compute it correctly for PAM5, we don't count non-base (Pl) atoms in the indexing.)
        
        class stuff: #e rename
            "track first & last atom seen during some subsection of the chain"
            first_atom = None
            first_index = None
            last_atom = None
            last_index = None
            def see(self, atom, index):
                # assume live atom
                if self.first_atom is None:
                    self.first_atom = atom
                    self.first_index = index
                self.last_atom = atom
                self.last_index = index
                return
            def atom_index_pairs(self):
                """
                Return a list of the unique (atom, index) pairs we saw.
                (Its length will be 0 or 1 or 2.)
                """
                res = []
                if self.first_atom is not None:
                    res.append( (self.first_atom, self.first_index) )
                    assert self.last_atom is not None
                    if self.last_atom is not self.first_atom:
                        res.append( (self.last_atom, self.last_index) )
                return res
            pass
        
        before_stuff = stuff()
        after_stuff = stuff()
        
        old_atom_index = None # note: any int is a possible value, in principle
        
        before = True # changed to False when we find old_atom during loop

        old_index_to_atom_dict = {}

        for atom, baseindex in old_chain.baseatom_index_pairs(): # skips non-base atoms
            # note: this is in order for chain (arb direction), or ring (arbitrary origin & direction)
            # note: in current implem, found indices will start at 1, but the method can't guarantee
            # that in general (since negative indices might be required for a user-set origin),
            # so this code should't assume they avoid any int values.
            #e possible optim: call chain method to do this search in a faster way??
            old_index_to_atom_dict[baseindex] = atom
                #e possible optim: use this to partly replace the _stuff objects?
                #e possible optim: cache on the chain itself, for use by several moving markers?
            if atom.killed():
                if atom is old_atom:
                    old_atom_index = baseindex
                    before = False
            else:
                if before:
                    before_stuff.see(atom, baseindex)
                else:
                    after_stuff.see(atom, baseindex)
            continue
        assert not before
        
        ###e now find new_atom (and index offset) from that info (in *_stuff and old_atom_index)
        # note: no guarantee any atoms were live, so either or both stuffs might be empty of atoms;
        # if not empty, they might have found the same atom as first and last, or not.
        # For now, just use default behavior -- later some user-settings will affect this.
        # Default behavior: move towards lower-numbered bases, or if that fails, towards higher;
        # mark self as needing user confirmation (not urgently), no index offset.
        # But how do we know which direction is towards lower-numbered bases? Maybe something else set a chain base direction?
        # for now, kluge it by comparing atom key? but we'll need this direction info elsewhere too... need it to be on the chain.
        # and it might not be preserved from one chain to a new one. (can the chains just reverse their lists to standardize it??)

        # create the list of other atoms to look at, in order.
        # our variables are lists of atom, index pairs.
        before_look = before_stuff.atom_index_pairs()
        after_look = after_stuff.atom_index_pairs()
        if old_chain.ringQ:
            # we're looking before first, so just put everything before [todo: clarify that comment]
            lookat = after_look + before_look # in base index order, but relative to old_atom around ring
            lookat.reverse() # in looking order (last atom before old_atom is looked at first)
        else:
            lookat = reversed_list(before_look) + after_look #e do we also need to record in which of these lists we find the answer?

        new_atom, old_index_of_new_atom = None, None
        
        for atom, index in lookat:
            # note: lookat might be empty; if not, for now we use
            # only the first element
            new_atom, old_index_of_new_atom = atom, index
            break
                # (in future we might decide if this atom is good enough
                #  in some way, and continue if not)

        # didit will be set to true below if possible:
        didit = False # whether we succeed in moving to a valid new location

        if new_atom is not None:
            didit = self._move_to_this_atom(new_atom)
            #e pass index offset, or info to compute it? or compute it
            # in this method now, or before this line?

        if didit:
            # save info to move direction onto new chain
            # (possible optim: only save a few indices in the dict --
            #  for now I assume it's not worthwhile, we'll die soon anyway...
            #  to do it, we'd only save old_index_to_atom_dict items whose
            #  index (key) was old_index_of_new_atom + one of (-1,0,1))
            self._info_for_step2 = new_atom, old_index_to_atom_dict, old_index_of_new_atom, old_chain
        else:
            # in future this will depend on settings:
            self.kill()
        return didit
    
    def _f_move_to_live_atom_step2(self, new_chain_info): #e todo: split docstring
        """
        [friend method, called from dna_updater]
        Our atom died; see if there is a live atom on our old chain which we want to move to;
        if so, move to the best one (updating all our properties accordingly) and return True;
        if not, die and return False.
        """
        
        # will be set to 1 or -1 below if possible:
        advise_new_chain_direction = 0
            # base index direction to advise new chain to take
            # (-1 or 1, or 0 if we don't know)

        new_atom, old_index_to_atom_dict, old_index_of_new_atom, old_chain = self._info_for_step2
        del self._info_for_step2
        assert new_atom is self.atoms[0] #k
        assert old_chain is self._chain # guess true now, but remove when works if not required, as i think
        
        reldir = self.compute_new_chain_relative_direction(
            new_atom,
            new_chain_info,
            old_index_to_atom_dict,
            old_index_of_new_atom
         )
        advise_new_chain_direction = reldir * old_chain.index_direction # can be 0 or -1 or 1

        #e if that method didn't guess a direction, we could decide to die here
        # (didit = False), but for now we don't... in future this will depend on settings:
        didit = True
            
        if didit:
            self._advise_new_chain_direction = advise_new_chain_direction ### @@@ USE ME
        else:
            self.kill()
        return didit
    
    def _move_to_this_atom(self, atom): #e arg for index change too?
        #e assert correct kind of atom, for a per-subclass kind... call a per-subclass atom_ok function?
        self._set_marker_atom(atom)
        #e other updates (if not done by submethod)?
        #e set a flag telling the user to review this change, if settings ask us to... (or let caller do this??)
        return True

    def compute_new_chain_relative_direction(self,
                                             new_atom,
                                             new_chain_info,
                                             old_index_to_atom_dict,
                                             old_index_of_new_atom
                                            ): #e fill in param info in docstring
        """
        Figure out what base direction to advise our new chain to adopt,
        relative to its current one,
        if we can and in case we're asked to advise it later.

        @param new_atom:
        @type new_atom: atom
        
        @param new_chain_info:
        @type new_chain_info: dict from ...
        
        @param old_index_to_atom_dict: dict from old chain baseindex to atom,
                                       including at least new_atom and its old
                                       immediate neighbors, and as many more
                                       atoms (with old baseindices on the same
                                       old self.chain_or_ring) as you want
        @type old_index_to_atom_dict: dict (int to atom)
        
        @param old_index_of_new_atom:
        @type old_index_of_new_atom: int
        
        @return: base index direction to advise new chain to take (-1 or 1, or 0 if we don't know)

        Do this by figuring out how the old
        chain's base direction maps onto the new one's, if any bases adjacent
        in the old chain are still adjacent in the new one. Record the result
        as a sign, relative to the *current* direction of the new chain.
        (If it's direction is flipped, we are not notified, but its index_direction
         will be reversed at the same time, so our stored sign, relative to that,
         will remain correct. This assumes that reversing a chain reverses both
         its .index_direction and the visible order of its atoms, at the same time.) ### REVIEW this point when done
        """
        
        # implem notes:
        # old_atom is not relevant here at all, i think -- for old direction we look at old indexes around new atom.
        # new_atom and its both-newly-and-oldly-adjacent atoms are the only ones relevant to look at here;
        # for each such atom (at most 2, not counting new_atom) we just compare its index delta in old and new info.
        # if they disagree, we can either give up, or favor the one in the old direction the marker moved. [for now: latter.]
        # if the latter, we can just pick the first old-and-new-adj atom to look at, and use it.
        # we can test an atom for old-adjacent during our scan... not sure... maybe we want a dict
        # for old_chain_info which has index as key, only for old_chain? yes. we pass it in.
        
        new_atom_new_info = new_chain_info[new_atom.key]
        new_atom_new_chain_id, new_atom_new_index = new_atom_new_info

        assert old_index_to_atom_dict[old_index_of_new_atom] is new_atom
        for try_this_old_index in (old_index_of_new_atom + 1, old_index_of_new_atom - 1): #e maybe only pass in this much info?
            # note: we do this in order of which result we'll use,
            # so we can use the first result we get.
            # The order of +1 / -1 really depends on the old direction in which the marker wants to move.
            # In future that will be a setting, and it's hardcoded in at least one other place besides here.
            ### FIX SOON, for 2nd strand marker -- when adding new markers, try to add to left edge of axis & 2 strands
            # and have them move in same way on each. Hmm, that doesn't require this variable, it's still forward
            # in base index if we assume that's same on the two strands from this point... if it's not it's probably user-set.
            # but if 2nd strand has direction but no marker, do we add a backwards marker there? I doubt that can happen... we'll see.
            try:
                try_this_old_atom = old_index_to_atom_dict[try_this_old_index]
                info = new_chain_info[try_this_old_atom.key]
            except KeyError: # from either of the two lookups
                pass
            else:
                new_chain_id, new_index = info
                # is the trial atom in the same new chain, at an adjacent index?
                if new_chain_id == new_atom_new_chain_id:
                    new_index_delta = new_index - new_atom_new_index # could be anything except 0
                    assert new_index_delta != 0
                    assert type(new_index_delta) == type(1)
                    if new_index_delta in (-1,1):
                        old_index_delta = try_this_old_index - old_index_of_new_atom
                        assert old_index_delta in (-1,1) # by construction
                        res = new_index_delta / old_index_delta
                        assert res in (-1,1) # a fact of math (and that the '/' operator works right)
                        return res
                            # note: relative to current direction, which we
                            # don't know in this method and which might not be 1
        return 0

# pseudocode i didn't need, remove after commit:
##        some_atoms = ...
##
##        for atom in some_atoms:
##            try:
##                old_chain_id, old_index = old_chain_info[atom.key]
##                new_chain_id, new_index = new_chain_info[atom.key]
##            except KeyError:
##                pass
##            else:
##                assert old_chain_id == old_chain.chain_id() # or, the same as for old_atom
##                if new_chain_id == same as for new_atom:
##                    hmm.append( (old_index, new_index) )
##        if len(hmm) > 1:
##            # we have enough info for a guess; make sure it's consistent!
##            
##        return -1 or 1 }
    
    pass # end of class DnaAtomMarker

#e subclasses for SegmentMarker & StrandMarker??

# end
