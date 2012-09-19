# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
BasePair.py - BasePair, StackedBasePairs flyweight objects

WARNING -- this is not yet used; it's really just a scratch file.
Furthermore, it will probably never be used, since the recognition
of base pairs by the dna updater will occur differently, but once
it's happened, the scanning of them can occur more efficiently
by using the already-recognized DnaLadders. So I'll probably move
it to outtakes soon. In fact, why not now? Ok, moving it now.

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

TODO: split into several files.
"""

from model.chem import Atom # for isinstance

## see also crossovers.py

from model.bond_constants import atoms_are_bonded, find_bond

# ==

class DnaStructureError(Exception): #e tentative #e refile #e inherit from a more specific subclass of Exception?
    """
    Exception for structure errors in DNA pseudoatoms or bonds.
    Should not be seen by users except when there are bugs
    in the code for making or updating such structures,
    but should be raised and handled as appropriate internally.
    """
    pass

class DnaGeometryError(Exception):
    """
    [for when we need to use geom to guess higher level structure, but can't]
    """
    pass

class Flyweight(object):
    """
    Abstract superclass for flyweight objects.
    (May not mean anything except to indicate what they are informally?)
    """
    pass

# ==

class BasePair(Flyweight):
    #e Q: needs __eq__? if so, does it compare strand-alignment (strand1 vs strand2)?
    axis_atom = None # must always exist
    strand1_atom = None # can be None for "single strand2" (rare?)
    strand2_atom = None # can be None for "single strand1"
    def __init__(self, axis_atom, strand1_atom = None, strand2_atom = None, _trustme = False):
        """
        @param _trustme: (default False) optimize by doing no validation of arguments.
        """
        self.axis_atom = axis_atom
        self.strand1_atom = strand1_atom
        self.strand2_atom = strand2_atom
        if _trustme:
            # Warning to developers who modify this class:
            # in skipping validations, don't also skip any necessary
            # initialization of caches or other derived attributes!
            # For now, there are none.. review whether still true. @@@
            return
        assert axis_atom is not None
        assert isinstance(axis_atom, Atom) ### or a more specific class?
        if strand1_atom is None:
            assert strand2_atom is None ## ??? not if a "lone strand2" is permitted when we're created!
            # following code tries not to depend on that assertion, while we review whether it's valid
        if strand1_atom is None and strand2_atom is None:
            self._find_both_strand_atoms()
                # this might set only one if only one is there,
                # or raise a DnaStructureError exception;
                # implem: _find_first, _find_second
        elif strand1_atom is None or strand2_atom is None:
            # Logic issue: did caller mean we're single, or to find the other strand atom?
            # Answer: only one can be correct, since the axis atom either does or doesn't
            # have two strand atoms on it. So just look at see.
            self._find_second_strand_atom()
                # this might leave it as None if only one is there,
                # or raise a DnaStructureError exception
        self._validate()
        return
    def _find_both_strand_atoms(self):
        """
        """
        assert 0 # nim
    def _find_first_strand_atom(self):
        """
        """
        assert 0 # nim
    def _find_second_strand_atom(self):
        """
        """
        assert 0 # nim
    def _validate(self):
        """
        """
        assert 0 # nim
    def stacked_base_pairs(self):
        """
        Determine and return a list of the 0, 1, or 2 base pairs
        which are stacked to this one, as objects of this class,
        in a corresponding internal alignment of the strands.
        """
        # just make one for each axis neighbor, then align them to this one,
        # perhaps by making a StackedBasePairs and asking it to do that.
        # (or we might be called by that? no, only if its init is not told them both...)
        # or perhaps by a method on this class, "align strands to this base pair"
        # which can switch them, with option/retval about whether to do it geometrically.
        assert 0 # nim
    def align_to_basepair(self, other, guess_from_geometry = True, axis_unbonded_ok = False):
        """
        Switch our strands if necessary so as to align them
        to the given other BasePair (which must be stacked to us by an axis bond),
        in terms of backbone bonding.

        @param other: another basepair. We modify self, not other, to do the alignment.
        @type other: BasePair (same class as self)

        @param guess_from_geometry: If there is no backbone bonding, this option (when true, the default)
        permits us to use geometric info to
        guess strand correspondence for doing the alignment. Our return value will be True if we did that.
        (If we have to but can't, we raise DnaGeometryError.)

        @param axis_unbonded_ok: default False; if true, permits axis atoms
        to be unbonded. We pretend they are going to become bonded in order
        to do our work, but don't change them.

        @return: whether we had to guess from geometry, and did so successfully.
        """
        if not axis_unbonded_ok:
            assert atoms_are_bonded( self.axis_atom, other.axis_atom )
        # TODO: just look for bonds (direct or via Pl) between the 4 involved strand atoms;
        # exception if anything is inconsistent.
        assert 0 # nim
    pass

# ==

class StackedBasePairs(Flyweight):
    """
    Represent a pointer to two adjacent (stacked) base pairs,
    which understands the correspondence between their axes (bonded)
    and strands (not necessarily bonded).
    """
    #e Q: needs __eq__? if so, does it compare strand-alignment (strand1 vs strand2), and direction (bp1 vs bp2)?
    #e need copy method? if so, shallow or deep (into base pairs)?
    #e need immutable flag?
    basepair1 = None
    basepair2 = None
    def __init__(self, bp1, bp2):
        #e hmm, doesn't seem like convenient init info, unless helper funcs are usually used to make one
        # (how was it done for recognizing PAM5 crossover-making sites? ### REVIEW)
        self.basepair1 = bp1
        self.basepair2 = bp2
        self._check_if_stacked()
        self._update_backbone_info()
            # whether nicked, which strand is which in bp2 --
            # might use geom to guess, if both strands go to other axes here
            # (same thing happens if we move across a place like that...
            #  can we record the answer on the strands somehow??
            #  maybe just save a copy of self at that point on the atoms involved?
            #  as a jig which gets invalidated as needed? then this class is not a Jig
            #  but can be owned by one, in a form whose mutability is not used. ####)
        assert 0 # nim?
    #e need copy method?
    def move_right(self, amount = 1):
        """
        Move right (usually towards higher-numbered bases on strand 1,
        but depends on whether we've reversed direction) by the given amount.

        @param amount: how many base pairs to move right. (Negative values mean to move left.)
        @type amount: int
        """
        if amount > 1:
            for i in range(amount):
                self.move_right() # accumulate result code? stop if it fails? raise a special exception, CantMove?
        if amount <= 0:
            for i in range(amount):
                self.move_left()
        assert amount == 1
        ...
        assert 0 # nim
    def move_left(self, amount = 1):
        """
        Move left (usually towards lower-numbered bases on strand 1,
        but depends on whether we've reversed direction) by the given amount.

        @param amount: how many base pairs to move left. (Negative values mean to move right.)
        @type amount: int
        """
        if amount != 1:
            return self.move_right( - amount)
        # primitive: move one step left
        ...
        assert 0 # nim
    def interchange_strands_same_direction(self):
        """
        """
        assert 0 # nim
    def interchange_strands_reverse_direction(self):
        """
        """
        assert 0 # nim
    def reverse_direction(self):
        """
        """
        assert 0 # nim
    def in_standard_orientation(self):
        """
        Are we now in standard orientation (moving towards increasing
        base indexes on strand 1, and with the primary strand being
        strand 1 if this is defined)?

        @note: it might not be useful to find out "no" without knowing
        which of those Qs has "no" separately, so we might split this
        into two methods.
        """
        assert 0 # nim
    def is_strand1_nicked(self):
        assert 0 # nim - maybe just return atoms_are_bonded (approp atoms)? check if atoms exist first? if not, what is result? #Q
    def is_strand2_nicked(self):
        assert 0 # nim
    def nick_strand1(self): #k desired?
        """
        Break the backbone bond connecting strand1 across these two base pairs.
        """
        assert 0 # nim
    pass


## next_base_pair( base_pair_stacking, base_pair) # like bond, atom


# end
