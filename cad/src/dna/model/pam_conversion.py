# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
pam_conversion.py -- help dna model objects convert between PAM models

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from utilities.GlobalPreferences import dna_updater_is_enabled

from utilities.constants import PAM_MODELS
from utilities.constants import MODEL_PAM3, MODEL_PAM5
from utilities.constants import Pl_STICKY_BOND_DIRECTION

from utilities.constants import diDEFAULT

from dna.model.dna_model_constants import LADDER_STRAND1_BOND_DIRECTION

import foundation.env as env
from utilities.Log import orangemsg, redmsg

from model.elements import Pl5

from geometry.VQT import V

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

    _save_as_pam = None
    
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
            # Note: this only means conversion is possible -- we don't yet know
            # if it's requested by options on this mapping and chunk.
            # The ladder memo will decide that.
            self._ladder_memo = mapping.get_memo_for(self.ladder)
            self._save_as_pam = self._ladder_memo._f_save_as_what_PAM_model()
        return
    
    def _f_save_as_what_PAM_model(self):
        return self._save_as_pam

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
        if self._save_as_pam == MODEL_PAM3:
            return 0
        chunk = self.chunk
        res = 0
        for Pl in self.Pl_atoms: # in order, possible Nones at end (or in middle when not converting to PAM5)
            if Pl is not None:
                # not sure this is correct: if Pl.molecule is not self.chunk:
                if Pl.key not in chunk.atoms: # method for that? _Pl_alive?
                    res += 1
        return res

    def _compute_Pl_atoms(self): 
        if self._save_as_pam == MODEL_PAM3:
            return None # or if this fails, [None] * (length+1)

        # find out strand direction, based on where we are in ladder
        chunk = self.chunk
        ladder = chunk.ladder
        rail = chunk.get_ladder_rail()
        assert rail in ladder.strand_rails
        if rail is ladder.strand_rails[0]:
            direction = LADDER_STRAND1_BOND_DIRECTION
        else:
            direction = - LADDER_STRAND1_BOND_DIRECTION
        
        baseatoms = rail.baseatoms

        # note: we never look at Pls cached on neighbor_baseatoms
        # since any such Pl would belong in a neighbor chunk, not ours
        
        if direction == Pl_STICKY_BOND_DIRECTION:
            # Pls want to stick to the right within baseatoms;
            # pass baseatom pairs in current order
            pairs = zip( [None] + baseatoms, baseatoms + [None] )
        else:
            # Pls want to stick to the left; pass reversed pairs
            # (but no need to reverse the result)
            pairs = zip( baseatoms + [None], [None] + baseatoms )

        res = [self._compute_one_Pl_atom(a1, a2) for (a1, a2) in pairs]

        return res

    def _compute_one_Pl_atom(self, a1, a2):
        """
        Find or make the live or cached/nonlive Pl atom
        which binds, or should bind, adjacent baseatoms a1 and a2,
        where bond direction going from a1 to a2 agrees with
        Pl_STICKY_BOND_DIRECTION.
        
        One of those atoms might be passed as None,
        indicating we want a Pl at the end, bound to only one baseatom,
        or None if there should be no such Pl atom.

        @param a1: a baseatom or None
        @param a2: an adjacent baseatom or None
        """
        chunk = self.chunk
        # If both atoms are real (not None), we store that Pl with a2,
        # since that is in the right direction from it,
        # namely Pl_STICKY_BOND_DIRECTION.
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
        if self._save_as_pam != MODEL_PAM5:
            return None
        
        ### REVIEW: is this also a good time to compute (and store in it?) its position?
        # guess yes, since we have a1 and a2 handy and know their bond directions.
        # Note that this only runs once per writemmp, but the position is fixed then
        # so that's fine. We don't cache it between those since it's so likely to
        # become invalid, so not worth tracking that.
        if a2 is not None:
            res = a2._f_get_fake_Pl( - Pl_STICKY_BOND_DIRECTION) # IMPLEM; can find cached, or make
                # Note: res is not an Atom, and not part of undoable state.
                # It can act like an Atom in a few ways we use here --
                # most importantly, having a fixed .key not overlapping a real atom .key.
            assert res is None or isinstance(res, Fake_Pl)
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

# ==

# TODO: (remember single strand domains tho -- what kind of chunks are they?)

# ==

class Fake_Pl(object): #bruce 080327
    """
    not an Atom! but acts like one in a few ways --
    especially, has an atom.key allocated from the same pool
    as real Atoms do.
    """
    ## element = Pl5 # probably not needed

    ## display = diDEFAULT # probably not needed now,
        # though someday we might try to preserve this info
        # across PAM5 <-> PAM3+5 conversion

    def __init__(self):
        from model.chem import atKey # bad: helps cause import cycle with chem ###FIX
        self.key = atKey.next()

    def posn(self):
        return V(0,0,0) # STUB
    
    def writemmp(self, mapping):
        """
        Write a real mmp atom record for self (not a real atom),
        and whatever makes sense to write for a fake Pl atom
        out of the other mmp records written for a real atom:
        the bond records for whatever bonds have then had both atoms
        written (internal and external bonds are treated identically),
        and any bond_direction records needed for the bonds we wrote.

        Let mapping options influence what is written for any of those
        records.

        @param mapping: an instance of class writemmp_mapping. Can't be None.
        
        @note: compatible with Atom.writemmp and Node.writemmp,
               though we're not a subclass of Atom or Node.
        """
        # WARNING: has common code with Atom.writemmp
        num_str = mapping.encode_next_atom(self)
        ## display = self.display
        display = diDEFAULT
        disp = mapping.dispname(display) # note: affected by mapping.sim flag
        posn = self.posn() # might be revised below
        ## element = self.element
        element = Pl5
        eltnum = element.eltnum
        xyz = posn * 1000
            # note, xyz has floats, rounded below (watch out for this
            # if it's used to make a hash) [bruce 050404 comment]
        xyz = [int(coord + 0.5) for coord in xyz]
            #bruce 080327 add 0.5 to improve rounding accuracy
        print_fields = (num_str, eltnum, xyz[0], xyz[1], xyz[2], disp)
        mapping.write("atom %s (%d) (%d, %d, %d) %s\n" % print_fields)
        mapping.write("# bug: writing bonds of that fake_Pl is nim\n")
    pass

# end

