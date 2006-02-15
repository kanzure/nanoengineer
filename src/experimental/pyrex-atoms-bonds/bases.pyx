# Pyrex file for base classes

import unittest
import random

cdef extern from "basehelp.c":
    checkForErrors()
    cdef struct intset:
        pass
    cdef struct chunkbase:
        pass
    cdef struct atombase:
        int positionIndex
    intset *intset_init()
    intset_add(intset*, int)
    intset_contains(intset*, int)
    intset_remove(intset*, int)
    intset_del(intset*)
    chunkbase *chunkbase_init()
    chunkbase_addatom(chunkbase*, atombase*, double, double, double)
    void chunkbase_del(chunkbase*)
    atombase *atombase_init()
    void atombase_del(atombase*)

cdef class __IntSet:
    cdef intset *x
    def __init__(self):
        self.x = intset_init()
        checkForErrors()
    def __del__(self):
        intset_del(self.x)
    def add(self, n):
        intset_add(self.x, n)
    def remove(self, n):
        intset_remove(self.x, n)
    def contains(self, n):
        return intset_contains(self.x, n)

class IntSet(__IntSet):
    # __del__ doesn't get used until you derive a non-cdef class
    pass

cdef class __AtomBase:
    cdef atombase *x
    def __init__(self):
        self.x = atombase_init()
        checkForErrors()
    def __del__(self):
        atombase_del(self.x)

class AtomBase(__AtomBase):
    pass

cdef class BondBase:
    pass

cdef class __ChunkBase:
    cdef chunkbase *x
    def __init__(self):
        self.x = chunkbase_init()
        checkForErrors()
    def __del__(self):
        chunkbase_del(self.x)
    def addatom(self, __AtomBase atm, x, y, z):
        chunkbase_addatom(self.x, atm.x, x, y, z)

class ChunkBase(__ChunkBase):
    # Maintain a normal Python list of atoms so that the
    # atoms don't get GCed while the chunk is still alive
    def __init__(self):
        __ChunkBase.__init__(self)
        self.atomlist = [ ]
    def addatom(self, ab, x, y, z):
        __ChunkBase.addatom(self, ab, x, y, z)
        self.atomlist.append(ab)

class Tests(unittest.TestCase):

    def test_IntSet(self):
        x = IntSet()
        for i in range(10000):
            if (i & 1) == 0:
                x.add(i)
        assert not x.contains(-3)
        assert not x.contains(-2)
        assert not x.contains(-1)
        assert x.contains(0)
        assert not x.contains(1)
        assert x.contains(2)
        assert not x.contains(3)
        assert x.contains(4)
        assert not x.contains(5)
        assert not x.contains(9995)
        assert x.contains(9996)
        assert not x.contains(9997)
        assert x.contains(9998)
        assert not x.contains(9999)
        assert not x.contains(10000)
        assert not x.contains(10001)

    def test_zzz(self):
        cb = ChunkBase()
        for i in range(12000):
            x = random.random()
            y = random.random()
            z = random.random()
            ab = AtomBase()
            cb.addatom(ab, x, y, z)

def test():
    suite = unittest.makeSuite(Tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
