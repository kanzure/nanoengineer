# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
DnaChain.py - Dna-aware AtomChainOrRing subclasses, AxisChain and StrandChain

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna.model.DnaMarker import DnaSegmentMarker
from dna.model.DnaMarker import DnaStrandMarker

from utilities import debug_flags

from utilities.debug import print_compact_stack, print_compact_traceback

from dna.model.dna_model_constants import LADDER_ENDS
from dna.model.dna_model_constants import LADDER_END0

from dna.updater.dna_updater_globals import rail_end_atom_to_ladder

import foundation.env as env
from utilities.Log import redmsg

from model.bond_constants import find_bond, find_Pl_bonds
from model.bond_constants import atoms_are_bonded

# ==

DEBUG_NEIGHBOR_BASEATOMS = False # DO NOT COMMIT WITH True
    #bruce 080530 for bug in length 1 sticky end ghost bases

# ==

try:
    _chain_id_counter
except NameError:
    _chain_id_counter = 0

# ==

### REVIEW: should a DnaChain contain any undoable state? (it doesn't now) (guess: no)

class DnaChain(object):
    """
    Base class for various kinds of DnaChain. Mostly abstract --
    just has baseatoms (which must be set by subclass),
    index_direction, and methods that only depend on those.
    """

    # default values of public instance variables:

    strandQ = None # will be set to a boolean saying whether we're made of strand or axis atoms

    baseatoms = () # public for read; sequence of all our atoms with a baseindex
        # (whether in strand or axis) (leaves out Pl, bondpoints, termination atoms)
        # note: subclass-specific __init__ must set this; used in __repr__

    neighbor_baseatoms = (-1, -1) # when set, each element is None or a
        # neighboring baseatom (in a directly connected chain, possibly self
        # if self is a ring)
        # note: set by _f_update_neighbor_baseatoms, some doc is there

    index_direction = 1 # instances negate this when they reverse baseatoms
        # (and thus its indexing) using reverse_baseatoms. It records the
        # relation between the current and original baseindex direction.
        #
        # note: baseindex direction is not necessarily the same as bond
        # direction for strands (which is not even defined for axis bonds).

        # note: i'm not sure index_direction is needed -- it's used, but it
        # might be that it's only changed after it doesn't matter to the
        # current overall algorithm. OTOH, it might turn out that when
        # merging ladders and reversing it, we have to tell their markers
        # we did that, which is not done now [071204].
        #
        # update 080602: this is NO LONGER USED (as of long ago, probably when
        # DnaMarkers got two atoms each) except to maintain its own value
        # (in self and other chains made from self). TODO: remove it.

    def __repr__(self):
        classname = self.__class__.__name__.split('.')[-1]
        if self.strandQ is None:
            basetype = 'strandQ-unknown'
        else:
            basetype = self.strandQ and 'strand' or 'axis'
        res = "<%s (%d %s bases) at %#x>" % \
              (classname, len(self), basetype, id(self))
        return res

    def _reverse_neighbor_baseatoms(self):
        self.neighbor_baseatoms = list(self.neighbor_baseatoms)
        self.neighbor_baseatoms.reverse()
        if DEBUG_NEIGHBOR_BASEATOMS:
            if self.neighbor_baseatoms[0] != -1 or \
               self.neighbor_baseatoms[1] != -1:
                msg = "reversed %r.neighbor_baseatoms to get %r" % (self, self.neighbor_baseatoms)
                print_compact_stack( "\n" + msg + ": ")
        return

    def baseatom_index_pairs(self):
        """
        Return a list of pairs (baseatom, baseindex) for every pseudoatom
        in self.chain_or_ring which corresponds to a base or basepair,
        using an arbitrary origin for baseindex, and a direction corresponding
        to how we store the atoms, which is arbitrary until something corrects it;
        ###REVIEW whether to correct it by list reversal or setting index_direction,
        and whether to also store a base_offset for use by this function.

        (This skips PAM5 Pl atoms in strands, and would skip any bondpoint-like
        termination atoms if we still had them. [###REVIEW -- do we, in PAM5? nim if so?])
        """
        # doc - iterator or just return a list? for now, return list, for simplicity & robustness
        #e would it be an optim to cache this? note the reverse method would have to redo or inval it.
        baseatoms = self.baseatoms
        return zip(baseatoms, range(len(baseatoms)))

    def start_baseindex(self):
        return 0

    def baselength(self):
        return len(self.baseatoms)

    def __len__(self):
        return self.baselength()

    def __nonzero__(self): # 080311
        # avoid Python calling __len__ for this [review: need __eq__ as well?]
        return True

    def end_baseatoms(self):
        return (self.baseatoms[0], self.baseatoms[-1]) # might be same atom

    def reverse_baseatoms(self):
        if debug_flags.DEBUG_DNA_UPDATER:
            self.debug_check_bond_direction("reverse_baseatoms start")
        self.baseatoms = list(self.baseatoms)
        self.baseatoms.reverse()
        self.index_direction *= -1
        self._bond_direction *= -1
        self._reverse_neighbor_baseatoms()
        if debug_flags.DEBUG_DNA_UPDATER:
            self.debug_check_bond_direction("reverse_baseatoms end")
        return

    # ==

    # kluge: bond direction code/attrs are also here, even though it only applies to strands,
    # since strands can have different classes with no more specific common superclass.

    _bond_direction = 0 # 0 = not yet computed, or error (unset or inconsistent);
        # 1 or -1 means it was set by _recompute_bond_direction
        # (see bond_direction docstring for meaning)

    _bond_direction_error = False # False = error, or not yet known

        # to interpret those: if both are default, we've never run _recompute_bond_direction,
        # since it either sets a specific direction or signals an error.

    def bond_direction(self):
        """
        Only legal if self is a chain of strand base atoms.

        If self has a known, consistently set bond direction,
        throughout its length and also in the directional bonds
        to the next strand base atoms just outside it
        (which can be two actual bonds each if a PAM5 Pl intervenes),
        return that direction; 1 means left to right, -1 means right to left,
        treating baseindex as growing from left to right
        (self.index_direction is ignored).

        Otherwise set self._bond_direction_error and return 0.

        The value is cached to avoid recomputing it when known,
        and (nim; externally implemented) set when merging ladders
        to avoid recomputing it on merged ladders.

        The cached value is negated by self.reverse_baseatoms().
        """
        if not self._bond_direction and not self._bond_direction_error:
            self._recompute_bond_direction()
        return self._bond_direction

    def _recompute_bond_direction(self): # probably won't ever be needed; if so, remove once everything's working
        """
        Set self._bond_direction and self._bond_direction_error correctly.
        See self.bond_direction() docstring for definition of correct values.
        """
        # 1 = right, -1 = left, 0 = inconsistent or unknown # implem? maybe not needed, now that we have _f_set_bond_direction...
        assert 0, "nim (and never will be) in %r" % self #### this means more things must call _f_set_bond_direction, eg merge_ladders

    def _f_set_bond_direction(self, dir, error = None):
        """
        [friend method, for self (certain subclasses) or to optimize merging strand chains]
        #doc
        """
        assert dir in (-1, 0, 1)
        if error is None:
            error = (dir == 0)
        self._bond_direction = dir
        self._bond_direction_error = error
        return

    def bond_direction_is_arbitrary(self):
        """
        Are we so short that our bond direction (relative to index direction)
        is arbitrary, so caller could reverse it using
        self._f_reverse_arbitrary_bond_direction(),
        with no problematic effect?
        """
        # review: also condition result on self._bond_direction??
        return len(self.baseatoms) <= 1 # even if original chain's atom_list was longer

    def _f_reverse_arbitrary_bond_direction(self):
        assert self.bond_direction_is_arbitrary()
        self._bond_direction *= -1
        self._reverse_neighbor_baseatoms()
            # REVIEW: is _reverse_neighbor_baseatoms correct here?
            # This might depend on whether the caller of this also
            # called self.reverse_baseatoms()! @@@
        return

    def debug_check_bond_direction(self, when = ""):
        """
        Verify our bond direction is set correctly (if possible),
        and assertfail and/or print a debug warning if not.
        """
        ## assert self.strandQ
        assert self.baseatoms, "%r has no baseatoms" % self
        if not self.strandQ:
            return
        assert self._bond_direction
        assert not self._bond_direction_error

        if self.bond_direction_is_arbitrary():
            return # no way to check it

        # verify it by comparing it to actual bonds

        if when:
            when = " (%s)" % when

        # STUB: only works fully for PAM3
        atom1 = self.baseatoms[0]
        atom2 = self.baseatoms[1]
        bond = find_bond(atom1, atom2)
        errormsg = "" # might be set to an error string
        actual_direction = 0 # might be set to a bond direction
        if bond:
            actual_direction = bond.bond_direction_from(atom1)
        elif atom1.Pl_neighbors() or atom2.Pl_neighbors():
            # look for atom1-Pl-atom2 (2 bonds, same direction)
            bond1, bond2 = find_Pl_bonds(atom1, atom2) # might be None, None
            if not bond1:
                errormsg = "no Pl5 between adjacent baseatoms %r and %r" % (atom1, atom2)
            else:
                dir1 = bond1.bond_direction_from(atom1)
                dir2 = - bond2.bond_direction_from(atom2)
                if dir1 == dir2:
                    actual_direction = dir1 # might be 0
                else:
                    errormsg = "Pl5 between %r and %r has inconsistent or unset bond directions" % (atom1, atom2)
        else:
            errormsg = "no bond between adjacent baseatoms %r and %r" % (atom1, atom2)
        if not errormsg:
            # check actual_direction
            ## not needed: assert actual_direction
            recorded_direction = self._bond_direction
            assert recorded_direction # redundant with earlier assert
            if actual_direction != recorded_direction:
                # error
                errormsg = "bond direction from %r to %r: recorded %r, actual %r" % \
                      (atom1, atom2, recorded_direction, actual_direction)
        # now errormsg tells whether there is an error.
        if errormsg:
            prefix = "debug_check_bond_direction%s in %r" % (when, self)
            msg = "%s: ERROR: %s" % (prefix, errormsg)
            print "\n*** %s ***\n" % msg
            summary_format = "DNA updater: bug: [N] failure(s) of debug_check_bond_direction, see console prints"
            env.history.deferred_summary_message( redmsg(summary_format))
        return

    # ==

    def _f_update_neighbor_baseatoms(self):
        """
        [friend method for dna updater]

        This must be called at least once per ladder rail chain
        (i.e. _DnaChainFragment object, I think, 080116),
        during each dna updater run which encounters it (whether as a
        new or preexisting rail chain).

        It computes or recomputes whichever attributes carry info about
        the neighboring baseatoms in neighboring rail chains (which
        connect to self at the ends), based on current bonding.

        Specifically, it sets self.neighbor_baseatoms[end] for end in LADDER_ENDS
        to either None (if this chain ends on that ladder-end) or to the
        next atom in the next chain (if it doesn't end). (Atoms with
        _dna_updater__error set are not allowed as "next atoms" -- None will
        be set instead.)

        For end atom order (used as index in self.neighbor_baseatoms),
        it uses whatever order has been established by the DnaLadder
        we're in, which may or may not have reversed our order. (Ladders
        have been made, finished, and merged, before we're called.)

        For strands, it finds neighbors using bond direction, and knows
        about skipping Pl atoms; for axes, in the ambiguous length==1 case,
        it uses an arbitrary order, but
        makes sure this is consistent with strands when at least one strand
        has no nick at one end of this chain's ladder. [#todo: explain better]
        If this doesn't force an order, then if this had already been set
        before this call and either of the same non-None atoms are still
        in it now, preserve their position.

        The attrs we set are subsequently reversed by our methods
        _f_reverse_arbitrary_bond_direction and reverse_baseatoms.
        [###REVIEW whether it's correct in _f_reverse_arbitrary_bond_direction;
        see comment there.]

        @note: the ordering/reversal scheme described above may need
        revision. The special case for length==1 axis described above is
        meant to ensure
        that axis and strand order correspond between two ladders which
        are connected on the axis and one strand, but not the other strand
        (i.e. which have an ordinary nick), if the ladder we're on has length 1
        (i.e. if there are two nicks in a row, on the same or opposite strands).
        If this ever matters, we might need to straighten out this order
        in DnaLadder.finished() for length==1 ladders. The ladders are already
        made and merged by the time we're called, so whatever reversals they'll
        do are already done. [update, 080602: this was implemented today,
        to fix a bug; no change to DnaLadder.finished() seemed to be needed.]
        """
        assert self.strandQ in (False, True)
        self.neighbor_baseatoms = list(self.neighbor_baseatoms)
        # do most atoms one end at a time...
        for end in LADDER_ENDS: # end_baseatoms needs ladder end, not chain end
            next_atom = -1 # will be set to None or an atom, if possible
            if self.strandQ:
                # similar to code in DnaLadder._can_merge_at_end
                end_atom = self.end_baseatoms()[end]
                assert self._bond_direction
                    # relative to LADDER_ENDS directions
                    # (since that's in the same direction as our baseatoms array)
                    # (review: not 100% sure this is set yet;
                    #  but the assert is now old and has never failed)
                if end == LADDER_END0:
                    arrayindex_dir_to_neighbor = -1
                else:
                    arrayindex_dir_to_neighbor = 1
                bond_dir_to_neighbor = self._bond_direction * arrayindex_dir_to_neighbor
                next_atom = end_atom.strand_next_baseatom(bond_direction = bond_dir_to_neighbor)
                assert next_atom is None or next_atom.element.role == 'strand'
                # (note: strand_next_baseatom returns None if end_atom or the atom it
                #  might return has ._dna_updater__error set.)
                # store next_atom at end of loop
                if len(self.baseatoms) > 1: #080602 debug code
                    if arrayindex_dir_to_neighbor == 1:
                        next_interior_atom = self.baseatoms[1]
                    else:
                        next_interior_atom = self.baseatoms[-2]
                    if next_interior_atom is next_atom:
                        print "\n*** PROBABLE BUG: next_interior_atom is next_atom %r for end_atom %r in %r" % \
                              (next_atom, end_atom, self)
                    pass
            else:
                # do axis atoms in this per-end loop, only if chain length > 1;
                # otherwise do them both at once, after this loop.
                if len(self.baseatoms) > 1:
                    # easy case - unambiguous other-chain neighbor atom
                    # (Note: length-2 axis ring is not possible, since it would
                    #  require two bonds between the same two Ax pseudoatoms.
                    #  It's also not physically possible, so that's fine.)
                    end_atom = self.end_baseatoms()[end]
                    next_atom_candidates = end_atom.axis_neighbors() # len 1 or 2,
                        # and one should always be the next one in this chain
                        # (I guess it can't have _dna_updater__error set,
                        #  since such atoms are not made into chains;
                        #  so I assert this, 080206);
                        # the other one (if present) might have it set
                    if end == LADDER_END0:
                        next_to_end_index = 1
                    else:
                        next_to_end_index = -2
                    not_this_atom = self.baseatoms[next_to_end_index]
                    assert not not_this_atom._dna_updater__error # 080206
                    next_atom_candidates.remove(not_this_atom)
                        # it has to be there, so we don't mind raising an
                        # exception when it's not
                    assert len(next_atom_candidates) <= 1, \
                           "too many candidates: %r" % (next_atom_candidates,)
                        # Note: got exception here when lots of Ss had two
                        # Ax neighbors due to errors in an mmp file;
                        # assertion message untested [080304]
                    if next_atom_candidates:
                        next_atom = next_atom_candidates[0]
                        if next_atom._dna_updater__error:
                            ## print "avoiding bug 080206 by not seeing next axis atom with error", next_atom
                            next_atom = None
                    else:
                        next_atom = None
                    pass
                pass
            if next_atom != -1:
                self.neighbor_baseatoms[end] = next_atom # None or an atom
                assert next_atom is None or not next_atom._dna_updater__error # 080206
                if DEBUG_NEIGHBOR_BASEATOMS:
                    msg = "set %r.neighbor_baseatoms[%r] = %r, whole list is now %r" % \
                          (self, end, next_atom, self.neighbor_baseatoms)
                    print_compact_stack( "\n" + msg + ": ")
            continue
        # ... but in length==1 case, do axis atoms both at once
        if not self.strandQ and len(self.baseatoms) == 1:
            end_atom = self.baseatoms[0]
            next_atoms = end_atom.axis_neighbors() # len 0 or 1 or 2
            # remove atoms with errors [fix predicted bug, 080206]
            # (review: should axis_neighbors, or a variant method, do this?)
            ###### SHOULD REVIEW ALL USES OF axis_neighbors FOR NEEDING THIS @@@@@
            next_atoms = filter( lambda atom: not atom._dna_updater__error , next_atoms )
            while len(next_atoms) < 2:
                next_atoms.append(None)

            # if order matters, reverse this here, if either strand
            # in the same ladder indicates we ought to, by its next atom
            # bonding to one of these atoms (having no nick); I think any
            # advice we get from this (from 1 of 4 possible next atoms)
            # can't be inconsistent, but I haven't proved this. (Certainly
            # it can't be for physically reasonable structures.)
            # [bruce 080116 proposed, bruce 080602 implemented, as bugfix]
            order_was_forced_by_strands = False # might be set below
            try:
                # very near a release, so cause no new harm...
                ladder = rail_end_atom_to_ladder(end_atom)
                assert self is ladder.axis_rail
                evidence_counters = [0, 0] # [wrong order, right order]
                for strand in ladder.strand_rails:
                    strand._f_update_neighbor_baseatoms()
                        # redundant with caller, but necessary since we don't
                        # know whether it called this already or not;
                        # calling it twice on a strand is ok (2nd call is a noop);
                        # not important to optimize since length-1 ladders are rare.
                    for strand_end in LADDER_ENDS:
                        for axis_end in LADDER_ENDS:
                            axis_next_atom = next_atoms[axis_end] # might be None
                            strand_next_atom = strand.neighbor_baseatoms[strand_end] # might be None
                            if axis_next_atom and strand_next_atom and \
                               atoms_are_bonded( axis_next_atom, strand_next_atom):
                                evidence_counters[ strand_end == axis_end ] += 1
                            continue
                        continue
                    continue
                badvote, goodvote = evidence_counters
                    # note: current order of next_atoms is arbitrary,
                    # so we need symmetry here between badvote and goodvote
                if badvote != goodvote:
                    if badvote > goodvote:
                        next_atoms.reverse()
                        badvote, goodvote = goodvote, badvote
                        pass
                    order_was_forced_by_strands = True
                if badvote and goodvote:
                    # should never happen for physically reasonable structures,
                    # but is probably possible for nonsense structures
                    print "\nBUG or unreasonable structure: " \
                          "badvote %d goodvote %d for next_atoms %r " \
                          "around %r with %r" % \
                          (badvote, goodvote, next_atoms, self, end_atom)
                    pass
                pass
            except:
                msg = "\n*** BUG: ignoring exception while disambiguating " \
                      "next_atoms %r around %r with %r" % \
                      (next_atoms, self, end_atom)
                print_compact_traceback( msg + ": " )
                pass

            reverse_count = 0 # for debug prints only

            if not order_was_forced_by_strands:
                # For stability of arbitrary choices in case self.neighbor_baseatoms
                # was already set, let non-None atoms still in it determine the order
                # to preserve their position, unless the order was forced above.
                for end in LADDER_ENDS:
                    old_atom = self.neighbor_baseatoms[end]
                    if old_atom and old_atom is next_atoms[1-end]:
                        assert old_atom != -1 # next_atoms can't contain -1
                        next_atoms.reverse() # (this can't happen twice)
                        reverse_count += 1

            self.neighbor_baseatoms = next_atoms

            if DEBUG_NEIGHBOR_BASEATOMS:
                msg = "set %r.neighbor_baseatoms = next_atoms %r, " \
                      "order_was_forced_by_strands = %r, reverse_count = %r" % \
                      (self, next_atoms, order_was_forced_by_strands, reverse_count)
                print_compact_stack( "\n" + msg + ": ")
                pass
            pass

        # we're done
        assert len(self.neighbor_baseatoms) == 2
        assert type(self.neighbor_baseatoms) == type([])
        for atom in self.neighbor_baseatoms:
            assert atom is None or atom.element.role in ['axis', 'strand']
                # note: 'unpaired-base' won't appear in any chain
        return # from _f_update_neighbor_baseatoms

    def at_wholechain_end(self): # bruce 080212
        """
        Return True if we are located at one or both ends of our wholechain
        (if it has any ends -- if it's a ring, it has none),
        based on self.neighbor_baseatoms.
        """
        next1, next2 = self.neighbor_baseatoms
        assert next1 != -1
        assert next2 != -1
        return (next1 is None) or (next2 is None)

    def wholechain_end_baseatoms(self): # bruce 080212
        """
        Return a list of whichever end baseatoms of our wholechain
        we have (as end baseatoms of self). (Length will be 0 to 2.)

        Only correct if self.neighbor_baseatoms has already been set.
        AssertionError if it hasn't.
        """
        next1, next2 = self.neighbor_baseatoms
        assert next1 != -1
        assert next2 != -1
        res = []
        if next1 is None:
            res.append(self.baseatoms[0])
        if next2 is None:
            res.append(self.baseatoms[-1])
        # note: for a len 1 wholechain, this has two copies of same atom -- good, i think
        return res

    pass # end of class DnaChain

