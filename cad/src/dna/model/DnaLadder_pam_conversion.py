# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaLadder_pam_conversion.py - PAM3+5 <-> PAM5 conversion methods for DnaLadder,
and (perhaps in future) related helper functions.

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from model.elements import Pl5

from utilities.constants import MODEL_PAM3, MODEL_PAM5, PAM_MODELS, MODEL_MIXED
from utilities.constants import noop

from utilities.Log import redmsg, quote_html


from platform.PlatformDependent import fix_plurals

import foundation.env as env

from dna.model.dna_model_constants import LADDER_ENDS
from dna.model.dna_model_constants import LADDER_BOND_DIRECTION_TO_OTHER_AT_END_OF_STRAND1

from dna.model.pam3plus5_math import other_baseframe_data, compute_duplex_baseframes

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

    # todo: also a command to "convert to default PAM display" which sets chunk.display_as_pam = None
    # (what to call it?)
    # (or just make the one that corresponds to that, do that, if it's pam3 at least??)
    
    def _cmd_convert_to_pam(self, which_model):
        """
        Command to convert all of self to one of the PAM_MODELS.
        """
        env.history.graymsg(quote_html("Debug fyi: Convert %r to %s" % (self, which_model))) #####
        for chunk in self.all_chunks():
            chunk.display_as_pam = which_model
            chunk.changed() # calls assy.changed(); might be needed
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
        want = self.arbitrary_baseatom().molecule.display_as_pam
        if not want:
            want = default_pam_model # might be None, which means, whatever you already are
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
        if self.axis_rail and self.axis_rail.baseatoms[0].element.symbol not in ('Gv5', 'Ax3'):
            # todo: summary message about why
            # guess the reason is Ax5... if this happens, improve msg to be specific
            print "conversion from PAM axis element %r is not yet implemented" % \
                  self.axis_rail.baseatoms[0].element.symbol
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

        print "WARNING: _convert_to_pam(%r, %r) is unfinished, will fail somehow" % (self, pam_model) #### @@@
        
        # first compute and store current baseframes on self, where private
        # methods can find them on demand. REVIEW: need to do this on connected ladders
        # not being converted, for sake of bridging Pl atoms? Not if we can do those
        # on demand, but then we'd better inval them all first! Instead, caller passes
        # a ladders_dict (see that parameter in various methods, for doc).
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

        self._convert_axis_to_pam(pam_model) # moves and transmutes axis atoms # IMPLEM
        for rail in self.strand_rails:
            self._convert_strand_rail_to_pam(pam_model, rail)# IMPLEM
                # moves and transmutes sugars, makes or removes Pls,
                # but does not notice or remove ghost bases
            continue
        if pam_model == MODEL_PAM5:
            self._make_bridging_Pls_as_needed()# IMPLEM

        if pam_model == MODEL_PAM3: # (do this last)
            # todo: remove ghost bases if desired
            pass

        # optional: remove all baseframe data except at the ends
        # (in case needed by bridging Pls) -- might help catch bugs or save RAM
        
        return True  # could put above in try/except and return False for exceptions

    def _f_finish_converting_bridging_Pl_atoms(self, ladders_dict): #bruce 080408        
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
        for Pl in self._bridging_Pl_atoms():
            Pl._f_Pl_finish_converting_if_needed(ladders_dict)
                # note: this might kill Pl.
        return

    def _bridging_Pl_atoms(self):
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
        # same implem is correct for axis ladders (superclass) and free floating
        # single strands (subclass)
        res = {}
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
                if end_atom._dna_updater__error:
                    print "bug: %r has _dna_updater__error %r in %r, returning no _bridging_Pl_atoms" % \
                          (end_atom, end_atom._dna_updater__error, self)
                    return []
                possible_Pl = end_atom.next_atom_in_bond_direction( bond_direction_to_other)
                # might be None or a non-Pl atom; if a Pl atom, always include in return value,
                # unless it has a _dna_updater__error, in which case complain and bail
                if possible_Pl is not None and possible_Pl.element is Pl5:
                    if possible_Pl._dna_updater__error:
                        print "bug: possible_Pl %r has _dna_updater__error %r in %r, returning no _bridging_Pl_atoms" % \
                          (possible_Pl, possible_Pl._dna_updater__error, self)
                    return []
                    res[possible_Pl.key] = possible_Pl
                continue
            continue
        return res.values()

    # ==
    
    def clear_baseframe_data(self):
        self._baseframe_data = None
            # if not deleted, None means it had an error,
            # not that it was never computed, so:
        del self._baseframe_data
        return
    
    def _f_baseframe_data_at(self, whichrail, index): # bruce 080402 # refile within class?
        """
        #doc
        """
        baseframe_data = self._baseframe_data
        if whichrail == 0:
            return baseframe_data[index]
        assert whichrail == 2
        return other_baseframe_data( baseframe_data[index] )
            # maybe: store this too (precomputed), as an optim

    def _compute_and_store_new_baseframe_data(self, ends_only = False): #bruce 080408 #### @@@@ CALL ME from [+]main and [-]corners
        """
        @return: success boolean
        """
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
        del ends_only # using this is an optim, not yet implemented
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
        self._baseframe_data = baseframes # even if None
        if baseframes is None:
            # todo: print summary message? give reason (hard, it's a math exception)
            # (warning: good error detection might be nim in there)
            return False
        return True
    
    pass

# end
