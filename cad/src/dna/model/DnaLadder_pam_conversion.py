# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaLadder_pam_conversion.py - PAM3+5 <-> PAM5 conversion methods for DnaLadder,
and (perhaps in future) related helper functions.

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from model.elements import Pl5, Ss5, Ax5, Gv5
from model.elements import      Ss3, Ax3
from model.elements import Singlet

from model.bonds import bond_direction #e rename
from utilities.constants import Pl_STICKY_BOND_DIRECTION

from utilities.constants import MODEL_PAM3, MODEL_PAM5, PAM_MODELS, MODEL_MIXED
from utilities.constants import noop

from utilities.Log import redmsg, quote_html

from geometry.VQT import V

from platform.PlatformDependent import fix_plurals

import foundation.env as env

from dna.model.dna_model_constants import LADDER_ENDS
from dna.model.dna_model_constants import LADDER_BOND_DIRECTION_TO_OTHER_AT_END_OF_STRAND1

from dna.model.pam3plus5_math import other_baseframe_data
from dna.model.pam3plus5_math import compute_duplex_baseframes
from dna.model.pam3plus5_math import correct_Ax3_relative_position
from dna.model.pam3plus5_math import relpos_in_other_frame
from dna.model.pam3plus5_math import SPRIME_D_SDFRAME
from dna.model.pam3plus5_math import baseframe_rel_to_abs

from dna.model.pam3plus5_ops import Gv_pos_from_neighbor_PAM3plus5_data
from dna.model.pam3plus5_ops import insert_Pl_between
from dna.model.pam3plus5_ops import find_Pl_between
from dna.model.pam3plus5_ops import kill_Pl_and_rebond_neighbors

from dna.updater.dna_updater_globals import _f_ladders_with_up_to_date_baseframes_at_ends
from dna.updater.dna_updater_globals import _f_atom_to_ladder_location_dict
from dna.updater.dna_updater_globals import _f_baseatom_wants_pam

# ==

class DnaLadder_pam_conversion_methods:
    """
    """
    def pam_model(self): #bruce 080401, revised 080408
        """
        Return an element of PAM_MODELS (presently MODEL_PAM3 or MODEL_PAM5)
        which indicates the PAM model of all atoms in self,
        if this is the same for all of self's baseatoms;
        if not, return MODEL_MIXED. Assume it's the same in any one rail
        of self.

        @note: we are considering allowing mixed-PAM ladders, as long as each
               rail is consistent. If we do, all uses of this method will
               need review, since they were written before it could return
               MODEL_MIXED in that case.
        """
        results = [rail.baseatoms[0].element.pam for rail in self.all_rails()]
        res = results[0]
        for res1 in results:
            if res1 != res:
                print "fyi: inconsistent pam models %r in rails of %r" % (results, self) #### temporary
                return MODEL_MIXED
                    # prevents pam conversion, may cause other bugs if callers not reviewed @@@
            continue
        return res
    
    def _pam_conversion_menu_spec(self, selobj): #bruce 080401, split 080409
        """
        Return a menu_spec list of context menu entries related to
        PAM conversion, which is (or might be) specific to selobj being
        a PAM atom or chunk whose DnaLadder is self. (If we have no entries,
        return an empty menu_spec list, namely [].)

        (Other kinds of selobj might be permitted later.)
        """
        del selobj # there's not yet any difference in this part of the cmenu
            # for different selobj or selobj.__class__ in same DnaLadder
        res = []
        if len(self.strand_rails) == 2: # todo: methodize this common code
            what = "basepair"
        else:
            what = "base"
        pam_model = self.pam_model()
        if pam_model == MODEL_PAM3:
            res.append( (fix_plurals("Convert %d %s(s) to PAM5" % (len(self), what)),
                         self.cmd_convert_to_pam5) )
        elif pam_model == MODEL_PAM5:
            res.append( (fix_plurals("Convert %d %s(s) to PAM3" % (len(self), what)),
                         self.cmd_convert_to_pam3) )
        elif pam_model == MODEL_MIXED:
            res.append( (fix_plurals("Mixed PAM models in %d %s(s), conversion nim" % (len(self), what)),
                         noop,
                         'disabled') )
        else:
            assert 0, "unexpected value %r of %r.pam_model()" % (pam_model, self)
        pass
        # TODO:
        # later, add conversions between types of ladders (duplex, free strand, sticky end)
        # and for subsections of a ladder (base pairs of selected atoms?)
        # and for larger parts of the model (duplex == segment, strand, DnaGroup),
        # and commands to do other things to those (e.g. select them).
        return res

    def cmd_convert_to_pam5(self):
        """
        Command to convert all of self to PAM5.
        """
        self._cmd_convert_to_pam(MODEL_PAM5)

    def cmd_convert_to_pam3(self):
        """
        Command to convert all of self to PAM3.
        """
        self._cmd_convert_to_pam(MODEL_PAM3)