# ==

class _DnaChainFragment(DnaChain): #e does it need to know ringQ? is it misnamed??
    """
    [as of 080109 these are created in make_new_ladders()
     and passed into DnaLadder as its rail chains
     via init arg and add_strand_rail]
    """
    def __init__(self,
                 atom_list,
                 index_direction = None,
                 bond_direction = None,
                 bond_direction_error = None,
                 strandQ = None
                ):
        self.strandQ = strandQ
        self.baseatoms = atom_list
        if index_direction is not None:
            self.index_direction = index_direction
        else:
            pass # use default index_direction (since arbitrary)
        if bond_direction is not None or bond_direction_error is not None:
            bond_direction = bond_direction or 0
            bond_direction_error = bond_direction_error or False
            self._f_set_bond_direction( bond_direction, bond_direction_error)
        if debug_flags.DEBUG_DNA_UPDATER:
            self.debug_check_bond_direction("_DnaChainFragment.__init__")
    pass

# ==

class DnaChain_AtomChainWrapper(DnaChain): ###### TODO: refactor into what code is on this vs what is on a higher-level WholeChain
    #e inherit ChainAPI? (we're passed to a DnaMarker as its chain -- no, more likely, as an element of a list which is that@@@)
    """
    Abstract class, superclass of AxisChain and StrandChain.

    Owns and delegates to an AtomChainOrRing, providing DNA-specific
    navigation and indexing.

    Used internally for base indexing in strands and segments,
    mainly while updating associations between the user-visible
    nodes for those and the pseudoatoms comprising them.

    Note: this base indexing is for purposes of moving origin markers
    for user convenience when editing several associated chains
    (e.g. the axis and two strand of a duplex). By default it
    is likely to be assigned as a "base pair index", which means
    that on the "2nd strand" it will go backwards compared to
    the actual "physical" base index within that strand. So it
    should not be confused with that. Further, on rings it
    may jump in value at a different point than whatever user-
    visible index is desired. If in doubt, consider it
    an internal thing, not to be user-exposed without using
    markers, relative directions, offsets, and ring-origins
    to interpret it.

    Note: some of the atoms in our chain_or_ring might be killed;
    we never remove atoms or modify our atom list after creation
    (except perhaps to reverse or reorder it). Instead, client code
    makes new chain objects.
    """
    # default values of instance variables:

