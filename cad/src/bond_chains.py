# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
bond_chains.py -- helper functions related to chains of bonds

(See also: pi_bond_sp_chain.py)

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from bond_constants import DIRBOND_CHAIN_MIDDLE
from bond_constants import DIRBOND_CHAIN_END
from bond_constants import DIRBOND_NONE
from bond_constants import DIRBOND_ERROR

def grow_bond_chain(bond, atom, next_bond_in_chain): #bruce 070415; generalized from grow_pi_sp_chain
    """
    Given a bond and one of its atoms, grow the bond chain containing bond
    (of the kind defined by next_bond_in_chain, called on a bond and one of its
    atoms) in the direction of atom,
    adding newly found bonds and atoms to respective lists (listb, lista) which we'll return,
    until the chain ends or comes back to bond and forms a ring
    (in which case return as much of the chain as possible, but not another ref to bond or atom).
       Return value is the tuple (ringQ, listb, lista) where ringQ says whether a ring was detected
    and len(listb) == len(lista) == number of new (bond, atom) pairs found.
       Note that each (bond, atom) pair found (at corresponding positions in the lists)
    has a direction (in bond, from atom to bond.other(atom)) which is backwards along the direction of chain growth.
       Note that listb never includes the original bond, so it is never a complete list of bonds in the chain.
    In general, to form a complete chain, a caller must piece together a starting bond and two bond lists
    grown in opposite directions, or one bond list if bond is part of a ring.
    (See also XXX [nim, to be modified from make_pi_bond_obj], which calls us twice and does this.)
       The function next_bond_in_chain(bond, atom) must return another bond containing atom
    in the same chain or ring, or None if the chain ends at bond (on the end of bond which is atom),
    and must be defined in such a way that its progress from bond to bond, through any atom, is consistent from
    either direction. (I.e., if given bond1 and atom1 it returns bond2 and atom2, then given bond2 and atom1 it
    must return bond1 and bond1.other(atom1).) However, we don't promise to do full checking on whether the function
    satisfies this requirement.
       That requirement means it's not possible to find a ring which comes back to bond
    but does not include bond (by coming back to atom before coming to bond's other atom),
    so if that happens, we raise an exception.
    """
    listb, lista = [], []
    origbond = bond # for detecting a ring
    origatom = atom # for error checking
    while 1:
        nextbond = next_bond_in_chain(bond, atom) # the function called here is the main difference from grow_pi_sp_chain
        if nextbond is None:
            return False, listb, lista
        if nextbond is origbond:
            assert atom is not origatom, "grow_bond_chain(%r, %r, %r): can't have 3 bonds in chain at atom %r; data: %r" % \
                   (origbond, origatom, next_bond_in_chain, atom, (nextbond, listb, lista)) #revised to fix bug 2328 [bruce 070424]
            assert nextbond.other(atom) is origatom
            return True, listb, lista
        nextatom = nextbond.other(atom)
        listb.append(nextbond)
        lista.append(nextatom)
        bond, atom = nextbond, nextatom
    pass

def grow_directional_bond_chain(bond, atom): #bruce 070415
    """
    Grow a chain of directional bonds. For details, see docstring of grow_bond_chain.
    """
    return grow_bond_chain(bond, atom, next_directional_bond_in_chain)

