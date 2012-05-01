#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
import sys
import string
import unittest
import time
import types
import numpy

# This is a prototype of the desired API for Pyrex atoms, bonds, and
# atom sets. See "Pyrex atoms and bonds" page on the wiki.

DEBUG = 0

class FailureExpected(Exception):
    pass

genkeyCount = 1

def genkey():
    global genkeyCount
    n = genkeyCount
    genkeyCount += 1
    return n

def pointer(x):
    if type(x) not in (types.IntType, types.LongType):
        x = id(x)
    x = long(x)
    if x < 0:
        x += 1 << 32
    return hex(x)[:-1]   # lose "L"

"""
http://docs.python.org/lib/module-struct.html

#define MAX_NUM_NEIGHBORS 8  // ask Damian for the real number
struct atom {
    unsigned int key;
    PyArrayObject *positionArray;
    unsigned int positionIndex;
    unsigned int numNeighbors;
    unsigned int bondIndices[MAX_NUM_NEIGHBORS];
};

struct bond {
    unsigned int atom1index;
    unsigned int atom2index;
    unsigned int bondorder;
};

int followbond(int fromAtom, struct bond *b)
{
    if (b->atom1index == fromAtom || b->atom2index == fromAtom)
        return b->atom1index + b->atom2index - fromAtom;
    else return SOME_KINDA_ERROR_CODE;
}
"""

# Make sure that whatever we're getting, it will fit into the field of
# a struct.
def isSmallInteger(x):
    return type(x) == types.IntType
def isNumericArray(x):
    return type(x) == Numeric.ArrayType

class CStruct:
    def __init__(self):
        self.__struct__ = { }
    def kids(self):
        lst = [ ]
        for k in self.STRUCTINFO.keys():
            lst.append((k, getattr(self, k)))
        return lst
    def dumpInfo(self, index=None, indent=0):
        ind = indent * "    "
        if index == None: index = ""
        else: index = "%s " % index
        r = ind + index + repr(self) + "\n"
        for key, value in self.kids():
            if isinstance(value, CStruct):
                r += value.dumpInfo(key, indent + 1)
            else:
                r += ind + ("    %s=%s\n" % (key, repr(value)))
        if indent == 0:
            print r
        return r
    def __setattr__(self, attr, value):
        if DEBUG > 2: print "SET", attr, pointer(value)
        if attr in self.STRUCTINFO.keys():
            assert self.STRUCTINFO[attr](value), \
                   attr + " fails " + repr(self.STRUCTINFO[attr])
            self.__struct__[attr] = value
            return
        self.__dict__[attr] = value
    def __getattr__(self, attr):
        if attr == "__repr__":
            raise AttributeError, attr
        if attr in self.STRUCTINFO.keys():
            try:
                value = self.__struct__[attr]
            except KeyError:
                value = 0
        else:
            value = self.__dict__[attr]
        if DEBUG > 2: print "GET", attr, value
        return value

class CStructWithKey(CStruct):
    def __init__(self):
        CStruct.__init__(self)
        assert hasattr(self, "STRUCTINFO")
        assert "key" in self.STRUCTINFO.keys()
        self.key = genkey()

class AtomBase(CStructWithKey):
    STRUCTINFO = {
        "key": isSmallInteger,
        "array": isNumericArray,
        "arrayIndex": isSmallInteger,
        "numNeighbors": isSmallInteger,
        "neighbor1": isSmallInteger,
        "neighbor2": isSmallInteger,
        "neighbor3": isSmallInteger,
        "neighbor4": isSmallInteger,
        "neighbor5": isSmallInteger,
        "neighbor6": isSmallInteger,
        "neighbor7": isSmallInteger,
        "neighbor8": isSmallInteger
        }
    def __init__(self):
        CStructWithKey.__init__(self)
        self.sets = [ ]

class BondBase(CStructWithKey):
    STRUCTINFO = {
        "key": isSmallInteger,
        "atom1index": isSmallInteger,
        "atom2index": isSmallInteger,
        "order": isSmallInteger,
        }