# @@@ move to WholeChain, I think - 080114
##    controlling_marker = None

    # REVIEW: need to delegate ringQ, or any other vars or methods, to self.chain_or_ring?

    def __init__(self, chain_or_ring):

        self.chain_or_ring = chain_or_ring
        self.ringQ = chain_or_ring.ringQ

        #e possible optim: can we discard the bonds stored in chain_or_ring, and keep only the atomlist,
        # maybe not even in that object?
        # (but we do need ringQ, and might need future chain_or_ring methods that differ for it.)
        # decision 071203: yes, and even more, discard non-base atoms, optimize base scanning.
        # make sure we can iterate over all atoms incl bos and Pls, sometime, for some purposes.
        # use a method name that makes that explicit.
        # For now, just store a separate list of baseatoms (in each subclass __init__ method).
        return

    def iteratoms(self): # REVIEW: different if self.index_direction < 0?
        """
        # get doc from calling method
        """
        return self.chain_or_ring.iteratoms()

    _chain_id = None
    def chain_id(self): #k this is used, but as of 071203 i'm not sure the use will survive, so review later whether it's needed @@
        """
        Return a unique, non-reusable id (with a boolean value of true)
        for "this chain" (details need review and redoc).
        """
        #e revise/refile (object_id_mixin?);
        # REVIEW whether on self or self.chain_or_ring (related: which is stored in the marker?)
        if not self._chain_id:
            global _chain_id_counter
            _chain_id_counter += 1
            self._chain_id = _chain_id_counter
        return self._chain_id

