# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaMarker.py - marked positions on atom chains, moving to live atoms as needed

Used internally for base indexing in strands and segments; perhaps used in the
future to mark subsequence endpoints for relations or display styles.

    WARNING: this code [as of 080115] is broken and is being heavily revised,
    since the marker really needs to
    be on a higher-level WholeChain which covers multiple AtomChainOrRings.


@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_model.ChainAtomMarker import ChainAtomMarker

from dna_model.DnaStrand import DnaStrand
from dna_model.DnaSegment import DnaSegment
from dna_model.DnaGroup import DnaGroup

from dna_updater.dna_updater_constants import DEBUG_DNA_UPDATER
from dna_updater.dna_updater_constants import DEBUG_DNA_UPDATER_VERBOSE

from drawer import drawwirecube

from debug import print_compact_stack

# ==

# constants

_CONTROLLING_IS_UNKNOWN = True # represents an unknown value of self.controlling
    # note: this value of True is not strictly correct, but simplifies the code
    #e rename?

# ==

# globals and their accessors

_marker_newness_counter = 1

_homeless_dna_markers = {}

def _f_get_homeless_dna_markers(): # MISNAMED, see is_homeless docstring. Maybe rename to end "markers_that_need_update"?
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

_superclass = ChainAtomMarker

class DnaMarker( ChainAtomMarker):
    """
    A ChainAtomMarker specialized for DNA axis or strand atoms
    (base atoms only, not Pl atoms).

    Abstract class; see subclasses DnaSegmentMarker and
    DnaStrandMarker.

    Description of how this object stays updated in various situations: ### UPDATE after details are coded @@@

    When read from an mmp file, or copied, it is valid but has no
    cached chain, etc... these will be added when the dna updater
    creates a new chain and ladder and one of these "takes over
    this marker". Part of that "takeover" is for self to record info
    so next_atom is not needed for understanding direction, or anything
    else about the chain self is presently on, since that chain might
    not be valid when self later needs to move along it.
    (This info consists of self's index (which rail and where) and direction
     in a DnaLadder.)

    After copy, in self.fixup_after_copy(), ... ### NIM; spelling? (check atom order then, and record info so next_atom not needed) @@@

    After Undo, our _undo_update method will arrange for equivalent
    checks or updates to be done... ### REVIEW, IMPLEM (also check atom order then, and record info so next_atom not needed) @@@

    If our marker atom dies, self.remove_atom() records this so the
    dna updater will move self to a new marker atom, and make sure
    the new (or preexisting) chain/ladder there takes over self. ### DOIT for preexisting -- can happen! @@@
    (We have a wholechain which can't be preexisting after we're moved,
     but our ladder and its ladder rail chain can be.)

    If our next_atom dies or becomes unbonded from our marker_atom,
    but our marker_atom remains alive, we can probably stay put but
    we might need a new direction indicator in place of next_atom.
    The dna updater handles this too, as a special case of "moving us".
        ### REVIEW, does it work? what call makes this happen? has to come out of changed_atoms, we might not be "homeless" @@@

    After any of these moves or other updates, our marker_atom and next_atom
    are updated to be sufficient when taken alone to specify our
    position and direction on a chain of atoms. This is so those attrs
    are the only ones needing declaration for undo/copy/save for that purpose.
    
    We also maintain internal "cached" attrs like our index within a ladder,
    for efficiency and to help us move when those atoms become killed or
    get changed in other ways.
    """
    ### REVIEW: what if neither atom is killed, but their bonding changes?
    # do we need to look for marker jigs on changed atoms
    # and treat them as perhaps needing to be moved? YES. DOIT. #### @@@@
    # [same issue as in comment in docstring "we might not be homeless"]

    
    # Jig or Node API class constants:
    
    sym = "DnaMarker" # ?? maybe used only on subclasses for SegmentMarker & StrandMarker? maybe never visible?
        # TODO: not sure if this gets into mmp file, but i suppose it does... and it gets copied, and has undoable properties...
        # and in theory it could appear in MT, though in practice, probably only in some PM listwidget, but still,
        # doing the same things a "visible node" can do is good for that.

    # we'll define mmp_record_name differently in each subclass
    ## mmp_record_name = "DnaMarker" # @@@@ not yet read; also the mmp format might be verbose (has color)

    # icon_names = ("missing", "missing-hidden")
    icon_names = ('border/dna.png', 'border/dna.png') # stubs; not normally seen for now
    
    copyable_attrs = _superclass.copyable_attrs + ()
        # todo: add some more -- namely the user settings about how it moves, whether it lives, etc


    # future user settings, which for now are per-subclass constants:

    control_priority = 1

    _wants_to_be_controlling = True # class constant; false variant is nim


    # default values of instance variables:

    wholechain = None
    
    controlling = _CONTROLLING_IS_UNKNOWN

    _owning_strand_or_segment = None

    _advise_new_chain_direction = 0 ###k needed??? @@@
        # temporarily set to 0 or -1 or 1 for use when moving self and setting a new chain

    _newness = None
    
    # guess: also needs a ladder, and indices into the ladder (which rail, rail/chain posn, rail/chain direction)@@@@
    
