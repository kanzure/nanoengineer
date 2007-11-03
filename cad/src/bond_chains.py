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
    
# end