class AtomSetBase(CStruct):
    STRUCTINFO = {
        "key": isSmallInteger,
        }
    def __init__(self):
        CStruct.__init__(self)
        self._dct = { }
    def kids(self):
        lst = [ ]
        for k in self.keys():
            lst.append((k, self[k]))
        return lst
    def __setitem__(self, key, atom):
        if key != atom.key:
            raise KeyError
        self._dct[key] = atom
        atom.sets.append(self)
    def __del__(self):
        self.clear()
    def __getitem__(self, key):
        return self._dct[key]
    def __delitem__(self, key):
        self._dct[key].sets.remove(self)
        del self._dct[key]
    def __iter__(self):
        class MyIterator:
            def __init__(self, lst):
                self.lst = lst
                self.pointer = 0
            def next(self):
                if self.pointer == len(self.lst):
                    raise StopIteration
                i = self.lst[self.pointer]
                self.pointer += 1
                return i
        return MyIterator(self.values())
    def keys(self):
        return self._dct.keys()
    def add(self, atom):
        self[atom.key] = atom
    def remove(self, atom):
        del self[atom.key]
    def update(self, other):
        for k in other.keys():
            self[k] = other[k]
    def values(self):
        lst = [ ]
        for k in self.keys():
            lst.append(self[k])
        return lst
    def items(self):
        return self.values()
    def clear(self):
        for k in self.keys():
            del self[k]
    def filter(self, predicate):
        other = AtomSetBase()
        for k in self.keys():
            if predicate(self[k]):
                other.add(self[k])
        return other
    # should there also be methods for map and reduce?
    def atomInfo(self):
        ar = Numeric.zeros((len(self.keys()), 4), 'd')
        i = 0
        for k in self.keys():
            atm = self[k]
            ar[i] = atm.array[atm.arrayIndex]
            i += 1
        return ar

class Structure:
    def __init__(self):
        self.bondlist = [ ]
        self.atomset = AtomSetBase()
        self.atomArray = None   # Numeric array
    def __len__(self):
        return len(self.atomArray)
    def bondThese(self, atm1, atm2, order):
        def addBond(atm, other):
            attr = "neighbor" + repr(atm.numNeighbors + 1)
            setattr(atm, attr, other)
            atm.numNeighbors += 1
        addBond(atm1, atm2.key)
        addBond(atm2, atm1.key)
        b = BondBase()
        b.atom1index = atm1.key
        b.atom2index = atm2.key
        b.order = order
        self.bondlist.append(b)
    def bondThese(self, key1, key2, order):
        def addBond(atm, other):
            attr = "neighbor" + repr(atm.numNeighbors + 1)
            setattr(atm, attr, other)
            atm.numNeighbors += 1
        atm1 = self.atomset[key1]
        atm2 = self.atomset[key2]
        addBond(atm1, key2)
        addBond(atm2, key1)
        b = BondBase()
        b.atom1index = key1
        b.atom2index = key2
        b.order = order
        self.bondlist.append(b)

#############################################################

def water():
    w = Structure()
    w.atomArray = Numeric.array(
        ((1.0, -0.983, -0.008, 0.000),  # hydrogen
         (8.0, 0.017, -0.008, 0.000),   # oxygen
         (1.0, 0.276, -0.974, 0.000)))  # hydrogen
    for i in range(len(w)):
        a = AtomBase()
        a.array = w.atomArray
        a.arrayIndex = i
        w.atomset.add(a)
    w.bondThese(1, 2, 1)
    w.bondThese(2, 3, 1)
    if DEBUG > 1: w.atomset.dumpInfo()
    return w

class PerformanceLog:
    def __init__(self):
        self.records = [ ]
    def measure(self, name, fn, n=1):
        tt = time.time
        t1 = tt()
        for i in range(n):
            fn()
        t2 = tt()
        self.records.append("%s: %.2f nanoseconds per element"
                            % (name, (t2 - t1) / n))
    def dump(self):
        print "Performance information"
        for x in self.records:
            print x

PL = PerformanceLog()

