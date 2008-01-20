# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaLadder.py - ... 

Used internally; may or may not be a Node, though some kinds
of Chunk might own a ladder or "ladder rail".

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

Context:

The PAM atoms in any PAM DNA structure will be internally divided into
"ladders", in which all the bonding strictly follows the pattern

 ... -+-+-+-+-+-+- ... (strand 1)
      | | | | | | 
 ... -+-+-+-+-+-+- ... (axis)
      | | | | | | 
 ... -+-+-+-+-+-+- ... (strand 2; missing if single-stranded)

(with the strand bond directions antiparallel and standardized).

The dna updater will maintain these ladders, updating them
when their structure is changed. So a changed atom in a ladder will
either dissolve or fragment its ladder (or mark it for the updater to
do that when it next runs), and the updater, dealing with all changed
atoms, will scan all the atoms not in valid ladders to make them into
new ladders (merging new ladders end-to-end with old ones, when that's
valid, and whe they don't become too long to be handled efficiently).

A Dna Segment will therefore consist of a series of ladders (a new one
at every point along it where either strand has a nick or crossover,
or at other points to make it not too long). Each "ladder rail"
(one of the three horizontal atom-bond chains in the figure")
will probably be a separate Chunk, though the entire ladder should
have a single display list for efficiency (so its rung bonds are
in a display list) as soon as that's practical to implement.

So the roles for a ladder include:
- guide the dna updater in making new chunks
- have display code and a display list

A ladder will be fully visible to copy and undo (i.e. it will
contain undoable state), but will not be stored in the mmp file.
"""

from bond_constants import atoms_are_bonded

from dna_model.DnaChain import merged_chain

from dna_model.DnaLadderRailChunk import DnaAxisChunk, DnaStrandChunk
    # note: if these imports are an issue, they could be moved
    # to a controller class, since they are needed only by remake_chunks method

from dna_updater.dna_updater_constants import DEBUG_DNA_UPDATER
from dna_updater.dna_updater_constants import DEBUG_DNA_UPDATER_VERBOSE

from dna_model.dna_model_constants import LADDER_ENDS
from dna_model.dna_model_constants import LADDER_END0
from dna_model.dna_model_constants import LADDER_END1
from dna_model.dna_model_constants import LADDER_BOND_DIRECTION_TO_OTHER_AT_END_OF_STRAND1

from dna_model.dna_model_constants import MAX_LADDER_LENGTH # @@@@ TODO: also use this to split long ladders

# ==

# globals and accessors

_invalid_dna_ladders = {}

def _f_get_invalid_dna_ladders():
    """
    Return the invalid dna ladders,
    and clear the list so they won't be returned again
    (unless they are newly made invalid).

    Friend function for dna updater. Other calls
    would cause it to miss newly invalid ladders,
    causing serious bugs.
    """
    res = _invalid_dna_ladders.values()
    _invalid_dna_ladders.clear()
    res = filter( lambda ladder: not ladder.valid, res ) # probably not needed
    return res

# ==

### REVIEW: should a DnaLadder contain any undoable state?
# (guess: yes... maybe it'll be a Group subclass, for sake of copy & undo?
#  for now, assume just an object (not a Node), and try to fit it into
#  the copy & undo code in some other way... or I might decide it's entirely
#  implicit re them.) If that gets hard, make it a Group. (Where in the internal MT?
#  whereever the chunks would have been, without it.)

class DnaLadder(object):
    """
    [see module docstring]
        
    @note: a valid ladder is not always in
    correspondence with atom chunks for its rails
    (since the chunks are only made or fixed after ladder merging),
    so the methods in self can't find an atom's ladder via atom.molecule.
    Instead we assume that no atom is in more than one valid ladder
    at a time, and set a private atom attribute to point to that ladder.
    """
    valid = False # public for read, private for set; whether structure is ok and we own our atoms
    error = False # ditto; whether num_strands or strand bond directions are wrong (parallel) # todo: use more?
    def __init__(self, axis_rail):
        self.axis_rail = axis_rail
        self.assy = axis_rail.baseatoms[0].molecule.assy #k
        self.strand_rails = []
    def baselength(self):
        return len(self.axis_rail)
    def __len__(self):
        return self.baselength()
    def add_strand_rail(self, strand_rail): # review: _f_, since requires a lot of calling code?
        """
        This is called while constructing a dna ladder (self)
        which already has an axis rail and 0 or 1 strand rails.
        
        Due to how the calling code works, it's guaranteed
        that the atomlist in the new strand rail corresponds to that
        in the existing axis rail, either directly or in reverse order --
        even if one or both of those rails is a ring rather than a chain.
        (That is, it's never necessary to "rotate a ring" to make this
        alignment possible. The caller splits rings into chains if
        necessary to avoid this need.)
        We depend on this and assert it, in self.finished().
        """
        assert strand_rail.baselength() == self.axis_rail.baselength(), \
               "baselengths in %r don't match: %r (%d) != %r (%d)" % \
               (self,
                strand_rail,
                strand_rail.baselength(),
                self.axis_rail,
                self.axis_rail.baselength())
        self.strand_rails.append(strand_rail)
        return
    def finished(self): # note: only for the subclass with axis_rail present [todo: split this class]
        """
        This is called once to signify that construction of self is done
        as far as the caller is concerned (i.e. it's called add_strand_rail
        all the times it's going to), and it should be finished internally.
        This involves reversing rails as needed to make their baseatoms
        correspond (so each base pair's 3 PAM atoms (or each lone base's 2 PAM atoms)
        has one atom per rail, at the same relative baseindex),
        and perhaps(?) storing pointers at each rail-end to neighboring rails.
        See add_strand_rail docstring for why optional reversing is sufficient,
        even when some rails are rings.
        """
        assert not self.valid # not required, just a useful check on the current caller algorithm
        ## assert len(self.strand_rails) in (1, 2)
        # happens in mmkit - leave it as just a print at least until we implem "delete bare atoms" -
        if not ( len(self.strand_rails) in (1, 2) ):
            print "error: DnaLadder %r has %d strand_rails " \
                  "(should be 1 or 2)" % (self, len(self.strand_rails))
            self.error = True
        axis_rail = self.axis_rail
        # make sure rungs are aligned between the strand and axis rails
        # (note: this is unrelated to their index_direction,
        #  and is not directly related to strand bond direction)
        # (note: it's trivially automatically true if our length is 1;
        #  the following alg does nothing then, which we assert)
        axis_left_end_baseatom = axis_rail.end_baseatoms()[LADDER_END0]
        for strand_rail in self.strand_rails:
            if strand_rail.end_baseatoms()[LADDER_END0].axis_neighbor() is not axis_left_end_baseatom:
                # we need to reverse that strand
                # (note: we might re-reverse it below, if bond direction wrong)
                assert strand_rail.end_baseatoms()[LADDER_END1].axis_neighbor() is axis_left_end_baseatom
                assert self.baselength() > 1 # shouldn't happen otherwise
                strand_rail.reverse_baseatoms()
                assert strand_rail.end_baseatoms()[LADDER_END0].axis_neighbor() is axis_left_end_baseatom
            continue
        del axis_left_end_baseatom # would be wrong after the following code
        self._finish_strand_rails()
        return
    def _finish_strand_rails(self): # also used in DnaSingleStrandDomain
        """
        verify strand bond directions are antiparallel, and standardize them;
        then self.set_valid()
        (note there might be only the first strand_rail;
         this code works even if there are none)
        """
        for strand_rail in self.strand_rails:
            if strand_rail is self.strand_rails[0]:
                desired_dir = 1
                reverse = True # if dir is wrong, reverse all three rails
            else:
                desired_dir = -1
                reverse = False # if dir is wrong, error
                    # review: how to handle it in later steps? mark ladder error, don't merge it?
            have_dir = strand_rail.bond_direction() # 1 = right, -1 = left, 0 = inconsistent or unknown
                # @@@ IMPLEM note - this is implemented except for merged ladders; some bugs for length==1 chains.
                # strand_rail.bond_direction must check consistency of bond
                # directions not only throughout the rail, but just after the
                # ends (thru Pl too), so we don't need to recheck it for the
                # joining bonds as we merge ladders. BUT as an optim, it ought
                # to cache the result and use it when merging the rails,
                # otherwise we'll keep rescanning rails as we merge them. #e
            if have_dir == 0:
                print "error: %r strand %r has unknown or inconsistent bond " \
                      "direction - response is NIM(bug)" % (self, strand_rail) #### @@@ response is NIM (BUG)
                self.error = True
                reverse = True # might as well fix the other strand, if we didn't get to it yet
            else:
                if have_dir != desired_dir:
                    if strand_rail.bond_direction_is_arbitrary():
                        strand_rail._f_reverse_arbitrary_bond_direction()
                        have_dir = strand_rail.bond_direction() # only needed for assert
                        assert have_dir == desired_dir
                    elif reverse:
                        for rail in self.all_rails(): # works for ladder or single strand domain
                            rail.reverse_baseatoms()
                    else:
                        print "error: %r strands have parallel bond directions"\
                              " - response is NIM(bug)" % self #### @@@ response is NIM (BUG); split into two single strands??
                        self.error = True
                        # should we just reverse them? no, unless we use minor/major groove to decide which is right.
            continue
        self.set_valid(True)
    def num_strands(self):
        return len(self.strand_rails)
    def set_valid(self, val):
        if val != self.valid:
            self.valid = val
            if val:
                # tell the rail end atoms their ladder;
                # see _rail_end_atom_to_ladder for how this hint is interpreted
                for atom in self.rail_end_baseatoms():
                    # (could debug-warn if already set)
                    atom._DnaLadder__ladder = self
                    if DEBUG_DNA_UPDATER_VERBOSE:
                        print "%r owning %r" % (self, atom)
            else:
                # un-tell them
                for atom in self.rail_end_baseatoms():
                    # (could debug-warn if not set to self)
                    atom._DnaLadder__ladder = None
                    del atom._DnaLadder__ladder
                    if DEBUG_DNA_UPDATER_VERBOSE:
                        print "%r de-owning %r" % (self, atom)
                # tell the next run of the dna updater we're invalid
                _invalid_dna_ladders[id(self)] = self
        return
    def rail_end_baseatoms(self):
        """
        yield the 3 or 6 atoms which are end-atoms for one of our 3 rails,
        in arbitrary order #k
        """
        for rail in self.all_rails():
            # note: rail is a DnaChain, not a DnaLadderRailChunk!
            atom1, atom2 = rail.end_baseatoms()
            yield atom1
            if atom2 is not atom1:
                yield atom2
        return
# superceded by rail.neighbor_baseatoms:
##    def neighboring_ladder_rail_end_atoms(self): # might use this in "make new wholechains on modified_valid_ladders" 080114
##        """
##        Yield the 0 to 6 pairs (our rail end atom, neighboring other-ladder end atom)
##        (or equivalent info using rail & end indices??)
##        showing how our rails connect to other ladder rails,
##        or to None when they end.
##        If we are length 1, use arbitrary left-right choice for axis.(?)
##        """
##        nim
        
    def invalidate(self):
        # note: this is called from dna updater and from
        # DnaLadderRailChunk.delatom, so changed atoms inval their
        # entire ladders
        self.set_valid(False)

    # == ladder-merge methods
    
    def can_merge(self):
        """
        Is self valid, and mergeable (end-end) with another valid ladder?

        @return: If no merge is possible, return None; otherwise, for one
                 possible merge (chosen arbitrarily if more than one is
                 possible), return the tuple (other_ladder, merge_info)
                 where merge_info is private info to describe the merge.
        """
        if not self.valid or self.error:
            return None # not an error
        for end in LADDER_ENDS:
            other_ladder_and_merge_info = self._can_merge_at_end(end) # might be None
            if other_ladder_and_merge_info:
                return other_ladder_and_merge_info
        return None
    def do_merge(self, other_ladder_and_merge_info):
        """
        Caller promises that other_ladder_and_merge_info was returned by
        self.can_merge() (and is not None).
        Do the specified permitted merge (with another ladder, end to end,
        both valid).
        
        Invalidate the merged ladders; return the new valid ladder
        resulting from the merge.
        """
        other_ladder, merge_info = other_ladder_and_merge_info
        end, other_end = merge_info
        return self._do_merge_with_other_at_ends(other_ladder, end, other_end)
    def _can_merge_at_end(self, end): # TODO: update & clean up docstring
        """
        Is the same valid other ladder attached to each rail of self
        at the given end (0 or 1), and if so, can we merge to it
        at that end (based on which ends of which of its rails
        our rails attach to)? (If so, return other_ladder_and_merge_info, otherwise None.)

        ### REVIEW (what's done now, what;s best): Note that self or the other ladder might
        be length==1 (in which case only end 0 is mergeable, as an
        arbitrary decision to make only one case mergeable), ### OR we might use bond_dir, then use both cases again
        and that the other ladder might only merge when flipped.
        
        Also note that bond directions (on strands) need to match. ### really? are they always set?
        
        TODO: Also worry about single-strand regions. [guess: just try them out here, axis ends are None, must match]
        """
        # algorithm:
        # use strand1 bond direction to find only possible other ladder
        # (since that works even if we're of baselength 1);
        # then if other ladder qualifies,
        # check both its orientations to see if all necessary bonds
        # needed for a merge are present. (Only one orientation can make sense,
        # given the bond we used to find it, but checking both is easier than
        # checking which one fits with that bond, especially if other or self
        # len is 1.)

        strand1 = self.strand_rails[0]
        end_atom = strand1.end_baseatoms()[end]
        assert self is _rail_end_atom_to_ladder(end_atom) # sanity check
        bond_direction_to_other = LADDER_BOND_DIRECTION_TO_OTHER_AT_END_OF_STRAND1[end]
        next_atom = end_atom.strand_next_baseatom(bond_direction = bond_direction_to_other)
        if next_atom is None:
            # end of the chain (since bondpoints are not baseatoms), or
            # inconsistent bond directions at or near end_atom
            # (report error??)
            return None
        other = _rail_end_atom_to_ladder(next_atom) # other ladder
        if other.error:
            return None
        # other.valid is checked in _rail_end_atom_to_ladder
        if other is self:
            return None
        if len(self) + len(other) > MAX_LADDER_LENGTH:
            return None
        # enable this optim once i verify it works without it: @@
        ## if self.num_strands() != other.num_strands():
        ##    return None # optimization
        # try each orientation for other ladder;
        # first collect the atoms to test for bonding to other
        our_end_atoms = self.end_atoms(end)
        for other_end in LADDER_ENDS:
            other_end_atoms = other.end_atoms(other_end)
                # note: .end_atoms returns a sequence of length 3,
                # with each element being a rail's end-atom or None for a missing rail;
                # the rail order is strand-axis-strand, which on the left is in
                # top to bottom order, but on the right is in bottom to top order.
                # strand1 is always present; strand2 is missing for either kind of
                # single strands; axis_rail is missing for free-floating single strands.
            still_ok = True
            for atom1, atom2, strandQ in zip(our_end_atoms, other_end_atoms, (True, False, True)):
                ok = _end_to_end_bonded(atom1, atom2, strandQ)
                if not ok:
                    still_ok = False
                    break
            if still_ok:
                # success
                merge_info = (end, other_end)
                other_ladder_and_merge_info = other, merge_info
                return other_ladder_and_merge_info
        return None
    def end_atoms(self, end):
        """
        Return a list of our 3 rail-end atoms at the specified end,
        using None for a missing atom due to a missing strand2 or axis_rail,
        in the order strand1, axis, strand2 for the left end,
        or the reverse order for the right end (since flipping self
        also reverses that rail order in order to preserve strand bond
        directions).
        """
        # note: top to bottom on left, bottom to top on right,
        # None in place of missing atoms for strand2 or axis_rail
        assert len(self.strand_rails) in (1,2)
        strand_rails = self.strand_rails + [None] # + [None] needed in case len is 1
        rails = [strand_rails[0], self.axis_rail, strand_rails[1]] # order matters
        def atom0(rail):
            if rail is None:
                return None
            return rail.end_baseatoms()[end]
        res0 = map( atom0, rails)
        if end != LADDER_END0:
            res0.reverse()
        return res0
    def __repr__(self):
        ns = self.num_strands()
        if ns == 2:
            extra = ""
        elif ns == 1:
            extra = " (single strand)"
        elif ns == 0:
            # don't say it's an error if 0, since it might be still being made
            extra = " (0 strands)"
        else:
            extra = " (error: %d strands)" % ns
        return "<%s at %#x, axis len %d%s>" % (self.__class__.__name__, id(self), self.axis_rail.baselength(), extra)
    def _do_merge_with_other_at_ends(self, other, end, other_end): # works in either class; when works, could optim for single strand
        """
        Merge two ladders, at specified ends of each one:
        self, at end, with other, at other_end.
        
        Invalidate the merged ladders; return the new valid ladder
        resulting from the merge.
        """
        if DEBUG_DNA_UPDATER:
            print "dna updater: fyi: _do_merge_with_other_at_ends(self = %r, other_ladder = %r, end = %r, other_end = %r)" % \
              (self, other, end, other_end)

        # algorithm: (might differ for subclasses)
        # - make merged rails (noting possible flip of each ladder)
        #   (just append lists of baseatoms)
        # - put them into a new ladder
        # - when debugging, could check all the same things that
        #   finished does, assert no change
        def rail_to_baseatoms(rail, flipQ):
            if not rail:
                return []
            elif not flipQ:
                return rail.baseatoms
            else:
                res = list(rail.baseatoms)
                res.reverse()
                return res
        flip_self = (end != LADDER_END1)
        flip_other = (other_end != LADDER_END0)
        self_baseatom_lists = [rail_to_baseatoms(rail, flip_self)
                               for rail in self.all_rail_slots_from_top_to_bottom()]
        other_baseatom_lists = [rail_to_baseatoms(rail, flip_other)
                               for rail in other.all_rail_slots_from_top_to_bottom()]
        if flip_self:
            self_baseatom_lists.reverse()
        if flip_other:
            other_baseatom_lists.reverse()
        # now (after flipping) we need to attach self END1 to other END0,
        # i.e. "self rail + other rail" for each rail.
        def concatenate_rail_atomlists((r1, r2)):
            assert (r1 and r2) or (not r1 and not r2)
            return r1 + r2
        new_baseatom_lists = map( concatenate_rail_atomlists,
                                  zip(self_baseatom_lists, other_baseatom_lists))
        # flip the result if we flipped self, so we know it defines a legal set of rails for a ladder
        # (todo: could optim by never flipping self, instead swapping ladders and negating both flips)
        if flip_self:
            new_baseatom_lists.reverse
            for i in len(new_baseatom_lists):
                new_baseatom_lists[i].reverse()
        # invalidate old ladders before making new rails or new ladder
        self.invalidate() # @@@@ ok at this stage?
        other.invalidate()
        # now make new rails and new ladder
        new_rails = [ _new_rail( baseatom_list, strandQ, bond_direction)
                      for baseatom_list, strandQ, bond_direction in
                      zip( new_baseatom_lists,
                           (True, False, True),
                           (1, 0, -1 ) # TODO: grab from a named constant?
                          ) ]
        new_ladder = _new_ladder(new_rails)
        if DEBUG_DNA_UPDATER:
            print "dna updater: fyi: merge results in %r" % (new_ladder,)
        return new_ladder

    # ==

    def all_rails(self):
        """
        Return a list of all our rails (axis and 1 or 2 strands), in arbitrary order,
        not including missing rails.
        [implem is subclass-specific]
        """
        return [self.axis_rail] + self.strand_rails
    
    def all_rail_slots_from_top_to_bottom(self):
        """
        Return a list of all our rails (axis and 1 or 2 strands), in top to bottom order,
        using None for missing rails.
        [implem is subclass-specific]
        """
        if len(self.strand_rails) == 2:
            return [self.strand_rails[0], self.axis_rail, self.strand_rails[1]]
        else:
            return [self.strand_rails[0], self.axis_rail, None]
    
    def remake_chunks(self):
        """
        #doc
        
        @return: list of all newly made (by this method) DnaLadderRailChunks
                 (or modified ones, if that's ever possible)
        """
        assert self.valid
        # but don't assert not self.error
        res = []
        for rail in self.all_rails():
            if rail is self.axis_rail:
                want_class = DnaAxisChunk
            else:
                want_class = DnaStrandChunk
            old_chunk = rail.baseatoms[0].molecule # from arbitrary atom in rail
            assy = old_chunk.assy
            assert assy is self.assy
            part = assy.part
            part.ensure_toplevel_group()
            group = old_chunk.dad # put new chunk in same group as old
                # (but don't worry about where inside it, for now)
            if group is None:
                # this happens for MMKit chunks with "dummy" in their names;
                # can it happen for anything else? should fix in mmkit code.
                if "dummy" not in old_chunk.name:
                    print "dna updater: why is %r.dad == None? (assy = %r)" % (old_chunk, assy) ###
                group = part.topnode
            assert group.is_group()
            chunk = want_class(assy, rail)
            if DEBUG_DNA_UPDATER_VERBOSE:
                print "%r.remake_chunks made %r" % (self, chunk)
            chunk.color = old_chunk.color # works, at least if a color was set
            #e put it into the model in the right place [stub - puts it in the same group]
            # (also - might be wrong, we might want to hold off and put it in a better place a bit later during dna updater)
            # also works: part.addnode(chunk), which includes its own ensure_toplevel_group
            group.addchild(chunk)
            # todo: if you don't want this location for the added node chunk,
            # just call chunk.moveto when you're done,
            # or if you know a group you want it in, call group.addchild(chunk) instead of this.
            res.append(chunk)
        return res
    
    pass # end of class DnaLadder

# ==

# @@@@@ review points:
# - we get added to _invalid_dna_ladders when something invals us... some of the ladder api from rest is really a DnaDomain api
# - a lot of things happening to ladders needs to happen to these but is NIM
class DnaSingleStrandDomain(DnaLadder):
    """
    Represent a free floating single strand domain;
    act somewhat like a ladder with no axis rail or second strand rail
    in terms of ability to interface with other code.
    """
    # TODO, should be sibling class -- these are both kinds of DnaDomains, and this has less not more than ladder;
    # maybe about half of ladder's code looks like it's common code (what's the right classname for the interface?
    # single or duplex domain? domain with some strands?)
    valid = False # same as in super; set to True in _finish_strand_rails
    def __init__(self, strand_rail):        
        self.axis_rail = None
        self.assy = strand_rail.baseatoms[0].molecule.assy
        self.strand_rails = [strand_rail]
        self._finish_strand_rails()
            # check bond direction, reverse if needed
    def baselength(self):
        return len(self.strand_rails[0])
    def finished(self):
        assert 0, "illegal in this class" # or could be a noop
    def add_strand_rail(self, strand_rail):
        assert 0, "illegal in this class"
    def all_rails(self):
        """
        Return a list of all our rails (1 strand).
        [implem is subclass-specific]
        """
        return self.strand_rails
    def all_rail_slots_from_top_to_bottom(self):
        """
        Return a list of all our rails (1 strand), in top to bottom order,
        using None for missing rails (so length of return value is 3).
        [implem is subclass-specific]
        """
        return [self.strand_rails[0], None, None]
    def __repr__(self):
        ns = self.num_strands()
        if ns == 1:
            extra = ""
        else:
            extra = " (error: %d strands)" % ns
        if self.axis_rail:
            extra += " (error: has axis_rail)"
        classname = self.__class__.__name__.split('.')[-1]
        return "<%s at %#x, len %d%s>" % (classname, id(self), self.baselength(), extra)
    pass

# ==

def _rail_end_atom_to_ladder(atom): # FIX: not really private, and part of an import cycle (used here and in DnaLadderRailChunk).
    """
    Atom is believed to be the end-atom of a rail in a valid DnaLadder.
    Return that ladder. If anything looks wrong, either console print an error message
    and return None (which is likely to cause exceptions in the caller),
    or raise some kind of exception (which is what we do now, since easiest).
    """
    # various exceptions are possible from the following; all are errors
    try:
        ladder = atom._DnaLadder__ladder
        assert isinstance(ladder, DnaLadder)
        assert ladder.valid
            # or: if not, print "likely bug: invalid ladder %r found on %r during merging" % (ladder, atom) #k
        assert atom in ladder.rail_end_baseatoms()
        return ladder
    except:
        print "following exception is an error in _rail_end_atom_to_ladder(%r): " % (atom,)
        raise
    pass

def _end_to_end_bonded( atom1, atom2, strandQ):
    """
    Are the expected end-to-end bonds present between end atoms
    from different ladders? (The atoms are None if they are from
    missing rails, i.e. strand2 of any single-stranded ladder
    or axis_rail of a free-floating single-stranded ladder;
    we expect no bonds between two missing atoms, but we do need
    bonds between None and a real end-atom, so we return False then.)

    param atom1: an end atom of a ladder rail, or None (for a missing rail in a ladder)

    param atom2: like atom1, for a possibly-adjacent ladder
    
    param strandQ: whether these atoms are part of strand rails (vs axis rails).
    type strandQ: boolean
    """
    if atom1 is None and atom2 is None:
        # note: this can happen for strandQ or not
        return True
    if atom1 is None or atom2 is None:
        # note: this can happen for strandQ or not
        return False
    if atoms_are_bonded(atom1, atom2):
        # note: no check for strand bond direction (assume caller did that)
        # (we were not passed enough info to check for it, anyway)
        return True
    if strandQ:
        # also check for an intervening Pl in case of PAM5
        return strand_atoms_are_bonded_by_Pl(atom1, atom2)
    else:
        return False

def strand_atoms_are_bonded_by_Pl(atom1, atom2): #e refile 
    """
    are these two strand base atoms bonded (indirectly) by means of a single
    intervening Pl atom (PAM5)?
    """
    if atom1 is atom2:
        # assert 0??
        return False # otherwise following code could be fooled!
# one way to support PAM5:
##    set1 = atom1.Pl_neighbors() # IMPLEM
##    set2 = atom2.Pl_neighbors()
##    for Pl in set1:
##        if Pl in set2:
##            return True
##    return False
    # another way, easier for now:
    set1 = atom1.neighbors()
    set2 = atom2.neighbors()
    for Pl in set1:
        if Pl in set2 and Pl.element.symbol.startswith("Pl"): # KLUGE
            return True
    return False

# ==

# helpers for _do_merge_with_other_at_ends

def _new_rail(baseatoms, strandQ, bond_direction):
    """
    """
    if baseatoms == []:
        # special case
        return None
    assert len(baseatoms) > 1 # since result of merge of nonempty rails
        # (might not be needed, but good to sanity-check)
    if strandQ:
        assert bond_direction
    return merged_chain( baseatoms, strandQ, bond_direction)

def _new_ladder(new_rails):
    """
    @param new_rails: a sequence of length 3; each element is a new rail,
                      or None; top to bottom order.
    """
    strand1, axis, strand2 = new_rails
    assert strand1
    if not axis:
        assert not strand2
        return _new_single_strand_domain(strand1)
    else:
        return _new_axis_ladder(strand1, axis, strand2)
    assert 0

def _new_single_strand_domain(strand1):
    return DnaSingleStrandDomain(strand1)

def _new_axis_ladder(strand1, axis, strand2):
    ladder = DnaLadder(axis)
    ladder.add_strand_rail(strand1)
    if strand2:
        ladder.add_strand_rail(strand2)
    ladder.finish() ###k @@@@ ok here?
    return ladder

# end
