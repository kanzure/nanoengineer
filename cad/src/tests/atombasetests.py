# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Python atoms, atom sets, diff factories, diff objects (tests)

http://tinyurl.com/rv7fx

May need changes to work in this location.  Used to be in cad/src.

Probably depends on atombasehelp.c, which will likely move as the
cad/src directory is cleaned out.

@author: Will
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""

import unittest
from atombase import *

############################################################

__key = 1
def genkey():
    global __key
    n = __key
    __key = n + 1
    return n
def resetgenkey():
    global __key
    __key = 1


class Atom(AtomBase):
    def __init__(self):
        AtomBase.__init__(self)
        self.key = genkey()

class Bond(BondBase):
    def __init__(self):
        BondBase.__init__(self)
        self.key = genkey()

class AtomDict(AtomDictBase):
    def __init__(self):
        AtomDictBase.__init__(self)
        self.key = genkey()

class BondDict(BondDictBase):
    def __init__(self):
        BondDictBase.__init__(self)
        self.key = genkey()

class Structure:
    def __init__(self):
        self.atomset = AtomDict()
        self.bondset = BondDict()
    def __len__(self):
        return len(self.atomset.keys())

def water(x = 0.0, y = 0.0, z = 0.0):
    w = Structure()
    posns = (
        (Numeric.array((x - 0.983, y - 0.008, z + 0.000)),  # hydrogen
         Numeric.array((x + 0.017, y - 0.008, z + 0.000)),   # oxygen
         Numeric.array((x + 0.276, y - 0.974, z + 0.000))))  # hydrogen
    elts = (1, 8, 1)
    atoms = [ ]
    for i in range(len(posns)):
        a = Atom()
        a._posn = posns[i]
        a._eltnum = elts[i]
        a._atomtype = 1
        w.atomset.add(a)
        atoms.append(a)
    for k1, k2 in ((atoms[0].key, atoms[1].key),
                   (atoms[1].key, atoms[2].key)):
        b = Bond()
        b.atomkey1 = k1
        b.atomkey2 = k2
        b.v6 = 1
        w.bondset.add(b)
    return w

def selectH(atom):
    return atom._eltnum == 1

def selectSingle(bond):
    return bond.v6 == 1

def transmuteOC(atom):
    # change oxygen to carbon
    if atom._eltnum == 8:
        atom._eltnum = 6

def transmuteHN(atom):
    # change hydrogen to nitrogen
    if atom._eltnum == 1:
        atom._eltnum = 7

class TestCase(unittest.TestCase):

    def setUp(self):
        resetgenkey()

class AtomTests(TestCase):

    def test_eltnum_atombase(self):
        ab = Atom()
        assert ab._eltnum == 0
        assert ab._atomtype == 0
        ab._atomtype = 2
        assert ab._atomtype == 2

    def test_atoms_uniqueKeys(self):
        a1 = Atom()
        a1.key = 1
        a2 = Atom()
        a2.key = 2
        assert a1.key != a2.key

