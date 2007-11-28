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
    
    def _f_move_to_live_atom(self):
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
        
        chain = self._chain
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
            first_index = -1
            last_atom = None
            last_index = -1
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
        
        old_atom_index = -1
        
        baseindex = 0 # incremented for base atoms during loop; found indices will start at 1
        before = True # changed to False when we find old_atom during loop

        atom_list = chain.atom_list
        if chain.index_direction < 0: ### IMPLEM, -1 or 1... better if we can get chain to reverse the list when it's made ###
            # do this now, so our baseindex counter is in the right order
            atom_list = reversed_list(atom_list)
        
        for atom in atom_list: # in order for chain (arb direction), or ring (arbitrary origin & direction)
            #e or call chain method to do this search? faster using atom dict? or it might know atom -> index...
            if not atom.element.sym.startswith('P'): # KLUGE, should use an element attribute, whether it's base-indexed
                baseindex += 1
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
# do this earlier, so baseindex is correct:
##        if chain.index_direction < 0: ### IMPLEM, -1 or 1
##            before_look.reverse()
##            after_look.reverse()
##            before_look, after_look = after_look, before_look
        if chain.ringQ:
            # we're looking before first, so just put everything before [todo: clarify that comment]
            lookat = after_look + before_look # in base index order, but relative to old_atom around ring
            lookat.reverse() # in looking order (last atom before old_atom is looked at first)
        else:
            lookat = reversed_list(before_look) + after_look #e do we also need to record in which of these lists we find the answer?

        newatom, newindex = None, -1
        
        for atom, index in lookat: # might be empty
            newatom, newindex = atom, index
            ok = True # this atom ok? (not sure if this can ever be false in future...)
            if ok:
                break
            continue
        
        if newatom is None:
            didit = False
        else:
            didit = self._move_to_this_atom(newatom) #e pass index offset, or info to compute it?
        if not didit:
            self.kill()
        return didit
    
    def _move_to_this_atom(self, atom): #e arg for index change too?
        #e assert correct kind of atom, for a per-subclass kind... call a per-subclass atom_ok function?
        self._set_marker_atom(atom)
        #e other updates (if not done by submethod)?
        #e set a flag telling the user to review this change, if settings ask us to... (or let caller do this??)
        return True
    
    pass

#e subclasses for SegmentMarker & StrandMarker??

# end