# guessing this is for WholeChain, not here... 080114
##    def _f_own_atoms(self): # @@@ review: is this really a small chain or whole chain method?
##        """
##        Own our atoms, for chain purposes.
##        This does not presently store anything on the atoms, even indirectly,
##        but we do take over the markers and decide between competing ones
##        and tell them their status, and record the list of markers (needs update??)
##        and the controlling marker for our chain identity (needs update??).
##        This info about markers might be DNA-specific ...
##        and it might be only valid during the dna updater run, before
##        more model changes are made. [#todo: update docstring when known]
##        """
##
##        # NOTE/TODO: if useful, this might record a list of all live markers
##        # found on that chain in the chain, as well as whatever marker
##        # is chosen or made to control it. (But note that markers might
##        # get removed or made independently without the chain itself
##        # changing. If so, some invalidation of those chain attributes
##        # might be needed.)
##
##        if debug_flags.DEBUG_DNA_UPDATER_VERBOSE:
##            print "%r._f_own_atoms() is a stub - always makes a new marker" % self #####FIX
##        chain = self.chain_or_ring
##        # stub -- just make a new marker! we'll need code for this anyway...
##        # but it's WRONG to do it when an old one could take over, so this is not a correct stub, just one that might run.
##        atom = chain.atom_list[0]
##        assy = atom.molecule.assy
##        marker_class = self._marker_class
##        assert issubclass(marker_class, DnaMarker)
##        marker = marker_class(assy, [atom], chain = self)
##            # note: chain has to be self, not self.chain
##            # (the marker calls some methods that are only on self).
##        self.controlling_marker = marker
##        marker.set_whether_controlling(True)
##        ## and call that with False for the other markers, so they die if needed -- ### IMPLEM
##        #e For a chosen old marker, we get advice from it about chain direction,
##        # then call a direction reverser if needed; see comments around index_direction.

    def virtual_fragment(self, start_baseindex, baselength): #e misnamed if not virtual -- review
        """
        #doc

        [as of 080109 these are created in make_new_ladders() and passed into DnaLadder as its rail chains
         via init arg and add_strand_rail]
        """
        if debug_flags.DEBUG_DNA_UPDATER:
            self.debug_check_bond_direction("entering DnaChain_AtomChainWrapper.virtual_fragment")
        # current implem always returns a real fragment; might be ok
        baseindex = start_baseindex - self.start_baseindex()
        subchain = self.baseatoms[baseindex : baseindex + baselength]
        # note: if self._bond_direction_error, self._bond_direction will be 0
        # and cause the subchain direction to be recomputed... but it can't
        # be recomputed on that kind of chain (using the current code)...
        # so we pass the error flag too.
        return _DnaChainFragment(subchain,
                                 index_direction = self.index_direction,
                                 bond_direction = self._bond_direction,
                                 bond_direction_error = self._bond_direction_error,
                                 strandQ = self.strandQ
                               )
            #e more args? does it know original indices? (i doubt it)

    pass # end of class DnaChain_AtomChainWrapper

