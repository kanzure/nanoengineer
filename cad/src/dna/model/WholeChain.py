# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
WholeChain.py - a complete chain or ring of PAM atoms, made of one or more
smaller chains (or 1 smaller ring) often known as rails (short for ladder rails,
referring to DnaLadder), with refs to markers and a strand or segment

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna.model.dna_model_constants import LADDER_END0
from dna.model.dna_model_constants import LADDER_END1

from dna.model.DnaMarker import DnaMarker # for isinstance
from dna.model.DnaMarker import DnaSegmentMarker # constructor
from dna.model.DnaMarker import DnaStrandMarker # constructor

from utilities.debug import print_compact_traceback

class WholeChain(object):
    """
    A WholeChain knows a sequence of 1 or more rails, i.e. smaller chains
    (of DNA PAM atoms) which are linked into a single longer chain or ring
    (or which were so linked when it was constructed).
    
    (If it's not a ring, then it is required to be a maximal chain,
    i.e. to not be able to be extended with more atoms at the ends,
    at the time it's constructed.)

    It is immutable once constructed, as are its rails.
    Modifications to the underlying chaining from which it and its
    rails are derived result in its becoming invalid
    (in various ways needed by different users of it)
    and (for some of those users) replaced by one or more newly
    constructed wholechains.

    Its jobs and role in the DNA Data Model include:

    - Understand base indexing for any whole segment or strand.

    - Be able to find (and/or keep track of) all the DnaMarkers
    along its atoms.

    - Help a DnaMarker scan its atoms to decide where to move to,
    and help it actually move.

    - Decide which marker should determine strand or segment identity
    and base indexing scheme for the atoms in this wholechain
    (if it's valid). Markers might contain user-settable attributes
    (or inherit those from their owning strand or segment) to know
    how to do this, e.g. a higher or lower priority in controlling
    base indexing, policies for which direction to move in and how
    to adjust base index when moving, how to move when new bases
    are inserted (detectable if these go between the two marker
    atoms), etc. [### todo: say some of that on DnaMarker docstring]

    Specialized kinds of markers might serve as, for example,
    startpoints or endpoints of sequence constraints, or good places
    for a base index discontinuity in a ring (if the index origin
    should not be used).

    Invariants, and how it maintains them:

    - At any given time, just after any dna updater run, the valid WholeChains
    are in 1-1 correspondence with the set of DnaSegment and DnaStrand objects,
    via their controlling markers.

    - Just after any dna updater run, each WholeChain knows about the DnaMarkers
    on its atoms, of which there are one or more, with exactly one being a 
    "controlling marker", which determines the identity of the
    DnaSegment and DnaStrand object which own the wholechain's atoms,
    and determines the base indexing scheme they use (origin and direction).
    
    - When things change (i.e. when user operations make wholechains invalid),
    and the dna updater runs again (always before the next undo checkpoint
    takes its snapshot of the model state), the dna updater
    (and methods in the markers and wholechains) decide how to maintain this
    association (wholechain -> controlling marker -> owning strand or segment)
    based on how the controlling marker moves and whether it stays / stops being
    / becomes controlling. (The wholechain chooses
    or makes a new controlling marker as needed for this.)

    - To do this, the wholechain uses the now-invalid wholechains to help it
    figure out when and how to modify existing DnaSegment or DnaStrand objects,
    and/or delete them or make new ones. (It does this mainly by moving
    DnaMarkers whose atoms got deleted to new locations (of non-deleted atoms)
    along their old wholechains, and then having new wholechains decide which
    markers should determine their strand's or segment's identity, by being
    the wholechain's one "controlling marker".)

    State:
    
    - A WholeChain contains no state for undo/copy/save; that's in the associated
    DnaSegment and DnaStrand objects and their DnaMarkers. (The set of DnaMarkers
    belonging to a DnaSegment and DnaStrand object is the same as the set of
    all the valid markers along its wholechain's atoms.)
    """

    # default values of subclass-specific constants
    _DnaMarker_class = None # class of DnaMarker to make
    
    # default values of instance variables
    _strand_or_segment = None
    _controlling_marker = None
    _num_bases = -1 # unknown, to start with (used in __repr__ and __len__)
    _all_markers = () # in instances, will be a mutable dict
        # (len is used in __repr__; could be needed before __init__ done)
    
    def __init__(self, dict_of_rails): # fyi: called by update_PAM_chunks
        """
        Construct self, own our chunks (and therefore our atoms).

        @note: this does not choose or make a marker or own our markers.
        For that see own_markers.
        
        @param dict_of_rails: maps id(rail) -> rail for all rails in wholechain

        @note: we can assume that rail._f_update_neighbor_baseatoms() has
               already been called (during this run of the dna updater)
               for every rail (preexisting or new) in dict_of_rails.
               Therefore it is ok for us to rely on rail.neighbor_baseatoms
               being set and correct for those rails, but conversely it is
               too late to use that info in any old wholechains of markers.
        """
        assert dict_of_rails, "a WholeChain can't be empty"
        self._dict_of_rails = dict_of_rails
        self.ringQ = (len(self.end_baseatoms()) == 0) # 080311

        # Scan all our atoms, for several reasons.
        # One is to find all the DnaMarkers on them.
        # These markers may have moved along their old wholechain,
        # and even if they didn't, they may no longer be on a pair of
        # adjacent atoms on the same wholechain, so don't assume they are.
        # (E.g. we might find one with one atom on self and the other on some
        #  other wholechain.) For each marker we find, figure out whether it's
        # still valid, record its position if so, kill it if not.
        
        markers_1 = {} # collects markers from all our atoms during loop, maps them to (rail, baseindex) for their marked_atom
        markers_2 = {} # same, but for their next_atom (helps check whether they're still valid, and compute new position)
        num_bases = 0
        end0_baseatoms = self._end0_baseatoms = {} # end0 atom key -> rail (aka chain)
        end1_baseatoms = self._end1_baseatoms = {}
        for rail in dict_of_rails.itervalues():
            baseatoms = rail.baseatoms
            assert baseatoms
            num_bases += len(baseatoms)
            end0_baseatoms[baseatoms[0].key] = rail
            end1_baseatoms[baseatoms[-1].key] = rail
            chunk = baseatoms[0].molecule
            chunk.set_wholechain(self)
            for baseindex in range(len(baseatoms)):
                atom = baseatoms[baseindex]
                for jig in atom.jigs:
                    # note: this is only correct because marker move step1 has
                    # found new atoms for them (or reconfirmed old ones), and
                    # has called marker.setAtoms to ensure they are recorded
                    # on those atoms.
                    if isinstance(jig, DnaMarker):
                        marker = jig
                        assert not marker.killed(), "marker %r is killed" % ( marker, )
                            # might fail if they're not yet all in the model @@@
                            # someday: possible optim: cache the set of markers on each rail
                            # (and maintain it as markers move)?
                            # might matter when lots of old rails.
                        if marker.marked_atom is atom:
                            markers_1[marker] = (rail, baseindex)
                        if marker.next_atom is atom: # not elif, both can be true
                            markers_2[marker] = (rail, baseindex)
            continue

        self._num_bases = num_bases

        # kill markers we only found on one of their atoms
        # or that are not on adjacent atoms in self,
        # and determine and record position for the others
        # [revised 080311]
        
        markers = {} # maps markers found on both atoms to (atom1info, atom2info),
            # but values are later replaced with PositionInWholeChains or discarded
        
        for marker in markers_1.iterkeys():
            if not marker in markers_2:
                marker._f_kill_during_move(self, "different wholechains")
            else:
                markers[marker] = (markers_1[marker], markers_2.pop(marker))
            continue
        for marker in markers_2.iterkeys(): # note the markers_2.pop above
            marker._f_kill_during_move(self, "different wholechains")
            continue

        del markers_1, markers_2

        for marker in markers.keys():
            # figure out new position and direction,
            # store it in same dict (or remove marker if invalid)
            # LOGIC BUG - des this need _all_markers stored, to use self.yield_... @@@@@
            pos0 = marker._f_new_position_for(self, markers[marker])
            if pos0 is not None:
                rail, baseindex, direction = pos0
                pos = PositionInWholeChain(self, rail, baseindex, direction)
                assert isinstance(pos, PositionInWholeChain) # sanity check, for now
                markers[marker] = pos
                marker._f_new_pos_ok_during_move(self) # for debug
            else:
                marker._f_kill_during_move(self, "not on adjacent atoms on wholechain")
                del markers[marker]

        self._all_markers = markers
        
        return # from __init__

    def __len__(self):
        if self._num_bases == -1:
            # We're being called too early during init to know the value.
            # If we just return -1, Python raises ValueError: __len__() should return >= 0.
            # That is not understandable, so raise a better exception.
            # Don't just work: it might hide bugs, and returning 0 might make
            # us seem "boolean false"! (We define __nonzero__ to try to avoid that,
            # but still it makes me nervous to return 0 here.)
            # Note that we need __repr__ to work now (e.g. in the following line),
            # so don't make it use len() unless it checks _num_bases first.
            # (As of now it uses _num_bases directly.)
            assert 0, "too early for len(%r)" % self
        assert self._num_bases > 0 # if this fails, we're being called too early (during __init__), or had some bug during __init__
        return self._num_bases

    def __nonzero__(self):
        return True # needed for safety & efficiency, now that we have __len__! @@@@  TODO: same in other things with __len__; __eq__ too?
    
    def destroy(self): # 080120 7pm untested
        # note: can be called from chunk._undo_update from one of our chunks;
        # try to make it ok to call this multiple times
        for marker in self.all_markers():
            marker.forget_wholechain(self)
        self._all_markers = ()
        self._controlling_marker = None
        self._strand_or_segment = None # review: need to tell it to forget us, too? @@@
        for rail in self.rails():
            chunk = rail.baseatoms[0].molecule