class BondTests(TestCase):

    def test_basic_bondbase(self):
        bb = Bond()
        assert bb.v6 == 0
        bb.v6 = 2
        assert bb.v6 == 2

    def test_bondset_keysSorted(self):
        """
        bondset.keys() # sorted
        bondset.values() # sorted by key
        bondset.items() # sorted by key
        """
        bondset = BondDict()
        # create them forwards
        bond1 = Bond()
        bond2 = Bond()
        bond3 = Bond()
        bond4 = Bond()
        bond5 = Bond()
        # add them backwards
        bondset.add(bond5)
        bondset.add(bond4)
        bondset.add(bond3)
        bondset.add(bond2)
        bondset.add(bond1)
        # they better come out forwards
        assert bondset.keys() == [ 2, 3, 4, 5, 6 ]
        assert bondset.values() == [
            bond1, bond2, bond3, bond4, bond5
            ]
        assert bondset.items() == [
            (2, bond1), (3, bond2), (4, bond3),
            (5, bond4), (6, bond5)
            ]

    def test_bondset_contains(self):
        """
        (bond.key in bondset) should be equivalent to, but
        much faster than, (bond.key in bondset.keys())

        ###BUGS: bond.key is now named bond.bond_key;
        # and it is not globally unique (it never was,
        # but as of 080229 it collides much more often).
        """
        bondset = BondDict()
        # create them forwards
        bond1 = Bond()
        bond2 = Bond()
        bond3 = Bond()
        bond4 = Bond()
        bond5 = Bond()
        # add some, not others
        bondset.add(bond1)
        bondset.add(bond2)
        bondset.add(bond3)
        # check if they're in keys() correctly
        assert bond1.key in bondset.keys()
        assert bond2.key in bondset.keys()
        assert bond3.key in bondset.keys()
        assert bond4.key not in bondset.keys()
        assert bond5.key not in bondset.keys()
        # test the __contains__/sq_contains method
        assert bond1.key in bondset
        assert bond2.key in bondset
        assert bond3.key in bondset
        assert bond4.key not in bondset
        assert bond5.key not in bondset

    def test_bondset_gracefulRemoves(self):
        """
        del bondset[bond.key]

        ###BUGS: bond.key is now named bond.bond_key;
        # and it is not globally unique (it never was,
        # but as of 080229 it collides much more often).
        """
        bond1 = Bond()
        bond2 = Bond()
        bond3 = Bond()
        bondset = BondDict()
        bondset.add(bond1)
        bondset.add(bond2)
        bondset.add(bond3)
        assert len(bondset) == 3
        assert bond1.sets.tolist() == [ bondset.key ]
        assert bond2.sets.tolist() == [ bondset.key ]
        assert bond3.sets.tolist() == [ bondset.key ]
        del bondset[bond1.key]
        del bondset[bond2.key]
        del bondset[bond3.key]
        assert len(bondset) == 0
        assert bond1.sets.tolist() == [ ]
        assert bond2.sets.tolist() == [ ]
        assert bond3.sets.tolist() == [ ]

    def test_bondset_updateFromAnotherBondlist(self):
        """
        bondset.update( bondset2 )
        """
        alst = [ ]
        for i in range(5):
            a = Bond()
            alst.append(a)
        bondset = BondDict()
        for a in alst:
            bondset.add(a)
        assert bondset.keys() == [ 1, 2, 3, 4, 5 ]
        bondset2 = BondDict()
        bondset2.update(bondset)
        assert bondset2.keys() == [ 1, 2, 3, 4, 5 ]

    def test_bondset_updateFromDict(self):
        """
        bondset.update( any dict from bond.key to bond )
        """
        adct = { }
        for i in range(5):
            a = Bond()
            adct[a.key] = a
        bondset = BondDict()
        bondset.update(adct)
        assert bondset.keys() == [ 1, 2, 3, 4, 5 ]

    def test_bondset_removeFromEmpty(self):
        bondset = BondDict()
        a = Bond()
        try:
            bondset.remove(a)
            self.fail("shouldn't be able to remove from an empty bondset")
        except KeyError:
            pass

    def test_bondset_filter(self):
        w = water()
        bondset = BondDict()
        for bond in filter(selectSingle, w.bondset.values()):
            bondset.add(bond)
        bondinfo = bondset.bondInfo()
        assert type(bondinfo) == Numeric.arraytype
        assert bondinfo.tolist() == [[3, 4, 1], [4, 5, 1]]


