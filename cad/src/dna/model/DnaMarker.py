# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaMarker.py - marked positions on atom chains, moving to live atoms as needed

Used internally for base indexing in strands and segments; perhaps used in the
future to mark subsequence endpoints for relations or display styles.

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

TODO: complete the marker-moving code; don't kill markers instead of moving them.
"""

from dna.model.ChainAtomMarker import ChainAtomMarker

from dna.model.DnaStrand import DnaStrand
from dna.model.DnaSegment import DnaSegment

# for parent_node_of_class:
from dna.model.DnaGroup import DnaGroup
from dna.model.DnaStrandOrSegment import DnaStrandOrSegment

from dna.model.DnaGroup import find_or_make_DnaGroup_for_homeless_object

from dna.updater.dna_updater_prefs import pref_draw_internal_markers

from utilities import debug_flags

from graphics.drawing.drawers import drawwirecube

from utilities.constants import orange

from files.mmp.files_mmp_registration import MMP_RecordParser
from files.mmp.files_mmp_registration import register_MMP_RecordParser

# ==

# constants

_CONTROLLING_IS_UNKNOWN = True # represents an unknown value of self.controlling
    # note: this value of True is not strictly correct, but simplifies the code
    #e rename?

# ==

# globals and their accessors [TODO -- move these to updater globals or so]

_marker_newness_counter = 1

_homeless_dna_markers = {}

def _f_get_homeless_dna_markers(): # MISNAMED, see is_homeless docstring in superclass. Maybe rename to
        # something that ends in "markers_that_need_update"?
    """
    Return the homeless dna markers,
    and clear the list so they won't be returned again
    (unless they are newly made homeless).

    [Friend function for dna updater. Other calls
     would cause it to miss newly homeless markers,
     causing serious bugs.]
    """
    res = _homeless_dna_markers.values()
    _homeless_dna_markers.clear()
    res = filter( lambda marker: marker.is_homeless(), res ) # review: is filtering needed?
    return res

def _f_are_there_any_homeless_dna_markers(): # MISNAMED, see _f_get_homeless_dna_markers docstring
    """
    [friend function for dna updater]

    Are there any DnaMarkers needing action by the dna updater?

    @see: _f_get_homeless_dna_markers

    @note: this function does not filter the markers that have been
           recorded as possibly needing update. _f_get_homeless_dna_markers
           does filter them. So this might return True even if that would
           return an empty list. This is ok, but callers should be aware of it.
    """
    return not not _homeless_dna_markers

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
    icon_names = ('modeltree/DnaMarker.png', 'modeltree/DnaMarker-hide.png') # stubs; not normally seen for now
    
    copyable_attrs = _superclass.copyable_attrs + ()
        # todo: add some more -- namely the user settings about how it moves, whether it lives, etc


    # future user settings, which for now are per-subclass constants:

    control_priority = 1

    _wants_to_be_controlling = True # class constant; false variant is nim


    # default values of instance variables:

    wholechain = None

    _position_holder = None # mutable object which records our position
        # in self.wholechain, should be updated when we move
        # [080307, replacing _rail and _baseindex from 080306]

    controlling = _CONTROLLING_IS_UNKNOWN

    _inside_its_own_strand_or_segment = False # 080222 ### REVIEW: behavior when copied? undo? (copy this attr along with .dad?) @@@@
        # whether self is inside the right DnaStrandOrSegment in the model tree
        # (guess: matters only for controlling markers)

##    _advise_new_chain_direction = 0 ###k needed??? @@@
##        # temporarily set to 0 or -1 or 1 for use when moving self and setting a new chain

    _newness = None

    _info_for_step2 = None # rename -- just for asserts - says whether more action is needed to make it ok [revised 080311]

# not needed I think [080311]:
##    # guess: also needs a ladder, and indices into the ladder (which rail, rail/chain posn, rail/chain direction)@@@@
    
    # == Jig or Node API methods (overridden or extended from ChainAtomMarker == _superclass):

    def __init__(self, assy, atomlist):
        """
        """
        _superclass.__init__(self, assy, atomlist) # see also super's _length_1_chain attr
        global _marker_newness_counter
        _marker_newness_counter += 1
        self._newness = _marker_newness_counter
        if debug_flags.DEBUG_DNA_UPDATER_VERBOSE: # made verbose on 080201
            print "dna updater: made %r" % (self,)
        return

    def kill(self):
        """
        Extend Node method, for debugging and for notifying self.wholechain
        """
        if debug_flags.DEBUG_DNA_UPDATER_VERBOSE:
            msg = "dna updater: killing %r" % (self,)
            print msg
        if self.wholechain:
            self.wholechain._f_marker_killed(self)
            self._clear_wholechain()
        self._inside_its_own_strand_or_segment = False # guess
        _superclass.kill(self)
        return
    
    def _draw_jig(self, glpane, color, highlighted = False):
        """
        [overrides superclass method]
        """
        if self._should_draw(): # this test is not present in superclass
            for a in self.atoms:
                chunk = a.molecule
                dispdef = chunk.get_dispdef(glpane)
                disp, rad = a.howdraw(dispdef)
                if self.picked:
                    rad *= 1.01
                drawwirecube(color, a.posn(), rad)
                # draw next_atom in a different color than marked_atom
                color = orange # this is the other thing that differs from superclass
        return

    def _should_draw(self):
        return pref_draw_internal_markers()

    def is_glpane_content_itself(self): #bruce 080319
        """
        @see: For documentation, see Node method docstring.

        @rtype: boolean

        [overrides Jig method, but as of 080319 has same implem]
        """
        # Note: we want this return value even if self *is* shown
        # (due to debug prefs), provided it's an internal marker.
        # It might even be desirable for other kinds of markers
        # which are not internal. See comment in Jig method,
        # for the effect of this being False for things visible in GLPane.
        # [bruce 080319]
        return False

    def gl_update_node(self): # not presently used
        """
        Cause whatever graphics areas show self to update themselves.

        [Should be made a Node API method, but revised to do the right thing
         for nodes drawn into display lists.]
        """
        self.assy.glpane.gl_update()
    
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
    
    def set_wholechain(self, wholechain, position_holder, controlling = _CONTROLLING_IS_UNKNOWN):
        """
        [to be called by dna updater]
        
        @param wholechain: a new WholeChain which now owns us (not None)
        """
        # revised 080306/080307
        assert wholechain
        self.wholechain = wholechain
        self._position_holder = position_holder
        self.set_whether_controlling(controlling) # might kill self

    def _clear_wholechain(self): # 080306
        self.wholechain = None
        self._position_holder = None
        self.controlling = _CONTROLLING_IS_UNKNOWN # 080306; never kills self [review: is that ok?]
        return
    
    def forget_wholechain(self, wholechain):
        """
        Remove any references we have to wholechain.
        
        @param wholechain: a WholeChain which refs us and is being destroyed
        """
        assert wholechain
        if self.wholechain is wholechain:
            self._clear_wholechain()
        return

    def _undo_update(self): # in class DnaMarker
        """
        """
        ## print "note: undo_update is partly nim in %r" % self
        _homeless_dna_markers[id(self)] = self # ok?? sufficient?? [080118]
        # guess, 080227: this should be enough, since our own attrs (in superclass)
        # are declared as undoable state... but just to be safe, do these as well:
        self._clear_wholechain()
            # a new one will shortly be made by the dna updater and take us over
        self._inside_its_own_strand_or_segment = False
        self._info_for_step2 = None # precaution
        _superclass._undo_update(self)
        return
    
    def remove_atom(self, atom, **opts):
        """
        [extends superclass method]
        """
        _homeless_dna_markers[id(self)] = self # TODO: also do this when copied? not sure it's needed.
        _superclass.remove_atom(self, atom, **opts)
        return

    def changed_structure(self, atom): # 080118
        """
        [extends superclass method]
        """
        # (we extend this method so that if bonds change so that marked_atom and
        #  next_atom are no longer next to one another, we'll get updated as
        #  needed.)
        _homeless_dna_markers[id(self)] = self
        _superclass.changed_structure(self, atom)
        return
        
    #e also add a method [nim in api] for influencing how we draw the atom?
    # guess: no -- might be sufficient (and is better, in case old markers lie around)
    # to just use the Jig.draw method, and draw the marker explicitly. Then it can draw
    # other graphics too, be passed style info from its DnaGroup/Strand/Segment, etc.

    # == ChainAtomMarker API methods (overridden or extended):

    # == other methods

    def getDnaGroup(self):
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
        
    def _f_get_owning_strand_or_segment(self, make = False):
        """
        [friend method for dna updater]
        Return the DnaStrand or DnaSegment which owns this marker,
        or None if there isn't one,
        even if the internal model tree
        has not yet been updated to reflect this properly
        (which may only happen when self is newly made or
         perhaps homeless).

        @param make: if True, never return None, but instead make a new
                     owning DnaStrandOrSegment and move self into it,
                     or decide that one we happen to be in can own us.
        
        Note: non-friend callers (outside the dna updater, and not running
        just after creating this before the updater has a chance to run
        or gets called explicitly) should instead use the appropriate
        method out of get_DnaStrand or get_DnaSegment.
        """
        # fyi - used in WholeChain.find_or_make_strand_or_segment
        # revised, and make added, 080222
        if self._inside_its_own_strand_or_segment:
            return self._get_DnaStrandOrSegment()
        if make:
            # if we're in a good enough one already, just make it official
            in_this_already = self._already_in_suitable_DnaStrandOrSegment()
            if in_this_already:
                self._inside_its_own_strand_or_segment = True
                return in_this_already # optim of return self._get_DnaStrandOrSegment()
            # otherwise make a new one and move into it (and return it)
            return self._make_strand_or_segment()
        return None

    def _already_in_suitable_DnaStrandOrSegment(self):
        """
        [private helper for _f_get_owning_strand_or_segment]
        We're some wholechain's controlling marker,
        but we have no owning strand or segment.
        Determine whether the one we happen to be inside (if any)
        can own us. If it can, return it (but don't make it actually
         own us). Otherwise return None.
        """
        candidate = self._get_DnaStrandOrSegment() # looks above us in model tree
        if not candidate:
            return None
        if candidate is not self.dad:
            return None
        if not isinstance( candidate, self._DnaStrandOrSegment_class):
            return None
        # does it own anyone else already?
        for member in candidate.members:
            if isinstance(member, self.__class__):
                if member._inside_its_own_strand_or_segment:
                    return None
        return candidate

    def _make_strand_or_segment(self):
        """
        [private helper for _f_get_owning_strand_or_segment]
        We're some wholechain's controlling marker,
        and we need a new owning strand or segment.
        Make one and move into it (in the model tree).
        """
        chunk = self.marked_atom.molecule # 080120 7pm untested [when written, in class WholeChain]
        # find the right DnaGroup (or make one if there is none).
        # ASSUME the chunk was created inside the right DnaGroup
        # if there is one. There is no way to check this here -- user
        # operations relying on dna updater have to put new PAM atoms
        # inside an existing DnaGroup if they want to use it.
        # We'll leave them there (or put them all into an arbitrary
        # one if different atoms in a wholechain are in different
        # DnaGroups -- which is an error by the user op).
        dnaGroup = chunk.parent_node_of_class(DnaGroup)
        if dnaGroup is None:
            # If it was not in a DnaGroup, it should not be in a DnaStrand or
            # DnaSegment either (since we should never make those without
            # immediately putting them into a valid DnaGroup or making them
            # inside one). But until we implement the group cleanup of just-
            # read mmp files, we can't assume it's not in one here!
            # However, we can ignore it if it is (discarding it and making
            # our own new one to hold our chunks and markers),
            # and just print a warning here, trusting that in the future
            # the group cleanup of just-read mmp files will fix things better.
            if chunk.parent_node_of_class(DnaStrandOrSegment):
                print "dna updater: " \
                      "will discard preexisting %r which was not in a DnaGroup" \
                      % (chunk.parent_node_of_class(DnaStrandOrSegment),), \
                      "(bug or unfixed mmp file)"
            dnaGroup = find_or_make_DnaGroup_for_homeless_object(chunk)
                # Note: all our chunks will eventually get moved from
                # whereever they are now into this new DnaGroup.
                # If some are old and have group structure around them,
                # it will be discarded. To avoid this, newly read old mmp files
                # should get preprocessed separately (as discussed also in
                # update_DNA_groups).
        # now make a strand or segment in that DnaGroup (review: in a certain subGroup?)
        strand_or_segment = dnaGroup.make_DnaStrandOrSegment_for_marker(self)
        strand_or_segment.move_into_your_members(self)
            # this is necessary for the following assignment to make sense
            # (review: is it ok that we ignore the return value here?? @@@@)
        assert self._get_DnaStrandOrSegment() is strand_or_segment
        self._inside_its_own_strand_or_segment = True
        return strand_or_segment
        
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

    # ==

    # marker move methods. These are called by dna updater and/or our new WholeChain
    # in this order: [### REVIEW, is this correct? @@@@@@] 
    # - _f_move_to_live_atompair_step1, for markers that need to move; might kill self
    # - f_kill_during_move, if wholechain scan finds problem with a marker on one of its atoms; will kill self
    # - xxx_own_marker if a wholechain takes over self ### WRONG, called later
    # - _f_move_to_live_atompair_step2, for markers for which step1 returned true (even if they were killed by f_kill_during_move)
    #   - this prints a bug warning if neither of f_kill_during_move or xx_own_marker was called since _step1 (or if _step1 not called?)
    
    def _f_move_to_live_atompair_step1(self): # rewritten 080311 ### RENAME, no step1 @@@
        """
        [friend method, called from dna_updater]

        One of our atoms died or changed structure (e.g. got rebonded).
        We still know our old wholechain and our position along it
        (since this is early during a dna updater run),
        so use that info to move a new location on our old wholechain
        so that we are on two live atoms which are adjacent on it.
        Track base position change as we do this (partly nim, since not used).
        
        If this works, return True; later updater steps must call one of XXX ###doc
        to verify our atoms are still adjacent on the same new wholechain,
        and record it and our position on it. (Also record any info they need
        to run, but for now, this is only used by assertions or debug prints,
        since just knowing our two atoms and total base index motion should
        be sufficient.)
        
        If this fails, die and return False.

        @return: whether this marker is still alive after this method runs.
        @rtype: boolean
        """
        # REVIEW: should we not return anything and just make callers check marker.killed()?
        
        if self._info_for_step2 is not None:
            print "bug? _info_for_step2 is not None as _f_move_to_live_atompair_step1 starts in %r" % self
        
        self._info_for_step2 = None
        
        # Algorithm -- just find the nearest live atom in the right direction.
        # Do this by scanning old atom lists in chain objects known to markers,
        # so no need for per-atom stored info.
        # [Possible alternative (rejected): sort new atoms for best new home -- bad,
        #  since requires storing that info on atoms, or lots of lookup.]

        if not self.is_homeless():
            # was an assert, but now I worry that some code plops us onto that list
            # for other reasons so this might not always be true, so make it safe
            # and find out (ie debug print) [bruce 080306]
            print "bug or ok?? not %r.is_homeless() in _f_move_to_live_atompair_step1" % self # might be common after undo??

        old_wholechain = self.wholechain
        if not old_wholechain:
            if debug_flags.DEBUG_DNA_UPDATER:
                print "fyi: no wholechain in %r._f_move_to_live_atompair_step1()" % self
                # I think this might be common after mmp read. If so, perhaps remove debug print.
                # In any case, tolerate it. Don't move, but do require new wholechain
                # to find us. Note: this seems to happen a lot for 1-atom chains, not sure why. @@@ DIAGNOSE
            self._info_for_step2 = True
            return not self.killed() #bruce 080318 bugfix, was return True
                # note: this can return False. I didn't verify it can return True,
                # but probably it can (e.g. after mmp read).
            # don't do:
            ## self.kill()
            ## return False

        old_atom1 = self.marked_atom
        old_atom2 = self.next_atom # might be at next higher or next lower index, or be the same

        if not old_atom1.killed() and not old_atom2.killed():
            # No need to move (note, these atoms might be the same)
            # but (if they are not the same) we don't know if they are still
            # bonded so as to be adjacent in the new wholechain. I don't yet know
            # if that will be checked in this method or a later one.
            # Also, if we return True, we may need to record what self needs to do in a later method.
            # And we may want all returns to have a uniform debug print.
            # So -- call a common submethod to do whatever needs doing when we find the
            # atom pair we might move to.
            return self._move_to(old_atom1, old_atom2)
                # note: no pos arg means we're reusing old pos

        # We need to move (or die). Find where to move to if we can.

        if old_atom1 is old_atom2:
            # We don't know which way to scan, and more importantly,
            # either this means the wholechain has length 1 or there's a bug.
            # So don't try to move in this case.
            if len(old_wholechain) != 1:
                print "bug? marker %r has only one atom but its wholechain %r is length %d (not 1)" % \
                      (self, len(old_wholechain))
            assert old_atom1.killed() # checked by prior code
            if debug_flags.DEBUG_DNA_UPDATER:
                print "kill %r since we can't move a 1-atom marker" % self
            self.kill()
            return False

        # Slide this pair of atoms along the wholechain
        # (using the pair to define a direction of sliding and the relative
        #  index of the amount of slide) until we find two adjacent unkilled
        # atoms (if such exist). Try first to right, then (if self was not a
        # ring) to the left.
        # (Detect a ring by whether the initial position gets returned at the
        #  end (which is detected by the generator and makes it stop after
        #  returning that), or by old_wholechain.ringQ (easier, do that).)

        for direction_of_slide in (1, -1):
            if old_wholechain.ringQ and direction_of_slide == -1:
                break
            pos_holder = self._position_holder
            pos_generator = pos_holder.yield_rail_index_direction_counter(
                                relative_direction = direction_of_slide,
                                counter = 0, countby = direction_of_slide,
                             )
                # todo: when markers track their current base index,
                # pass its initial value to counter
                # and our direction of motion to countby.
                # (Maybe we're already passing the right thing to countby,
                #  if base indexing always goes up in the direction
                #  from marked_atom to next_atom, but maybe it doesn't
                #  for some reason.)

            if direction_of_slide == 1:
                _check_atoms = [old_atom1, old_atom2]
                    # for assertions only -- make sure we hit these atoms first,
                    # in this order
            else:
                _check_atoms = [old_atom1] # if we knew pos of atom2 we could
                    # start there, and we could save it from when we go to the
                    # right, but there's no need.

            unkilled_atoms_posns = [] # the adjacent unkilled atoms and their posns, at current loop point

            NEED_N_ATOMS = 2 # todo: could optimize, knowing that this is 2
            
            for pos in pos_generator: 
                rail, index, direction, counter = pos
                atom = rail.baseatoms[index]
                if _check_atoms:
                    popped = _check_atoms.pop(0)
                    ## assert atom is popped - fails when i delete a few duplex atoms, then make bare axis atom
                    if not (atom is popped):
                        print "\n*** BUG: not (atom %r is _check_atoms.pop(0) %r), remaining _check_atoms %r, other data %r" % \
                              (atom, popped, _check_atoms, (unkilled_atoms_posns, self, self._position_holder))
                if not atom.killed():
                    unkilled_atoms_posns.append( (atom, pos) )
                else:
                    unkilled_atoms_posns = []
                if len(unkilled_atoms_posns) >= NEED_N_ATOMS:
                    # we found enough atoms to be our new position.
                    # (this is the only new position we'll consider --
                    #  if anything is wrong with it, we'll die.)
                    if direction_of_slide == -1:
                        unkilled_atoms_posns.reverse()
                    atom1, pos1 = unkilled_atoms_posns[-2]
                    atom2, pos2 = unkilled_atoms_posns[-1]
                    del pos2
                    return self._move_to(atom1, atom2, pos1)
                continue # next pos from pos_generator
            continue # next direction_of_slide

        # didn't find a good position to the right or left.

        if debug_flags.DEBUG_DNA_UPDATER_VERBOSE:
            print "kill %r since we can't find a place to move it to" % self
        self.kill()
        return False
    
    def _move_to(self, atom1, atom2, atom1pos = None): # revised 080311
        """
        [private helper for _move_step1; does its side effects
         for an actual or possible move, and returns its return value]
        
        Consider moving self to atom1 and atom2 at atom1pos.
        If all requirements for this being ok are met, do it
        (including telling wholechain and/or self where we moved to,
         in self.position_holder)
        (this might be done partly in _move_step2, in which case
         we must record enough info here for it to do that).
        Otherwise die.
        Return whether we're still alive after the step1 part of this.
        """
        assert not atom1.killed() and not atom2.killed()
        
        if atom1pos is not None:
            # moving to a new position
            rail, index, direction, counter = atom1pos
            del counter # in future, use this to update our baseindex
            assert atom1 is rail.baseatoms[index]
        else:
            # moving to same position we're at now (could optimize)
            rail, index, direction = self._position_holder.pos
            atom1, atom2 = self.marked_atom, self.next_atom        
            assert atom1 is rail.baseatoms[index]
        
        ok_for_step1 = True
    
        # semi-obs comment:
        # The atom pair we might move to is (atom1, atom2), at the relative
        # index relindex(?) from the index of self.marked_atom (in the direction
        # from that to self.next_atom). (This is in terms of
        # the implicit index direction in which atom2 comes after atom1, regardless
        # of internal wholechain indices, if those even exist. If we had passed
        # norepeat = False and old_wholechain was a ring, this might be
        # larger than its length as we wrapped around the ring indefinitely.) ## move some to docstring of method used in caller
        
        # We'll move to this new atom pair if they are adjacent in a new chain
        # found later (and consistent in bond direction if applicable? not sure).
        #
        # We can probably figure out whether they're adjacent right now, but for
        # now let's try waiting for the new chain and deciding then if we're
        # still ok. (Maybe we won't even have to -- maybe we could do it lazily
        # in set_whether_controlling, only checking this if we want to stay alive
        # once we know whether we're controlling. [review])

        if ok_for_step1:
            self.setAtoms([atom1, atom2]) # maybe needed even in "move to same pos" case
            self._position_holder.set_position(rail, index, direction)
                # review: probably not needed, since if we actually moved,
                # a new wholechain will take us over, so we could probably
                # set this holder as invalid instead -- not 100% sure I'm right
            self._info_for_step2 = True # this means, we do need to check atom adjacency in a later method
        else:
            # in future, whether to die here will depend on settings in self.
            # review: if we don't die here, do we return False or True?
            self.kill()
        return ok_for_step1

    def _f_kill_during_move(self, new_wholechain, why): # 080311
        """
        [friend method, called from WholeChain.__init__ during dna_updater run]
        """
        if debug_flags.DEBUG_DNA_UPDATER: # SOON: _VERBOSE
            print "_f_kill_during_move(%r, %r %r)" % (self, new_wholechain, why)
        # I think we're still on an old wholechain, so we can safely
        # die in the usual way (which calls a friend method on it).
        assert self.wholechain is not new_wholechain
        # not sure we can assert self.wholechain is not None, but find out...
        # actually this will be normal for mmp read, or other ways external code
        # can create markers, so remove when seen: @@@@
        if self.wholechain is None:
            print "\nfyi: remove when seen: self.wholechain is None during _f_kill_during_move(%r, %r, %r)" % \
                  ( self, new_wholechain, why)
        self.kill()
        self._info_for_step2 = None # for debug, record no need to do more to move self
        return

    def _f_new_position_for(self, new_wholechain, (atom1info, atom2info)): # 080311
        """
        Assuming self.marked_atom has the position info atom1info
        (a pair of rail and baseindex) and self.next_atom has atom2info
        (also checking this assumption by asserts),
        both in new_wholechain,
        figure out new position and direction for self in new_wholechain
        if we can. It's ok to rely on rail.neighbor_baseatoms
        when doing this. We need to work properly (and return proper
        direction) if one or both atoms are on a length-1 rail,
        and fail gracefully if atoms are the same and/or new_wholechain
        has only one atom.

        If we can, return new pos as a tuple (rail, baseindex, direction),
        where rail and baseindex are for atom1 (revise API if we ever
        need to swap our atoms too). Caller will make those into a
        PositionInWholeChain object for new_wholechain.

        If we can't, return None. This happens
        if our atoms are not
        adjacent in new_wholechain (too far away, or the same atom).

        Never have side effects.
        """
        rail1, baseindex1 = atom1info
        rail2, baseindex2 = atom2info

        assert self.marked_atom is rail1.baseatoms[baseindex1]
        assert self.next_atom is rail2.baseatoms[baseindex2]

        if self.marked_atom is self.next_atom:
            return None
        
        # Note: now we know our atoms differ, which rules out length 1
        # new_wholechain, which means it will yield at least two positions
        # below each time we scan its atoms, which simplifies following code.

        # Simplest way to work for different rails, either or both
        # of length 1, is to try scanning in both directions.
        
        try_these = [
            (rail1, baseindex1, 1),
            (rail1, baseindex1, -1),
         ]
        for rail, baseindex, direction in try_these:
            pos = rail, baseindex, direction
            generator = new_wholechain.yield_rail_index_direction_counter( pos )

            # I thought this should work, but it failed -- I now think it was
            # just a logic bug (since we might be at the wholechain end and
            # therefore get only one position from the generator),
            # but to remove sources of doubt, do it the more primitive
            # way below.
            ## pos_counter_A = generator.next()
            ## pos_counter_B = generator.next() # can get exceptions.StopIteration - bug?

            iter = 0
            pos_counter_A = pos_counter_B = None
            for pos_counter in generator:
                iter += 1
                if iter == 1:
                    # should always happen
                    pos_counter_A = pos_counter
                elif iter == 2:
                    # won't happen if we start at the end we scan towards
                    pos_counter_B = pos_counter
                    break
                continue
            del generator
            assert iter in (1, 2)
            railA, indexA, directionA, counter_junk = pos_counter_A
            assert (railA, indexA, directionA) == (rail, baseindex, direction)
            if iter < 2:
                ## print "fyi: only one position yielded from %r.yield_rail_index_direction_counter( %r )" % \
                ##    ( new_wholechain, pos )
                ##      # remove when debugged, this is probably normal, see comment above
                # this direction doesn't work -- no atomB!
                pass
            else:
                # this direction works iff we found the right atom
                railB, indexB, directionB, counter_junk = pos_counter_B
                atomB = railB.baseatoms[indexB]
                if atomB is self.next_atom:
                    return rail, baseindex, direction
                pass
            continue # try next direction in try_these

        return None
        
    def _f_new_pos_ok_during_move(self, new_wholechain): # 080311
        """
        [friend method, called from WholeChain.__init__ during dna_updater run]
        """
        del new_wholechain
        self._info_for_step2 = None # for debug, record no need to do more to move self
        return
    
    def _f_should_be_done_with_move(self): # 080311
        """
        [friend method, called from dna_updater]
        """
        if self.killed():
            return
        if self._info_for_step2: # TODO: fix in _undo_update @@@@@
            print "bug? marker %r was not killed or fixed after move" % self
        # Note about why we can probably assert this: Any marker
        # that moves either finds new atoms whose chain has a change
        # somewhere that leads us to find it (otherwise that chain would
        # be unchanged and could have no new connection to whatever other
        # chain lost atoms which the marker was on), or finds none, and
        # can't move, and either dies or is of no concern to us.
        self._info_for_step2 = None # don't report the same bug again for self
        return

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
    mmp_record_name = "DnaSegmentMarker"
    def get_DnaSegment(self):
        """
        Return the DnaSegment that owns us, or None if none does.
        [It's not yet decided whether the latter case can occur
        normally if we have survived a run of the dna updater.]

        @see: self.controlling, for whether we control base indexing
        (and perhaps other aspects) of the DnaSegment that owns us.

        @see: getDnaGroup
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
    mmp_record_name = "DnaStrandMarker"
    def get_DnaStrand(self):
        """
        Return the DnaStrand that owns us, or None if none does.
        [It's not yet decided whether the latter case can occur
        normally if we have survived a run of the dna updater.]

        @see: self.controlling, for whether we control base indexing
        (and perhaps other aspects) of the DnaStrand that owns us.

        @see: getDnaGroup
        """
        res = self._get_DnaStrandOrSegment()
        assert isinstance(res, DnaStrand)
        return res
    pass