def next_directional_bond_in_chain(bond, atom):
    """
    Assuming bond is in a chain of directional bonds,
    being traversed towards atom (one of bond's atoms),
    return the next bond in the chain if there is one,
    or None if there is not one (due to an error,
    such as the chain branching, or due to the chain ending).

    For some errors, print error messages (this behavior needs REVIEW)
    and return None.
    """
    #bruce 070415, revised 071016; should be ok with or without open bonds being directional
    assert bond.is_directional()
    # note, as of mark 071014, atom might be a Singlet
    statuscode, bond1, bond2 = atom.directional_bond_chain_status()
    if statuscode == DIRBOND_CHAIN_MIDDLE:
        assert bond1
        assert bond2
        if bond is bond1:
            return bond2
        elif bond is bond2:
            return bond1
        else:
            # error -- REVIEW: how should we report it? not sure, so print them for now.
            # anyway, stop propogating the chain on any error (ie return None).
            print "error or bug: atom %r has directional bond %r reaching chain containing %r and %r" % \
                  (atom, bond, bond1, bond2)
            return None
        pass
    elif statuscode == DIRBOND_CHAIN_END:
        assert bond1
        assert bond2 is None
        if bond is not bond1:
            print "error or bug: atom %r has directional bond %r different than chain-end bond %r" % \
                  (atom, bond, bond1)
        return None
    elif statuscode == DIRBOND_NONE:
        print "bug: atom %r has directional bond %r but directional_bond_chain_status of DIRBOND_NONE" % \
              (atom, bond)
        return None
    elif statuscode == DIRBOND_ERROR:
        print "error: atom %r with directional bond %r has directional_bond_chain_status of DIRBOND_ERROR" % \
              (atom, bond)
        return None
    else:
        assert 0, "bug: atom %r with directional bond %r has unrecognized directional_bond_chain_status %r" % \
               (atom, bond, statuscode)
        return None
    pass

# ==