class AtomDictTests(TestCase):

    def test_atomset_basic(self):
        """
        atomset[atom.key] = atom
        """
        atom1 = Atom()
        atomset = AtomDict()
        atomset[atom1.key] = atom1
        try:
            atomset[atom1.key+1] = atom1  # this should fail
            raise FailureExpected
        except KeyError:
            pass

    def test_atomset_keysIn(self):
        """
        atomset.add(atm1)
        atm1.key in atomset --> True
        atm2.key in atomset --> False
        """
        atomset = AtomDict()
        # create them forwards
        atom1 = Atom()
        atom2 = Atom()
        atomset.add(atom1)
        assert atomset.has_key(atom1.key)
        assert not atomset.has_key(atom2.key)
        assert atom1.key in atomset
        assert atom2.key not in atomset

    def test_atomset_keysSorted(self):
        """
        atomset.keys() # sorted
        atomset.values() # sorted by key
        atomset.items() # sorted by key
        """
        atomset = AtomDict()
        # create them forwards
        atom1 = Atom()
        atom2 = Atom()
        atom3 = Atom()
        atom4 = Atom()
        atom5 = Atom()
        # add them backwards
        atomset.add(atom5)
        atomset.add(atom4)
        atomset.add(atom3)
        atomset.add(atom2)
        atomset.add(atom1)
        # they better come out forwards
        assert atomset.keys() == [ 2, 3, 4, 5, 6 ]
        assert atomset.values() == [
            atom1, atom2, atom3, atom4, atom5
            ]
        assert atomset.items() == [
            (2, atom1), (3, atom2), (4, atom3),
            (5, atom4), (6, atom5)
            ]

    def test_atomset_contains(self):
        """
        (atm.key in atomset) should be equivalent to, but
        much faster than, (atm.key in atomset.keys())
        """
        atomset = AtomDict()
        # create them forwards
        atom1 = Atom()
        atom2 = Atom()
        atom3 = Atom()
        atom4 = Atom()
        atom5 = Atom()
        # add some, not others
        atomset.add(atom1)
        atomset.add(atom2)
        atomset.add(atom3)
        # check if they're in keys() correctly
        assert atom1.key in atomset.keys()
        assert atom2.key in atomset.keys()
        assert atom3.key in atomset.keys()
        assert atom4.key not in atomset.keys()
        assert atom5.key not in atomset.keys()
        # test the __contains__/sq_contains method
        assert atom1.key in atomset
        assert atom2.key in atomset
        assert atom3.key in atomset
        assert atom4.key not in atomset
        assert atom5.key not in atomset

    def test_atomset_gracefulRemoves(self):
        """
        del atomset[atom.key]
        """
        atom1 = Atom()
        atom2 = Atom()
        atom3 = Atom()
        atomset = AtomDict()
        atomset.add(atom1)
        atomset.add(atom2)
        atomset.add(atom3)
        assert len(atomset) == 3
        assert atom1.sets.tolist() == [ atomset.key ]
        assert atom2.sets.tolist() == [ atomset.key ]
        assert atom3.sets.tolist() == [ atomset.key ]
        del atomset[atom1.key]
        del atomset[atom2.key]
        del atomset[atom3.key]
        assert len(atomset) == 0
        assert atom1.sets.tolist() == [ ]
        assert atom2.sets.tolist() == [ ]
        assert atom3.sets.tolist() == [ ]

    def test_atomset_updateFromAnotherAtomlist(self):
        """
        atomset.update( atomset2 )
        """
        alst = [ ]
        for i in range(5):
            a = Atom()
            alst.append(a)
        atomset = AtomDict()
        for a in alst:
            atomset.add(a)
        assert atomset.keys() == [ 1, 2, 3, 4, 5 ]
        atomset2 = AtomDict()
        atomset2.update(atomset)
        assert atomset2.keys() == [ 1, 2, 3, 4, 5 ]

    def test_atomset_updateFromDict(self):
        """
        atomset.update( any dict from atom.key to atom )
        """
        adct = { }
        for i in range(5):
            a = Atom()
            adct[a.key] = a
        atomset = AtomDict()
        atomset.update(adct)
        assert atomset.keys() == [ 1, 2, 3, 4, 5 ]

    def test_atomset_removeFromEmpty(self):
        atomset = AtomDict()
        a = Atom()
        try:
            atomset.remove(a)
            self.fail("shouldn't be able to remove from an empty atomset")
        except KeyError:
            pass

    def test_atomset_filter(self):
        w = water()
        atomset = AtomDict()
        for atm in filter(selectH, w.atomset.values()):
            atomset.add(atm)
        atominfo = atomset.atomInfo()
        assert type(atominfo) == Numeric.arraytype
        assert atominfo.tolist() == [
            [1, 1, -0.983, -0.008, 0.000],
            [1, 1, 0.276, -0.974, 0.000]
            ]

    def test_atomset_map(self):
        w = water()
        map(transmuteOC, w.atomset.values())
        atominfo = w.atomset.atomInfo()
        assert type(atominfo) == Numeric.arraytype
        assert atominfo.tolist() == [
            [1, 1, -0.983, -0.008, 0.000],
            [6, 1, 0.017, -0.008, 0.000],   # carbon
            [1, 1, 0.276, -0.974, 0.000]
            ]