##            rail.destroy() # IMPLEM @@@@ [also, goodness is partly a guess]
            if hasattr(chunk, 'forget_wholechain'): # KLUGE
                chunk.forget_wholechain(self)
            continue
        self._dict_of_rails = {}
        return
    
    def rails(self):
        """
        Return all our rails, IN ARBITRARY ORDER (that might be revised)
        """
        return self._dict_of_rails.values()

    def end_rails(self): # bruce 080212; rename?
        """
        Return a list of those of our rails which have end_atoms of self
        as a whole (which they determine by which neighbor_baseatoms they
        have).

        @note: if we are a ring, this list will have length 0.
               if we are a length-1 wholechain, it will have length 1.
               if we are a longer wholechain, it will have length 1 or 2,
               depending on whether we're made of one rail or more.
               (We assert that the length is 0 or 1 or 2.)
        """
        # note: if this shows up in any profiles, it can be easily
        # optimized by caching its value.
        res = [rail for rail in self.rails() if rail.at_wholechain_end()]
        assert len(res) <= 2
        return res

    def end_baseatoms(self):
        """
        Return a list of our end_baseatoms, based on rail.neighbor_baseatoms
        (used via rail.wholechain_end_baseatoms())
        for each of our rails (set by dna updater, not always valid during it).

        @note: result is asserted length 0 or 2; will be 0 if we are a ring
        or 2 if we are a chain.

        @note: Intended for use by user ops between dna updater runs,
               but legal to call during self.__init__ as soon as
               self._dict_of_rails has been stored.
        """
        res = []
        for rail in self.end_rails():
            res.extend(rail.wholechain_end_baseatoms())
        assert len(res) in (0, 2), "impossible set of %r.end_baseatoms(): %r" % \
               (self, res)
        return res
    
    def get_all_baseatoms(self):
        """
        Returns a list of all base atoms within the whole chain. 
        The atoms are IN ARBITRARY ORDER because self.rails() returns the rails
        in arbitrary order.
        """
        baseAtomList = []
        for rail in self.rails:
            baseAtomList.extend(rail.baseatoms)
        return baseAtomList
        
    def __repr__(self):
        classname = self.__class__.__name__.split('.')[-1]
        res = "<%s (%d bases, %d markers) at %#x>" % \
              (classname, self._num_bases, len(self._all_markers), id(self))
        return res
    
    def all_markers(self):
        """
        Assuming we still own all our atoms (not checked),
        return all the DnaMarkers on them.
        """
        return self._all_markers.keys()

    def own_markers(self):
        """
        Choose or make one of your markers to be controlling,
        then tell them all that you own them and whether
        they're controlling (which might kill some of them).
        (But don't move them in the model tree, not even the newly made ones.)
        
        Also cache whatever base-indexing info is needed
        (in self, our rails/chunks, and/or their atoms).
        [As of 080116 this part is not yet needed or done.]
        """
        self._controlling_marker = self._choose_or_make_controlling_marker()
        for (marker, position_holder) in self._all_markers.items(): # can't be iteritems!
