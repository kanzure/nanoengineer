# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
pam_conversion.py -- help dna model objects convert between PAM models

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from utilities.GlobalPreferences import dna_updater_is_enabled

from utilities.constants import PAM_MODELS
from utilities.constants import Pl_STICKY_BOND_DIRECTION

import foundation.env as env
from utilities.Log import orangemsg, redmsg

from model.elements import Pl5

# ==

# refile with class writemmp_mapping

class writemmp_mapping_memo(object):
    mapping = None
    def __init__(self, mapping):
        self.mapping = mapping
    def destroy(self): # todo: call, to avoid ref cycles 
        self.mapping = None
    pass

# ==

# helpers for DnaLadderRailChunk and subclasses

class DnaLadderRailChunk_writemmp_mapping_memo(writemmp_mapping_memo):
    """
    """
    
    convert_pam_enabled = False

    _ladder_memo = None
    
    def __init__(self, mapping, chunk):
        # immediately memoize some settings which need to be constant
        # during use, as a bug precaution. Also do whatever precomputes
        # are convenient.
        writemmp_mapping_memo.__init__(self, mapping)
        self.chunk = chunk
        self.ladder = chunk.ladder
        if not dna_updater_is_enabled():
            msg = "Warning: can't convert PAM model when dna updater is disabled; affects [N] chunk(s)"
            env.history.deferred_summary_message( orangemsg( msg))
        elif not self.ladder:
            # (might happen if dna updater is turned off at runtime -- not sure;
            #  note, doing that might have worse effects, like self.ladder existing
            #  but being out of date, causing traceback errors. #### FIX those sometime (elsewhere).)
            print "error: ladder not set during writemmp, can't convert pam model, in %r" % chunk
            msg = "Error: [N] chunk(s) don't have ladders set"
            env.history.deferred_summary_message( redmsg( msg))
        else:
            self.convert_pam_enabled = True
        if self.convert_pam_enabled:
            self._ladder_memo = mapping.get_memo_for(self.ladder)
        return
    
    def _f_save_as_what_PAM_model(self):
        if not self.convert_pam_enabled:
            return None
        return self._ladder_memo._f_save_as_what_PAM_model()

    pass