def unpack(result):
    x1, x2, x3 = result
    x1 = x1.tolist()
    if type(x2) == Numeric.arraytype:
        x2 = x2.tolist()
        x3 = x3.tolist()
    return (x1, x2, x3)

class DiffTests(TestCase):

    def test_basicdiffs(self):
        w = water()
        db = DiffFactoryBase(w.atomset.values())

        map(transmuteOC, w.atomset.values())
        diffobj = db.snapshot()
        keys, olds, news = unpack(diffobj._eltnum)
        assert keys == [4]
        assert olds == [8]
        assert news == [6]

        map(transmuteHN, w.atomset.values())
        diffobj = db.snapshot()
        keys, olds, news = unpack(diffobj._eltnum)
        assert keys == [3, 5]
        assert olds == [1, 1]
        assert news == [7, 7]

        for atom in w.atomset.values():
            p = atom._posn
            atom._posn = Numeric.array((p[0], p[1], p[2] + 1))
        diffobj = db.snapshot()
        keys, olds, news = unpack(diffobj._posn)
        assert keys == [3, 4, 5]
        assert olds == [0., 0., 0.]
        assert news == [1., 1., 1.]

    def test_diffDicts(self):

        w = water()
        db = DiffFactoryBase(w.atomset.values())

        atomdict = AtomDict()
        for x in w.atomset.values():
            atomdict.add(x)
        diffobj = db.snapshot()
        keys, olds, news = unpack(diffobj.sets)
        assert keys == [3, 4, 5]
        assert olds == [[1], [1], [1]]
        assert news == [[1, 5], [1, 5], [1, 5]]

    def test_diffFactoryAddObject(self):

        w = water()
        db = DiffFactoryBase(w.atomset.values())

        # Create a new atom and add it to the atomset
        a = Atom()
        db.addObject(a)
        # When we add the new atom, we update the existing snapshot
        # with the new atom's data

        # Position it, and add it to the old structure - these changes
        # will appear in the next diff
        a._posn = Numeric.array((3.1416, 2.71828, 1.4707))
        a._eltnum = 7   # nitrogen
        a._atomtype = 1
        w.atomset.add(a)

        # What x coords changed? The new atom, when we positioned it
        diffobj = db.snapshot()
        keys, olds, news = unpack(diffobj._posn)
        assert keys == [8]
        assert olds[0][0] == 0.0
        assert news[0][0] == 3.1416

        # Move the whole structure, the diff includes all the x changes
        for atm in w.atomset.values():
            p = atm._posn
            atm._posn = Numeric.array((p[0] + 2, p[1], p[2]))
        diffobj = db.snapshot()
        keys, olds, news = unpack(diffobj._posn)
        assert keys == [3, 4, 5, 8]
        assert map(lambda x: x[0], olds) == [-0.983, 0.017, 0.276, 3.1416]
        assert map(lambda x: x[0], news) == [1.017, 2.017, 2.276, 5.1416]

class Tests(AtomTests, BondTests, AtomDictTests, DiffTests):
    pass

def test():
    suite = unittest.makeSuite(Tests, 'test')
    #suite = unittest.makeSuite(Tests, 'test_atomset_keysSorted')
    #suite = unittest.makeSuite(Tests, 'test_atomset_gracefulRemoves')
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    test()