##            print "debug loop: %r.own_marker %r" % (self, marker)
            controllingQ = (marker is self._controlling_marker)
            ## assert not marker.killed(), \
            # [precaution 080222 - change assert to debug print & bug mitigation:]
            if marker.killed():
                print "\n***BUG: " \
                   "marker %r (our controlling = %r) is killed" % \
                   ( marker, controllingQ )
                # this might fail if they're not yet all in the model,
                # but we put them there when we make them, and we don't kill them when they
                # lose atoms, so they ought to be there @@@
                # (it should not fail from them being killed between __init__ and now
                #  and unable to tell us, since nothing happens in caller to kill them)
                self._f_marker_killed(marker) #k guess 080222
                continue
            marker.set_wholechain(self, position_holder, controlling = controllingQ)
                # own it; tell it whether controlling (some might die then,
                # and if so they'll call self._f_marker_killed
                # which removes them from self._all_markers)
            continue
        for marker in self.all_markers():
            # [precaution 080222 - change assert to debug print & bug mitigation:]
            ## assert not marker.killed(), \
            if marker.killed():
                print "\n***BUG: " \
                    "marker %r died without telling %r" % (marker, self)
                self._f_marker_killed(marker)
            continue
        
        # todo: use controlling marker to work out base indexing per rail...
        
        return

    def _f_marker_killed(self, marker):
        """
        [friend method for DnaMarker]
        One of our markers is being killed
        (and calls this to advise us of that).
        [Also called by self if we realize that failed to happen.]
        """
        try:
            self._all_markers.pop(marker)
        except:
            msg = "bug: can't pop %r from %r._all_markers: " % (marker, self)
            print_compact_traceback( msg)
            pass
        return

    # ==
    
    def find_strand_or_segment(self):
        """
        Return our associated DnaStrandOrSegment, which is required
        to be already defined in self.
        """
        assert self._strand_or_segment
        return self._strand_or_segment

    def find_or_make_strand_or_segment(self):
        """
        Return our associated DnaStrandOrSegment. If we don't yet know it
        or don't have one, ask our controlling marker (which we must have
        before now) to find or make it.
        """
        if self._strand_or_segment:
            return self._strand_or_segment
        assert self._controlling_marker, "%r should have called _choose_or_make_controlling_marker before now" % self
        strand_or_segment = self._controlling_marker._f_get_owning_strand_or_segment(make = True)
        assert strand_or_segment, "%r._controlling_marker == %r has no " \
               "owning_strand_or_segment and can't make one" % \
               (self, self._controlling_marker)
        self._strand_or_segment = strand_or_segment
        return strand_or_segment

    # == ### review below

    def _choose_or_make_controlling_marker(self):
        """
        [private]
        Choose one of our markers to control this wholechain, or make a new one
        (at a good position on one of our atoms) to do that.
        Return it, but don't save it anywhere (caller must do that).
        """
        marker = self._choose_controlling_marker()
        if not marker:
            marker = self._make_new_controlling_marker()
        assert marker
        return marker
    
    def _choose_controlling_marker(self):
        """
        [private]
        Look at the existing markers on our atoms which are able to be
        controlling markers.
        If there are none, return None.
        Otherwise choose one of them to be our controlling marker,
        and return it (don't save it anywhere, or tell any markers
        whether they are controlling now; caller must do those things
        if/when desired; fyi, as of 080116 own_markers does this).

        If one or more are already controlling, it will be one of them. [### REVIEW -- not sure this point is right]
        If more than one are controlling, we have rules to let them compete.
        If none is, ditto.
        """
        all_markers = self.all_markers() # valid anytime after __init__
        candidates = [marker
                      for marker in all_markers
                      if marker.wants_to_be_controlling()]
        if not candidates:
            return None
        # choose one of the candidates
        list_of_preferred_markers_this_time = [] ### stub - in real life let external code add markers to this list, pop them all here
        items = []
        for marker in candidates:
            order_info = (marker in list_of_preferred_markers_this_time, # note: False < True in Python
                          marker.control_priority,
                          marker.get_oldness(), # assume oldness is unique -- inverse of something allocated by a counter
                          )
            items.append( (order_info, marker) )
        items.sort()
        return items[-1][1]

    def _make_new_controlling_marker(self):
        """
        [private]
        self has no marker which wants_to_be_controlling().
        Make one (on some good choice of atom on self)
        (and in the same group in the model tree as that atom)
        and return it. (Don't store it as our controlling marker,
        or tell it it's controlling -- caller must do that if desired.
        But *do* add it to our list of all markers on our atoms.)

        @note: we always make one, even if this is a 1-atom wholechain
        (which means (for now) that it's not possible to make a good
         or fully correct one).
        We do that because the callers really need every wholechain to have one.
        """
        # improvements, 080222: should pick end atom with lowest .key, but to be easier and work for rings,
        # might pick end atom of any rail with lowest key (over all rails). Also this is best for segments
        # and also ok for strands but maybe not best for strands (who should look at Ax atoms in same basepairs,
        # but note, these can be same for different strand atoms!).

        end_atoms = self.end_baseatoms() # should find 2 atoms unless we're a ring
        if not end_atoms:
            # we're a ring - just consider all end atoms of all our rails
            # (don't bother not including some twice for length-1 rails,
            #  no need in following code)
            end_atoms = []
            for rail in self.rails():
                end_atoms.append( rail.baseatoms[0] )
                end_atoms.append( rail.baseatoms[-1] )
            pass
        assert end_atoms

        candidates = [(atom.key, atom) for atom in end_atoms]
            # todo: for strands, first sort by attached Ax key?
            # todo: include info to help find next_atom?
        candidates.sort() # lowest key means first-made basepair by Dna Generator
        atom = candidates[0][1]
        
        # now pick the best next_atom

        rail, index, direction_into_chain = self._find_end_atom_chain_and_index( atom)
            # Q. is index for end1 positive or -1?
            # A. positive (or 0 for length-1 rail), but following code doesn't care.
            # Q. does best next_atom come from same rail if possible?
            # A. (guess yes, doing that for now)
        ## direction_into_chain = index and -1 or 1
        
        if len(rail.baseatoms) > 1:
            next_atom = rail.baseatoms[index + direction_into_chain]
            position = (rail, index, direction_into_chain)
        elif rail.neighbor_baseatoms[LADDER_END1]: # ignore index and direction_into_chain
            next_atom = rail.neighbor_baseatoms[LADDER_END1]
            # direction within rail is 1, not necessarily same as direction within next_atom's rail
            position = (rail, index, 1)
        elif rail.neighbor_baseatoms[LADDER_END0]:
            next_atom = rail.neighbor_baseatoms[LADDER_END0] # reverse direction!
            atom, next_atom = next_atom, atom
            # direction within rail is -1, but we need the direction within the next rail!
            rail2, index2, dir2junk = self._find_end_atom_chain_and_index(next_atom)
            # if rail2 is len 1, dir2 and index2 are useless for finding
            # direction2 (direction in next rail), so always do this:
            if atom is rail2.neighbor_baseatoms[LADDER_END1]:
                direction2 = 1
            else:
                assert atom is rail2.neighbor_baseatoms[LADDER_END0]
                direction2 = -1
            position = rail2, index2, direction2
        else:
            # a 1-atom wholechain, hmm ...
            # DnaMarker support for this added 080216, not fully tested
            # (note that a 1-atom wholechain *ring* is not possible,
            #  but if it was it'd be handled by the above if/else cases)
            next_atom = atom
            direction = 1 # arbitrary, but needs to be in (-1, 1)
            position = (rail, index, direction)

        # now make the marker on those atoms
        # (todo: in future, we might give it some user settings too)
        assert atom.molecule, "%r has no .molecule" % atom
        
        assy = atom.molecule.assy
        
        assert assy
        assert atom.molecule.part, "%r has no .part; .molecule is %r" % (atom, atom.molecule)
        assert next_atom.molecule, "%r has no .molecule" % next_atom
        assert next_atom.molecule.part, "%r has no .part; .molecule is %r" % (next_atom, next_atom.molecule)
        assert atom.molecule.part is next_atom.molecule.part, \
               "%r in part %r, %r in part %r, should be same" % \
               (atom, atom.molecule.part, next_atom, next_atom.molecule.part)
        
        marker_class = self._DnaMarker_class # subclass-specific constant
        marker = marker_class(assy, [atom, next_atom]) # doesn't give it a wholechain yet

        # give it a temporary home in the model (so it doesn't seem killed) --
        # in fact, it matters where we put it, since later code assumes it
        # *might* already be inside the right DnaStrandOrSegment (and checks
        # this). So we put it in the same group as the marked atom.

        part = atom.molecule.part
        part.place_new_jig(marker)
            # (overkill in runtime, but should be correct, since both marker's
            #  atoms should be in the same group)
        
        # and remember it's on our atoms, and where on them it is
        self._append_marker(marker, *position)
        
        return marker

    def _append_marker(self, marker, rail, baseindex, direction): # 080306
        assert not marker in self._all_markers
        self._all_markers[marker] = PositionInWholeChain(self, rail, baseindex, direction)
        return
    
    def _find_end_atom_chain_and_index(self, atom):
        # REVIEW: rename chain -> rail, in this method name? (and all local vars in file)
        """
        Assume atom is an end_baseatom of one of our rails (aka chains).
        (If not true, raise KeyError.)
        Find that rail and atom's index in it, and return them as
        the tuple (rail, index_in_rail, direction_into_rail).
        The index is nonnegative, meaning that we use 0 for
        either end of a length-1 rail (there is no distinction
        between the ends in that case).
        """
        key = atom.key
        try:
            rail = self._end0_baseatoms[key]
            return rail, 0, 1
        except KeyError:
            rail = self._end1_baseatoms[key]
                # raise KeyError if atom is not an end_atom of any of our rails
            return rail, len(rail) - 1, -1
        pass
        
    # todo: methods related to base indexing
    
    def yield_rail_index_direction_counter(self,  # in class WholeChain
                                           pos,
                                           counter = 0,
                                           countby = 1,
                                           relative_direction = 1):
        """
        #doc
        @note: the first position we yield is always the one passed,
               with counter at its initial value
        """
        # possible optim: option to skip (most) killed atoms, and optimize that
        # to notice entire dead rails (noticeable when their chunks get killed)
        # and pass them in a single step. We might still need to yield the
        # final repeat of starting pos.
        rail, index, direction = pos
        # assert one of our rails, valid index in it
        assert direction in (-1, 1)
        while 1:
            # yield, move, adjust, check, continue
            yield rail, index, direction, counter
            # move
            counter += countby
            index += direction * relative_direction
            # adjust
            def jump_off(rail, end):
                neighbor_atom = rail.neighbor_baseatoms[end]
                # neighbor_atom might be None, atom, or -1 if not yet set
                assert neighbor_atom != -1
                if neighbor_atom is None:
                    new_rail = None # outer code will return due to this, ending the generated sequence
                    index, direction = None, None # illegal values (to detect bugs in outer code)
                else:
                    new_rail, index, direction = self._find_end_atom_chain_and_index(neighbor_atom)
                    direction *= relative_direction
                    assert new_rail
                    # can't assert new_rail is not rail -- might be a ring of one rail
                return new_rail, index, direction
            if index < 0:
                # jump off END0 of this rail
                rail, index, direction = jump_off(rail, LADDER_END0)
            elif index >= len(rail):
                # jump off END1 of this rail
                rail, index, direction = jump_off(rail, LADDER_END1)
            else:
                pass
            # check
            if not rail:
                return
            assert 0 <= index < len(rail)
            assert direction in (-1, 1)
            if (rail, index, direction) == pos:
                # we wrapped around a ring to our starting position.
                # (or, someday, to another limit pos passed by caller?)
                # yield it one more time, as a signal that we're a ring, and
                # to help with algorithms looking at every pair of successive
                # positions; then return.
                yield rail, index, direction, counter
                return
            elif (rail, index) == pos[0:2]:
                assert 0, "bug: direction got flipped somehow in " \
                       "%r.yield_rail_index_direction_counter%r at %r" % \
                       ( self,
                         (pos, counter, countby, relative_direction),
                         (rail, index, direction, counter) )
            continue
        assert 0 # not reached
        pass

    pass # end of class WholeChain