##    # todo: also a command to "convert to default PAM display"
####    # which sets chunk.display_as_pam = None
##    # (what to call it?)
##    # (or just make the one that corresponds to that, do that, if it's pam3 at least??) [no]
    
    def _cmd_convert_to_pam(self, which_model):
        """
        Command to convert all of self to one of the PAM_MODELS.
        """
        #revised, bruce 080411
        _f_baseatom_wants_pam.clear() # precaution
            # ASSUME WE ARE DOING THIS FOR ONLY SELF, NOT ANYTHING ELSE AT SAME TIME
        
        env.history.graymsg(quote_html("Debug fyi: Convert %r to %s" % (self, which_model))) #####
        
##        for chunk in self.all_chunks():
##            chunk.display_as_pam = which_model
##            chunk.changed() # calls assy.changed(); might be needed

        for rail in self.all_rails():
            for baseatom in rail.baseatoms:
                _f_baseatom_wants_pam[baseatom.key] = which_model
        self.arbitrary_baseatom().molecule.assy.changed() # might be needed
        for chunk in self.all_chunks():
            chunk.display_as_pam = None
            del chunk.display_as_pam
            chunk.save_as_pam = None
            del chunk.save_as_pam
        
        self.invalidate()
            # this tells dna updater to remake self from scratch;
            # it will notice display_as_pam differing from element.pam of the
            # atoms, and do the actual conversion [mostly nim as of 080401 430pm]
        ### BUG: the above, alone, doesn't cause dna updater to actually run.
        # KLUGE WORKAROUND:
        self.arbitrary_baseatom()._changed_structure()
        return

    def _f_convert_pam_if_desired(self, default_pam_model): #bruce 080401
        """
        [friend method for dna updater]

        If self's atoms desire it, try to convert self to a different pam model for display.
        On any conversion error, report to history (summary message),
        mark self with an error, and don't convert anything in self.
        On success, only report to history if debug_prefs desire this.
        Return success-related flags.

        @note: if conversion is wanted and succeeded, it is unfinished
               regarding bridging Pl atoms between two strand-rail-ends
               (usually of this and another ladder, but possibly between
                two strand-rail-ends of this ladder). If any such atoms
               will ultimately be needed on self, they are present, but
               some atoms may be present which need to be killed; and
               the position of live Pl atoms, and the related +5 data
               on Ss3 atoms next to Pl atoms which need to be killed,
               may not yet be fully updated. So, after all ladders have
               been asked to convert, the caller needs to iterate over
               them again to find bridging Pls to fix, and fix those
               by calling _f_finish_converting_bridging_Pl_atoms on each
               ladder.

        @return: a pair of booleans: (conversion_wanted, conversion_succeeded).
        """
        want = self._want_pam(default_pam_model)
            # might be None, which means, whatever you already are
        have = self.pam_model() # might be MODEL_MIXED
        if want == have or want is None:
            # no conversion needed
            return False, False
        assert want in PAM_MODELS # can't be MODEL_MIXED
        succeeded = self._convert_to_pam(want) # someday this can work for self being MODEL_MIXED
        if not succeeded:
            summary_format = "Error: PAM conversion failed for [N] DnaLadder(s)"
            env.history.deferred_summary_message( redmsg( summary_format))
            # Now change the chunk options so they don't keep trying to reconvert...
            # this is hard, since self's chunks haven't yet been remade,
            # so each atom might have different chunks and might share them with
            # other ladders. Not sure what the best solution is... it's good if
            # changing the ladder lets user try again, but nothing "automatically"
            # tries again. Maybe wait and revise chunk options after ladder chunks
            # are remade? For any error, or just a PAM error? I think any error.
            # Ok, do that right in DnaLadder.remake_chunks. But what do we change
            # them to? "nothing" is probably best, even though in some cases that
            # means we'll retry a conversion. Maybe an ideal fix needs to know,
            # per chunk, the last succeeding pam as well as the last desired one?
        return True, succeeded

    def _want_pam(self, default_pam_model): #bruce 080411
        """
        """
        atom = self.arbitrary_baseatom()
            # by construction, all our baseatoms want the same pam_model
        try:
            return _f_baseatom_wants_pam[atom.key] # supersedes everything else
        except KeyError:
            pass
        want = atom.molecule.display_as_pam
        if not want:
            want = default_pam_model # might be None, which means, whatever you already are
        return want
    
    def _convert_to_pam(self, pam_model): #bruce 080401
        """
        [private helper for _f_convert_pam_if_desired; other calls might be added]
        
        Assume self is not already in pam_model but wants to be.
        
        If conversion to pam_model can succeed, then do it by
        destructively modifying self's atoms, but preserve their identity
        (except for Pl) and the identity of self, and return True.
        
        (This usually or always runs during the dna updater, which means
         that the changes to atoms in self will be ignored, rather than
         causing self to be remade.)
        
        If conversion can't succeed, set an error in self and return False
        (but emit no messages). Don't modify self or its atoms in this case.
        """
        if self.error or not self.valid:
            # caller should have rejected self before this point
            # (but safer to not assert this, but just debug print for now)
            print "bug: _convert_to_pam on ladder with error or not valid:", self
            # todo: summary message about why
            return False
        if self.pam_model() == MODEL_MIXED:
            # todo: summary message about why
            return False
        if self.axis_rail:
            element = self.axis_rail.baseatoms[0].element
            if element not in (Gv5, Ax3):
                # todo: summary message about why
                # guess the reason is Ax5...
                print "conversion from PAM axis element %r is not yet implemented (in %r)" % \
                      (self.axis_rail.baseatoms[0].element, self)
                return False
        if 0 and 'safety stub': # debug pref to simulate failure?
            ###### STUB (but correct if this should always fail, i think):
            print "_convert_to_pam(%r, %r) is NIM" % (self, pam_model) ###
            self.set_error("_convert_to_pam is NIM")
                # review: is this comment obs?
                # bug: doesn't prevent command from being offered again, even if ladder unmodified
                # (maybe fixed by checking for error in cmenu maker? i forget if this comment
                #  came after that check was added or before)
            return False # simulate failure

        print "WARNING: _convert_to_pam(%r, %r) is unfinished, will probably fail somehow" % (self, pam_model) #### @@@
        env.history.orangemsg( "Warning: convert to %s is under development, may have bugs" % pam_model ) ####
        
        # first compute and store current baseframes on self, where private
        # methods can find them on demand. REVIEW: need to do this on connected ladders
        # not being converted, for sake of bridging Pl atoms? Not if we can do those
        # on demand, but then we'd better inval them all first! Instead, caller initializes
        # a global _f_ladders_with_up_to_date_baseframes_at_ends (formerly a parameter
        # ladders_dict) (search for mentions of that global in various places, for doc).
        ok = self._compute_and_store_new_baseframe_data()
            # note: this calls _make_ghost_bases [nim] if necessary to make sure we
            # temporarily have a full set of 2 strand_rails.
            # what to do for non-axis ladders is not yet reviewed or implemented. @@@@
        if not ok:
            print "baseframes failed for", self
            # todo: summary message
            return False

        # print "fyi, %r._compute_and_store_new_baseframe_data computed this:" % self, self._baseframe_data

        # now we know we'll succeed (unless there are structural errors detected
        # only now, which shouldn't happen since we should detect them all
        # earlier and not form the ladder or mark it as an error, but might
        # happen anyway), and enough info is stored to do the rest per-atom
        # for all atoms entirely convertable inside this ladder (i.e. all except
        # bridging Pls).

        # we'll do the following things:
        # - if converting to PAM5, make a Pl at each corner that doesn't have
        #   one but needs one (even if it belongs to the other ladder there,
        #   in case that one is remaining PAM3 so won't make it itself).
        #   Mark this Pl as non-definitive in position; it will be fixed later
        #   (when its other ladder's baseframes are also surely available)
        #   by self._f_finish_converting_bridging_Pl_atoms.
        # - create or destroy interior Pls as needed.
        # - transmute and reposition the atoms of each basepair or base.
        # - if we converted to PAM3, remove ghost bases if desired.
        # Most of these steps can be done in any order, since they rely on the
        # computed baseframes to know what to do. They are all most efficient
        # if we know the base indices as we go, so do them in a loop or loops
        # over base indices.

        self._convert_axis_to_pam(pam_model) # moves and transmutes axis atoms
        for rail in self.strand_rails:
            self._convert_strand_rail_to_pam(pam_model, rail)
                # moves and transmutes sugars, makes or removes Pls,
                # but does not notice or remove ghost bases
            continue
        if pam_model == MODEL_PAM5:
            self._make_bridging_Pls_as_needed()

        if pam_model == MODEL_PAM3: # (do this last)
            # todo: remove ghost bases if desired
            pass

        # optional: remove all baseframe data except at the ends
        # (in case needed by bridging Pls) -- might help catch bugs or save RAM
        
        return True  # could put above in try/except and return False for exceptions

    def _convert_axis_to_pam(self, want_pam_model):
        """
        moves and transmutes axis atoms, during conversion to specified pam_model
        """
        # note: make this work even if not needed (already correct pam model)
        # for robustness (if in future we have mixed models, or if bugs call it twice),
        # but say this happens in a print (since unexpected)
        assert self.valid and not self.error
        axis_atoms = self.axis_rail.baseatoms
        if want_pam_model == MODEL_PAM5:
            # they are presumably Ax3, need to become Gv5 and get moved.
            # (but don't move if already Gv5 for some reason)
            for i in range( len(axis_atoms)):
                atom = axis_atoms[i]
                if atom.element is not Gv5:
                    # move it in space to a saved or good position for a Gv5
                    # (this works even if the neighbors are Ss5 and atom
                    # is Ax5, since it uses baseframes, not neighbor posns)
                    newpos = Gv_pos_from_neighbor_PAM3plus5_data(
                        atom.strand_neighbors(),
                        remove_data_from_neighbors = True
                     )
                        # fyi, done inside that (should optim by passing i at least):
                        ## origin, rel_to_abs_quat, y_m = self._baseframe_data[i]
                    assert newpos is not None, "can't compute new position for Gv5!"
                        # should never happen, even for bare axis
                        # (no strand_neighbors), since we made up ghost bases earlier
                    atom.setposn(newpos)
                    # transmute it
                    atom.mvElement(Gv5)
                else:
                    print "unexpected: %r is already Gv5" % atom
                    # this might turn out to be normal if we can someday convert
                    # PAM5-with-Ax5 (in old mmp files) to PAM5-with-Gv5.
                continue
            pass
        elif want_pam_model == MODEL_PAM3:
            # they might be already Ax3 (unexpected, no move needed (but might be ok or good?))
            # or Ax5 (legal but not yet supported in callers; no move needed
            #  if posn correct, but this is not guaranteed so move might be good)
            # or Gv5 (move needed). Either way, transmute to Ax3.
            for i in range( len(axis_atoms)):
                atom = axis_atoms[i]
                if atom.element is Gv5:
                    atom._f_Gv_store_position_into_Ss3plus5_data()
                # always move in space (even if atom is already Ax5 or even Ax3),
                # since PAM3 specifies only one correct Ax3 position, given the
                # baseframes (ref: the wiki page mentioned in another file)
                origin, rel_to_abs_quat, y_m = self._baseframe_data[i]
                    # it's ok to assume that data exists and is up to date,
                    # since our callers (known since we're a private helper)
                    # just recomputed it
                relpos = correct_Ax3_relative_position(y_m)
                newpos = baseframe_rel_to_abs(origin, rel_to_abs_quat, relpos)
                atom.setposn( newpos)
                # transmute it
                # don't bother checking for unexpected element, or whether this is needed
                atom.mvElement(Ax3) ###k check if enough invals done, atomtype updated, etc @@@
            pass
        else:
            assert 0
        return
    
    def _convert_strand_rail_to_pam(self, want_pam_model, rail):
        #bruce 080409, modified from _convert_axis_to_pam
        """
        [private helper, during conversion to specified pam_model]

        moves and transmutes strand sugar PAM atoms, and makes or removes Pls,
        but does not notice ghost status of bases or remove ghost bases
        """
        assert self.valid and not self.error
        # note: make this work even if not needed (already correct pam model)
        # for robustness (if in future we have mixed models, or if bugs call it twice),
        # but say this happens in a print (since unexpected)
        strand_baseatoms = rail.baseatoms
        is_strand2 = (rail is not self.strand_rails[0])
        if want_pam_model == MODEL_PAM5:
            # atoms are presumably Ss3, need to become Ss5 and get moved
            # and get Pls inserted between them (inserting Pls at the ends
            # where self joins other ladders is handled by a separate method)
            for i in range( len(strand_baseatoms)):
                atom = strand_baseatoms[i]
                if atom.element is Ss3:
                    # transmute it [just to prove we can do these steps
                    #  in whatever order we want]
                    atom.mvElement(Ss5)
                    
                    # move it in space
                    origin, rel_to_abs_quat, y_m = self._baseframe_data[i]
                    if is_strand2:
                        relpos = V(0, 2 * y_m, 0)
                    else:
                        relpos = V(0, 0, 0)
                        # could optimize this case: newpos = origin
                    newpos = baseframe_rel_to_abs(origin, rel_to_abs_quat, relpos)
                    atom.setposn(newpos)

                    if i + 1 < len(strand_baseatoms):
                        # insert a Pl linker between atom i and atom i+1,
                        # and put it at the correct position in space
                        # (share code with the corner-Pl-inserter)

                        # assume seeing one Ss3 means entire strand is Ss3 and
                        # has no Pl linkers now
                        Pl = insert_Pl_between(atom, strand_baseatoms[i+1])

                        # move that Pl to the correct position
                        Pl._f_Pl_set_position_from_Ss3plus5_data()
                        pass
                    pass    
                elif atom.element is Ss5:
                    print "unexpected: strand rail %r (judging by atom %r) seems to be already PAM5" % (rail, atom)
                    # don't break loop here, in case this repairs a bug from an earlier exception
                    # partway through a pam conversion (not too likely, but then neither is this case at all,
                    # so we don't need to optimize it)
                    pass
                else:
                    print "likely bug: %r is not Ss3 or Ss5" % atom
                continue
            pass
        elif want_pam_model == MODEL_PAM3:
            # atoms might be already Ss3 (unexpected, no move needed (but might be ok or good?))
            # or Ss5 (move needed). Either way, transmute to Ss3, store Pl data, remove Pls.
            for i in range( len(strand_baseatoms)):
                atom = strand_baseatoms[i]

                # move it in space (doesn't matter what element it is)
                origin, rel_to_abs_quat, y_m = self._baseframe_data[i]
                relpos = SPRIME_D_SDFRAME
                if is_strand2:
                    relpos = relpos_in_other_frame(relpos, y_m)
                newpos = baseframe_rel_to_abs(origin, rel_to_abs_quat, relpos)
                atom.setposn(newpos)

                # transmute it
                atom.mvElement(Ss3)

                if i + 1 < len(strand_baseatoms):
                    # find a Pl linker between atom i and atom i+1
                    # (None if not there since they are directly bonded)
                    Pl = find_Pl_between(atom, strand_baseatoms[i+1])
                    if Pl is not None:
                        # store Pl data
                        Pl._f_Pl_store_position_into_Ss3plus5_data()
                        # remove Pl
                        kill_Pl_and_rebond_neighbors(Pl)
                    pass
                continue
            pass
        else:
            assert 0
        return # from _convert_strand_rail_to_pam

    def _make_bridging_Pls_as_needed(self): #bruce 080410
        """
        We just converted self to PAM5 (or tried to).
        Find all places where self touches another ladder
        (or touches itself at the corners, where a strand rail ends),
        and if any of them now need, but don't yet have, a bridging Pl atom,
        make one, with a non-definitive position.

        (Also make one at strand ends, i.e. between Ss5-X,
         if needed and correct re bond directions.)
        ### REVIEW: is that case handled in _f_finish_converting_bridging_Pl_atoms?
        """
        assert self.valid and not self.error
        # similar code to _bridging_Pl_atoms, and much of its checks are
        # redundant and not needed in both -- REVIEW which one to remove them from
        if self.error or not self.valid:
            # caller should have rejected self before this point
            # (but safer to not assert this, but just debug print for now)
            print "bug: _make_bridging_Pls_as_needed on ladder with error or not valid:", self
            return
        res = {}
        for end_atom, next_atom in self._corner_atoms_with_next_atoms_or_None():
            # next_atom might be None (??) or a non-Pl atom
            if next_atom is not None and next_atom.element is Pl5:
                continue # nothing to do here (we never remove a Pl or move it)
            # review: is next_atom a bondpoint, None, or both, when a strand ends? I think a bondpoint,
            # this code only works properly for that case.
            if next_atom is None:
                print "***BUG: _make_bridging_Pls_as_needed(%r) doesn't handle next_atom is None" % self
                continue
            # assume it's a bondpoint or Ss3 or Ss5. We want Pl iff either atom is Ss5.
            def atom_wants_Pl(atom):
                return atom.element is Ss5 # maybe: also check for error on this atom?
            want_Pl = atom_wants_Pl(end_atom) or atom_wants_Pl(next_atom)
            if want_Pl:
                # inserting Pl5 between Ss5-X is only correct at one end
                # of a PAM5 strand ... see if the direction in which it prefers
                # to stick with Ss points to an X among these atoms, and if so,
                # don't insert it, though the function would work if we tried.
                if Pl_STICKY_BOND_DIRECTION == bond_direction(end_atom, next_atom):
                    Pl_sticks_to = next_atom # not literally true if next_atom is a bondpoint, fyi
                else:
                    Pl_sticks_to = end_atom
                if not Pl_sticks_to.is_singlet():
                    insert_Pl_between(end_atom, next_atom)
            continue
        return
        
    def _f_finish_converting_bridging_Pl_atoms(self): #bruce 080408        
        """
        [friend method for dna updater]

        @see: _f_convert_pam_if_desired, for documentation.

        @note: the ladders in the dict are known to have valid baseframes
               (at least at the single basepairs at both ends);
               this method needs to look at neighboring ladders
               (touching self at corners) and use end-baseframes from
               them; if it sees one not in the dict, it makes it compute and
               store its baseframes (perhaps just at both ends as an optim)
               and also stores that ladder in the dict so this won't
               be done to it again (by some other call of this method
               from the same caller using the same dict).
        """
        assert self.valid and not self.error
        for Pl in self._bridging_Pl_atoms():
            Pl._f_Pl_finish_converting_if_needed()
                # note: this might kill Pl.
        return

    def _bridging_Pl_atoms(self):
        #bruce 080410 revised this to call _corner_atoms_with_next_atoms_or_None
        # (split out from this)
        """
        [private helper]

        Return a list of all Pl atoms which bridge ends of strand rails
        between self and another ladder, or between self and self
        (which means the Pl is connecting end atoms not adjacent in self,
         not an interior Pl atom [but see note for a possible exception]).

        Make sure this list includes any Pl atom only once.

        @note: a length-2 ring is not allowed, so this is not ambiguous --
               a Pl connecting the end atoms of a length-2 strand rail is an
               interior one; two such Pls are possible in principle but are
               not allowed. (They might be constructible, so at least we
               should not crash then -- we'll try to use bond directions
               to decide which one is interior and which one is bridging.)
        """
        if self.error or not self.valid:
            # caller should have rejected self before this point
            # (but safer to not assert this, but just debug print for now)
            print "bug: _bridging_Pl_atoms on ladder with error or not valid:", self
            return
        res = {}
        for end_atom, next_atom in self._corner_atoms_with_next_atoms_or_None():
            if end_atom._dna_updater__error:
                print "bug: %r has _dna_updater__error %r in %r, returning no _bridging_Pl_atoms" % \
                      (end_atom, end_atom._dna_updater__error, self)
                return []
            possible_Pl = next_atom
            # might be None or a non-Pl atom; if a Pl atom, always include in return value,
            # unless it has a _dna_updater__error, in which case complain and bail
            if possible_Pl is not None and possible_Pl.element is Pl5:
                if possible_Pl._dna_updater__error:
                    print "bug: possible_Pl %r has _dna_updater__error %r in %r, returning no _bridging_Pl_atoms" % \
                      (possible_Pl, possible_Pl._dna_updater__error, self)
                return []
                res[possible_Pl.key] = possible_Pl
            continue
        return res.values()

    def _corner_atoms_with_next_atoms_or_None(self): #bruce 080410 split this out of _bridging_Pl_atoms
        """
        @note: we don't check for self.error or not self.valid, but our results
               can be wrong if caller didn't check for this and not call us then
               (since strand bond directions can be different than we assume).
        
        @return: a list of pairs (end_atom, next_atom), each describing one of
                 our corners (ends of strand rails, of which we have 2 per
                 strand rail); end_atom is always an Ss3 or Ss5 atom in self,
                 but next_atom might be None, or a Pl in same or other ladder,
                 or X in same ladder, or Ss3 or SS5 in other ladder;
                 "other ladder" can be self if the strand connects to self.
                 All these cases should be handled by callers;
                 so must be checking result for repeated atoms,
                 or for _dna_updater__error set on the atoms.
        """
        # same implem is correct for axis ladders (superclass) and free floating
        # single strands (subclass)
        res = []
        for rail in self.strand_rails:
            assert rail is not None
            for end in LADDER_ENDS:
                bond_direction_to_other = LADDER_BOND_DIRECTION_TO_OTHER_AT_END_OF_STRAND1[end]
                if rail is not self.strand_rails[0]:
                    # note: ok if len(self.strand_rails) == 0, since we have no
                    # itertions of the outer loop over rail in that case
                    bond_direction_to_other = - bond_direction_to_other
                    # ok since we don't pam_convert ladders with errors
                    # (including parallel strand bonds) ### REVIEW: is that check implemented?
                end_atom = rail.end_baseatoms()[end]
                next_atom = end_atom.next_atom_in_bond_direction( bond_direction_to_other)
                    # 
                res.append( (end_atom, next_atom) )
                continue
            continue
        return res

    def fix_bondpoint_positions_at_ends_of_rails(self): #bruce 080411
        fix_soon = {}
        def _fix(atom):
            fix_soon[atom.key] = atom
        # first, strand rails [this is not working as of 080411 +1:14am PT]
        for end_atom, next_atom in self._corner_atoms_with_next_atoms_or_None():
            _fix(end_atom)
            if next_atom is not None and next_atom.element is Pl5:
                # a Pl, maybe with a bondpoint
                _fix(next_atom)
        # next, axis rails [this seems to work]
        if self.axis_rail:
            _fix(self.axis_rail.baseatoms[0])
            _fix(self.axis_rail.baseatoms[-1])
        # now do it
        for atom in fix_soon.values():
            if atom.element is Singlet:
                print "didn't expect X here:", atom
                continue
            atom.reposition_baggage()
                # Note: on baseatoms (and on Pl if we extend it for that),
                # this ends up setting a flag which causes a later call
                # by the same dna updater run as we're in now
                # to call self._f_reposition_baggage. As of now,
                # that only works for baseatoms, not Pls sticking out from them.
                # But maybe the direct code will work ok for Pl.
            continue
        return
    
    # ==
    
    def clear_baseframe_data(self):
        assert self.valid # otherwise caller must be making a mistake to call this on self
        self._baseframe_data = None
            # if not deleted, None means it had an error,
            # not that it was never computed, so:
        del self._baseframe_data
        # probably not needed:
        ladders_dict = _f_ladders_with_up_to_date_baseframes_at_ends
        if ladders_dict.has_key(self):
            print "unexpected: %r in ladders_dict too early, when cleared" % self
            # only unexpected due to current usage, not an error in principle
        ladders_dict.pop(self, None) 
        return

    def _f_store_locator_data(self): #bruce 080411
        """
        #doc
        
        @see: related method, whichrail_and_index_of_baseatom
        """
        print "storing locator data for", self #####
        locator = _f_atom_to_ladder_location_dict
        look_at_rails = self.rail_indices_and_rails()
        length = len(self)
        for index in range(length):
            for whichrail, rail in look_at_rails:
                if whichrail == 1:
                    continue # KLUGE optim -- skip axis rail;
                        # see LADDER_RAIL_INDICES (may exist only in docstrings)
                baseatom = rail.baseatoms[index]
                locator[baseatom.key] = (self, whichrail, index)
                # print "fyi: stored locator[%r.key] = %r" % (baseatom, locator[baseatom.key])
                if index in (0, 1, length - 1): # slow, remove when works ###
                    assert self.rail_at_index(whichrail).baseatoms[index] is baseatom
                    assert self.whichrail_and_index_of_baseatom(baseatom) == (whichrail, index) # by search in self
                    assert self._f_use_locator_data(baseatom) == (whichrail, index) # using locator global
                continue
            continue
        return

    def _f_use_locator_data(self, baseatom): #bruce 080411 # so far, used only for asserts above
        locator = _f_atom_to_ladder_location_dict
        ladder, whichrail, index = locator[baseatom.key]
        assert ladder is self
        return whichrail, index

    def _f_baseframe_data_at(self, whichrail, index): # bruce 080402
        """
        #doc
        """
        if not self.valid: #bruce 080411
            # maybe make this an assertion failure?
            print "likely bug: invalid ladder in _f_baseframe_data_at(%r, %r, %r)" % \
                  (self, whichrail, index)
        ladders_dict = _f_ladders_with_up_to_date_baseframes_at_ends
        # review: is this code needed elsewhere?
        # caller is not sure self._baseframe_data is computed and/or
        # up to date, and is keeping a set of ladders in which it's knowmn
        # to be up to date (at least at the ends, which is all it needs
        # for the ladders it's not sure about) in the above global known
        # locally as ladders_dict.
        # If we're not in there, compute our baseframe data and store it
        # (at least at the first and last basepair) and store self into
        # ladders_dict. [bruce 080409]
        assert type(ladders_dict) is type({})
        if self not in ladders_dict:
            assert index == 0 or index == len(self) - 1, \
                   "_f_baseframe_data_at%r: index not at end but self not in ladders_dict" % \
                   ( (self, whichrail, index), )
            self._compute_and_store_new_baseframe_data( ends_only = True)
            pass
        if index == 0 or index == len(self) - 1:
            assert ladders_dict.has_key(self)
        else:
            assert ladders_dict[self] == False, \
                "_f_baseframe_data_at%r: index not at end but ladders_dict[self] != False, but %r" % \
                   ( (self, whichrail, index), ladders_dict[self])
                   # not ends_only, i.e. full recompute
        baseframe_data = self._baseframe_data
        if whichrail == 0:
            return baseframe_data[index]
        assert whichrail == 2
        return other_baseframe_data( * baseframe_data[index] )
            # maybe: store this too (precomputed), as an optim

    def _compute_and_store_new_baseframe_data(self, ends_only = False):
        #bruce 080408
        """
        @return: success boolean
        """
        assert self.valid and not self.error
        # note: this implem is for an axis ladder, having any number of strands.
        # The DnaSingleStrandDomain subclass overrides this. #### DOIT
        # This version, when converting to PAM5, first makes up "ghost bases"
        # for missing strands, so that all strands are present. For PAM5->PAM3
        # it expects those to be there, but if not, makes them up anyway;
        # then at the end (with PAM3) removes any ghost bases present.
        # Ghost bases are specially marked Ss or Pl atoms.
        # The ghost attribute is stored in the mmp file, and is copyable and undoable. #### DOIT
        self._baseframe_data = None
        assert self.axis_rail, "need to override this in the subclass"
        if ends_only:
            print "fyi: %r._compute_and_store_new_baseframe_data was only needed at the ends, optim is nim" % self ### remove when seen as expected
        # using ends_only is an optim, not yet implemented
        if len(self.strand_rails) < 2:
            self._make_ghost_bases() # IMPLEM -- until then, conversion fails on less than full duplexes
                # need to DECIDE how we'll do this when we implement the
                # "mmp save only" version, for which we'd prefer virtual
                # ghost bases. @@@@
        assert len(self.strand_rails) == 2
        data = []
        for rail in self.all_rail_slots_from_top_to_bottom():
            baseatoms = rail.baseatoms
            posns = [a.posn() for a in baseatoms]
            data.append(posns)
        baseframes = compute_duplex_baseframes(self.pam_model(), data)
        # even if this is None, we store it, and store something saying we computed it
        # so we won't try to compute it again -- though uses of it will fail.
        print "fyi: computed baseframes (ends_only = %r) for %r; success == %r" % \
              (ends_only, self, (baseframes is not None)) #######
        print " details of self: valid = %r, error = %r, assy = %r, contents:\n%s" % \
              (self.valid, self.error, self.axis_rail.baseatoms[0].molecule.assy,
               self.ladder_string()) ########
        self._baseframe_data = baseframes # even if None
        ladders_dict = _f_ladders_with_up_to_date_baseframes_at_ends
        if ladders_dict.get(self, None) is not None:
            print "unexpected: %r was already computed (ends_only = %r), doing it again (%r)" % \
                  (self, ladders_dict[self], ends_only)
        if ends_only:
            # partial recompute: only record if first recompute for self            
            ladders_dict.setdefault(self, ends_only) 
        else:
            # full recompute: overrides prior record
            if ladders_dict.get(self, None) == True:
                print " in fact, very unexpected: was computed at ends and is now computed on whole"
            ladders_dict[self] = ends_only 
        if baseframes is None:
            # todo: print summary message? give reason (hard, it's a math exception)
            # (warning: good error detection might be nim in there)
            return False
        return True
    
    pass

# end
