#!/usr/bin/python

import unittest
import time
import types
import struct
import Numeric
import proto

# This is a prototype of the desired API for Pyrex atoms, bonds, and
# atom sets. See "Pyrex atoms and bonds" page on the wiki.

DEBUG = False

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
    int atomtype;  // element and hybridization
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

class Struct:
    def __init__(self, permitted):
        self.__permitted = permitted
        self.__values = { }
    def __setattr__(self, attr, value):
        if attr not in self.__permitted.keys():
            raise AttributeError, attr
        if type(value) != self.__permitted[attr]:
            raise TypeError, value
        self.__values[attr] = value
    def __getattr__(self, attr):
        if attr not in self.__permitted.keys():
            raise AttributeError, attr
        return self.__values[attr]



ATOMFORMAT = "IiPII8I"
BONDFORMAT = "III"

class AtomBase:
    def __init__(self):
        self.struct = struct.pack(ATOMFORMAT,
                    0,  # key
                    0,  # atomtype
                    0,  # array
                    0,  # arrayIndex
                    0,  # number of neighbors
                    0,  # neighbor 1
                    0,  # neighbor 2
                    0,  # neighbor 3
                    0,  # neighbor 4
                    0,  # neighbor 5
                    0,  # neighbor 6
                    0,  # neighbor 7
                    0,  # neighbor 8
                    )
##         self.struct = Struct({
##             "key": types.IntType,
##             "atomtype": types.IntType,
##             "array": types.IntType,
##             "arrayIndex": types.IntType,
##             "numNeighbors": types.IntType,
##             "neighbor1": types.IntType,
##             "neighbor2": types.IntType,
##             "neighbor3": types.IntType,
##             "neighbor4": types.IntType,
##             "neighbor5": types.IntType,
##             "neighbor6": types.IntType,
##             "neighbor7": types.IntType,
##             "neighbor8": types.IntType
##             })
        self.key = genkey()
        self.sets = [ ]
    def dumpInfo(self, indent=0):
        ind = indent * "    "
        print ind + repr(self)
        print ind + "key=" + repr(self.key)
        print ind + "array=" + repr(self.array)
        print ind + "arrayIndex=" + repr(self.arrayIndex)
    def __repl(self, index, value):
        z = list(struct.unpack(ATOMFORMAT, self.struct))
        z[index] = value
        self.struct = apply(struct.pack, tuple([ATOMFORMAT,] + z))
    def __fetch(self, index):
        z = struct.unpack(ATOMFORMAT, self.struct)
        return z[index]
    def __setattr__(self, attr, value):
        if DEBUG: print "SET", attr, pointer(value)
        if attr in ("struct", "sets"):
            self.__dict__[attr] = value
            return
        if attr == "key":
            self.__repl(0, value)
            return
        if attr == "array":
            proto.xdecref(self.__fetch(2))
            n = proto.pointer2int(value)
            proto.incref(n)
            self.__repl(2, n)
            return
        if attr == "arrayIndex":
            self.__repl(3, value)
            return
        raise AttributeError, (self, attr, value)
    def __getattr__(self, attr):
        value = notfound = "not found"
        if attr in ("struct", "sets"):
            value = self.__dict__[attr]
        elif attr == "key":
            value = self.__fetch(0)
        elif attr == "array":
            z = struct.unpack(ATOMFORMAT, self.struct)
            value = proto.int2pointer(self.__fetch(2))
        elif attr == "arrayIndex":
            value = self.__fetch(3)
        if value is not notfound:
            if DEBUG: print "GET", attr, value
            return value
        raise AttributeError, (self, attr)

class BondBase:
    pass

class AtomSetBase:
    def __init__(self):
        self._dct = { }
    def dumpInfo(self, indent=0):
        ind = indent * "    "
        print ind + repr(self)
        for v in self.values():
            v.dumpInfo(indent+1)
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

#############################################################

def water():
    atominfo = Numeric.array(
        ((1.0, -0.983, -0.008, 0.000),  # hydrogen
         (8.0, 0.017, -0.008, 0.000),   # oxygen
         (1.0, 0.276, -0.974, 0.000)))  # hydrogen
    if DEBUG: print "atominfo", pointer(atominfo)
    atomset = AtomSetBase()
    for i in range(len(atominfo)):
        a = AtomBase()
        a.array = atominfo
        a.arrayIndex = i
        atomset.add(a)
    return atomset

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
        h1 = w[1]
        ox = w[2]
        h2 = w[3]
        atomset = AtomSetBase()
        atomset.add(h1)
        atomset.add(h2)
        if DEBUG: atomset.dumpInfo()
        atominfo2 = atomset.atomInfo()
        assert atominfo2.tolist() == [
            [1.0, -0.983, -0.008, 0.000],
            [1.0, 0.276, -0.974, 0.000]
            ]

    def test_atomset_filter(self):
        w = water()
        def isHydrogen(atom):
            e, x, y, z = atom.array[atom.arrayIndex]
            return e == 1
        atomset = w.filter(isHydrogen)
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
        map(transmute, w)
        atominfo = w.atomInfo()
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
    test()
