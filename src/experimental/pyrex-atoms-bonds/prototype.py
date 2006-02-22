#!/usr/bin/python

import unittest
import time
import Numeric

# This is a prototype of the desired API for Pyrex atoms, bonds, and
# atom sets. See "Pyrex atoms and bonds" page on the wiki.

class FailureExpected(Exception):
    pass

genkeyCount = 1

def genkey():
    global genkeyCount
    n = genkeyCount
    genkeyCount += 1
    return n

class Atom:
    def __init__(self):
        self.key = genkey()
        self.sets = [ ]
        self.array = None   # Numeric array
        self.arrayIndex = None   # index into Numeric array

class Bond:
    pass

class AtomSet:
    def __init__(self):
        self._dct = { }
        self.pointer = 0
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
        return self
    def next(self):
        k = self.keys()
        if self.pointer == len(k):
            raise StopIteration
        i = k[self.pointer]
        self.pointer += 1
        return self[i]
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
        other = AtomSet()
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
    atomset = AtomSet()
    for i in range(len(atominfo)):
        a = Atom()
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
        atom1 = Atom()
        atomset = AtomSet()
        atomset[atom1.key] = atom1
        try:
            atomset[atom1.key+1] = atom1  # this should fail
            raise FailureExpected
        except KeyError:
            pass

    def test_atomset_keysSorted(self):
        atomset = AtomSet()
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
        assert atomset.keys() == [ 1, 2, 3, 4, 5 ]
        assert atomset.values() == [
            atom1, atom2, atom3, atom4, atom5
            ]

    def test_atomset_gracefulRemoves(self):
        atom1 = Atom()
        atom2 = Atom()
        atom3 = Atom()
        atomset = AtomSet()
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
            alst.append(Atom())
        atomset = AtomSet()
        for a in alst:
            atomset.add(a)
        assert atomset.keys() == [ 1, 2, 3, 4, 5 ]
        atomset2 = AtomSet()
        atomset2.update(atomset)
        assert atomset2.keys() == [ 1, 2, 3, 4, 5 ]

    def test_atomset_updateFromDict(self):
        adct = { }
        for i in range(5):
            a = Atom()
            adct[a.key] = a
        atomset = AtomSet()
        atomset.update(adct)
        assert atomset.keys() == [ 1, 2, 3, 4, 5 ]

    def test_atomset_removeFromEmpty(self):
        atomset = AtomSet()
        a = Atom()
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
        atomset = AtomSet()
        atomset.add(h1)
        atomset.add(h2)
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
    runner = unittest.TextTestRunner()
    runner.run(suite)
    PL.dump()

if __name__ == "__main__":
    test()
