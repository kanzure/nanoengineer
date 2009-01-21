# Copyright 2007-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
PAM_Atom_methods.py - methods for class Atom, which are only meant
to be called on PAM Atoms.

@author: Bruce, Mark, Ninad
@version: $Id$
@copyright: 2007-2009 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 080327 split out of chem.py class Atom,
in which these methods had been written

TODO:

REVIEW whether any of these methods are sometimes called on non-PAM atoms,
always doing nothing or returning a null value, e.g. getDnaBaseName.

also refactor some code that remains in chem.py but has
PAM-element-specific sections, like the transmute context menu
entries for PAM elements, and some bond_geometry_error_string things
(which needs a separate refactoring first, for other reasons)
"""

# WARNING: this module is imported by chem.py and therefore indirectly by
# chunk.py. Therefore its import dependence on other things needs to be
# minimized. However, it seems ok at this point to import quite a bit of dna
# updater code. Today I moved all imports to toplevel (including those with
# old warnings that that didn't work when they were written) and experienced
# no problems.

# Even so, further refactoring (which among other things would mitigate this)
# is desirable. (The ultimate issue is having PAM-specific methods on class
# Atom, as opposed to on a PAM-specific subclass of class Atom; and having
# that class Atom known directly to class Chunk.) [bruce 090119]

from Numeric import dot

from geometry.VQT import norm, V

##from foundation.state_constants import S_CHILDREN

from utilities import debug_flags

from utilities.debug import print_compact_stack

from utilities.constants import Pl_STICKY_BOND_DIRECTION, MODEL_PAM5
from utilities.constants import average_value

from model.bond_constants import DIRBOND_CHAIN_MIDDLE
from model.bond_constants import DIRBOND_CHAIN_END
from model.bond_constants import DIRBOND_NONE
from model.bond_constants import DIRBOND_ERROR
from model.bond_constants import find_bond

from model.elements import Pl5

from model.global_model_changedicts import _changed_otherwise_Atoms 

from dna.model.pam3plus5_math import baseframe_abs_to_rel
from dna.model.pam3plus5_math import baseframe_rel_to_abs
from dna.model.pam3plus5_math import default_Pl_relative_position
from dna.model.pam3plus5_math import default_Gv_relative_position

from dna.model.pam3plus5_ops import Pl_pos_from_neighbor_PAM3plus5_data
from dna.model.pam3plus5_ops import _f_baseframe_data_at_baseatom
from dna.model.pam3plus5_ops import _f_find_new_ladder_location_of_baseatom
from dna.model.pam3plus5_ops import kill_Pl_and_rebond_neighbors

from dna.model.pam_conversion_mmp import Fake_Pl

from dna.updater.dna_updater_prefs import legal_numbers_of_strand_neighbors_on_axis

from dna.updater.fix_bond_directions import PROPOGATED_DNA_UPDATER_ERROR
from dna.updater.fix_bond_directions import _f_detailed_dna_updater_error_string

VALID_ELEMENTS_FOR_DNABASENAME = ('Ss5', 'Ss3', 'Sh5', 'Se3', 'Sj5', 'Sj3',)
    # TODO: use a boolean element attribute instead.
    # review: not the same as role == 'strand'... but is it if we exclude Pl?

def make_vec_perp_to_vec(vec1, vec2): #bruce 080405
    # todo: refile, or find an existing func the same
    """
    return a modified copy of vec1 with its component parallel to vec2 subtracted out.
    """
    remove_this_direction = norm(vec2)
    return vec1 - dot(vec1, remove_this_direction) * remove_this_direction #k

_GV5_DATA_INDEX = 2

# ==

class PAM_Atom_methods:
    """
    Intended only as a pre-mixin for class Atom.
    """
    # Someday will be refactored into subclasses of Atom.
    # Then those can be moved inside the dna package.
    # (Maybe this could be moved there right now?)

    # ===
    #
    # The Atom methods below this point might be moved into subclasses for
    # specific types of atoms.
    #
    # (Some of these methods might need trivial default defs on class Atom
    #  until old code is fully revised to only call them on the subclasses.)
    #
    # Several general methods above also have special cases that might be
    # revised to be in subclass methods that extend them. These include:
    #
    #  drawing_color
    #  _draw_atom_style
    #  draw_atom_sphere
    #  draw_wirespheres
    #  max_pixel_radius
    #  writemmp
    #  readmmp_info_atom_setitem
    #  getInformationString
    #
    # (But some of these might be purely graphical, perhaps usable by more than
    # one subclass, and might thus remain in the superclass, or in a separately
    # refactored Atom drawing controller class.)
    #
    # [bruce 071113 comment, and reordered existing methods to move these here]
    #
    # ===

    # default values of instance variables (some not needed):

    _dna_updater__error = "" # intentionally not undoable/copyable

    # this is now higher up, with an undo _s_attr decl:
    ## _dnaBaseName = "" #bruce 080319 revised

    # note: _dnaStrandId_for_generators is set when first demanded, or can be
    # explicitly set using setDnaStrandId_for_generators().

    _fake_Pls = None # see comments where used

    _DnaLadder__ladder = None # for private use by class DnaLadder
        # note: not named with _f_, so I can use the pseudo-name-mangling
        # convention to indicate ownership by objects of a different class
        # [bruce 080413 added class definition, revised using code]

    # not: _s_attr__nonlive_Pls = S_CHILDREN

    # for default value assignments of _PAM3plus5_Pl_Gv_data and
    # _f_Pl_posn_is_definitive, and comments about them, see class Atom
    # (which inherits this class); they are only used by methods in this
    # class, except for a few foundational methods in class Atom
    # (for copy and soon for mmp save/load), but since it uses them
    # at all, we define them there. [bruce 080523]
    #
    # _PAM3plus5_Pl_Gv_data = ...
    # 
    # _f_Pl_posn_is_definitive = ...
    
    # == methods for either strand or axis PAM atoms

    def dna_updater_error_string(self,
                                 include_propogated_error_details = True,
                                 newline = '\n'
                                 ):
        #bruce 080206; 080214 also covers check_bond_geometry
        ### REVIEW: integrate with bad_valence etc
        """
        Return "" if self has no dna updater error (recorded by the dna updater
        in the private attribute self._dna_updater__error), or an error string
        if it does.

        By default, the error string is expanded to show the source
        of propogated errors from elsewhere in self's basepair (assuming the updater
        has gotten through the step of propogating them, which it does immediately
        after assigning/updating all the direct per-atom error strings).

        Any newlines in the error string (which only occur if it was expanded)
        are replaced with the optional newline argument (by default, left unchanged).

        @param include_propogated_error_details: see main docstring
        @type include_propogated_error_details: boolean

        @param newline: see main docstring
        @type newline: string

        @see: helper functions like _atom_set_dna_updater_error which should
              eventually become friend methods in a subclass of Atom.
        """
        if self.check_bond_geometry():
            # bruce 080214; initial kluge --
            # if this happens, ignore the rest (non-ideal)
            return self.check_bond_geometry() # (redoing this is fast)
        if not self._dna_updater__error:
            # report errors from self's DnaLadder, if it has one
            ladder = getattr(self.molecule, 'ladder', None) # kluge for .ladder
            if ladder and ladder.error:
                return ladder.error
            return ""
        # otherwise report error from self
        res = self._dna_updater__error
        if include_propogated_error_details and \
           res == PROPOGATED_DNA_UPDATER_ERROR:
            res = _f_detailed_dna_updater_error_string(self)
        res = res.replace('\n', newline) # probably only needed in then clause
        return res

    def _pam_atom_cmenu_entries(self): #bruce 080401
        """
        Return a menu_spec list of context menu entries specific to self being
        a PAM atom, or None.
        """
        assert self.element.pam
        ladder = self.molecule.ladder
        res = []
        if ladder:
            dnaladder_menu_spec = ladder.dnaladder_menu_spec(self)
            if dnaladder_menu_spec:
                if res: # never happens yet
                    res.append(None)
                res.extend(dnaladder_menu_spec)
            # more?
            pass
        return res

    def reposition_baggage_using_DnaLadder(self,
                                           dont_use_ladder = False,
                                           only_bondpoints = False
                                           ):
        #bruce 080404; added options, bruce 080501
        """
        Reposition self's bondpoints (or other monovalent "baggage" atoms
        if any), making use of structural info from self.molecule.ladder.

        @note: as of late 080405, this doesn't yet actually make use of
               self.molecule.ladder. (Perhaps it could be optimized by
               making it do so?)

        @note: since we don't expect any baggage except bondpoints on PAM atoms,
               we don't bother checking for that, even though, if this did
               ever happen, it might be arbitrary which baggage element ended
               up at what position. This can easily be fixed if necessary.

        @warning: by default, it's only safe to call this when self.molecule.ladder
                  is correct (including all its chunks and rails --
                  no need for its parent Group structure or markers),
                  which if the dna updater is running means after self's
                  new ladder's chunks were remade.

        @param dont_use_ladder: if true, don't assume self.molecule.ladder is
                                correct. (As of 080501, this option has no
                                effect, since the current implem doesn't use
                                self.molecule.ladder or anything else fixed
                                by the dna updater, except possibly bond
                                directions on open bonds.)

        @type dont_use_ladder: boolean

        @param only_bondpoints: if true, only reposition bondpoints, not other
                                baggage.

        @type only_bondpoints: boolean
        """
        # And, if it turns out this ever needs to look inside
        # neighbor atom dnaladders (not in the same base pair),
        # we'll need to revise the dna updater's indirect caller
        # to call it in a separate loop over ladders than the one
        # that calls remake_chunks on all of the new ladders.

        # Note: I don't think there's any issue of the changes we do here
        # causing an infinite repeat (or even a single repeat) of the
        # dna updater -- we reset the flag that makes it call us,
        # and moving bondpoints (or real atoms) doesn't count as
        # changing the atoms for purposes of dna updater, and even
        # if it did, the updater ignores new changes from this step.
        # If we ever kill and remake bondpoints here, then we'll
        # need to also reset the flag at the end, but even if we forget,
        # it won't cause an immediate rerun of the dna updater
        # (due to its ignoring the changes from this step).

        self._f_dna_updater_should_reposition_baggage = False
            # even in case of exceptions (also simplifies early return)

        del dont_use_ladder # correct, since present implem never uses it

        baggage, others = self.baggage_and_other_neighbors()

        if only_bondpoints: # bruce 080501
            for n in baggage[:]:
                if not n.is_singlet():
                    baggage.remove(n)
                    others.append(n)
                continue
            pass

        if not baggage:
            return # optimization and for safety; might simplify following code

        # Notes:
        #
        # - If baggage might not be all bondpoints, we might want to filter
        #   it here and only look at the bondpoints. (See docstring.)
        #   [Now this is done by the only_bondpoints option. [bruce 080501]]
        #
        # - I'm assuming that Ax, Pl, Ss neighbors can never be baggage.
        #   This depends on their having correct valence, since the test
        #   used by baggage_and_other_neighbors is len(bonds), not valence.

        # how to do it depends on type of PAM element:
        if self.element.role == 'axis': # Ax3, Ax5, or Gv5
            # which real neighbors do we have?
            # (depends on ladder len1, single strand or duplex)
            # ...
            # short term important case: we have one bondpoint
            # along axis, make it opposite the other axis bond,
            # and maybe we also have another "strand bondpoint".
            strand_neighbors = []
            axis_neighbors = []
            for other in others: # would also work if baggage was in this loop
                role = other.element.role
                if role == 'strand':
                    strand_neighbors += [other]
                elif role == 'axis':
                    axis_neighbors += [other]
                # other roles are possible too, but we can ignore them for now
                # (unpaired-base(?), None)
                # (in future we'll need to count unpaired-bases to understand
                #  how many axis bondpoints are missing) ### TODO
                continue
            if len(axis_neighbors) == 1:
                # move a bondpoint to the opposite position from this one
                # (for now, just move the already-closest one)
                selfpos = self.posn()
                axisvec = axis_neighbors[0].posn() - selfpos
                newpos = selfpos - axisvec # correct only in direction, not distance
                moved_this_one = self.move_closest_baggage_to(
                    newpos,
                    baggage,
                    remove = True,
                    min_bond_length = 3.180 / 2 )
                    # this first corrects newpos for distance (since no option
                    # prevents that) (an option does set the minimum distance
                    # -- after 080405 fix in _compute_bond_params this is no
                    # longer needed, but remains as a precaution)
                    # (doing it first is best for finding closest one)
                    # (someday we might pass bond order or direction to help 
                    #  choose? then bond order would affect distance, perhaps)

                    # passing baggage means only consider moving something 
                    # in that list;
                    # remove = True means remove the moved one from that list;
                    # return value is the one moved, or None if none was found
                    # to move.
                if not moved_this_one:
                    return # optim?
                pass
            ### todo: also fix bondpoints meant to go to strand atoms
            pass
        elif self.element.role == 'strand': # might be Pl5 or Ss5 or Ss3
            if self.element.symbol == 'Ss3':
                ### TODO: split this section into its own method
                
                # if we have one real strand bond, make the open directional
                # bond opposite it (assume we have correct structure of
                # directional bonds with direction set -- one in, one out)
                strand_neighbors = []
                axis_neighbors = []
                for other in others:
                    role = other.element.role
                    if role == 'strand':
                        strand_neighbors += [other]
                    elif role == 'axis':
                        axis_neighbors += [other]
                    continue
                honorary_strand_neighbor = None # might be set below
                reference_strand_neighbor = None # might be set below
                if len(strand_neighbors) == 1:
                    reference_strand_neighbor = strand_neighbors[0]
                elif not strand_neighbors and not axis_neighbors:
                    # totally bare (e.g. just deposited)
                    reference_strand_neighbor = self.next_atom_in_bond_direction(1)
                    # should exist, but no need to check here
                if reference_strand_neighbor is not None:
                    direction_to_it = find_bond(self, 
                        reference_strand_neighbor).bond_direction_from(self)
                    moveme = self.next_atom_in_bond_direction( - direction_to_it )
                    if moveme is not None and moveme in baggage:
                        honorary_strand_neighbor = moveme
                        selfpos = self.posn()
                        strandvec = reference_strand_neighbor.posn() - selfpos
                        newpos = selfpos - strandvec
                            # correct only in direction, not distance
                        moved_this_one = self.move_closest_baggage_to(
                            newpos,
                            [moveme] )
                        if moved_this_one is not moveme:
                            # should never happen
                            print "error: moved_this_one %r is not moveme %r" % \
                                  (moved_this_one, moveme)
                        pass
                    pass
                if len(axis_neighbors) == 0:
                    # see if we can figure out which baggage should point towards axis
                    candidates = list(baggage)
                    if honorary_strand_neighbor is not None:
                        # it's in baggage, by construction above
                        candidates.remove(honorary_strand_neighbor)
                    if reference_strand_neighbor is not None \
                       and reference_strand_neighbor in candidates:
                        candidates.remove(reference_strand_neighbor)
                    if len(candidates) != 1:
                        # I don't know if this ever happens (didn't see it in test,
                        #  can't recall if I thought it should be possible)
                        ## print " for %r: candidates empty or ambiguous:" % self, candidates
                        pass
                    else:
                        # this is the honorary axis neighbor; we'll repoint it.
                        honorary_axis_neighbor = candidates[0]
                        # but which way should it point? just "not along the strand"?
                        # parallel to the next strand atom's? that makes sense...
                        # we'll start with that if we have it (otherwise with 
                        # whatever it already is),
                        # then correct it to be perp to our strand.
                        axisvecs_from_strand_neighbors = []
                        for sn in strand_neighbors: # real ones only
                            its_axisbond = None # might be set below
                            its_rung_bonds = [b 
                                              for b in sn.bonds 
                                              if b.is_rung_bond() ]
                            if len(its_rung_bonds) == 1:
                                its_axisbond = its_rung_bonds[0]
                            elif not its_rung_bonds:
                                its_runglike_bonds = \
                                    [b 
                                     for b in sn.bonds 
                                     if not b.bond_direction_from(sn) ]
                                    # might be rung bonds, might be open bonds with
                                    # no direction set
                                if len(its_runglike_bonds) == 1:
                                    its_axisbond = its_runglike_bonds[0]
                            if its_axisbond is not None:
                                # that gives us the direction to start with
                                axisvec_sn = its_axisbond.spatial_direction_from(sn)
                                # but correct it to be perpendicular to our bond to sn
                                axisvec_sn = make_vec_perp_to_vec(
                                                axisvec_sn, 
                                                sn.posn() - self.posn() )
                                axisvecs_from_strand_neighbors += [axisvec_sn]
                            continue
                        axisvec = None # might be set below
                        if axisvecs_from_strand_neighbors:
                            axisvec = average_value(axisvecs_from_strand_neighbors)
                        if axisvec is None: # i.e. no strand_neighbors
                            axisvec = honorary_axis_neighbor.posn() - self.posn() 
                                # this value (which it has now) would not change it
                            # print " for %r: axisvec %r starts as" % (self, axisvec,)
                            # now remove the component parallel to the presumed 
                            # strand bonds' average direction
                            presumed_strand_baggage = filter( None,
                                [reference_strand_neighbor, honorary_strand_neighbor] )
                            vecs = [norm(find_bond(self, sn).bond_direction_vector()) 
                                    for sn in presumed_strand_baggage]
                            if vecs:
                                strand_direction = average_value(vecs)
                                axisvec = make_vec_perp_to_vec( axisvec,
                                                                strand_direction )
                            pass
                        assert axisvec is not None
                        self.move_closest_baggage_to( self.posn() + axisvec,
                                                      [honorary_axis_neighbor] )
                        # assume it worked (since all candidates were in baggage)
                        pass
                    pass
                pass
            pass
        # (no other cases are possible yet, at least when called by dna updater)
        # (flag was reset above, so we're done)
        return

    # == end of methods for either strand or axis PAM atoms

    # == PAM Pl atom methods

    def Pl_preferred_Ss_neighbor(self): # bruce 080118, revised 080401
        """
        For self a Pl atom (PAM5), return the Ss neighbor
        it prefers to be grouped with (e.g. in the same chunk,
        or when one of its bonds is broken) if it has a choice.

        (If it has no Ss atom, print bug warning and return None.)

        @warning: the bond direction constant hardcoded into this method
        is an ARBITRARY GUESS as of 080118. Also it ought to be defined
        in some dna-related constants file (once this method is moved
        to a dna-related subclass of Atom).
        """
        assert self.element is Pl5
        candidates = [
            # note: these might be None, or conceivably a non-Ss atom
            self.next_atom_in_bond_direction( Pl_STICKY_BOND_DIRECTION),
            self.next_atom_in_bond_direction( - Pl_STICKY_BOND_DIRECTION)
        ]
        candidates = [c
                      for c in candidates
                      if c is not None and \
                      c.element.symbol.startswith("Ss")
                      # KLUGE, matches Ss3 or Ss5
                  ]
            # note: this cond excludes X (good), Pl (bug if happens, but good).
            # It also excludes Sj and Hp (bad), but is only used from dna updater
            # so that won't be an issue. Non-kluge variant would test for
            # "a strand base atom".
        ## if debug_pref("DNA: Pl5 stick with PAM5 over PAM3 chunk, " \
        ##               "regardless of bond direction?", ...):
        if 0: # see if this caused my last bridging Pl bug, bruce 080413 330pm PT:
            candidates_PAM5 = [c for c in candidates if c.element.pam == MODEL_PAM5]
                # Try these first, so we prefer Ss5 over Ss3 if both are present,
                # regardless of bond direction. [bruce 080401]
            candidates = candidates_PAM5 + candidates
##        for candidate in candidates:
##            if ...:
##                return candidate
        # all necessary tests were done above -- just return first one, 
        # if any are there
        if candidates:
            return candidates[0]
        print "bug: Pl with no Ss: %r" % self
            # only a true statement (that this is a bug) when dna updater
            # is enabled, but that's ok since we're only used then
        return None

    def _f_Pl_finish_converting_if_needed(self):
        """
        [friend method for dna updater]

        Assume self is a Pl5 atom between two Ss3 or Ss5 atoms
        (or between one such atom and a bondpoint),
        in the same or different DnaLadders, WHICH MAY NOT HAVE YET REMADE
        THEIR CHUNKS (i.e. which may differ from atom.molecule.ladder for
         their atoms, if that even exists), which have finished doing
        a pam conversion or decided not to or didn't need to
        (i.e. which are in their proper post-conversion choice of model),
        and that self has proper directional bonds.

        Figure out whether self should continue to exist.
        (This is true iff either neighbor is a PAM5 atom, presumably Ss5.)

        If not, kill self and directly bond its neighbors,
        also recording its position on the neighbors which are Ss3 or Ss5
        if its position is definitive
        (if it's not, it means this already happened -- maybe not possible,
         not sure). (This won't be called twice on self; assert that
         by asserting self is not killed.)

        If so, ensure self's position is definitive, which means, if it's not,
        make it so by setting it from the "+5 data" on self's Ss neighbors
        intended for self, and removing that data. (This method can be
        called twice on self in this case; self's position would typically be
        non-definitive the first time and (due to our side effect that time)
        definitive the second time.)
        """
        assert not self.killed()
        sn = self.strand_neighbors() # doesn't include bondpoints
        pam5_neighbors = [n for n in sn if n.element.pam == MODEL_PAM5]
        should_exist = not not pam5_neighbors
        if not should_exist:
            # make sure it's not due to being called when we have no strand
            # neighbors (bare Pl) (this method is not legal to call then)
            assert sn, "error: %r._f_Pl_finish_converting_if_needed() " \
                       "illegal since no strand neighbors" % self
            if self._f_Pl_posn_is_definitive:
                self._f_Pl_store_position_into_Ss3plus5_data()
                    # sets flag to false
            if debug_flags.DEBUG_DNA_UPDATER_VERBOSE: # 080413
                print "fyi: stored pos of %r, "\
                      "will kill it and rebond neighbors" % self
            kill_Pl_and_rebond_neighbors(self)
            ###REVIEW: does killing self mess up its chain or its DnaLadderRailChunk?
            # (when called from dna updater, those are already invalid, they're
            # not the new ones we worry about -- UNLESS self was old and untouched
            # except by this corner Pl. That issue is a predicted unresolved bug
            # as of 080412 11:54pm PT. #### @@@@)
        else:
            if not self._f_Pl_posn_is_definitive:
                self._f_Pl_set_position_from_Ss3plus5_data()
                    # sets flag to true
            if debug_flags.DEBUG_DNA_UPDATER_VERBOSE: # 080413
                print "fyi: fixed pos of %r, keeping it" % self
        return

    def _f_Pl_set_position_from_Ss3plus5_data(self): #bruce 080402
        """
        [friend method for dna updater]

        Assume self is a Pl5 atom between two Ss3 or Ss5 atoms,
        in the same or different DnaLadders, WHICH MAY NOT HAVE YET REMADE
        THEIR CHUNKS (i.e. which may differ from atom.molecule.ladder for
        their atoms, if that even exists),
        and that self has proper directional bonds,
        and that self's current position is meaningless or out of date
        (and should be ignored).

        Set self's position using the "PAM3plus5 Pl-position data" (if any)
        stored on its neighbors, and remove that data from its neighbors.
        (If that data is not present, use reasonable defaults.)

        (Note that the analogous method on class Fake_Pl would *not*
         remove that data from its neighbors.)

        Assume that self's neighbors' DnaLadders (which, like self's,
        may not yet have remade their chunks) have up-to-date stored
        PAM basepair baseframe data to help do the necessary coordinate
        conversions. (This might not be checked. Using out of date data
        would cause hard-to-notice bugs.)

        No effect on other "PAM3plus5 data" (if any) on those neighbors
        (e.g. Gv-position data).
        """
        assert not self._f_Pl_posn_is_definitive

        # note: the following function is also called by class Fake_Pl

        abspos = Pl_pos_from_neighbor_PAM3plus5_data(
            self.bond_directions_to_neighbors(),
            remove_data_from_neighbors = True
        )

        # print "_f_Pl_set_position_from_Ss3plus5_data will set %r " \
        #       "on %r, now at %r" % (abspos, self, self.posn())

        if abspos is None:
            print "bug: _f_Pl_set_position_from_Ss3plus5_data " \
                  "can't set %r on %r, now at %r" % \
                  (abspos, self, self.posn())
        else:
            self.setposn(abspos)

        del self._f_Pl_posn_is_definitive
            # like doing self._f_Pl_posn_is_definitive = True,
            # but expose class default value to save RAM
        return

    def _f_Pl_store_position_into_Ss3plus5_data(self): #bruce 080402
        """
        [friend method for dna updater]

        Assume self is a Pl5 atom between two Ss3 or Ss5 atoms,
        in the same or different newly made DnaLadders -- WHICH MAY NOT
        HAVE YET REMADE THEIR CHUNKS (i.e. which may differ from atom.
         molecule.ladder for their atoms, if that even exists) --
        and that self has proper directional bonds,
        and that self's current position is definitive
        (i.e. that any "PAM3plus5 Pl-position data" on self's
         neighbors should be ignored, and can be entirely replaced).

        Set the "PAM3plus5 Pl-position data" on self's Ss3 or Ss5
        neighbors to correspond to self's current position.
        (This means that self will soon be killed, with its neighbors
         rebonded, and transmuted to Ss3 if necessary, but all that is
         up to the caller.)

        Assume that self's neighbors' DnaLadders have up-to-date stored
        PAM basepair baseframe data to help do the necessary coordinate
        conversions. (This might not be checked. Using out of date data
        would cause hard-to-notice bugs. Note that the global formerly called
        ladders_dict only assures that the baseframes are set at the ends.)

        No effect on other "PAM3plus5 data" (if any) on those neighbors
        (e.g. Gv-position data).

        @see: _f_Gv_store_position_into_Ss3plus5_data
        """
        assert self.element is Pl5
        assert self._f_Pl_posn_is_definitive

        # note: unlike with _f_Pl_set_position_from_Ss3plus5_data,
        # this method has no analogous method used during writemmp-only
        # PAM conversion -- either we're saving as PAM5 (moving data
        # onto Pl, not off of it), or as pure PAM3 (no Pl data at all).
        # PAM3+5 itself has no mmp format.

        pos = self.posn()
        for direction_to, ss in self.bond_directions_to_neighbors():
            if ss.element.role == 'strand':
                # (avoid bondpoints or (erroneous) non-PAM or axis atoms)
                ss._f_store_PAM3plus5_Pl_abs_position( - direction_to, pos)
            continue

        self._f_Pl_posn_is_definitive = False
        return

    def _f_Gv_store_position_into_Ss3plus5_data(self): # todo: refile within class
        #bruce 080409, modified from _f_Pl_store_position_into_Ss3plus5_data
        """
        [friend method for dna updater]

        Assume self is (or very recently was transmuted from??)
        a Gv5 atom axially between two Ss3 or Ss5 atoms
        (connected by rung bonds, in the same base pair),
        in the same DnaLadder (valid and error-free),
        and that self's current position is definitive
        (i.e. that any "PAM3plus5 Gv-position data" on self's
         neighbors should be ignored, and can be entirely replaced),
        as is true for all live Gv's except *very* transiently when they
        are created or removed during PAM conversion.

        Set the "PAM3plus5 Gv-position data" on self's Ss3 or Ss5
        neighbors to correspond to self's current position.
        (This means that self will soon be moved or transmuted
         (or perhaps just has been??), with its neighbors
         also transmuted to Ss3 if necessary, but all that is
         up to the caller.)

        Assume that self's DnaLadder -- WHICH MAY NOT HAVE YET REMADE ITS CHUNKS
        (i.e. which may differ from atom.molecule.ladder for its atoms, if that
         even exists) -- has up-to-date stored PAM basepair baseframe data to
        help do the necessary coordinate conversions. (This might not be checked.
        Using out of date data would cause hard-to-notice bugs. Note that the
        global formerly called ladders_dict only assures that the baseframes
        are set for the basepairs at the ends of a ladder.)

        No effect on other "PAM3plus5 data" (if any) on self's neighbors
        (e.g. Pl-position data).

        @see: _f_Pl_store_position_into_Ss3plus5_data
        """
        assert self.element.role == 'axis'
        pos = self.posn()
        sn = self.strand_neighbors()
        if len(sn) != 2:
            print "bug? %r has unexpected number of strand_neighbors %r" % (self, sn)
            # since ghost bases should be added to bring this up to 2
        for ss in sn:
            assert ss.element.role == 'strand'
                # (avoid bondpoints or (erroneous) non-PAM or axis atoms)
            ss._f_store_PAM3plus5_Gv_abs_position( pos)
            continue
        return

    # == end of PAM Pl atom methods

    # == PAM strand atom methods (some are more specific than that,
    # e.g. not on Pl or only on Pl, but these are not yet divided up
    # except that some methods or attrs have Pl or Ss in their names,
    # and some of those have been moved into the Pl atom methods section above)

    def _writemmp_PAM3plus5_Pl_Gv_data( self, mapping): #bruce 080523
        """
        Write the mmp info record (or similar extra data)
        which represents a non-default value of self._PAM3plus5_Pl_Gv_data.
        """
        vecs = self._PAM3plus5_Pl_Gv_data
        assert vecs is not None
        # should be a list of 3 standard "atom position vectors"
        # (they are relative rather than absolute, but can still
        #  be written in the same manner as atom positions)
        record = "info atom +5data =" # will be extended below
        for vec in vecs:
            if vec is None:
                vecstring = " ()" # (guessing this is easier to read than None)
            else:
                xs, ys, zs = mapping.encode_atom_coordinates( vec )
                vecstring = " (%s, %s, %s)" % (xs, ys, zs)
                    # note: 4 of these chars could be left out if we wanted to
                    # optimize the format
            record += vecstring
        record += "\n"
        mapping.write( record)
        return

    def _readmmp_3plus5_data(self, key, val, interp): #bruce 080523
        """
        Read the value part of the mmp info record
        which represents a non-default value of self._PAM3plus5_Pl_Gv_data.
        Raise exceptions on errors.

        @param val:
        @type val: string
        """
        del key
        val = val.replace("()", "(None, None, None)") # kluge, for convenience
        for ignore in "(),":
            val = val.replace(ignore, " ") # ditto
        val = val.strip()
        coord_strings = val.split()
        assert len(coord_strings) == 9, "wrong length: %r" % (coord_strings,)
        def decode(coord_string):
            if coord_string == "None":
                return None
            return interp.decode_atom_coordinate(coord_string)
        coords = map( decode, coord_strings) # each element is a float or None
        def decode_coords( x, y, z ):
            if x is None or y is None or z is None:
                return None
            return V(x, y, z)
        x1, y1, z1, x2, y2, z2, x3, y3, z3 = coords
        d1 = decode_coords(x1, y1, z1)
        d2 = decode_coords(x2, y2, z2)
        d3 = decode_coords(x3, y3, z3)
        self._PAM3plus5_Pl_Gv_data = [d1, d2, d3]
        return

    def setDnaBaseName(self, dnaBaseName): # Mark 2007-08-16
        #bruce 080319 revised, mainly to support undo/copy
        """
        Set the Dna base letter. This is only valid for PAM atoms in the list
        VALID_ELEMENTS_FOR_DNABASENAME, i.e. strand sugar atoms,
        presently defined as ('Ss5', 'Ss3', 'Sh5', 'Se3', 'Sj5', 'Sj3').

        @param dnaBaseName: The DNA base letter. This must be "" or one letter
                            (this requirement is only partially enforced here).
        @type  dnaBaseName: str

        @raise: AssertionError, if self is not a strand sugar atom or if we
                notice the value is not permitted.
        """
        assert type(dnaBaseName) == type("") #bruce 080326

        assert self.element.symbol in VALID_ELEMENTS_FOR_DNABASENAME, \
               "Can only assign dnaBaseNames to PAM strand sugar atoms. " \
               "Attempting to assign dnaBaseName %r to %r of element %r." \
               % (dnaBaseName, self, self.element.name)

        if dnaBaseName == 'X':
            dnaBaseName = ""

        assert len(dnaBaseName) <= 1, \
               "dnaBaseName must be empty or a single letter, not %r" % \
               (dnaBaseName,) #bruce 080326

        # todo: check that it's a letter
        # maybe: canonicalize the case; if not, make sure it doesn't matter

        if self._dnaBaseName != dnaBaseName:
            self._dnaBaseName = dnaBaseName
            _changed_otherwise_Atoms[self.key] = self #bruce 080319
            # todo: in certain display styles (which display dna base letters), 
            # call self.molecule.changeapp(0)
            self.changed() # bruce 080319
        return

    def getDnaBaseName(self):
        """
        Returns the value of attr I{_dnaBaseName}.

        @return: The DNA base name, or None if the attr I{_dnaBaseName} does 
                 not exist.
        @rtype:  str
        """
        # Note: bruce 080311 revised all direct accesses of atom._dnaBaseName
        # to go through this method, and renamed it to be private.
        # (I also stopped storing it in mmp file when value is X, unassigned.
        #  This is desirable to save space and speed up save and load.
        #  If some users of this method want the value on certain atoms
        #  to always exist, this method should be revised to look at
        #  the element type and return 'X' instead of "" for appropriate
        #  elements.)

        #UPDATE: The following is now revised per above coment. i.e. if it 
        #can't find a baseName for a valid element symbol (see list below)
        #it makes the dnaBaseName as 'X' (unassigned base) . This is useful 
        #while reading in the strand sequence. See chunk.getStrandSequence()
        #or DnaStrand.getStrandSequence() for an example. --Ninad 2008-03-12

        valid_element_symbols = VALID_ELEMENTS_FOR_DNABASENAME
        allowed_on_this_element = (self.element.symbol in valid_element_symbols)

        baseNameString = self.__dict__.get('_dnaBaseName', "") # modified below

        if not allowed_on_this_element:
            #bruce 080319 change: enforce this never existing on disallowed
            # element (probably just a clarification, since setting code was
            # probably already enforcing this)
            baseNameString = ""
        else:
            if not baseNameString:
                baseNameString = 'X' # unassigned base
            pass

        if len(baseNameString) > 1:
            #bruce 080326 precaution, should never happen
            baseNameString = ""

        return baseNameString

    def get_strand_atom_mate(self):
        """
        Returns the 'mate' of this dna pseudo atom (the atom on another strand 
        to which this atom is "base-paired"), or None if it has no mate.
        @return: B{Atom} (PAM atom) 
        """
        #Note: This method was created to support assignment of strand sequence 
        #to strand chunks. This should be moved to dna_model and
        #can be revised further. -- Ninad 2008-01-14
        # (I revised it slightly, to support all kinds of single stranded
        #  regions. -- Bruce 080117)
        if self.element.role != 'strand':
            # REVIEW: return None, or raise exception? [bruce 080117 Q]
            return None

        #First find the connected axis neighbor 
        axisAtom = self.axis_neighbor()
        if axisAtom is None:
            # single stranded region without Ax; no mate
            return None
        #Now find the strand atoms connected to this axis atom
        strandAtoms = axisAtom.strand_neighbors()

        #... and we want the mate atom of self
        for atm in strandAtoms:
            if atm is not self:
                return atm
        # if we didn't return above, there is no mate
        # (single stranded region with Ax)
        return None

    def setDnaStrandId_for_generators(self, dnaStrandId_for_generators): # Mark 070904
        """
        Set the Dna strand name. This is only valid for PAM atoms in the list
        'Se3', 'Pe5', 'Pl5' (all deprecated when the dna updater is active).

        @param dnaStrandId_for_generators: The DNA strand id used by the 
               dna generator 

        @type  dnaStrandId_for_generators: str

        @raise: AssertionError if self is not a Se3 or Pe5 or Pl5 atom.
        @see: self.getDnaStrandId_for_generators() for more comments.
        """
        # Note: this (and probably its calls) needs revision
        # for the dna data model. Ultimately its only use will be
        # to help when reading pre-data-model mmp files. Presently
        # it's only called when reading "info atom dnaStrandName"
        # records. Those might be saved on the wrong atomtypes
        # by current dna updater code, but the caller tolerates
        # exceptions here (but complains using a history summary).
        # [bruce 080225/080311 comment]
        assert self.element.symbol in ('Se3', 'Pe5', 'Pl5'), \
               "Can only assign dnaStrandNames to Se3, Pe5, or Pl5 (PAM) atoms. " \
               "Attempting to assign dnaStrandName %r to %r of element %r." \
               % (dnaStrandId_for_generators, self, self.element.name)

        # Make sure dnaStrandId_for_generators has all valid characters.
        #@ Need to allow digits and letters. Mark 2007-09-04
        #
        ## for c in dnaStrandId_for_generators:
        ##     if not c in string.letters:
        ##         assert 0, "Strand id for generatos %r has an invalid " \
        ##                "character (%r)." % \
        ##                (dnaStrandId_for_generators, c)

        self._dnaStrandId_for_generators = dnaStrandId_for_generators
        
    def getDnaStrand(self):
        """
        Returns the DnaStrand(group) node to which this atom belongs to. 
        
        Returns None if there isn't a parent DnaStrand group.
        @see: Chunk.getDnaStrand() which is used here. 
        """
        chunk = self.molecule
        
        if chunk and not chunk.isNullChunk():
            return chunk.getDnaStrand()
                    
        return None
    
    def getDnaSegment(self):
        """
        Returns the DnaSegment(group) node to which this atom belongs to. 
        
        Returns None if there isn't a parent DnaSegment group.
        @see: Chunk.getDnaSegment() which is used here. 
        """
        chunk = self.molecule
        
        if chunk and not chunk.isNullChunk():
            return chunk.getDnaSegment()
                    
        return None
    

    def getDnaStrandId_for_generators(self):
        """
        Returns the value of attr I{_dnaStrandId_for_generators}, or "" 
        if it doesn't exist.

        @return: The DNA strand id used by dna generator, or "" if the attr 
                 I{_dnaStrandId_for_generators} does not exist.
        @rtype:  str
        """
        # Note: this (and probably its calls) need revision for the
        # dna data model. [bruce 080225/080311 comment]
        
        # Note: bruce 080311 revised all direct accesses of
        # atom._dnaStrandId_for_generators to go through this method, and
        # renamed it to make it private.

        #UPDATE renamed previous attr dnastrandName to 
        # dnaStrandId_for_generators based on a discussion with Bruce. 
        #It was renamed to this new name 
        #in order to avoid confusion with the dna strand name which can 
        #be acceesed as node.name.  The new name 'dnaStrandId_for_generators'
        #and this comment makes it clear enough that this will only be used
        #by generators ... i.e. while creating a duplex from scratch by reading 
        #in the standard mmp files in cad/plugins/PAM*/*.mmp. See 
        #DnaDuplex._regroup to see how this is used.  -- Ninad 2008-03-12 

        return self.__dict__.get('_dnaStrandId_for_generators', "")

    def directional_bond_chain_status(self): # bruce 071016, revised 080212
        """
        Return a tuple (statuscode, bond1, bond2)
        indicating the status of self's bonds with respect to chains
        of directional bonds. The possible return values are:

        DIRBOND_CHAIN_MIDDLE, bond1, bond2 -- inside a chain involving these two bonds
          (note: there might be other directional bonds (open bonds) which should be ignored)

        DIRBOND_CHAIN_END, bond1, None -- at the end of a chain, which ends with this bond

        DIRBOND_NONE, None, None -- not in a chain

        DIRBOND_ERROR, None, None -- local error in directional bond structure,
          so caller should treat this as not being in a chain

        Note that all we consider is whether a bond is directional, not whether
        a direction is actually set (except for atoms with more than one open bond,
        to disambiguate bare chain ends).

        Similarly, when two bonds have directions set, we don't consider whether
        their directions are consistent. (One reason is that we need to grow
        a chain that covers both bonds so the user can set the entire
        chain's direction. REVIEW: better to stop at such errors, so only
        a consistent part of the chain would be changed at once??)

        But if self is monovalent (e.g. a bondpoint) and its neighbor is not,
        we consider its neighbor's status in determining its own.

        Note that when drawing a bond, each of its atoms can have an
        almost-independent directional_bond_chain_status (due to the
        possibility of erroneous structures), so both of its atoms
        need their directional_bond_chain_status checked for errors.
        """
        # note: I think this implem is correct with or without open bonds
        # being directional [bruce 071016] [revised 080212 to make more true]
        if not self.element.bonds_can_be_directional:
            # optimization
            return DIRBOND_NONE, None, None
        if len(self.bonds) == 1:
            # Special cases. This then-clause covers all situations for
            # self being monovalent, except a few that I think never happen.
            # (But if they do, fall through to general case below.)
            bond = self.bonds[0]
            neighbor = bond.other(self)
            if len(neighbor.bonds) > 1:
                # Monovalents defer to non-monovalent neighbors
                # (note: this applies to bondpoints (after mark 071014 changes)
                #  or to "strand termination atoms".)
                # Those neighbors may decide bond is not in their chain due
                # to their other bonds.
                statuscode, bond1, bond2 = neighbor.directional_bond_chain_status()
                if statuscode == DIRBOND_NONE or statuscode == DIRBOND_ERROR:
                    return statuscode, None, None
                elif statuscode == DIRBOND_CHAIN_MIDDLE:
                    # it matters whether we're in the neighbor's chain
                    if bond is bond1 or bond is bond2:
                        return DIRBOND_CHAIN_END, bond, None
                    else:
                        # we're attached to the chain but not in it.
                        # REVIEW: return DIRBOND_ERROR in some cases??
                        # (For example, when an atom has ._dna_updater__error
                        # set on it?) Note that for open bonds on bare
                        # strands, this happens routinely.
                        return DIRBOND_NONE, None, None # DIRBOND_ERROR?
                    pass
                elif statuscode == DIRBOND_CHAIN_END:
                    # it matters whether the neighbor's chain includes us.
                    # (for bare strand ends with two open bonds, this is up
                    #  to that neighbor even if arbitrary, as of 080212)
                    if bond is bond1:
                        return DIRBOND_CHAIN_END, bond, None
                    else:
                        return DIRBOND_NONE, None, None # DIRBOND_ERROR?
                    pass
                else:
                    assert 0, "%r got unrecognized statuscode %r from " \
                           "%r.directional_bond_chain_status" % \
                           (self, statuscode, neighbor)
                    return DIRBOND_ERROR, None, None
                pass
            else:
                # two connected monovalent atoms, one maybe-directional
                # bond... for now, proceed with no special case. If this ever
                # happens, review it. (e.g. we might consider it an error.)
                pass
            pass
        dirbonds = self.directional_bonds()
        num = len(dirbonds)
        if num == 2:
            # it doesn't matter how many of them are open bonds, in this case
            return DIRBOND_CHAIN_MIDDLE, dirbonds[0], dirbonds[1]
        elif num == 1:
            # whether or not it's an open bond
            return DIRBOND_CHAIN_END, dirbonds[0], None
        elif num == 0:
            return DIRBOND_NONE, None, None
        else:
            # more than 2 -- see if some of them can be ignored
            # [behavior at ends of bare strands was revised 080212]
            real_dirbonds = filter( lambda bond: not bond.is_open_bond(), dirbonds )
            num_real = len(real_dirbonds)
            if num_real == 2:
                # This works around the situation in which a single strand
                # (not at the end) has open bonds where axis atoms ought to
                # be, by ignoring those open bonds. (Note that they count as
                # directional, even though if they became real they would not
                # be directional since one atom would be Ax.)
                # POSSIBLE BUG: the propogate caller can reach this, if it can
                # start on an ignored open bond. Maybe we should require that
                # it is not offered in the UI in this case, by having it check
                # this method before deciding. ### REVIEW
                return DIRBOND_CHAIN_MIDDLE, real_dirbonds[0], real_dirbonds[1]
            else:
                # we need to look at bond directions actually set
                # (on open bonds anyway), to decide what to do.
                #
                # WARNING: this happens routinely at the end of a "bare strand"
                # (no axis atoms), since it has one real and two open bonds, 
                # all directional.
                # 
                # We might fix this by:
                # - making that situation never occur [unlikely]
                # - making bonds know whether they're directional even if 
                #   they're open (bond subclass)
                # - atom subclass for bondpoints
                # - notice whether a direction is set on just one open bond 
                #   [done below, 080212];
                # - construct open bonds on directional elements so the right 
                #   number are set [dna updater does that now, but a user bond
                #   dir change can make it false before calling us]
                # - (or preferably, marked as directional bonds without a 
                #    direction being set)
                
                # REVIEW: return an error message string?
                # [bruce 071112, 080212 updated comment]
                if num_real < 2:
                    # new code (bugfix), bruce 080212 -- look at bonds with
                    # direction set (assume dna updater has made the local
                    # structure make sense) (only works if cmenu won't set dir
                    # on open bond to make 3 dirs set ### FIX)
                    # kluge (bug): assume all real bonds have dir set. 
                    # Easily fixable in the lambda if necessary.
                    dirbonds_set = filter( lambda bond: bond._direction, dirbonds )
                        #k non-private method?
                    if len(dirbonds_set) == 2:
                        return DIRBOND_CHAIN_MIDDLE, dirbonds_set[0], dirbonds_set[1]
                if debug_flags.atom_debug:
                    print "DIRBOND_ERROR noticed on", self
                return DIRBOND_ERROR, None, None
        pass

    def isThreePrimeEndAtom(self):
        """
        Returns True if self is a three prime end atom of a DnaStrand.
        (This means the last non-bondpoint atom in the 5'->3' direction.)
        """
        if self.is_singlet():
            return False

        if not self.element.bonds_can_be_directional:
            return False # optimization

        nextatom = self.next_atom_in_bond_direction(1) 
        if nextatom is None or nextatom.is_singlet():
            return True # self is an end atom

        return False

    def isFivePrimeEndAtom(self):
        """
        Returns True if self is a five prime end atom of a DnaStrand.
        (This means the last non-bondpoint atom in the 3'->5' direction.)
        """
        if self.is_singlet():
            return False

        if not self.element.bonds_can_be_directional:
            return False # optimization

        nextatom = self.next_atom_in_bond_direction(-1) 
        if nextatom is None or nextatom.is_singlet():
            return True # self is an end atom

        return False

    def strand_end_bond(self): #bruce 070415, revised 071016 ### REVIEW: rename?
        """
        For purposes of possibly drawing self as an arrowhead,
        determine whether self is on the end of a chain of directional bonds
        (regardless of whether they have an assigned direction).
        But if self is a bondpoint attached to a chain of directional real bonds,
        treat it as not part of a bond chain, even if it's directional.
        [REVIEW: is that wise, if it has a direction set (which is probably an error)?]

        @return: None, or the sole directional bond on self (if it
                 might be correct to use that for drawing self as an
                 arrowhead).

        TODO: need a more principled separation of responsibilities
        between self and caller re "whether it might be correct to
        draw self as an arrowhead" -- what exactly is it our job to
        determine?

        REVIEW: also return an error code, for drawing red arrowheads
        in the case of certain errors?
        """
        if not self.element.bonds_can_be_directional:
            return None # optimization
        statuscode, bond1, bond2 = self.directional_bond_chain_status()
        if statuscode == DIRBOND_CHAIN_END:
            assert bond1
            assert bond2 is None
            return bond1
        else:
            return None
        pass

    def directional_bonds(self): #bruce 070415
        """
        Return a list of our directional bonds. Its length might be 0, 1, or 2,
        or in the case of erroneous structures [or some legal ones as of
        mark 071014 changes], 3 or more.
        """
        ### REVIEW: should this remain as a separate method, now that its result
        # can't be used naively?
        return filter(lambda bond: bond.is_directional(), self.bonds)

    def bond_directions_are_set_and_consistent(self): #bruce 071204 
        # REVIEW uses - replace with self._dna_updater__error??
        """
        Does self (a strand atom, base or base linker)
        have exactly two bond directions set, not inconsistently?

        @note: still used, but in some ways superceded by dna updater
               and the error code it can set.
        """
        count_plus, count_minus = 0, 0 # for all bonds
        for bond in self.bonds:
            dir = bond.bond_direction_from(self)
            if dir == 1:
                count_plus += 1
            elif dir == -1:
                count_minus += 1
        return (count_plus, count_minus) == (1, 1)

    def desired_new_real_bond_direction(self): #bruce 080213
        """
        Something is planning to make a new real directional bond
        involving self, and will modify self's open bonds and/or
        their bond directions, but not self's existing real bonds
        or their bond directions. What bond direction (away from self)
        should it give the new real bond?
        """
        count_plus, count_minus = 0, 0 # for real bonds only
        for bond in self.bonds:
            if not bond.is_open_bond(): # (could optim, doesn't matter)
                dir = bond.bond_direction_from(self)
                if dir == 1:
                    count_plus += 1
                elif dir == -1:
                    count_minus += 1
        counts = (count_plus, count_minus)
        if counts == (1, 0):
            return -1
        elif counts == (0, 1):
            return 1
        else:
            # Usually or always an error given how we are called,
            # but let the caller worry about this.
            # (Non-error cases are conceivable, e.g. within a dna generator,
            #  or if isolated single bases are being bonded by the user.)
            return 0
        pass

    def fix_open_bond_directions(self, bondpoint, want_dir): #bruce 080213
        """
        Something is planning to make a new real directional bond
        involving self, and will give it the bond direction want_dir
        (measured away from self). If bondpoint is not None, it plans
        to make this bond using that bondpoint (usually removing it).
        Otherwise... which bondpoint will it remove, if any?? ###REVIEW CALLERS

        If possible and advisable, fix all our open bond directions
        to best fit this situation -- i.e.:

        * make the direction from self to bondpoint equal want_dir
        (if bondpoint is not None);

        * if want_dir is not 0, remove equal directions from other
        open bonds of self to make the resulting situation consistent
        (do this even if you have to pick one arbitrarily? yes for now);

        * if want_dir is 0, do nothing (don't move any direction set on
        bondpoint to some other open bond of self, because this only
        happens on error (due to how we are called) and we should do
        as little as possible here, letting dna updater and/or user
        see and fix the error).

        @note: it's ok for this method to be slow.
        """
        debug = debug_flags.atom_debug
        if debug:
            print "debug fyi: fix_open_bond_directions%r" % \
                  ((self, bondpoint, want_dir),)

        if bondpoint:
            bondpoint_bond = bondpoint.bonds[0]
            # redundant: assert bond.other(bondpoint) is self
            bondpoint_bond.set_bond_direction_from( self, want_dir)
        else:
            bondpoint_bond = None
            # print this until I see whether & how this happens:
            msg = "not sure what fix_open_bond_directions%r " \
                "should do since bondpoint is None" % \
                ((self, bondpoint, want_dir),)
                # not sure, because we might want to deduct want_dir from the
                # desired total direction we need to achieve on the other
                # bonds, depending on what caller will do. (If caller will
                # pick one arbitrarily, we need to know which one that is
                # now!)
            if debug_flags.atom_debug:
                print_compact_stack(msg + ": ")
            else:
                print msg + " (set debug flag to see stack)"

        if not self.bond_directions_are_set_and_consistent():
            if debug:
                print "debug fyi: fix_open_bond_directions%r " \
                      "needs to fix other open bonds" % \
                      ((self, bondpoint, want_dir),)
            # Note: not doing the following would cause undesirable messages,
            # including history messages from the dna updater, but AFAIK would
            # cause no other harm when the dna updater is turned on (since the
            # updater would fix the errors itself if this could have fixed
            # them).
            if want_dir:
                num_fixed = [0]
                fixable_open_bonds = filter( lambda bond:
                                             bond.is_open_bond() and
                                             bond is not bondpoint_bond and
                                             bond.bond_direction_from(self) != 0 ,
                                             self.bonds )
                def number_with_direction( bonds, dir1 ):
                    """
                    return the number of bonds in bonds 
                    which have the given direction from self
                    """
                    return len( filter( 
                        lambda bond: bond.bond_direction_from(self) == dir1, 
                        bonds ))
                def fix_one( bonds, dir1):
                    "fix one of those bonds (by clearing its direction)"
                    bond_to_fix = filter( 
                        lambda bond: bond.bond_direction_from(self) == dir1, 
                        bonds )[0]
                    if debug:
                        print "debug fyi: fix_open_bond_directions(%r) " \
                              "clearing %r of direction %r" % \
                              (self, bond_to_fix, dir1)
                    bond_to_fix.clear_bond_direction()
                    num_fixed[0] += 1
                    assert num_fixed[0] <= len(self.bonds) # protect against infloop
                for dir_to_fix in (1, -1): # or, only fix bonds of direction want_dir?
                    while ( number_with_direction( self.bonds, 
                                                   dir_to_fix ) > 1 and
                            number_with_direction( fixable_open_bonds, 
                                                   dir_to_fix ) > 0 
                           ):
                        fix_one( fixable_open_bonds, dir_to_fix )
                    continue
            # if this didn't fix everything, let the dna updater complain
            # (i.e. we don't need to ourselves)
            pass

        return # from fix_open_bond_directions

    def next_atom_in_bond_direction(self, bond_direction): #bruce 071204
        """
        Assuming self is in a chain of directional bonds
        with consistently set directions,
        return the next atom (of any kind, including bondpoints)
        in that chain, in the given bond_direction.

        If the chain does not continue in the given direction, return None.

        If the assumptions are false, no error is detected, and no
        exception is raised, but either None or some neighbor atom
        might be returned.

        @note: does not verify that bond directions are consistent.
        Result is not deterministic if two bonds from self have
        same direction from self (depends on order of self.bonds).
        """
        assert bond_direction in (-1, 1)
        for bond in self.bonds:
            dir = bond.bond_direction_from(self)
            if dir == bond_direction:
                return bond.other(self)
        # todo: could assert self is a termination atom or bondpoint,
        # or if not, that self.bond_directions_are_set_and_consistent()
        # (if we do, revise docstring)
        return None

    def bond_directions_to_neighbors(self): #bruce 080402
        """
        @return: a list of pairs (bond direction to neighbor, neighbor)
                 for all neighbor atoms to which our bonds are directional
                 (including bondpoints, strand sugar atoms, or Pl atoms).
        """
        res = []
        for bond in self.bonds:
            dir = bond.bond_direction_from(self)
            if dir:
                res.append( (dir, bond.other(self)) )
        return res

    def axis_neighbor(self): #bruce 071203; bugfix 080117 for single strand
        """
        Assume self is a PAM strand sugar atom; return the single neighbor of
        self which is a PAM axis atom, or None if there isn't one
        (indicating that self is part of a single stranded region).

        @note: before the dna updater is turned on by default, this may or may
        not return None for the single-stranded case, since there is no
        enforcement of one way of representing single strands. After it is
        turned on, it is likely that it will always return None for free-
        floating single strands, but this is not fully decided. For "sticky
        ends" it will return an axis atom, since they will be represented
        internally as double strands with one strand marked as unreal.
        """
        axis_neighbors = filter( lambda atom: atom.element.role == 'axis',
                                 self.neighbors())
        if axis_neighbors:
            assert len(axis_neighbors) == 1, \
                   "%r.axis_neighbor() finds more than one: %r" % \
                   (self, axis_neighbors)
                # stub, since the updater checks needed to ensure this
                # are NIM as of 071203
            return axis_neighbors[0]
        return None

    def Pl_neighbors(self): #bruce 080122
        """
        Assume self is a PAM strand sugar atom; return the neighbors of self
        which are PAM Pl (pseudo-phosphate) atoms (or any variant thereof,
         which sometimes interposes between strand base sugar pseudoatoms).
        """
        res = filter( lambda atom: atom.element is Pl5,
                      self.neighbors())
        return res

    def strand_base_neighbors(self): #bruce 071204 (nim, not yet needed; rename?)
        """
        Assume self is a PAM strand sugar atom; return a list of the neighboring
        PAM strand sugar atoms (even if PAM5 linker atoms separate them from
        self).
        """
        # review: should the return value also say in which direction each one lies,
        # whether in terms of bond_direction or base_index_direction?       
        assert 0, "nim"

    def strand_next_baseatom(self, bond_direction = None): #bruce 071204
        """
        Assume self is a PAM strand sugar atom, and bond_direction is -1 or 1.
        Find the next PAM strand sugar atom (i.e. base atom) in the given
        bond direction, or None if it is missing (since the strand ends),
        or if any bond directions are unset or inconsistent,
        or if any other structural error causes difficulty,
        or if ._dna_updater__error is set in either self or in the atom
        we might otherwise return (even if that error was propogated
         from elsewhere in that atom's basepair, rather than being a
         problem with that atom itself).
        """
        # note: API might be extended to permit passing a baseindex direction
        # instead, and working on either strand or axis baseatoms.
        assert bond_direction in (-1, 1)
        if self._dna_updater__error: #bruce 080131 new feature (part 1 of 3)
            return None
        atom1 = self.next_atom_in_bond_direction(bond_direction) 
            # might be None or a bondpoint
        if atom1 is None:
            return None
        if atom1._dna_updater__error: #bruce 080131 new feature (part 2 of 3)
            return None
        # REVIEW: the following should probably test element.role == 'strand',
        # but that includes Se3 and Sh3 end-atoms, unlike this list.
        # Not an issue when dna updater is on and working,
        # but if it's disabled to work with an old file, that change
        # might cause bugs. But I don't feel fully comfortable with
        # making this depend at runtime on dna_updater_is_enabled()
        # (not sure why). So leave it alone for now. [bruce 080320]
        symbol = atom1.element.symbol 
            # KLUGE -- should use another element attr, or maybe Atom subclass
        if symbol[0:2] not in ('Ss', 'Sj', 'Hp', 'Pl'): 
            # base or base linker atoms (#todo: verify or de-kluge)
            return None
        if symbol.startswith('Pl'): # base linker atom
            # move one more atom to find the one to return
            atom1 = atom1.next_atom_in_bond_direction(bond_direction) 
                # might be None or a bondpoint
            assert atom1 is not self
                # (false would imply one bond had two directions,
                #  or two bonds between same two atoms)
            if atom1 is None:
                return None
            if atom1._dna_updater__error: #bruce 080131 new feature (part 3 of 3)
                return None
            if atom1.element.symbol[0:2] not in ('Ss', 'Sj', 'Hp'):
                return None
            pass
        return atom1

    def _f_get_fake_Pl(self, direction): #bruce 080327
        """
        [friend method for PAM3+5 -> PAM5 conversion code]

        Assume self is a PAM3 or PAM5 strand sugar atom
        (either PAM model is possible, at least transiently,
         during PAM3+5 conversion).

        Find or make, and return, a cached fake Pl5 atom
        with a properly allocated and unchanging atom.key,
        to be used in the PAM5 form of self if self does not
        have a real Pl atom in the given bond_direction.

        The atom we return might be used only for mmp writing
        of a converted form, without making any changes in the model,
        or it might become a live atom and get used in the model.
        To make it a live atom, special methods must be called [nim]
        which remove it from being able to be returned by this method.

        If self does have a real such Pl atom, the atom we
        might otherwise return might still exist, but this
        method won't be called to ask for it. It may or may
        not detect that case. If it detects it, it will
        treat it as an error. However, it's not an error for
        the cached atom to survive during the time a live Pl
        atom takes it place, and to be reused if that live
        Pl atom ever dies. OTOH, the cached Pl atom might have
        formerly been a live Pl atom in the same place
        (i.e. bonded to self in the given bond_direction),
        killed when self was converted to PAM3.

        The 3d position (atom.posn()) of the returned atom
        is arbitrary, and can be changed by the caller for its
        own purposes. Absent structure changes to self, the
        identity, key, and 3d position of the returned atom
        won't be changed between calls of this method
        by the code that implements the service of which this
        method is part of the interface.
        """
        fake_Pls = self._fake_Pls # None, or a 2-element list
            # Note: this list is NOT part of the undoable state, nor are the
            # fake atoms within it.
            #
            # REVIEW: should these have anything to do with storing Pl-posn
            # "+5" data? is that data in the undoable state? I think it is,
            # and these are not, so they probably don't help store it.

        if not fake_Pls:
            fake_Pls = self._fake_Pls = [None, None]
        assert direction in (1, -1)
        direction_index = (direction == 1) # arbitrary map from direction to [0,1] 
            ### clean up dup code when we have some
            
            # review: change this to data_index, store a Fake_Gv in the same
            # array?? (don't know yet if writemmp pam5 conversion will need
            # one -- maybe not, or if it does it can probably be a flyweight,
            # but not yet known)
        Pl = fake_Pls[direction_index]
        if Pl is None:
            Pl = fake_Pls[direction_index] = Fake_Pl(self, direction)
                ## not: self.__class__(Pl5, V(0,0,0))
        # obs cmt: maybe: let Pl be live, and if so, verify its bonding with self??
        assert isinstance(Pl, Fake_Pl)
        # nonsense: ## assert Pl.killed() # for now
        return Pl

    # methods related to storing PAM3+5 Pl data on Ss
    # (Gv and Pl data share private helper methods)

    def _f_store_PAM3plus5_Pl_abs_position(self, direction, abspos, **opts):
        #bruce 080402, split 080409
        """
        [friend method for PAM3plus5 code, called from dna updater]

        If self is a PAM3 or PAM5 strand sugar atom,
        store "PAM3+5 Pl-position data" on self,
        for a hypothetical (or actual) Pl in the given bond direction from self,
        at absolute position abspos, converting this to a relative position
        using the baseframe info corresponding to self stored in
        self's DnaLadder, which must exist and be up to date
        (assumed, not checked).

        @warning: slow for non-end atoms of very long ladders, due to a
                  linear search for self within the ladder. Could be optimized
                  by passing an index hint if necessary.

        @note: this method might be inlined, when called by Pls between
               basepairs in the same DnaLadder, since much of it could be
               optimized in a loop over basepairs in order (in that case).
        """
        assert direction in (1, -1)
        data_index = (direction == 1)
        self._store_PAM3plus5_abspos(data_index, abspos, **opts)
            # both Pl and Gv use this, with different data_index
        return

    def _store_PAM3plus5_abspos(self, data_index, abspos):
        """
        [private helper, used for Pl and Gv methods]
        """
        #bruce 080402, split 080409
        if not self.element.symbol.startswith('Ss'): 
            # kluge? needs to match Ss3 and Ss5, and not Pl.
            # not necessarily an error
            print "fyi: _store_PAM3plus5_abspos%r is a noop for this element" % \
                  (self, data_index, abspos)
                # remove when works if routine; leave in if never seen, to
                # notice bugs; current caller tries not to call in this case,
                # so this should not happen
            return

        if not self.can_make_up_Pl_abs_position(data_index and 1 or -1):
            # kluge: can store is the same as can make up, for now;
            # needed to fix bugs in pam conversion killing Pls next to
            # single strands [bruce 080413]
            return

        origin, rel_to_abs_quat, y_m_junk = _f_baseframe_data_at_baseatom(self)
        relpos = baseframe_abs_to_rel(origin, rel_to_abs_quat, abspos) 
        if not self._PAM3plus5_Pl_Gv_data:
            self._PAM3plus5_Pl_Gv_data = [None, None, None]
        self._PAM3plus5_Pl_Gv_data[data_index] = relpos
        if debug_flags.DEBUG_DNA_UPDATER_VERBOSE:
            print "fyi, on %r for data_index %r stored relpos %r" % \
                  (self, data_index, relpos)
            # todo: use these prints to get constants for
            # default_Pl_relative_position (and Gv) [review: done now?]
        return 

    def _f_recommend_PAM3plus5_Pl_abs_position(self,
                                               direction,
                                               make_up_position_if_necessary = True,
                                               **opts
                                               ):
        """
        #doc; return None or a position

        @warning: this can return None even if make_up_position_if_necessary
                  is passed, since some Ss atoms *can't* make up a position
                  (e.g. those in DnaSingleStrandDomains, at least for now)
        """
        #bruce 080402, split 080409
        assert direction in (1, -1)
        data_index = (direction == 1)
        res = self._recommend_PAM3plus5_abspos(data_index, **opts)
            # both Pl and Gv use this, with different data_index
        if res is None and make_up_position_if_necessary:
            res = self._make_up_Pl_abs_position(direction) # might be None!
                # note: don't store this, even if not remove_data
                # (even though save in PAM5, then reload file,
                #  *will* effectively store it, since in the file we don't
                #  mark it as "made up, should be ignored"; if we did,
                #  we'd want to erase that as soon as anything moved it,
                #  and it'd be a kind of hidden info with mysterious effects,
                #  so it's not a good idea to mark it that way)
        return res

    def _recommend_PAM3plus5_abspos(self,
                                    data_index,
                                    remove_data = False ):
        """
        [private helper, used for Pl and Gv methods]

        #doc; return None or a position; never make up a position
        """
        #bruce 080402, split 080409
        data = None
        if self._PAM3plus5_Pl_Gv_data:
            data = self._PAM3plus5_Pl_Gv_data[data_index] # might be None
            if remove_data:
                self._PAM3plus5_Pl_Gv_data[data_index] = None
                # don't bother removing the [None, None, ...] list itself
                # (optim: should we remove it to conserve RAM??)
        # data is None or a relative Pl or Gv position
        if data is None:
            return None
        else:
            relpos = data
            origin, rel_to_abs_quat, y_m_junk = _f_baseframe_data_at_baseatom(self)
            return baseframe_rel_to_abs(origin, rel_to_abs_quat, relpos)
        pass # end of _recommend_PAM3plus5_abspos

    def _make_up_Pl_abs_position(self, direction): #bruce 080402
        """
        """
        if not self.can_make_up_Pl_abs_position(direction):
            return None
        relpos = default_Pl_relative_position(direction)
        origin, rel_to_abs_quat, y_m_junk = _f_baseframe_data_at_baseatom(self) 
        return baseframe_rel_to_abs(origin, rel_to_abs_quat, relpos)

    def can_make_up_Pl_abs_position(self, direction): #bruce 080413
        try:
            ladder, whichrail, index = _f_find_new_ladder_location_of_baseatom(self)
            # not self.molecule.ladder, it finds the old invalid ladder instead
        except:
            print "bug? can_make_up_Pl_abs_position can't find new ladder of %r" % \
                  (self,)
            return True
                # should be False, but return True to mitigate new bugs caused
                # by this feature
        if not ladder:
            # probably can't happen
            print "bug? can_make_up_Pl_abs_position sees ladder of None for %r" % \
                  (self,)
            return True 
                # should be False (see comment above)
        return ladder.can_make_up_Pl_abs_position_for(self, direction)

    # methods related to storing PAM3+5 Gv data on Ss
    # (Gv and Pl data share private helper methods)

    def _f_store_PAM3plus5_Gv_abs_position(self, abspos): #bruce 080409
        """
        [friend method for PAM3plus5 code, called from dna updater]

        If self is a PAM3 or PAM5 strand sugar atom,
        store "PAM3+5 Gv-position data" on self,
        for a hypothetical (or actual) Gv attached to self,
        at absolute position abspos, converting this to a relative position
        using the baseframe info corresponding to self stored in
        self's DnaLadder, which must exist and be up to date
        (assumed, not checked), BUT WHICH MAY NOT
        HAVE YET REMADE ITS CHUNKS (i.e. which may differ from atom.
         molecule.ladder for its atoms, if that even exists).

        @warning: slow for non-end atoms of very long ladders, due to a
                  linear search for self within the ladder. Could be optimized
                  by passing an index hint if necessary.

        @note: this method might be inlined, since much of it could be
               optimized in a loop over basepairs in order (in that case);
               or it might be passed a baseindex hint, or baseframe info.
        """
        self._store_PAM3plus5_abspos( _GV5_DATA_INDEX, abspos)
            # both Pl and Gv use this, with different data_index
        return

    def _f_recommend_PAM3plus5_Gv_abs_position(self,
                                               make_up_position_if_necessary = True,
                                               **opts # e.g. remove_data = False
                                               ):
        """
        #doc; return None or a position
        """
        #bruce 080409
        res = self._recommend_PAM3plus5_abspos( _GV5_DATA_INDEX, **opts)
            # both Pl and Gv use this, with different data_index
        if res is None and make_up_position_if_necessary:
            res = self._make_up_Gv_abs_position()
        return res

    def _make_up_Gv_abs_position(self): #bruce 080409
        """
        @note: self should be a strand sugar atom
        """
        relpos = default_Gv_relative_position() # (a constant)
        # following code is the same as for the Pl version
        origin, rel_to_abs_quat, y_m_junk = _f_baseframe_data_at_baseatom(self) 
        return baseframe_rel_to_abs(origin, rel_to_abs_quat, relpos)

    # == end of PAM strand atom methods

    # == PAM axis atom methods

    def strand_neighbors(self): #bruce 071203
        """
        Assume self is a PAM axis atom; return the neighbors of self
        which are PAM strand sugar atoms. There are always exactly one or
        two of these [NIM] after the dna updater has run.
        """
        # [stub -- need more error checks in following (don't return Pl).
        #  but this is correct if structures have no errors.]
        res = filter( lambda atom: atom.element.role == 'strand',
                      self.neighbors())
        ##assert len(res) in (1, 2), \
        ##       "error: axis atom %r has %d strand_neighbors (should be 1 or 2)"\
        ##       % (self, len(res))
        # happens in mmkit - leave it as just a print at least until
        # we implem "delete bare atoms" -
        legal_nums = legal_numbers_of_strand_neighbors_on_axis()
        if not ( len(res) in legal_nums ):
            print "error: axis atom %r has %d strand_neighbors (should be %s)" % \
                  (self, len(res), " or ".join(map(str, legal_nums)))
        return res

    def axis_neighbors(self): #bruce 071204
        # (used on axis atoms, not sure if used on strand atoms)
        return filter( lambda atom: atom.element.role == 'axis',
                       self.neighbors())

    # == end of PAM axis atom methods

    pass # end of class PAM_Atom_methods

# end