# ==

def merged_chain(baseatoms,
                 strandQ,
                 bond_direction,
                 bond_direction_error = False):
    res = _DnaChainFragment( baseatoms,
                             bond_direction = bond_direction,
                             bond_direction_error = bond_direction_error,
                             strandQ = strandQ
                            )
    return res

# ==

class AxisChain(DnaChain_AtomChainWrapper):
    """
    A kind of DnaChain for just-found axis chains or rings.

    @warning: as of 080116, these are *not* used directly as DnaLadder rail chains.
    Instead, objects returned by self.virtual_fragment are used for that.
    """
    strandQ = False
    _marker_class = DnaSegmentMarker
    def __init__(self, chain_or_ring):
        DnaChain_AtomChainWrapper.__init__(self, chain_or_ring)
        self.baseatoms = chain_or_ring.atom_list
        return
    pass

# ==

class StrandChain(DnaChain_AtomChainWrapper):
    """
    A kind of DnaChain for just-found strand chains or rings.

    @warning: as of 080116, these are *not* used directly as DnaLadder rail chains.
    Instead, objects returned by self.virtual_fragment are used for that.

    Knows to skip Pl atoms when indexing or iterating over "base atoms"
    (but covers them in iteratoms). Also knows to look at bond_direction
    on all the bonds (in self and to neighbors), for being set and consistent,
    and to cache this info.
    """
    strandQ = True
    _marker_class = DnaStrandMarker
    def __init__(self, chain_or_ring):
