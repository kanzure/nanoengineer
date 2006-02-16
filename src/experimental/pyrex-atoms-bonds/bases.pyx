# Pyrex file for base classes

import time
import unittest
import random
import Numeric
import traceback

VERBOSE = 0

cdef extern from "Numeric/arrayobject.h":
    object PyArray_FromDims(int nd, int *d, int type)

cdef extern from "basehelp.c":
    checkForErrors()
    cdef struct intset:
        pass
    cdef struct chunkbase:
        pass
    cdef struct atombase:
        int positionIndex
    intset *intset_init()
    intset_size(intset*)
    intset_add(intset*, int)
    intset_addRange(intset*, int, int)
    intset_asarray(intset*)
    intset_fromList(intset*, PyObject)
    intset_contains(intset*, int)
    intset_remove(intset*, int)
    intset_del(intset*)
    double intset_contains_performance_test(intset*, int)
    double intset_addRangePerformance(intset*, int)
    chunkbase *chunkbase_init()
    chunkbase_addatom(chunkbase*, atombase*, int, double, double, double)
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
    def __len__(self):
        # scales approximately linearly, roughly 1 nanosecond per
        # element in the list
        return intset_size(self.x)
    def fromList(self, lst):
        intset_fromList(self.x, lst)
    def addRange(self, m, n):
        intset_addRange(self.x, m, n)
    def add(self, n):
        intset_add(self.x, n)
    def asArray(self):
        return intset_asarray(self.x)
    def remove(self, n):
        intset_remove(self.x, n)
    def contains(self, n):
        return intset_contains(self.x, n)
    def contains_performance(self, n):
        return intset_contains_performance_test(self.x, n)
    def add_performance(self, n):
        return intset_addRangePerformance(self.x, n)

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
    def addatom(self, __AtomBase atm, tp, x, y, z):
        chunkbase_addatom(self.x, atm.x, tp, x, y, z)

class ChunkBase(__ChunkBase):
    # Maintain a normal Python list of atoms so that the
    # atoms don't get GCed while the chunk is still alive
    def __init__(self):
        __ChunkBase.__init__(self)
        self.atomlist = [ ]
    def addatom(self, ab, tp, x, y, z):
        __ChunkBase.addatom(self, ab, tp, x, y, z)
        self.atomlist.append(ab)

def performanceTest(f, n=100):
    t1 = time.time()
    for i in range(n):
        f()
    t2 = time.time()
    return (t2 - t1) / n

class Tests(unittest.TestCase):

    def intsetsize(self):
        len(self.x)

    def intsetcontains(self):
        self.x.contains_performance(self.n)

    def test_IntSet(self):
        x = IntSet()
        N = 2170   # must be even
        for i in range(N):
            if (i & 1) == 0:
                x.add(i)
        assert not x.contains(-2)
        assert not x.contains(-1)
        assert x.contains(0)
        assert not x.contains(1)
        assert x.contains(2)
        assert not x.contains(3)
        assert x.contains(4)
        assert x.contains(N-4)
        assert not x.contains(N-3)
        assert x.contains(N-2)
        assert not x.contains(N-1)
        assert not x.contains(N)
        assert not x.contains(N+1)
        assert len(x) == N / 2

    def test_IntSetSizePerformance(self):
        self.x = x = IntSet()
        N = 10**4
        x.addRange(0, N)
        expectedTime = N * 1.0e-9
        T = performanceTest(self.intsetsize)
        if VERBOSE:
            print "test_IntSetSizePerformance", T, expectedTime
        assert T <= expectedTime

    def test_IntSetContainsPerformance(self):
        self.x = x = IntSet()
        N = 10**6
        x.addRange(0, N)
        T = x.contains_performance(N)
        expectedTime = 7.0e-9
        if VERBOSE:
            print "test_IntSetContainsPerformance", T, expectedTime
        assert T <= expectedTime

    def test_IntSetAddPerformance(self):
        self.x = x = IntSet()
        N = 10**6
        T = x.add_performance(N)
        expectedTime = 15.0e-9
        if VERBOSE:
            print "test_IntSetAddPerformance", T, expectedTime
        assert T <= expectedTime

    def test_IntSetAsArray(self):
        self.x = x = IntSet()
        N = int(10**5)
        a = Numeric.array(range(N), Numeric.UInt32)
        x.addRange(0, N)
        assert len(x) == len(a)
        assert len(x) == N
        xa = x.asArray()
        a = a - xa
        assert Numeric.vdot(a, a) == 0

    def test_chunkBase(self):
        cb = ChunkBase()
        n = 2
        for i in range(n):
            tp = random.randrange(10)
            x = random.random()
            y = random.random()
            z = random.random()
            ab = AtomBase()
            cb.addatom(ab, tp, x, y, z)

def test():
    suite = unittest.makeSuite(Tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