# suspect not needed 080116 @@@
##    _chain = None # (not undoable or copyable)


    # == Jig or Node API methods (overridden or extended from ChainAtomMarker == _superclass):

    def __init__(self, assy, atomlist): #####, chain = None):
##        # [can chain be None after we get copied? I think so...]
##        # (chain arg is not needed in _um_initargs since copying it can/should make it None. REVIEW, is that right? ###]
        """
##        @param chain: the atom chain or ring which we reside on when created (can it be None??)
##        @type chain: AtomChainOrRing instance ### REVIEW
        """
        _superclass.__init__(self, assy, atomlist)
##        if chain is not None:
##            self.set_chain(chain) ### prob not needed @@@@
        global _marker_newness_counter
        _marker_newness_counter += 1
        self._newness = _marker_newness_counter
        if DEBUG_DNA_UPDATER_VERBOSE: # made verbose on 080201
            print "dna updater: made %r" % (self,)
        return

    def kill(self):
        """
        Extend Node method, for debugging and for notifying self.wholechain
        """
        if DEBUG_DNA_UPDATER:
            msg = "dna updater: killing %r" % (self,)
            print msg
        if self.wholechain:
            self.wholechain._f_marker_killed(self)
            self.wholechain = None
        # review: what about self._owning_strand_or_segment? @@@
        _superclass.kill(self)
        return
    
    def _draw_jig(self, glpane, color, highlighted = False):
        """
        [overrides superclass method]
        """
        from constants import orange
        for a in self.atoms:
            chunk = a.molecule
            dispdef = chunk.get_dispdef(glpane)
            disp, rad = a.howdraw(dispdef)
            if self.picked:
                rad *= 1.01
            drawwirecube(color, a.posn(), rad)
            # draw next_atom in a different color than marked_atom (sp?)
            color = orange # this is what differs from superclass

    # ==
    
    def get_oldness(self):
        """
        Older markers might compete better for controlling their wholechain;
        return our "oldness" (arbitrary scale, comparable with Python standard
        ordering).
        """
        return (- self._newness)
    
    def wants_to_be_controlling(self):
        return self._wants_to_be_controlling
    
    def set_wholechain(self, wholechain, controlling = _CONTROLLING_IS_UNKNOWN):
        """
        [to be called by dna updater]
        @param wholechain: a new WholeChain which owns us (not None)
        """
        assert wholechain
        self.wholechain = wholechain
        self.set_whether_controlling(controlling) # might kill self

    def forget_wholechain(self, wholechain):
        """
        Remove any references we have to wholechain.
        
        @param wholechain: a WholeChain which refs us and is being destroyed
        """
        assert wholechain
        if self.wholechain is wholechain:
            self.wholechain = None
            # review: also do self.set_whether_controlling(False)?? @@@
        return

    def _undo_update(self): # in class DnaMarker
        """
        """
        print "bug: undo_update is partly nim in %r" % self ### @@@@
        _homeless_dna_markers[id(self)] = self # ok?? sufficient?? [080118]

    def remove_atom(self, atom):
        """
        [extends superclass method]
        """
        _homeless_dna_markers[id(self)] = self # TODO: also do this when copied? not sure it's needed.
        _superclass.remove_atom(self, atom)
        return

    def changed_structure(self, atom): # 080118
        """
        [extends superclass method]
        """
        # (we extend this method so that if bonds change so that marked_atom and
        #  next_atom (sp?) are no longer next to one another, we'll get
        #  updated as needed.)
        _homeless_dna_markers[id(self)] = self
        _superclass.changed_structure(self, atom)
        return
        
    #e also add a method [nim in api] for influencing how we draw the atom?
    # guess: no -- might be sufficient (and is better, in case old markers lie around)
    # to just use the Jig.draw method, and draw the marker explicitly. Then it can draw
    # other graphics too, be passed style info from its DnaGroup/Strand/Segment, etc.

    # == ChainAtomMarker API methods (overridden or extended):

    # == other methods

