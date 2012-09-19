# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
bond_chains.py -- helper functions related to chains of bonds

(See also: pi_bond_sp_chain.py)

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from model.bond_constants import DIRBOND_CHAIN_MIDDLE
from model.bond_constants import DIRBOND_CHAIN_END
from model.bond_constants import DIRBOND_NONE
from model.bond_constants import DIRBOND_ERROR

from model.bond_constants import find_bond

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
    (See also the method find_chain_or_ring_from_bond [modified from make_pi_bond_obj],
     which calls us twice and does this.)
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

# dict utils to be refiled:

def pop_arbitrary_item(dict1):
    """
    Assume dict1 is not empty; efficiently pop and return
    an arbitrary item (key, value pair) from it.
    """
    key, val_unused = item = arbitrary_item(dict1)
    del dict1[key]
    return item

def arbitrary_item(dict1):
    """
    If dict1 is not empty, efficiently return an arbitrary item
    (key, value pair) from it. Otherwise return None.
    """
    for item in dict1.iteritems():
        return item
    return None

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

    # per-subclass constants
    branches_ok = False # the other value is untested

    def atom_ok(self, atom):
        """
        Subclass-specific primitive for whether an atom qualifies.

        @note: if an atom is only ok if it matches the prior atom in some way,
               use bond_ok instead, for that part of the condition.

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
        And they never pay attention to what bond_ok returns
        unless both its atoms satisfy atom_ok.
        """
        return True
    def atom_list_of_ok_bonds(self, atom):
        """
        Assume self.atom_ok(atom). Return a list of
        atom's bonds for which the bond and its atoms
        satisfy bond_ok and atom_ok respectively.

        This list might have any length (including 0
        or more than 2); we don't assume it's an error
        if the length is more than 2, though callers
        of this method in certain subclasses are free to do so.

        The implementation assumes that self.atom_ok might be
        expensive enough to justify comparing bond's atoms to atom
        to avoid calling self.atom_ok redundantly on atom.
        """
        atom_ok = self.atom_ok
        assert atom_ok(atom)
        res = []
        for bond in atom.bonds:
            if self.bond_ok(bond):
                other = bond.other(atom)
                if atom_ok(other):
                    res.append(bond)
        return res
    def atom_is_branchpoint(self, atom):
        return len(self.atom_list_of_ok_bonds(atom)) > 2
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
        bonds = self.atom_list_of_ok_bonds(atom)
        assert bond in bonds # remove when works? #####
        if len(bonds) != 2:
            return None
        for otherbond in bonds:
            if otherbond is not bond:
                return otherbond
        assert 0, "bond %r occurs twice in %r -- should be impossible" % (bond, bonds)
        return None
    def find_chain_or_ring_from_bond(self, bond):
        """
        Return the maximal chain or ring of qualifying atoms
        connected by qualifying bonds, which includes bond.
        (See below for what is returned to represent the result.)

        (Return None if bond or either of its atoms doesn't qualify.) [### REVIEW - compare to lone-atom error return]

        If any qualifying atom has more than two qualifying bonds,
        behave differently depending on the per-subclass constant
        self.branches_ok: if it's False,
        treat this as an error which in some sense disqualifies that atom --
        complain, stop growing the chain, and don't include that atom in it
        (or any of its bonds). This error can lead to a chain with one atom
        and no bonds (which won't include the given bond), or to a longer
        chain which doesn't include bond (if one of its atoms had this error
        but the other one connected to a longer chain than bond).
        But do nothing to modify the offending atom or its bonds in the model
        (except perhaps to set flags in it which affect only future complaints).

        But if self.branches_ok is true, just include the branchpoint atom as one
        end of the returned chain. Note that the other end may or may not also
        be a branchpoint; if both ends are branchpoints, they may be the same
        atom, but the result will still be considered a chain rather than a
        ring.

        @note: The effect of self.branches_ok is implemented in self._found_chain,
        which could be extended in subclasses to change that behavior.

        @note: If any qualifying atom has no qualifying bonds,
        we'll never encounter it, since we encounter atoms
        only via qualifying bonds on them.)

        @return: None, or an object returned by one of the
        methods make_1atom_chain, make_chain, make_ring (unless the
        corresponding _found methods which call them are overridden,
        which is not encouraged). (Note: make_chain can return None if bond's
        atoms both have too many qualifying chain-bonds; also we can return None
        directly, as described elsewhere.)
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
        assert len(listb1) == len(lista1) # guess, bruce 080119
        if ringQ:
            # branchpoint atoms can't occur in rings
            assert atom2 is lista1[-1]
            res = self._found_ring( [bond] + listb1 ,
##                                    [atom2, atom1] + lista1 # wrong, has atom2 twice
                                    [atom1] + lista1 #bruce 080119 bugfix
                                   )
        else:
            ringQ, listb2, lista2 = grow_bond_chain(bond, atom2, self.next_bond_in_chain)
            assert len(listb2) == len(lista2) # guess, bruce 080119
            assert not ringQ
            ### consider: reverse lista2/listb2 instead, concat other way,
            # so as to keep listb1 in same order in ring or chain case
            # [bruce 080119 comment]
            listb1.reverse()
            lista1.reverse()
            # Note: depending on branches_ok, we worry about branchpoint atoms
            # at either or both ends, inside _found_chain.
            res = self._found_chain( listb1 + [bond] + listb2,
                                     lista1 + [atom1, atom2] + lista2 )
        return res
    def _found_ring(self, listb, lista):
        """
        @see: make_ring
        [subclasses should extend make_ring, which we call,
         rather than this method]
        """
        assert len(listb) == len(lista), \
               "%r finds ring but #bonds %r != #atoms %r" % \
               (self, len(listb), len(lista))
        if 0 and 'debug, but REMOVE WHEN WORKS, very slow':
            for i in range(len(listb)):
                assert find_bond(lista[i] , lista[(i-1) % len(lista)]) is listb[i]
            print "remove when works! in _found_ring len %d" % len(lista)
        return self.make_ring(listb, lista)
    def make_ring(self, listb, lista):
        """
        Return a representation of the ring of bonds and atoms
        in listb and lista, which have the same length,
        and in which listb[i] is a bond which connects the two atoms
        lista[i] and lista[(i+1) % len(lista)].

        The default implementation just returns (True, listb, lista),
        which has the same format as the grow_bond_chain return value.

        The return value is used by other methods of self in several ways:
        * as a possible return value of find_chain_or_ring_from_bond and
          related methods;
        * therefore, as a value passed to self.found_object_iteratoms
          when calling self.find_chains_or_rings.

        Subclasses can extend this method to return a different representation
        of a ring of bonded atoms, but they will probably also need to extend
        found_object_iteratoms to handle it.

        (Or they could extend it to do something and return None even for a
        real ring, but only if they never needed to call a method like
        self.find_chains_or_rings which needs to use self.found_object_iteratoms
        on the result.)
        """
        return (True, listb, lista)
    def _found_chain(self, listb, lista):
        """
        #doc [similar to _found_ring; usually return the output of make_chain];
        if not self.branches_ok, we worry about branchpoint atoms at either or both ends...
        this can cause us to return the output of make_1atom_chain, or even to return None.
        @see: make_chain
        [subclasses should extend make_chain, which we call,
         rather than this method]
        """
        assert len(lista) - 1 == len(listb) # one more atom than bond
        assert len(listb) > 0 # somewhat arbitrary - could easily be recoded to not assume this
        if not self.branches_ok: # a per-subclass constant
            is_branchpoint = self.atom_is_branchpoint
            if is_branchpoint( lista[0] ):
                del lista[0]
                del listb[0]
            if is_branchpoint( lista[-1] ):
                if not listb:
                    return None # i.e. a 0-atom chain
                del lista[-1]
                del listb[-1]
        if not listb:
            # note: this can only happen when self.branches_ok and both atoms
            # were branchpoints, but if we recoded this to relax our initial
            # assumption that len(listb) > 0, then testing it here would be correct.
            return self._found_1atom_chain(lista)
        # recheck these, in case things changed
        assert len(lista) - 1 == len(listb)
        assert len(listb) > 0
        assert not is_branchpoint( lista[0] )
        assert not is_branchpoint( lista[-1] )
        return self.make_chain(listb, lista)
    def make_chain(self, listb, lista): # TODO: doc similar to make_ring
        """
        TODO: doc similar to make_ring
        """
        return (False, listb, lista)
    def _found_1atom_chain(self, lista):
        assert len(lista) == 1
        return self.make_1atom_chain(lista[0])
    def make_1atom_chain(self, atom):
        """
        [subclasses may need to override this method]
        """
        return self.make_chain([], [atom])
    def found_object_iteratoms(self, chain_or_ring):
        """
        For anything returnable by one of the methods
        make_1atom_chain, make_chain, make_ring
        (or our methods which return their results, if overridden),
        return an iterator over that thing's contained atoms
        (or a sequence of them).

        This method must be extended (or replaced)
        to handle objects returnable by those methods,
        if they are extended (if the use of a method which
        calls this one, like self.find_chains_or_rings,
        is desired).
        """
        if chain_or_ring is None:
            return ()
        assert type(chain_or_ring) is type((False,[],[])) # ringQ, listb, lista
            # todo: define an API for those found/made objects,
            # so this default implem can handle them when they are instance objects
        return chain_or_ring[2]
    def find_chains_or_rings(self, atoms_dict):
        """
        Take ownership of the atom.key -> atom dict, atoms_dict,
        and find all chains, rings, or lone atoms that contain any atoms
        in that dict. (The search along bond chains ignores the dict,
        except to remove found atoms that reside in it -- typically
        the found objects contain many atoms besides those in the dict.)

        Remove atoms from atoms_dict as we search from them.
        Found objects are returned only once even if several of their
        atoms are initially in the dict. Upon normal return (anything
        except raising an exception), atoms_dict will be empty.

        @note: We treat all atoms equally (even if killed, or bondpoints);
        caller may want to filter them out before passing us atoms_dict.

        @return: a list of found objects, each returned by one of the
        methods make_1atom_chain, make_chain, make_ring (unless the
        corresponding _found methods which call them are overridden,
        which is not encouraged), with results of None filtered out.
        (Note that these methods are permitted to be overridden to
        have side effects and return None, so in some subclasses,
        the side effects for found objects may be the main result.)
        """
        assert not self.branches_ok # see review comment below for why
        res = []
        while atoms_dict:
            key_unused, atom = pop_arbitrary_item(atoms_dict)
            subres = self.find_chain_or_ring_from_atom(atom)
            if subres is not None:
                res.append(subres)
                # remove found object's atoms from atoms_dict, if present
                # (REVIEW: this removal might be wrong if self.branches_ok)
                for atom in self.found_object_iteratoms(subres):
                    atoms_dict.pop(atom.key, None)
            continue
        return res
    def find_chain_or_ring_from_atom(self, atom):
        assert not self.branches_ok # until review; see comment below for why
        if not self.atom_ok(atom):
            return None
        bonds = self.atom_list_of_ok_bonds(atom)
        if bonds:
            bond = bonds[0]
            # We'll search from bond, but from no other bond of atom.
            # The result should not be affected by which bond we choose
            # except perhaps in ways like ring or chain index-origins,
            # if those are arbitrary.
            #
            # Warning: doing at most one search from atom is only
            # correct when not self.branches_ok. Otherwise, one atom
            # can be in more than one ring or chain (though not if
            # "in" means "in interior"). If that case is ever used,
            # we'll need to revise this API to return a list, or just
            # inline this (modified) into find_chains_or_rings, or outlaw
            # branchpoint atoms in this method and have callers replace them
            # with all their non-branchpoint neighbors.
            #
            # (Note: we can ignore len(bonds), since the following
            #  will check whether it's too long, finding it again
            #  from atom.)
            subres = self.find_chain_or_ring_from_bond(bond)
        else:
            subres = self._found_1atom_chain([atom])
        return subres
    pass # end of class abstract_bond_chain_analyzer

# end