class Tests(unittest.TestCase):
    """
    atomset[atom.key] = atom
    atomset.update( any dict from atom.key to atom )
    atomset.update( atomset2 )
    del atomset[atom.key]
    atomset.keys() # sorted
    atomset.values() # sorted by key
    atomset.items() # sorted by key
    """
    def setUp(self):
        global genkeyCount
        genkeyCount = 1

    def test_atomset_basic(self):
        atom1 = AtomBase()
        atomset = AtomSetBase()
        atomset[atom1.key] = atom1
        try:
            atomset[atom1.key+1] = atom1  # this should fail
            raise FailureExpected
        except KeyError:
            pass

    def test_atomset_keysSorted(self):
        atomset = AtomSetBase()
        # create them forwards
        atom1 = AtomBase()
        atom2 = AtomBase()
        atom3 = AtomBase()
        atom4 = AtomBase()
        atom5 = AtomBase()
        # add them backwards
        atomset.add(atom5)
        atomset.add(atom4)
        atomset.add(atom3)
        atomset.add(atom2)
        atomset.add(atom1)
        # they better come out forwards
        assert atomset.keys() == [ 1, 2, 3, 4, 5 ]
        assert atomset.values() == [
            atom1, atom2, atom3, atom4, atom5
            ]

    def test_atomset_gracefulRemoves(self):
        atom1 = AtomBase()
        atom2 = AtomBase()
        atom3 = AtomBase()
        atomset = AtomSetBase()
        atomset.add(atom1)
        atomset.add(atom2)
        atomset.add(atom3)
        assert atom1.sets == [ atomset ]
        assert atom2.sets == [ atomset ]
        assert atom3.sets == [ atomset ]
        atomset.clear()
        assert atom1.sets == [ ]
        assert atom2.sets == [ ]
        assert atom3.sets == [ ]

    def test_bondlist(self):
        b = water().bondlist
        assert b[0].order == 1
        assert b[0].atom1index == 1
        assert b[0].atom2index == 2
        assert b[0].key == 4
        assert b[1].order == 1
        assert b[1].atom1index == 2
        assert b[1].atom2index == 3
        assert b[1].key == 5

    def test_atomset_updateFromAnotherAtomlist(self):
        alst = [ ]
        for i in range(5):
            alst.append(AtomBase())
        atomset = AtomSetBase()
        for a in alst:
            atomset.add(a)
        assert atomset.keys() == [ 1, 2, 3, 4, 5 ]
        atomset2 = AtomSetBase()
        atomset2.update(atomset)
        assert atomset2.keys() == [ 1, 2, 3, 4, 5 ]

    def test_atomset_updateFromDict(self):
        adct = { }
        for i in range(5):
            a = AtomBase()
            adct[a.key] = a
        atomset = AtomSetBase()
        atomset.update(adct)
        assert atomset.keys() == [ 1, 2, 3, 4, 5 ]

    def test_atomset_removeFromEmpty(self):
        atomset = AtomSetBase()
        a = AtomBase()
        try:
            atomset.remove(a)
            raise FailureExpected
        except KeyError:
            pass

    # I think we'll want this to make OpenGL run fast.
    def test_atomset_atomInfo(self):
        w = water()
        h1 = w.atomset[1]
        ox = w.atomset[2]
        h2 = w.atomset[3]
        atomset = AtomSetBase()
        atomset.add(h1)
        atomset.add(h2)
        atominfo2 = atomset.atomInfo()
        assert atominfo2.tolist() == [
            [1.0, -0.983, -0.008, 0.000],
            [1.0, 0.276, -0.974, 0.000]
            ]

    def test_atomset_dumpInfo(self):
        w = water()
        if DEBUG > 0: w.dumpInfo()
        # needs to be visually inspected for reasonableness

    def test_atomset_filter(self):
        w = water()
        def isHydrogen(atom):
            e, x, y, z = atom.array[atom.arrayIndex]
            return e == 1
        atomset = w.atomset.filter(isHydrogen)
        atominfo = atomset.atomInfo()
        assert atominfo.tolist() == [
            [1.0, -0.983, -0.008, 0.000],
            [1.0, 0.276, -0.974, 0.000]
            ]

    def test_atomset_map(self):
        w = water()
        def transmute(atom):
            e, x, y, z = atom.array[atom.arrayIndex]
            if e == 8:
                # change oxygen to carbon
                atom.array[atom.arrayIndex][0] = 6
        map(transmute, w.atomset)
        atominfo = w.atomset.atomInfo()
        assert atominfo.tolist() == [
            [1.0, -0.983, -0.008, 0.000],
            [6.0, 0.017, -0.008, 0.000],   # carbon
            [1.0, 0.276, -0.974, 0.000]
            ]


def test():
    suite = unittest.makeSuite(Tests, 'test')
    #suite = unittest.makeSuite(Tests, 'test_atomset_atomInfo')
    runner = unittest.TextTestRunner()
    runner.run(suite)
    PL.dump()

if __name__ == "__main__":
    for x in sys.argv[1:]:
        if x.startswith("debug="):
            DEBUG = string.atoi(x[6:])
    test()
