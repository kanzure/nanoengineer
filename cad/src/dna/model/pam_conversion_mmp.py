# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
pam_conversion_mmp.py -- help dna model objects convert between PAM models during writemmp

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

# Note: this file is indirectly imported by chem.py via PAM_Atom_methods,
# so its imports need to be kept fairly clean to avoid import cycles.
# [bruce 080510 comment]

from utilities.GlobalPreferences import dna_updater_is_enabled

from utilities.constants import PAM_MODELS
from utilities.constants import MODEL_PAM3, MODEL_PAM5
from utilities.constants import Pl_STICKY_BOND_DIRECTION

from utilities.constants import diDEFAULT

from utilities.constants import average_value
from utilities.constants import atKey

import foundation.env as env
from utilities.Log import orangemsg, redmsg

from model.elements import Pl5

from geometry.VQT import V

# ==

# TODO: refile this with class writemmp_mapping:
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

        # find out idealized strand direction, based on where we are in ladder
        # (not always equal to true strand direction, if ladder.error is set;
        #  that matters elsewhere (and is checked there) but doesn't matter here,
        #  I think -- not sure, it might cause trouble at the ends ####REVIEW --
        #  can/should we just leave out end-Pls then??)
        chunk = self.chunk
        baseatoms = chunk.get_baseatoms()
        direction = chunk.idealized_strand_direction()

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

        if res[0] is res[-1] and len(res) > 1 and res[0] is not None:
            # The same Pl atom is at both ends of res
            # (possible for a ring strand).
            # Decide which one to replace with None so that we never
            # return a list that contains one atom twice.
            # (I don't know whether it matters which end we leave it on,
            #  but we'll leave it on the "best one" anyway.)
            # [bruce 080516 bugfix]
            if direction == Pl_STICKY_BOND_DIRECTION:
                # Pls want to stick to the right,
                # so this one is happiest in res[0],
                # so remove it from res[-1]
                res[-1] = None
            else:
                res[0] = None
            pass

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

        @warning: for a ring strand in one chunk, we can return the same Pl atom
                  at both ends. (Only when we find an existing one, I think.)
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
            # (This is not exactly equivalent, in the case of a ring strand in one
            #  chunk. This is what leads to returning the same Pl in two places
            #  in that case, I think. [bruce 080516 comment])
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
            res = a2._f_get_fake_Pl( - Pl_STICKY_BOND_DIRECTION)
                # Note: res is not an Atom, and is not part of undoable state.
                # It can act like an Atom in a few ways we use here --
                # most importantly, having a fixed .key not overlapping a real atom .key.
            assert res is None or isinstance(res, Fake_Pl)
            return res # might be None
        else:
            return None #???
                # Note: reasoning: if neighbor baseatom exists,
                # put the Pl in that neighbor chunk.
                # (Which might be the other end of this chunk,
                #  for a ring strand in one chunk,
                #  but if so, we'll do that in a separate call.)
                # If not, there needn't be one (not sure about that).
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
        self.wrote_axis_chunks = [] # public attrs
        self.wrote_strand_chunks = []
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

    def advise_wrote_axis_chunk(self, chunk): # 080328
        """
        Record the fact that we finished writing the given axis chunk
        during the mmp save controlled by self.mapping.
        """
        self.wrote_axis_chunks.append(chunk)
        return

    def advise_wrote_strand_chunk(self, chunk): # 080328
        """
        Record the fact that we finished writing the given strand chunk
        during the mmp save controlled by self.mapping.
        """
        self.wrote_strand_chunks.append(chunk)
        return

    def write_rung_bonds(self, chunk1, chunk2): # 080328
        """
        Assuming the two given chunks of our ladder have just been
        written via self.mapping, and their rung bonds have not,
        write those compactly.
        """
        mapping = self.mapping
        s1, e1 = chunk1._f_compute_baseatom_range(mapping)
        s2, e2 = chunk2._f_compute_baseatom_range(mapping)
        record = "dna_rung_bonds %s %s %s %s\n" % (s1, e1, s2, e2)
        mapping.write(record)
        return

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

    owning_Ss_atom = None # not yet used
    bond_direction = 0 # not yet used (direction of self from that atom)
        # usually (or always?) this is (- Pl_STICKY_BOND_DIRECTION)

    def __init__(self, owning_Ss_atom, bond_direction):
        self.key = atKey.next()
        self.owning_Ss_atom = owning_Ss_atom
            # reference cycle -- either destroy self when atom is destroyed,
            # or just store owning_Ss_atom.key or so
        self.bond_direction = bond_direction
        return

    def posn(self): # stub - average posn of Ss neighbors (plus offset in case only one!)
        print "should use Pl_pos_from_neighbor_PAM3plus5_data for %r" % self #####
        # note: average_value seems to work here
        res = average_value( [n.posn() for n in self.neighbors()], V(0, 0, 0) )
        return res + V(0, 2, 0) # offset (kluge, wrong)

    def writemmp(self, mapping, dont_write_bonds_for_these_atoms = ()):
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
        posn = self.posn()
        ## element = self.element
        element = Pl5
        eltnum = element.eltnum

        #bruce 080521 refactored the code for printing atom coordinates
        # (and fixed a rounding bug, described in encode_atom_coordinates)
        xs, ys, zs = mapping.encode_atom_coordinates( posn )
        print_fields = (num_str, eltnum, xs, ys, zs, disp)
        mapping.write("atom %s (%d) (%s, %s, %s) %s\n" % print_fields)

        if mapping.write_bonds_compactly:
            # no need to worry about how to write bonds, in this case!
            # it's done implicitly, just by writing self between its neighbor Ss atoms,
            # due to the directional_bond_chain mmp record.
            # (to make this work fully, we need to include the strand-end bondpoints...
            #  and add a special case for a fake_Pl that bridges two chunks.
            #  ###### NONTRIVIAL -- we might not even have written the other chunk yet...)
            pass
        else:
            mapping.write("# bug: writing fake_Pl bonds is nim, when not using directional_bond_chain mmp record\n")
                # TODO: summary redmsg, so I don't forget this is nim...
            # todo: use dont_write_bonds_for_these_atoms,
            # and self._neighbor_atoms, but note they might not be written out yet...
            # we might just assume we know which ones were written or not,
            # and write the atom and bond records in one big loop in the caller...
            # e.g. have our chunk copy & modify the atom writemmp loop and write
            # the between-atom bonds itself (like using the directional_bond_chain
            #  record, but spelling it out itself).
            # (Would things be easiest if we made fake Ss atoms too,
            #  or (similarly) just did an actual conversion (all new atoms) before writing?
            #  The issue is, avoiding lots of overhead (and undo issues) from making new Atoms.)
        return

    def _neighbor_atoms(self): # needed?
        a1 = self.owning_Ss_atom
        a2 = a1.next_atom_in_bond_direction(self.bond_direction) # might be None
        assert a2 is not self
        res = [a1, a2]
        if self.bond_direction < 0:
            res.reverse() #k good? better to compare to +/- Pl_STICKY_BOND_DIRECTION??
        print "_neighbor_atoms -> ", res #######
        return res

    def neighbors(self):
        return filter(None, self._neighbor_atoms())

    pass # end of class

# end