# I suspect this is not needed 080116
##    def set_chain(self, chain): ### REVIEW, revise docstring. @@@@
##        """
##        A new chain
##            AtomChainOrRing object?? wholechain?? more args??
##        is taking us over (but we'll stay on the same atom).
##        (Also called during __init__ to set our initial chain.)
##
##        @param chain: the atom chain or ring which we now reside on (can't be None)
##        @type chain: AtomChainOrRing instance ### REVIEW
##        """
##        ## was: ChainAtomMarker.set_chain(self, chain)
##        assert not self.is_homeless()
##        #e assert chain contains self._get_marker_atom()?
##        assert chain is not None # or should None be allowed, as a way of unsetting it??
##        self._chain = chain
##
##        self.controlling = _CONTROLLING_IS_UNKNOWN

    def get_DnaGroup(self):
        """
        Return the DnaGroup we are contained in, or None if we're not
        inside one.

        @note: if we are inside a DnaStrand or DnaSegment, then our
        DnaGroup will be the same as its DnaGroup. But we can be outside
        one (if this is permitted) and still have a DnaGroup.
        
        @note: returning None should never happen
        if we have survived a run of the dna updater.

        @see: get_DnaStrand, get_DnaSegment
        """
        return self.parent_node_of_class( DnaGroup)

    def _get_DnaStrandOrSegment(self):
        """
        [private]
        Non-friend callers should instead use the appropriate
        method out of get_DnaStrand or get_DnaSegment.
        """
        return self.parent_node_of_class( DnaStrandOrSegment)
        
    def _f_get_owning_strand_or_segment(self):
        """
        [friend method for dna updater]
        Return the DnaStrand or DnaSegment which owns this marker,
        or None if there isn't one,
        even if the internal Node tree structure (node.dad)
        has not yet been updated to reflect this properly
        (which may only happen when self is homeless).

        Note: non-friend callers (outside the dna updater, and not running
        just after creating this before the updater has a chance to run
        or gets called explicitly) should instead use the appropriate
        method out of get_DnaStrand or get_DnaSegment.
        """
        # fyi - used in WholeChain.find_or_make_strand_or_segment
        return self._owning_strand_or_segment

    def _f_set_owning_strand_or_segment(self, strand_or_segment):
        """
        [friend method for dna updater]
        """
        self._owning_strand_or_segment = strand_or_segment
        
    # ==
    
    def set_whether_controlling(self, controlling):
        """
        our new chain tells us whether we control its atom indexing, etc, or not
        [depending on our settings, we might die or behave differently if we're not]
        """
        self.controlling = controlling
        if not controlling and self.wants_to_be_controlling():
            self.kill() # in future, might depend more on user-settable properties and/or on subclass
        return
    
    def _f_move_to_live_atom_step1(self): #e todo: split docstring; ### FIX/REVIEW/REFILE/REPLACE - move into WholeChain or smallchain? @@@
        """
        [friend method, called from dna_updater]
        Our atom died; see if there is a live atom on our old chain which we want to move to;
        if so, move to the best one (updating all our properties accordingly) and return True;
        if not, die and return False.

        @return: whether this marker is still alive after this method runs.
        @rtype: boolean
        """

        if 'SAFETY STUB 080118': # @@@@
            print "kill %r since move step1 is nim" % self ##### @@@@
            self.kill()
            return False
        
        # Algorithm -- just find the nearest live atom in the right direction.
        # Do this by scanning old atom lists in chain objects known to markers,
        # so no need for per-atom stored info.
        # [Possible alternative (rejected): sort new atoms for best new home -- bad,
        #  since requires storing that info on atoms, or lots of lookup.]

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
            """
            Track first & last live atom seen during some subsection of the chain.
            (If exactly one atom is seen, those will be the same.)
            (Only live atoms should be passed to self.see(atom, index).)
            """
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
            # (only makes sense since we iterate over baseindices in order)

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
    
    def _f_move_to_live_atom_step2(self, new_chain_info): #e todo: split docstring ### FIX/REVIEW/REFILE/REPLACE @@@
        """
        [friend method, called from dna_updater]
        Our atom died; see if there is a live atom on our old chain which we want to move to;
        if so, move to the best one (updating all our properties accordingly) and return True;
        if not, die and return False.
        """
        # this will be set to 1 or -1 below if possible:
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
    
    def _move_to_this_atom(self, atom): #e arg for index change too?   ### FIX/REVIEW/REFILE/REPLACE @@@
        #e assert correct kind of atom, for a per-subclass kind... call a per-subclass atom_ok function?
        self._set_marker_atom(atom)
        #e other updates (if not done by submethod)?
        #e set a flag telling the user to review this change, if settings ask us to... (or let caller do this??)
        return True

    def compute_new_chain_relative_direction(self,   ### FIX/REVIEW/REFILE/REPLACE @@@
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

    def DnaStrandOrSegment_class(self):
        return self._DnaStrandOrSegment_class
    pass # end of class DnaMarker

# ==

class DnaSegmentMarker(DnaMarker): #e rename to DnaAxisMarker? guess: no...
    """
    A kind of DnaMarker for marking an axis atom of a DnaSegment
    (and, therefore, a base-pair position within the segment).
    """
    _DnaStrandOrSegment_class = DnaSegment
    featurename = "Dna Segment Marker" # might never be visible
    mmp_record_name = "DnaSegmentMarker" # @@@@ not yet read
    def get_DnaSegment(self):
        """
        Return the DnaSegment that owns us, or None if none does.
        [It's not yet decided whether the latter case can occur
        normally if we have survived a run of the dna updater.]

        @see: self.controlling, for whether we control base indexing
        (and perhaps other aspects) of the DnaSegment that owns us.

        @see: get_DnaGroup
        """
        res = self._get_DnaStrandOrSegment()
        assert isinstance(res, DnaSegment)
        return res
    pass

# ==

class DnaStrandMarker(DnaMarker):
    """
    A kind of DnaMarker for marking an atom of a DnaStrand
    (and, therefore, a base position along the strand).
    """
    _DnaStrandOrSegment_class = DnaStrand
    featurename = "Dna Strand Marker" # might never be visible
    mmp_record_name = "DnaStrandMarker" # @@@@ not yet read
    def get_DnaStrand(self):
        """
        Return the DnaStrand that owns us, or None if none does.
        [It's not yet decided whether the latter case can occur
        normally if we have survived a run of the dna updater.]

        @see: self.controlling, for whether we control base indexing
        (and perhaps other aspects) of the DnaStrand that owns us.

        @see: get_DnaGroup
        """
        res = self._get_DnaStrandOrSegment()
        assert isinstance(res, DnaStrand)
        return res
    pass

# end