# ==

class PositionInWholeChain(object):
    """
    A mutable position (and direction) along a WholeChain.
    """
    def __init__(self, wholechain, rail, index, direction):
        self.wholechain = wholechain
        self.set_position(rail, index, direction)

    def set_position(self, rail, index, direction):
        self.rail = rail
        self.index = index # base index in current rail
        self.direction = direction # in current rail only
            # note: our direction in each rail is unrelated
        self.pos = (rail, index, direction)
        return
        
    def yield_rail_index_direction_counter(self, **options): # in class PositionInWholeChain
        return self.wholechain.yield_rail_index_direction_counter( self.pos, **options )

    # maybe: method to scan in both directions
    # (for now, our main caller does that itself)

    pass
    
# ==

class Axis_WholeChain(WholeChain):
    _DnaMarker_class = DnaSegmentMarker
    """
    A WholeChain for axis atoms.
    """
    pass

class Strand_WholeChain(WholeChain):
    _DnaMarker_class = DnaStrandMarker
    """
    A WholeChain for strand atoms.
    """
    pass

# ==

def new_Group_around_Node(node, group_class): #e refile, might use in other ways too [not used now, but might be correct]
    node.part.ensure_toplevel_group() # might not be needed
    name = "(internal Group)" # stub
    assy = node.assy
    dad = None #k legal?? arg needed?
    group = group_class(name, assy, dad) # same args as for Group.__init__(self, name, assy, dad) [review: reorder those anytime soon??]
    node.addsibling(group)
    group.addchild(node)
    return group
    
# end