# nevermind:
##        if debug_flags.DEBUG_DNA_UPDATER:
##            chain_or_ring.debug_check_bond_direction("init arg to %r" % self)
##            ## AttributeError: 'AtomChain' object has no attribute 'debug_check_bond_direction'
        DnaChain_AtomChainWrapper.__init__(self, chain_or_ring)
        baseatoms = filter( lambda atom:
                              not atom.element.symbol.startswith('P') ,
                                # KLUGE, should use an element attribute, whether it's base-indexed
                            chain_or_ring.atom_list )
        self.baseatoms = baseatoms # in order of rungindex (called baseindex in methods)
            # note: baseatoms affects methods with "base" in their name,
            # but not e.g. iteratoms (which must cover Pl)
        # Now check all bond directions, inside and just outside this chain.
        # Use the all-atom version, which includes Pl atoms.
        # Assume that every Pl atom ends up in some chain,
        # and gets checked here, so that all inter-chain bonds are covered.
        # (This is assumed when setting bond_direction on merged chains. #doc in what code)
        dir_so_far = None
        chain = self.chain_or_ring
        # 1. check bonds inside the chain.
        # if it's a chain, it contains: atom, bond, atom, bond, atom
        # (each bond connects the adjacent atoms).
        # if it's a ring, it's like that but missing the *first* atom
        # (due to a perhaps-arbitrary choice in the alg in
        #  find_chain_or_ring_from_bond), so it's bond, atom, bond, atom.
        # So we'll ignore the first atom in a chain to make these cases
        # the same, and then loop over the (bond, atom) pairs in that order,
        # which means the bond direction relative to left-to-right in this
        # scheme (i.e. relative to baseatoms index) is the negative of the one
        # we get from each bond, atom pair. (I recently changed the ring-finding
        # code in a way which changed this scheme and introduced a bug in this
        # code, though comments here suggest the sign factor was just a guess
        # anyway. Fixed the bug here [confirmed], 080121 10pm or so.)
        bonds = chain.bond_list