# ==

class _MMP_RecordParser_for_DnaSegmentMarker( MMP_RecordParser): #bruce 080227
    """
    Read the MMP record for a DnaSegmentMarker Jig.
    """
    def read_record(self, card):
        constructor = DnaSegmentMarker
        jig = self.read_new_jig(card, constructor)
            # note: for markers with marked_atom == next_atom,
            # the mmp record will have exactly one atom;
            # current reading code trusts this and sets self._length_1_chain
            # in __init__, but it would be better to second-guess it and verify
            # that the chain is length 1, and mark self as invalid if not.
            # [bruce 080227 comment]
            #
            # note: this includes a call of self.addmember
            # to add the new jig into the model
        return
    pass

class _MMP_RecordParser_for_DnaStrandMarker( MMP_RecordParser): #bruce 080227
    """
    Read the MMP record for a DnaStrandMarker Jig.
    """
    def read_record(self, card):
        constructor = DnaStrandMarker
        jig = self.read_new_jig(card, constructor)
            # see comments in _MMP_RecordParser_for_DnaSegmentMarker
        return
    pass

def register_MMP_RecordParser_for_DnaMarkers(): #bruce 080227
    """
    [call this during init, before reading any mmp files]
    """
    register_MMP_RecordParser( DnaSegmentMarker.mmp_record_name,
                               _MMP_RecordParser_for_DnaSegmentMarker )
    register_MMP_RecordParser( DnaStrandMarker.mmp_record_name,
                               _MMP_RecordParser_for_DnaStrandMarker )
    return

# end
