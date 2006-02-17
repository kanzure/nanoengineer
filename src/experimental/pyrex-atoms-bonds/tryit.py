import time
import unittest
import random
import Numeric
from bases import IntegerSet, AtomBase, ChunkBase

stuff = [ ]
N = int(10**6)
#N = int(10**6)

class Tests(unittest.TestCase):

    def test_IntegerSetFunctionality(self):
        x = IntegerSet()
        for i in range(0,2*N,2):
            x.add(i)
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

        x.remove(2*N-4)
        x.remove(2*N-2)
        assert not x.contains(2*N-4)
        assert not x.contains(2*N-2)

    def test_IntegerSetAsArrayMethod(self):
        x = IntegerSet()
        a = Numeric.array(range(N), Numeric.UInt32)
        x.addRange(0, N)
        assert len(x) == len(a)
        assert len(x) == N
        xa = x.asArray()
        # only way to test equality of two arrays
        a = a - xa
        assert Numeric.vdot(a, a) == 0

    def reportPerformance(self, name, time):
        stuff.append("%s() %g nanoseconds per element" % (name, time))

    def test_IntegerSetContainsPerformance(self):
        x = IntegerSet()
        x.addRange(0, N)
        T = x.contains_performance(N)
        self.reportPerformance("contains", T)

    def test_IntegerSetAddPerformance(self):
        x = IntegerSet()
        T = x.add_performance(N)
        self.reportPerformance("add", T)

    def test_IntegerSetAsarrayPerformance(self):
        x = IntegerSet()
        x.addRange(0, N)
        T = x.asarray_performance(N)
        self.reportPerformance("asarray", T)

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
    print "Performance numbers"
    for x in stuff:
        print x

if __name__ == "__main__":
    test()