class DnaStrandChunk_writemmp_mapping_memo(DnaLadderRailChunk_writemmp_mapping_memo):
    """
    """
    number_of_conversion_atoms = None
    
    def __init__(self, mapping, chunk):
        DnaLadderRailChunk_writemmp_mapping_memo.__init__(self, mapping, chunk)
        self.Pl_atoms = self._compute_Pl_atoms()
        self.number_of_conversion_atoms = self._compute_number_of_conversion_atoms()
        return
    
    def _f_number_of_conversion_atoms(self):
        return self.number_of_conversion_atoms

    def _compute_number_of_conversion_atoms(self):
        # Our conversion atoms are whatever Pl atoms we are going to write
        # which are not in self.chunk.atoms
        chunk = self.chunk
        res = 0
        for Pl in self.Pl_atoms: # in order, possible Nones at end
            if Pl is not None:
                # not sure this is correct: if Pl.molecule is not self.chunk:
                if Pl.key not in chunk.atoms: # method for that? _Pl_alive?
                    res += 1
        return res

    def _compute_Pl_atoms(self): # need to know strand direction, based on where we are in ladder ###
        baseatoms = self.chunk.get_baseatoms()
        assert 0, 'nim' ###### REMEMBER TO CARE ABOUT what pam model to convert to if any! if xx == MODEL_PAM5 -= in callers??

    def _compute_one_Pl_atom(self, i1, i2): # optim: pass a1 and a2 instead??
        """
        Find or make the live or cached/nonlive Pl atom
        which binds, or should bind, baseatoms[i1] to baseatoms[i2],
        where bond direction going from i1 to i2 agrees with
        Pl_STICKY_BOND_DIRECTION.
        One of those indices (i1, i2) might be out of range,
        indicating we want a Pl at the end, bound to only one baseatom,
        or None if there should be no such Pl atom.
        """
        chunk = self.chunk
        baseatoms = chunk.baseatoms
        # If both atoms (at i1, i2) are real, we store that Pl with a2
        # (the atom at i2) (since that is in the right direction from it,
        #  namely Pl_STICKY_BOND_DIRECTION).
        if 0 <= i2 < len(baseatoms):
            a2 = baseatoms[i2]
        else:
            a2 = None # or get it from neighbor_baseatom?
                # no, that Pl would belong in a neighbor chunk
        if 0 <= i1 < len(baseatoms):
            a1 = baseatoms[i1]
        else:
            a1 = None
        assert a2 is not None or a1 is not None
        # first return the Pl if it's live (bonded to a2 or a1)
        if a2 is not None:
            # if a2 exists in chunk, a live Pl between a1 and a2
            # would be preferentially bonded to a2, so also in chunk
            candidate = a2.next_atom_in_bond_direction( - Pl_STICKY_BOND_DIRECTION)
            if candidate is not None:
                # should be either a1 or our Pl
                if candidate.element is Pl5:
                    # todo: assert bound to a1 if it exists, or to
                    # neighbor_baseatom in that direction if *that* exists
                    if candidate.molecule is chunk: # required for returning live ones
                        return candidate
                    else:
                        print "bug? %r not in %r but should be" % \
                              (candidate, chunk,)
                        pass
        else:
            # if only a1 is in chunk, a live Pl bonded to it
            # (in the right direction) is only ok if it's also in chunk,
            # or (should be equivalent) if it prefers a1 to other neighbors.
            # For a live one, use "in chunk" as definitive test, to avoid bugs.
            candidate = a1.next_atom_in_bond_direction( + Pl_STICKY_BOND_DIRECTION)
            if candidate is not None:
                if candidate.element is Pl5:
                    if candidate.molecule is chunk: # no error if not, unlike a2 case
                        return candidate
            pass
        # now find or make a non-live Pl to return, iff conversion options desire this.
        assert 0, "do they?"
        ### REVIEW: is this also a good time to compute (and store in it?) its position?
        # guess yes, since we have a1 and a2 handy and know their bond directions.
        # Note that this only runs once per writemmp, but the position is fixed then
        # so that's fine. We don't cache it between those since it's so likely to
        # become invalid, so not worth tracking that.
        if a2 is not None:
            res = a2._f_get_nonlive_pam3plus5_Pl( - Pl_STICKY_BOND_DIRECTION) # IMPLEM
            assert res is None or res.element is Pl5
            return res # might be None
        else:
            return None #???
                # reasoning: if neighbor baseatom exists,
                # put the Pl in that neighbor chunk.
                # if not, there needn't be one (not sure about that).
        pass # end of def _compute_one_Pl_atom (not reached)
    
    pass # end of class DnaStrandChunk_writemmp_mapping_memo

# ==

# helpers for DnaLadder

class DnaLadder_writemmp_mapping_memo(writemmp_mapping_memo):

    def __init__(self, mapping, ladder):
        # assume never created except by chunks, so we know dna updater is enabled
        writemmp_mapping_memo.__init__(self, mapping)
        assert dna_updater_is_enabled()
        self.ladder = ladder
        self.save_as_pam = self._compute_save_as_pam()
        return
    
    def _f_save_as_what_PAM_model(self):
        return self.save_as_pam

    def _compute_save_as_pam(self):
        common_answer = None
        mapping = self.mapping
        for chunk in self.ladder.all_chunks():
            r = chunk._f_requested_pam_model_for_save(mapping)
            if not r:
                return None
            assert r in PAM_MODELS
                # todo: enforce in mmp read (silently)
            if not common_answer:
                common_answer = r
            if r != common_answer:
                return None
            continue
        assert common_answer
        return common_answer

    pass

# TODO: (remember single strand domains tho -- what kind of chunks are they?)


# end