class abstract_bond_chain_analyzer:
    """
    Abstract helper class for testing atoms and bonds as qualified
    to belong to chains or rings, and finding those chains or rings.
    Specific subclasses have specific definitions of qualifying atoms
    and bonds, and methods for creating found chain or ring or lone-atom
    objects, and for handling atoms with more than two qualifying bonds.
    """
    #bruce 071126, synthesizing some existing related code and new code
    # TODO: recode existing helper functions to use this.
    def atom_ok(self, atom):
        """
        Subclass-specific primitive for whether an atom qualifies.
        [subclass should override]
        """
        return True
    def bond_ok(self, bond):
        """
        Subclass-specific primitive for whether a bond qualifies,
        if its atoms do.

        The default version (always True) is often good enough.

        This class's methods never call self.bond_ok on a bond
        unless at least one of that bond's atoms satisfies atom_ok.
        And they never pay attention to bond_ok returning True
        unless both its atoms satisfy atom_ok.
        """
        return True
    def atom_list_of_ok_bonds_others(self, atom):
        """
        Assume self.atom_ok(atom). Return a list of
        all atom's bonds, each paired with its "other atom",
        i.e. a list of pairs (bond, otheratom) where bond's
        two atoms are atom and otheratom,
        for which the bond and both of its atoms
        satisfy bond_ok and atom_ok respectively.
        This list might have any length; we don't detect the
        errors of its length being 0 or more than 2.
        (In fact, we don't assume that these are errors,
        though all existing subclasses do. ### VERIFY)

        The implementation assumes that self.atom_ok might be
        expensive enough to justify comparing bond's atoms to atom
        to avoid calling self.atom_ok redundantly.
        """
        atom_ok = self.atom_ok
        assert atom_ok(atom)
        res = []
        for bond in atom.bonds:
            if self.bond_ok(bond):
                other = bond.other(atom)
                if atom_ok(other):
                    res.append((bond, other)) #k do any callers want other? looks like not. TODO: simplify them, don't include it.@@@
        return res
    def atom_is_branchpoint(self, atom):
        return len(self.atom_list_of_ok_bonds_others(atom)) > 2
    def next_bond_in_chain(self, bond, atom):
        """
        Assume bond & both its atoms qualify (but not that atom has been checked
        for having too many qualifying bonds); return the next bond on atom
        in a bond chain (never the given bond; always one with both atoms
        and itself qualifying), or None if the chain ends at atom
        due to there being fewer or more than two qualifying bonds on atom.
        
        (If the caller cares which of those conditions cause the chain
         to end at atom, it should check the last atom separately.
         This method doesn't assume that too many qualifying bonds
         is an error, even though it stops the chain if it finds this
         condition, including that atom at the end of the chain.
         Note that if a caller extends two chains in opposite
         directions from a bond and both of them end on an atom with
         too many qualifying bonds, those two ends might be the same atom.)
        """
        bonds_others = self.atom_list_of_ok_bonds_others(atom)
        assert (bond, bond.other(atom)) in bonds_others # remove when works?
        if len(bonds_others) != 2:
            return None
        for otherbond, otheratom_unused in bonds_others:
            if otherbond is not bond:
                return otherbond
        assert 0, "bond %r occurs twice in %r -- should be impossible" % (bond, bonds_others)
        return None
    def find_chain_or_ring_from_bond(self, bond, branches_ok = False):
        """
        Return the maximal chain or ring of qualifying atoms
        connected by qualifying bonds, which includes bond.
        (See below for what is returned to represent the result.)
        
        (Return None if bond or either of its atoms doesn't qualify.) [### REVIEW - compare to lone-atom error return]
        
        If any qualifying atom has more than two qualifying bonds,
        behave differently depending on branches_ok: if it's False (default),
        treat this as an error which in some sense disqualifies that atom --
        complain, stop growing the chain, and don't include that atom in it
        (or any of its bonds). This error can lead to a chain with one atom
        and no bonds (which won't include the given bond), or to a longer
        chain which doesn't include bond (if one of its atoms had this error
        but the other one connected to a longer chain than bond).
        But do nothing to modify the offending atom or its bonds in the model
        (except perhaps to set flags in it which affect only future complaints).

        But if branches_ok is true, just include the branchpoint atom as one
        end of the returned chain. Note that the other end may or may not also
        be a branchpoint; if both ends are branchpoints, they may be the same
        atom, but the result will still be considered a chain rather than a
        ring. [REVIEW: maybe best to delegate this worry entirely to self.make_chain]

        (If any qualifying atom has no qualifying bonds,
        we'll never encounter it, since we encounter atoms
        only via qualifying bonds on them.)

        @return: #doc format; use subclass methods to create returned objects
        """
        #bruce 071126 made this from make_pi_bond_obj; TODO: recode that to use this
        
        atom_ok = self.atom_ok
        atom1 = bond.atom1
        atom2 = bond.atom2
        if not atom_ok(atom1) or not atom_ok(atom2):
            return None

        bond_ok = self.bond_ok
        if not bond_ok(bond):
            return None
        
        ringQ, listb1, lista1 = grow_bond_chain(bond, atom1, self.next_bond_in_chain)
        if ringQ:
            # branchpoint atoms can't occur in rings
            assert atom2 is lista1[-1]
            return self.make_ring( [bond] + listb1 ,
                                   [atom2, atom1] + lista1 )
        else:
            ringQ, listb2, lista2 = grow_bond_chain(bond, atom2, self.next_bond_in_chain)
            assert not ringQ
            listb1.reverse()
            lista1.reverse()
            # TODO: worry about branchpoint atoms at either or both ends,
            # depending on branches_ok. (Maybe call different result constructors depending on ends?
            # (Or maybe let the chain constructor decide what to do about them? that seems best! @@@)
            return self.make_chain( listb1 + [bond] + listb2, lista1 + [atom1, atom2] + lista2 ) # one more atom than bond
        pass
    def make_ring(self, listb, lista):
        "[subclass can extend]"
        assert len(listb) == len(lista)
        return (True, listb, lista)
    def make_chain(self, listb, lista): # rename? found_ring vs make_ring, etc? @@@
        "[subclass can extend]" # TODO: have subclass provide submethod, rather than extending this? @@@
        # TODO: worry about branchpoint atoms at either or both ends... maybe only in subclasses...
        assert len(lista) - 1 == len(listb)
        assert len(listb) > 0 # somewhat arbitrary
        if not self.branches_ok: # class constant? @@@ or override this method in a subclass?
            is_branchpoint = self.atom_is_branchpoint
            if is_branchpoint( lista[0] ):
                del lista[0]
                del listb[0]
                if not listb:
                    return (False, listb, lista) ### make_lone_atom - but wait, did we check *it* for being a branchpoint?
            if is_branchpoint( lista[-1] ):
                del lista[-1]
                del listb[-1]
                if not listb:
                    return (False, listb, lista) ### make_lone_atom
            assert len(lista) - 1 == len(listb)
            assert len(listb) > 0
            assert not is_branchpoint( lista[0] )
            assert not is_branchpoint( lista[-1] )
            # fall thru
        return (False, listb, lista)
    #TODO: more methods: make them from an atom, or from a dict of atoms (zapping the found atoms)
    pass # end of class abstract_bond_chain_analyzer

# end
