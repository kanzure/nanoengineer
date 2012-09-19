# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
import time
import unittest
import random
import Numeric
from bases import *

N = int(10**6)
#N = int(10**6)

class PerformanceLog:
    def __init__(self):
        self.records = [ ]
    def __setitem__(self, name, time):
        self.records.append("%s: %.2f nanoseconds per element"
                            % (name, time))
    def dump(self):
        print "Performance information"
        for x in self.records:
            print x

PL = PerformanceLog()

class Tests(unittest.TestCase):

    def test_AtomSetFunctionality(self):
        x = AtomSet()
        x.quickFill(N, 2)
        assert len(x) == N

        assert not x.contains(-2)
        assert not x.contains(-1)
        assert x.contains(0)
        assert not x.contains(1)
        assert x.contains(2)
        assert not x.contains(3)
        assert x.contains(4)

        if (N & 1) == 0:
            assert x.contains(N-4)
            assert not x.contains(N-3)
            assert x.contains(N-2)
            assert not x.contains(N-1)
            assert x.contains(N)
            assert not x.contains(N+1)
        else:
            assert not x.contains(N-4)
            assert x.contains(N-3)
            assert not x.contains(N-2)
            assert x.contains(N-1)
            assert not x.contains(N)
            assert x.contains(N+1)

        assert x.contains(2*N-4)
        assert not x.contains(2*N-3)
        assert x.contains(2*N-2)
        assert not x.contains(2*N-1)
        assert not x.contains(2*N)
        assert not x.contains(2*N+1)

        del x[2*N-4]
        del x[2*N-2]
        assert len(x) == N - 2
        assert not x.contains(2*N-4)
        assert not x.contains(2*N-2)

    def test_AtomSetAsArrayMethod(self):
        x = AtomSet()
        a = Numeric.array(range(N), Numeric.UInt32)
        x.quickFill(N)
        assert len(x) == len(a)
        assert len(x) == N
        xa = x.asArray()
        # only way to test equality of two arrays
        a = a - xa
        assert Numeric.vdot(a, a) == 0

    def test_AtomSetContainsPerformance(self):
        x = AtomSet()
        T = x.contains_performance(N)
        PL["contains()"] = T

    def test_AtomSetSetPerformance(self):
        x = AtomSet()
        T = x.set_performance(N)
        PL["set()"] = T

    def test_AtomSetAsarrayPerformance(self):
        x = AtomSet()
        x.quickFill(N)
        T = x.asarray_performance(N)
        PL["asarray()"] = T

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
    PL.dump()

if __name__ == "__main__":
    test()