##        atoms = chain.atom_list[:len(bonds)] # buggy
        atoms = chain.atom_list[-len(bonds):] # bugfix part 1
        for bond, atom in zip(bonds, atoms):
            thisdir = - bond.bond_direction_from(atom) # minus sign is bugfix part 2
            if dir_so_far is None:
                # first iteration
                #e could optim by moving out of loop
                dir_so_far = thisdir
                if not thisdir: # missing bond direction
                    break
            else:
                # subsequent iterations
                assert dir_so_far in (-1, 1)
                if dir_so_far != thisdir:
                    # inconsistent or missing bond direction
                    dir_so_far = 0
                    break
            continue
        # 2. check pairs of bonds on the same atom, on the "end atoms".
        # (It doesn't matter which end-atom we dropped in the bond-inside-chain
        #  loop above, since that only affects how we measure bond directions,
        #  not which bonds we measure (all of them).)
        if not chain.atom_list[0].bond_directions_are_set_and_consistent() or \
           not chain.atom_list[-1].bond_directions_are_set_and_consistent():
            dir_so_far = 0
        if dir_so_far is None:
            assert len(chain.atom_list) == 1 and len(bonds) == 0
            # direction remains unknown, i guess...
            # but I think we can legally set it to either value,
            # and doing so simplifies the code that wants it to be set.
            # (That code may need to know it's arbitrary since we're
            # so short that reverse is a noop (except for negating directions),
            # but there's no point in marking it as arbitrary here, since
            # there might be other ways of making such short chains.
            # So instead, let that code detect that we're that short,
            # using our superclass method bond_direction_is_arbitrary, which says yes
            # even if this code didn't run (e.g. if atom_list had a Pl).)
            dir_so_far = 1
        # at this point, dir_so_far can be:
        # 0: error (inconsistent or missing bond direction)
        # 1 or -1: every bond inside and adjacent to chain has this direction
        assert dir_so_far, "bond direction error in %r, no point in continuing" % self
        self._f_set_bond_direction(dir_so_far)
        if debug_flags.DEBUG_DNA_UPDATER:
            self.debug_check_bond_direction("end of init")
            # note: this assertfails if direction is 0,
            # and if it didn't, later code would have bugs,
            # so we might as well assert dir_so_far above [done],
            # and really we ought to fix that error here or earlier.
            # So decide which is best: #### @@@@
            # - find wholechains w/o knowing bond dir, then fix it;
            # - or fix it earlier when we notice local bond direction
            #   errors (also requires propogation; not too hard).
        return # atoms bonds

    pass

# end
