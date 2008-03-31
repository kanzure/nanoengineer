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

 ...  -+-+-+-+-+-+-> ... (strand 1)
       | | | | | | 
 ...  -+-+-+-+-+-+-  ... (axis; missing for free-floating single strand)
       | | | | | | 
 ... <-+-+-+-+-+-+-  ... (strand 2; missing for any kind of single strand)

(with the strand bond directions antiparallel and standardized
to 1 on top (measured left to right == towards increasing baseatoms
index), -1 on bottom).

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

THIS MIGHT BE WRONG [the undo/copy part]: ####REVIEW @@@
A ladder will be fully visible to copy and undo (i.e. it will
contain undoable state), but will not be stored in the mmp file.
"""

from model.bond_constants import atoms_are_bonded

from dna.model.DnaChain import merged_chain

from dna.model.DnaLadderRailChunk import make_or_reuse_DnaAxisChunk
from dna.model.DnaLadderRailChunk import make_or_reuse_DnaStrandChunk
    # note: if these imports are an issue, they could be moved
    # to a controller class, since they are needed only by remake_chunks method

from dna.model.pam_conversion import DnaLadder_writemmp_mapping_memo

from utilities import debug_flags

def _DEBUG_LADDER_FINISH_AND_MERGE():
    return debug_flags.DEBUG_DNA_UPDATER_VERBOSE # for now

def _DEBUG_REVERSE_STRANDS():
    # same as _DEBUG_LADDER_FINISH_AND_MERGE, for now
    return debug_flags.DEBUG_DNA_UPDATER_VERBOSE


from dna.model.dna_model_constants import LADDER_ENDS
from dna.model.dna_model_constants import LADDER_END0
from dna.model.dna_model_constants import LADDER_END1
from dna.model.dna_model_constants import LADDER_BOND_DIRECTION_TO_OTHER_AT_END_OF_STRAND1
from dna.model.dna_model_constants import LADDER_STRAND1_BOND_DIRECTION

from dna.model.dna_model_constants import MAX_LADDER_LENGTH

from dna.updater.dna_updater_prefs import pref_per_ladder_colors

from utilities.Log import orangemsg, redmsg ##, quote_html
import foundation.env as env

from Numeric import dot
from geometry.VQT import cross

from model.elements import Pl5


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
    #TODO: split this class into a common superclass with DnaSingleStrandDomain
    # (see comment there) and a specific subclass for when we have axis_rail.
    valid = False # public for read, private for set; whether structure is ok and we own our atoms
    error = "" # ditto; whether num_strands or strand bond directions are wrong (parallel), etc # todo: use more?
        # on error, should be set to a short string (suitable for tooltip)
        # without instance-specific data (i.e. one of a small fixed set of
        # possible strings, so also suitable as part of a summary_format string)

    _class_for_writemmp_mapping_memo = DnaLadder_writemmp_mapping_memo
        # subclass can override if needed (presumably with a subclass of this value)
        ### REVIEW: what about for single strands? (our subclass) @@@@@@

    def __init__(self, axis_rail):
        self.axis_rail = axis_rail
        self.assy = axis_rail.baseatoms[0].molecule.assy #k
        self.strand_rails = []
        assert self.assy is not None, "%r.__init__: assy is None" % self

    def _f_make_writemmp_mapping_memo(self, mapping):
        """
        [friend method for class writemmp_mapping.get_memo_for(self)]
        """
        # note: same code in some other classes that implement this method
        return self._class_for_writemmp_mapping_memo(mapping, self)

    def baselength(self):
        return len(self.axis_rail)
    
    def __len__(self):
        return self.baselength()
    
    def __nonzero__(self): # 080311
        # avoid Python calling __len__ for this [review: need __eq__ as well?]
        return True
    
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
        if _DEBUG_REVERSE_STRANDS():
            strand_rail.debug_check_bond_direction("in %r.add_strand_rail" % self)
        return
    
    def finished(self): # Q. rename to 'finish'?
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
        # note: this method is only for the subclass with axis_rail present;
        # at the end it calls a common method.
        assert not self.valid # not required, just a useful check on the current caller algorithm
        ## assert len(self.strand_rails) in (1, 2)
        # happens in mmkit - leave it as just a print at least until we implem "delete bare atoms" -
        if not ( len(self.strand_rails) in (1, 2) ):
            # bug, so always print it
            print "\n***bug: DnaLadder %r has %d strand_rails " \
                  "(should be 1 or 2)" % (self, len(self.strand_rails))
            self.error = "bug: illegal number (%d) of strand rails" % len(self.strand_rails)
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
        if _DEBUG_REVERSE_STRANDS():
            print "\n *** _DEBUG_REVERSE_STRANDS start for %r" % self
        for strand_rail in self.strand_rails:
            if _DEBUG_REVERSE_STRANDS():
                print "deciding whether to reverse:", strand_rail
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
                # this should never happen now that fix_bond_directions is active
                # (since it should mark involved atoms as errors using _dna_updater__error
                #  and thereby keep them out of ladders), so always print it [080201]
                msg = "bug: %r strand %r has unknown or inconsistent bond " \
                      "direction - should have been caught by fix_bond_directions" % \
                      (self, strand_rail)
                print "\n*** " + msg
                ## env.history.redmsg(quote_html(msg))
                self.error = "bug: strand with unknown or inconsistent bond direction"
                reverse = True # might as well fix the other strand, if we didn't get to it yet
            else:
                if have_dir != desired_dir:
                    # need to reverse all rails in this ladder (if we're first strand,
                    #  or if dir is arb since len is 1) 
                    # or report error (if we're second strand)
                    if strand_rail.bond_direction_is_arbitrary():
                        if _DEBUG_REVERSE_STRANDS():
                            print "reversing %r (bond_direction_is_arbitrary)" % strand_rail
                        strand_rail._f_reverse_arbitrary_bond_direction()
                        have_dir = strand_rail.bond_direction() # only needed for assert
                        assert have_dir == desired_dir
                    elif reverse:
                        if _DEBUG_REVERSE_STRANDS():
                            print "reversing all rails in %r:" % (self,)
                        for rail in self.all_rails(): # works for ladder or single strand domain
                            if _DEBUG_REVERSE_STRANDS():
                                print "   including: %r" % (rail,)
                            ### review: this reverses even the ones this for loop didn't get to, is that desired? @@@
                            rail.reverse_baseatoms()
                    else:
                        # this can happen for bad input (not a bug);
                        # don't print details unless verbose,
                        # use a summary message instead
                        if debug_flags.DEBUG_DNA_UPDATER_VERBOSE:
                            print "\ndna updater input data error: %r's strands have parallel bond directions." % self
                            print "data about that:"
                            print "this rail %r in list of rails %r" % (strand_rail, self.strand_rails)
                            print "desired_dir = %r, reverse = %r, have_dir = %r" % (desired_dir, reverse, have_dir)
                            print "self.error now = %r (is about to be set)" % (self.error,)
                        if strand_rail.bond_direction_is_arbitrary():
                            print " *** bug: parallel strands but strand_rail.bond_direction_is_arbitrary() is true, should be false"
                        self.error = "parallel strand bond directions"
                        # should we just reverse them? no, unless we use minor/major groove to decide which is right.
                    pass
                else:
                    # strand bond direction is already correct
                    if _DEBUG_REVERSE_STRANDS():
                        print "no need to reverse %r" % strand_rail
            continue
        if _DEBUG_REVERSE_STRANDS():
            print "done reversing if needed; current rail baseatom order is:"
            for rail in self.all_rails():
                print "  %r" % rail.baseatoms # see if it gets it right after the first step
            for rail in self.strand_rails:
                strand_rail.debug_check_bond_direction("end of %r._finish_strand_rails" % self)
            print " *** _DEBUG_REVERSE_STRANDS end for %r\n" % self
        self.set_valid(True) # desired even if self.error was set above, or will be set below
        self._duplex_geometric_checks() # might set or append to self.error
        if self.error:
            # We want to display the error, but not necessarily by setting
            # atom._dna_updater__error for every atom (or at least not right here,
            # since we won't know all the atoms until we remake_chunks).
            # For now, just report it: [#e todo: fix inconsistent case in dna updater warnings @@@@]
            # Later display it in remake_chunks or in some ladder-specific display code. (And in tooltip too, somehow.)
            # Ideally we draw an unmissable graphic which points out the error.
            # (And same for the per-atom _dna_updater__error, which is too missable as mere orange color.) @@@@
            error_string = self.error
            if error_string.startswith("bug:"):
                prefix = "Bug"
                colorfunc = redmsg
                # remove "bug: " from error_string used in summary_format
                error_string = error_string[len("bug:"):].strip()
            else:
                prefix = "Warning"
                colorfunc = orangemsg
            summary_format = "%s: DNA updater: found [N] dna ladder(s) with %s" % \
                             ( prefix, error_string )
            env.history.deferred_summary_message( colorfunc( summary_format))
                # note: error prevents ladder merge, so no issue of reporting an error more than once
                # (as there would be otherwise, since same error would show up in the merged ladder)
        return

    def _duplex_geometric_checks(self):
        """
        Set (or append to) self.error, if self has any duplex geometric errors.
        """
        if len(self.strand_rails) == 2 and len(self) > 1:
            # use the middle two base pairs; check both strands
            i1 = (len(self) / 2) - 1
            i2 = i1 + 1
            axis_atoms = self.axis_rail.baseatoms[i1:i1+2] # note: for PAM5 these might be Gv, so formulas may differ... @@@
            strand1_atoms = self.strand_rails[0].baseatoms[i1:i1+2]
            strand2_atoms = self.strand_rails[1].baseatoms[i1:i1+2]
            error_from_this = self._check_geom( axis_atoms, strand1_atoms, strand2_atoms)
            if not error_from_this:
                axis_atoms.reverse()
                strand1_atoms.reverse()
                strand2_atoms.reverse()
                self._check_geom( axis_atoms, strand2_atoms, strand1_atoms)
        return
    
    def _check_geom(self, axis_atoms, strand1_atoms, strand2_atoms ):
        """
        Check the first 4 atoms (out of 6 passed to us, as 3 lists of 2)
        for geometric duplex errors.
        If strand2 is being passed in place of strand1 (and thus vice versa),
        all 3 atom lists should be reversed.
        If we set or add to self.error, return something true
        (which will be the error string we add, not including whatever
         separator we use to add it to an existing self.error).
        """
        old_self_error = self.error # for assert only
        error_here = "" # modified below
        axis_posns = [atom.posn() for atom in axis_atoms]
        strand1_posns = [atom.posn() for atom in strand1_atoms]
        rung0_vec = strand1_posns[0] - axis_posns[0]
        rung1_vec = strand1_posns[1] - axis_posns[1]
        axis_vec = axis_posns[1] - axis_posns[0]
        righthandedness = dot( cross(rung0_vec, rung1_vec), axis_vec )
        # todo: make sure it's roughly the right magnitude, not merely positive
        if not self.error or not self.error.startswith("bug:"):
            # check strand1 for reverse twist (append to error string if we already have one)
            if righthandedness <= 0:
                error_here = "reverse twist"
                if not self.error:
                    self.error = error_here
                else:
                    self.error += "\n" + error_here # is '\n' what we want?
        if not self.error:
            assert not error_here
            # check for wrong strand directions re major groove
            # (since no self.error, we can assume strands are antiparallel and correctly aligned,
            #  i.e. that bond directions point from strand1_atoms[0] to strand1_atoms[1])
            strand2_posns = [atom.posn() for atom in strand2_atoms]
            rung0_vec_2 = strand2_posns[0] - axis_posns[0]
            minor_groove_where_expected_ness = dot( cross( rung0_vec, rung0_vec_2 ), axis_vec )
            if minor_groove_where_expected_ness <= 0:
                error_here = "bond directions both wrong re major groove"
                if 0: # turn this on to know why it reported that error [080210]
                    print "data for %s:" % error_here
                    print axis_atoms, strand1_atoms, strand2_atoms
                    print rung0_vec, rung0_vec_2, axis_vec
                self.error = error_here
        if old_self_error or error_here:
            assert self.error
        assert self.error.startswith(old_self_error)
        assert self.error.endswith(error_here)
        return error_here

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
                    if debug_flags.DEBUG_DNA_UPDATER_VERBOSE:
                        print "%r owning %r" % (self, atom)
            else:
                # un-tell them
                for atom in self.rail_end_baseatoms():
                    # (could debug-warn if not set to self)
                    atom._DnaLadder__ladder = None
                    del atom._DnaLadder__ladder
                    if debug_flags.DEBUG_DNA_UPDATER_VERBOSE:
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
        
    def invalidate(self):
        # note: this is called from dna updater and from
        # DnaLadderRailChunk.delatom, so changed atoms inval their
        # entire ladders
        self.set_valid(False)
        
    def get_ladder_end(self, endBaseAtom):
        """
        Returns the end (0 or 1)of the ladder at the given end base atom
        @param endBaseAtom: One of the end atoms of the ladder. If this can't be
        found in the ladder end atoms, it returns None
        
        """
        for ladderEnd in LADDER_ENDS:
            if endBaseAtom in self.ladder_end_atoms(ladderEnd):
                return ladderEnd
        
        return None
    
    def get_endBaseAtoms_containing_atom(self, baseAtom):
        """
        Returns a list of end Base atoms that contain <baseAtom> (including that
        atom. 
        """
        endBaseAtomList = []
        sortedEndBaseAtomList = []
        end_strand_base_atoms = ()
        for ladderEnd in LADDER_ENDS:
            if baseAtom in self.ladder_end_atoms(ladderEnd):
                endBaseAtomList = self.ladder_end_atoms(ladderEnd)
                break
        if len(endBaseAtomList) > 2:
            end_strand_base_atoms = (endBaseAtomList[0], endBaseAtomList[2])
        else:
            #@TODO: single stranded dna. Need to figure out if it has 
            #strand1 or strand2 as its strand.
            pass
        
        
        strand1Atom = None
        axisAtom =  endBaseAtomList [1]
        strand2Atom = None
        for atm in end_strand_base_atoms:     
            if atm is not None:
                temp_strand = atm.molecule        
                rail = temp_strand.get_ladder_rail()
                #rail goes from left to right. (increasing chain index order)                
                
                if rail.bond_direction() == 1:
                    strand1Atom = atm
                elif rail.bond_direction() == -1:
                    strand2Atom = atm
     
        endBaseAtomList = [strand1Atom, axisAtom, strand2Atom]
        
        return endBaseAtomList                
     
    def is_ladder_end_baseatom(self, baseAtom):
        """
        Returns true if the given atom is an end base atom of a ladder (either
        at ladder end0 or ladder end1)
        """
        for ladderEnd in LADDER_ENDS:
            if endBaseAtom in self.ladder_end_atoms(ladderEnd):
                return True
        
        return False
    

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
        Is the same valid other ladder (with no error) attached to each rail of self
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
        # len is 1. But to avoid confusion when other len is 1, make sure only
        # one orientation of other can match, by using the convention
        # that the ladder-end-atoms go top to bottom on the right,
        # but bottom-to-top on the left.)

        strand1 = self.strand_rails[0]
        assert 1 == LADDER_STRAND1_BOND_DIRECTION # since it's probably also hardcoded implicitly
        assert strand1.bond_direction() == LADDER_STRAND1_BOND_DIRECTION, \
               "wrong bond direction %r in strand1 of %r" % \
               (strand1.bond_direction, self)
        end_atom = strand1.end_baseatoms()[end]
        assert not end_atom._dna_updater__error # otherwise we should not get this far with it
        assert self is _rail_end_atom_to_ladder(end_atom) # sanity check
        bond_direction_to_other = LADDER_BOND_DIRECTION_TO_OTHER_AT_END_OF_STRAND1[end]
        next_atom = end_atom.strand_next_baseatom(bond_direction = bond_direction_to_other)
            # (note: strand_next_baseatom returns None if end_atom or the atom it
            #  might return has ._dna_updater__error set, or if it reaches a non-Ss atom.)
        if next_atom is None:
            # end of the chain (since bondpoints are not baseatoms), or
            # inconsistent bond directions at or near end_atom
            # (report error in that case??)
            return None
        assert not next_atom._dna_updater__error
        other = _rail_end_atom_to_ladder(next_atom)
            # other ladder (might be self in case of ring)
        if other.error:
            return None
        # other.valid was checked in _rail_end_atom_to_ladder
        if other is self:
            return None
        if len(self) + len(other) > MAX_LADDER_LENGTH:
            return None
        # Now a merge is possible and allowed, if all ladder-ends are bonded
        # in either orientation.

        # optim: reject early if ladders have different numbers of rails --
        # enable this optim once i verify it works without it: @@
        ## if self.num_strands() != other.num_strands():
        ##    return None # optimization
        ## #e could also check axis present or not, same in both
        
        # try each orientation for other ladder;
        # first collect the atoms to test for bonding to other
        self_end_atoms = self.ladder_end_atoms(end)
        if debug_flags.DEBUG_DNA_UPDATER:
            assert end_atom in self_end_atoms
        for other_end in LADDER_ENDS:
            other_end_atoms = other.ladder_end_atoms(other_end, reverse = True)
                # note: .ladder_end_atoms returns a sequence of length 3,
                # with each element being a rail's end-atom or None for a missing rail;
                # the rail order is strand-axis-strand, which on the right is in
                # top to bottom order, but on the left is in bottom to top order.
                # strand1 is always present; strand2 is missing for either kind of
                # single strands; axis_rail is missing for free-floating single strands.
                #
                # bugfix 080122 (untested): reverse order for other_end to facilitate
                # comparison if the ladders abut (with standardized strand directions).
                # Not doing this presumably prevented all merges except those involving
                # length 1 ladders, and made those happen incorrectly when len(other) > 1.
            still_ok = True
            for atom1, atom2, strandQ in zip(self_end_atoms, other_end_atoms, (True, False, True)):
                ok = _end_to_end_bonded(atom1, atom2, strandQ)
                if not ok:
                    still_ok = False
                    break
            if still_ok:
                # success
                if debug_flags.DEBUG_DNA_UPDATER:
                    # end_atom and next_atom are bonded, so if we succeeded
                    # then they ought to be in the same positions in these lists:
                    assert next_atom in other_end_atoms
                    assert self_end_atoms.index(end_atom) == other_end_atoms.index(next_atom)
                merge_info = (end, other_end)
                other_ladder_and_merge_info = other, merge_info
                return other_ladder_and_merge_info
        return None
    
    def ladder_end_atoms(self, end, reverse = False):
        """
        Return a list of our 3 rail-end atoms at the specified end,
        using None for a missing atom due to a missing strand2 or axis_rail,
        in the order strand1, axis, strand2 for the right end,
        or the reverse order for the left end (since flipping self
        also reverses that rail order in order to preserve strand bond
        directions as a function of position in the returned list,
        and for other reasons mentioned in some caller comments).

        @param end: LADDER_END0 or LADDER_END1

        @param reverse: caller wants result in reverse order compared to usual
        (it will still differ for the two ends)

        @warning: the order being flipped for different ends
        means that a caller looking for adjacent baseatoms
        from abutting ends of two ladders needs
        to reverse the result for one of them
        (always, given the strand direction convention).
        To facilitate and (nim)optimize this the caller can pass
        the reverse flag if it knows ahead of time it wants
        to reverse the result.
        """
        # note: top to bottom on right, bottom to top on left
        # (when reverse option is false);
        # None in place of missing atoms for strand2 or axis_rail
        assert len(self.strand_rails) in (1,2)
        strand_rails = self.strand_rails + [None] # + [None] needed in case len is 1
        rails = [strand_rails[0], self.axis_rail, strand_rails[1]] # order matters
        def atom0(rail):
            if rail is None:
                return None
            return rail.end_baseatoms()[end]
        res0 = map( atom0, rails)
        if end != LADDER_END1:
            assert end == LADDER_END0
            res0.reverse()
        if reverse:
            res0.reverse() #e could optim by xoring those booleans
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
        # algorithm: (might differ for subclasses)
        # - make merged rails (noting possible flip of each ladder)
        #   (just append lists of baseatoms)
        # - put them into a new ladder
        # - when debugging, could check all the same things that
        #   finished does, assert no change
        flip_self = (end != LADDER_END1)
        flip_other = (other_end != LADDER_END0)

        if _DEBUG_LADDER_FINISH_AND_MERGE():
            print "dna updater: fyi: _do_merge_with_other_at_ends(self = %r, other_ladder = %r, end = %r, other_end = %r)" % \
              (self, other, end, other_end)
        if _DEBUG_LADDER_FINISH_AND_MERGE():
            # following was useful for a bug: 080122 noon
            print self.ladder_string("self", mark_end = end, flipQ = flip_self)
            print other.ladder_string("other", mark_end = other_end, flipQ = flip_other)
            print

        self_baseatom_lists = [rail_to_baseatoms(rail, flip_self)
                               for rail in self.all_rail_slots_from_top_to_bottom()]
        other_baseatom_lists = [rail_to_baseatoms(rail, flip_other)
                               for rail in other.all_rail_slots_from_top_to_bottom()]
        if flip_self:
            # the individual lists were already reversed in rail_to_baseatoms
            self_baseatom_lists.reverse()
        if flip_other:
            other_baseatom_lists.reverse()
        # now (after flipping) we need to attach self END1 to other END0,
        # i.e. "self rail + other rail" for each rail.
        def concatenate_rail_atomlists((r1, r2)):
            assert (r1 and r2) or (not r1 and not r2)
            res = r1 + r2
            assert res is not r1
            assert res is not r2
            return res
        new_baseatom_lists = map( concatenate_rail_atomlists,
                                  zip(self_baseatom_lists, other_baseatom_lists))
        # flip the result if we flipped self, so we know it defines a legal
        # set of rails for a ladder even if some rails are missing
        # (todo: could optim by never flipping self, instead swapping
        #  ladders and negating both flips)
        if flip_self:
            if _DEBUG_LADDER_FINISH_AND_MERGE():
                print "dna updater: fyi: new_baseatom_lists before re-flip == %r" % (new_baseatom_lists,)
            new_baseatom_lists.reverse() # bugfix 080122 circa 2pm: .reverse -> .reverse() [confirmed]
            for listi in new_baseatom_lists:
                listi.reverse()
        if _DEBUG_LADDER_FINISH_AND_MERGE():
            print "dna updater: fyi: new_baseatom_lists (after flip or no flip) == %r" % (new_baseatom_lists,)
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
        if debug_flags.DEBUG_DNA_UPDATER:
            print "dna updater: fyi: merged %r and %r to produce %r" % (self, other, new_ladder,)
        return new_ladder

    def ladder_string(self, name, flipQ = False, mark_end = None):
        """
        Return a multi-line string listing all baseatoms in self,
        labelling self as name, marking one end of self if requested by mark_end,
        flipping self if requested (mark_end is interpreted as referring
        to the unflipped state). Even empty rails are shown.

        @type name: string
        @type flipQ: boolean
        @type mark_end: None or LADDER_END0 or LADDER_END1
        """
        assert LADDER_END0 == 0 and LADDER_END1 == 1
            # make it easier to compute left/right mark
        classname = self.__class__.__name__.split('.')[-1]
        flipped_string = flipQ and " (flipped)" or ""
        label = "%s %r%s:" % (classname, name, flipped_string)
        baseatom_lists = [rail_to_baseatoms(rail, flipQ)
                               for rail in self.all_rail_slots_from_top_to_bottom()]
        if flipQ:
            # the individual lists were already reversed in rail_to_baseatoms
            baseatom_lists.reverse()
        if mark_end is not None:
            if flipQ:
                # make it relative to the printout
                mark_end = (LADDER_END0 + LADDER_END1) - mark_end
        left_mark = (mark_end == LADDER_END0) and "* " or "  "
        right_mark = (mark_end == LADDER_END1) and " *" or "  "
        strings = [left_mark +
                   (baseatoms and ("%r" % baseatoms) or "------") +
                   right_mark
                   for baseatoms in baseatom_lists]
        return "\n".join([label] + strings)
    
    # ==

    def all_rails(self):
        """
        Return a list of all our rails (axis and 1 or 2 strands), in arbitrary order,
        not including missing rails.
        [implem is subclass-specific]
        """
        return [self.axis_rail] + self.strand_rails

    # TODO: make self.strand_rails private; define a method of the same name for external use,
    # to be uniform with axis_rails and all_rails methods [bruce 080224 comment]

    def axis_rails(self):
        """
        Return a list of all our axis rails (currently, 1 in this class,
        0 in some subclasses), in arbitrary order,
        not including missing rails.
        [implem is subclass-specific]
        """
        return [self.axis_rail]
    
    def all_rail_slots_from_top_to_bottom(self):
        """
        Return a list of all our rails (axis and 1 or 2 strands), in top to bottom order,
        using None for missing rails.
        [implem is subclass-specific]
        """
        if len(self.strand_rails) == 2:
            return [self.strand_rails[0], self.axis_rail, self.strand_rails[1]]
        elif len(self.strand_rails) == 1:
            return [self.strand_rails[0], self.axis_rail, None]
        else:
            # this happens, after certain bugs, in debug code with self.error already set;
            # make sure we notice if it happens without self.error being set: [bruce 080219]
            if not self.error:
                self.error = "late-detected wrong number of strands, %d" % len(self.strand_rails)
                print "\n***BUG: %r: %s" % (self, self.error)
            return [None, self.axis_rail, None] # not sure this will work in callers
        pass

    # ==
    
    def remake_chunks(self):
        """
        Make new chunks for self, as close to the old chunks as we can
        (definitely in the same Part; in the same Group if they were in one).
        
        @return: list of all newly made (by this method) DnaLadderRailChunks
                 (or modified ones, if that's ever possible)
        """
        assert self.valid
        # but don't assert not self.error
        res = []
        ladder_color = None # might be reassigned
        if pref_per_ladder_colors():
            from dna.model.Dna_Constants import getNextStrandColor
            # todo: apply this in Chunk.drawing_color (extend that method),
            # so it doesn't erase the saved color
            ladder_color = getNextStrandColor()
        # note: if self.error, Chunk.draw will notice this and use black
        # (within its call of DnaLadderRailChunk.modify_color_for_error);
        # we won't reassign ladder_color, since we want old chunk colors
        # to last, so they can be preserved until errors are removed.
        for rail in self.all_rails():
            if rail is self.axis_rail:
                constructor = make_or_reuse_DnaAxisChunk
            else:
                constructor = make_or_reuse_DnaStrandChunk
            old_chunk = rail.baseatoms[0].molecule # from arbitrary baseatom in rail
            part = old_chunk.part
            if not part:
                # will this happen in MMKit? get it from assy
                assy = old_chunk.assy
                print "\nbug: %r in assy %r has no .part" % \
                      (old_chunk, assy)
                assert assy is self.assy
                # note: when some bugs happen, assy is None here [080227]
                assert assy is not None, "%r.remake_chunks notices self.assy is None" % self
                part = assy.part
                assert part, "%r.remake_chunks(): %r.part is None" % (self, assy)
                    # will this work in MMKit?
            # todo: assert rail atoms are in this part
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
            assert group.part is part
            chunk = constructor(self.assy, rail, self)
                # Note: these constructors need to be passed self,
                # in case they reuse an old chunk, which self takes over.
                # (Even though in theory they could figure out self somehow.)
                #
                # this pulls in all atoms belonging to rail
                # (including certain kinds of attached atoms);
                # it also may copy in certain kinds of info
                # from their old chunk (e.g. hidden state?)
            if debug_flags.DEBUG_DNA_UPDATER_VERBOSE:
                print "%r.remake_chunks made %r" % (self, chunk)
            chunk.color = old_chunk.color # works, at least if a color was set
            #e put it into the model in the right place [stub - puts it in the same group]
            # (also - might be wrong, we might want to hold off and put it in a better place a bit later during dna updater)
            # also works: part.addnode(chunk), which includes its own ensure_toplevel_group
            if ladder_color is not None:
                chunk.color = ladder_color
            group.addchild(chunk)
            # todo: if you don't want this location for the added node chunk,
            # just call chunk.moveto when you're done,
            # or if you know a group you want it in, call group.addchild(chunk) instead of this.
            res.append(chunk)
        return res

    # == chunk access methods

    def strand_chunks(self):
        """
        Return a list of all the strand chunks (DnaStrandChunk objects) of this DnaLadder.

        @see: our methods strand_chunks, all_chunks, axis_chunks,
              kill_ versions of each of those.
        """
        ###FIX: self.strand_rails is an attr, self.axis_rails is a method.
        return [rail.baseatoms[0].molecule for rail in self.strand_rails]

    def axis_chunks(self):
        """
        Return a list of all the axis chunks (DnaAxisChunk objects) of this DnaLadder.

        @see: our methods strand_chunks, all_chunks, axis_chunks,
              kill_ versions of each of those.
        """
        return [rail.baseatoms[0].molecule for rail in self.axis_rails()]

    def all_chunks(self):
        """
        Return a list of all the strand and axis chunks (DnaLadderRailChunk objects) of this DnaLadder.

        @see: our methods strand_chunks, all_chunks, axis_chunks,
              kill_ versions of each of those.
        """
        return [rail.baseatoms[0].molecule for rail in self.all_rails()]

    # == convenience methods
    
    def kill_strand_chunks(self):
        """
        Kill all the strand chunks (DnaStrandChunk objects) of this DnaLadder.

        @note: doesn't invalidate the ladder -- that's up to the dna updater
               to do later if it wants to.

        @see: our methods strand_chunks, all_chunks, axis_chunks,
              kill_ versions of each of those.
        """
        for chunk in self.strand_chunks():
            chunk.kill()

    def kill_axis_chunks(self):
        """
        Kill all the axis chunks (DnaAxisChunk objects) of this DnaLadder.

        @note: doesn't invalidate the ladder -- that's up to the dna updater
               to do later if it wants to.

        @see: our methods strand_chunks, all_chunks, axis_chunks,
              kill_ versions of each of those.
        """
        for chunk in self.axis_chunks():
            chunk.kill()

    def kill_all_chunks(self):
        """
        Kill all the strand and axis chunks (DnaLadderRailChunk objects) of this DnaLadder.

        @note: doesn't invalidate the ladder -- that's up to the dna updater
               to do later if it wants to.

        @see: our methods strand_chunks, all_chunks, axis_chunks,
              kill_ versions of each of those.
        """
        for chunk in self.all_chunks():
            chunk.kill()

    pass # end of class DnaLadder

# ==

# @@ review points:
# - this subclass should be a sibling class -- these are both kinds of
#   "ladder-like DnaDomains", and this has less not more code than DnaLadder;
#   maybe about half of DnaLadder's code looks like it's common code
#   (what's the right classname for the interface?
#    single or duplex domain? domain with some strands?)
# - the ladder api from the rest of the code (e.g. chunk.ladder)
#   is really a "ladder-like dna domain" api, since it work for single strand
#   ladders too (i.e. DnaLadder is not a perfect name for the common superclass)

class DnaSingleStrandDomain(DnaLadder):
    """
    Represent a free floating single strand domain;
    act exactly like a ladder with no axis rail or second strand rail
    in terms of ability to interface with other code.
    """
    valid = False # same as in super; set to True in _finish_strand_rails
    
    def __init__(self, strand_rail):        
        self.axis_rail = None
        self.assy = strand_rail.baseatoms[0].molecule.assy
        self.strand_rails = [strand_rail]
        assert self.assy is not None, "%r.__init__: assy is None" % self
        self._finish_strand_rails()
            # check bond direction, reverse if needed
        return
    
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
    
    def axis_rails(self):
        """
        Return a list of all our axis rails (none, in this subclass).
        [implem is subclass-specific]
        """
        return []
    
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
        error = atom._dna_updater__error and ("[%s]" % atom._dna_updater__error) or ""
        print "\nfollowing exception is an error in _rail_end_atom_to_ladder(%r%s): " % \
              (atom, error)
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
    are these two strand base atoms bonded (indirectly) by means of
    a single intervening Pl atom (PAM5)?
    """
    if atom1 is atom2:
        # assert 0??
        return False # otherwise following code could be fooled!
# one way to support PAM5:
##    set1 = atom1.Pl_neighbors() # [this is defined as of 080122]
##    set2 = atom2.Pl_neighbors()
##    for Pl in set1:
##        if Pl in set2:
##            return True
##    return False
    # another way, easier for now:
    set1 = atom1.neighbors()
    set2 = atom2.neighbors()
    for Pl in set1:
        if Pl in set2 and Pl.element is Pl5:
            return True
    return False

# ==

# helpers for _do_merge_with_other_at_ends

def rail_to_baseatoms(rail, flipQ):
    if not rail:
        return []
    elif not flipQ:
        return rail.baseatoms
    else:
        res = list(rail.baseatoms)
        res.reverse()
        return res

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
    else:
        assert not bond_direction
    if _DEBUG_LADDER_FINISH_AND_MERGE():
        # print all calls
        print "\n_new_rail(%r, %r, %r)" % (baseatoms, strandQ, bond_direction)
    if debug_flags.DEBUG_DNA_UPDATER:
        # check bondedness of adjacent baseatoms
        for i in range(len(baseatoms) - 1):
            atom1, atom2 = baseatoms[i], baseatoms[i+1]
            if strandQ:
                assert atoms_are_bonded(atom1, atom2) or \
                       strand_atoms_are_bonded_by_Pl(atom1, atom2), \
                       "*** missing bond between adjacent baseatoms [%d,%d of %d]: %r and %r" % \
                       (i, i+1, len(baseatoms), atom1, atom2)
            else:
                assert atoms_are_bonded(atom1, atom2), \
                       "*** missing bond between adjacent baseatoms [%d,%d of %d]: %r and %r" % \
                       (i, i+1, len(baseatoms), atom1, atom2)
    return merged_chain( baseatoms, strandQ, bond_direction)

def _new_ladder(new_rails):
    """
    Make a new DnaLadder of the appropriate subclass,
    given 3 new rails-or-None in top to bottom order.
    
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
    pass

def _new_single_strand_domain(strand1):
    """
    [private helper for _new_ladder]
    """
    return DnaSingleStrandDomain(strand1)

def _new_axis_ladder(strand1, axis, strand2):
    """
    [private helper for _new_ladder]
    """
    ladder = DnaLadder(axis)
    ladder.add_strand_rail(strand1)
    if strand2:
        ladder.add_strand_rail(strand2)
    ladder.finished()
    return ladder

# end
