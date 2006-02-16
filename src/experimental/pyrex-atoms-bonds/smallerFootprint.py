# Think about the set sizes for which this scheme is memory efficient.

import time
import unittest
import Numeric

VERBOSE = 0
stuff = [ ]

# Verifying Bruce's suspicion that the 9/9/9/5 scheme was a memory
# hog...

#def waste(setsize):
#    idealmem = int(setsize / 8.0)
#    numleaves = (setsize + 16383) / 16384
#    leafmem = numleaves * 512 * 4
#    nummiddles = (numleaves + 511) / 512
#    middlemem = nummiddles * 512 * 4
#    rootmem = 512 * 4
#    totalmem = rootmem + middlemem + leafmem
#    efficiency = (1.0 * idealmem) / totalmem
#    return (totalmem, idealmem, efficiency)

#for i in range(30):
#    setsize = int(8 * 1.6**i)
#    print setsize, waste(setsize)

class NodeStruct:
    def __init__(self, prefix):
        self.next = None
        self.previous = None
        self.prefix = prefix
        self.data = 128 * [ 0 ]
        self.size = (3 + 128) * 4

class Set:
    def __init__(self):
        self.root = None
        self.population = 0
        self.memUsage = 0
        self.bubbleCounter = 10

    def __len__(self):
        return self.population

    def idealMemUsage(self):
        # assume 1 bit per element, ideally
        return (self.population + 7) / 8

    def efficiency(self):
        return (1.0 * self.idealMemUsage()) / self.memUsage

    def __del__(self):
        if VERBOSE:
            stuff.append(("Memory efficiency", self.efficiency()))

    def findNodeWithPrefix(self, p):
        r = self.root
        while True:
            if r == None: return None
            if r.prefix == p: return r
            r = r.next

    def add(self, x):
        x0, x1, x2 = (x >> 12) & 0xfffff, (x >> 5) & 0x7f, x & 0x1f
        C = self.findNodeWithPrefix(x0)
        if C == None:
            # create a new node
            C = NodeStruct(x0)
            self.memUsage += C.size
            if self.root != None:
                self.root.previous = C
            C.next = self.root
            self.root = C
        # Set the bit in C's data
        z = C.data[x1]
        if (z & (1 << x2)) == 0:
            C.data[x1] = z | (1 << x2)
            self.population += 1

    def addRange(self, m, n):
        while m != n:
            self.add(m)
            m += 1

    def asArray(self):
        z = Numeric.zeros(self.population, 'u')
        lst = [ ]
        r = self.root
        while r != None:
            lst.append(r)
            r = r.next
        def sortOrder(x1, x2):
            return cmp(x1.prefix, x2.prefix)
        lst.sort(sortOrder)
        i = 0
        for node in lst:
            for j in range(128):
                w = node.data[j]
                for k in range(32):
                    if (w & (1 << k)) != 0:
                        z[i] = (node.prefix << 12) + (j << 5) + k
                        i += 1
        return z

    def remove(self, x):
        x0, x1, x2 = (x >> 12) & 0xfffff, (x >> 5) & 0x7f, x & 0x1f
        C = self.findNodeWithPrefix(x0)
        if C == None:
            return
        # Set the bit in C's data
        z = C.data[x1]
        if (z & (1 << x2)) != 0:
            C.data[x1] = z & ~(1 << x2)
            self.population -= 1

    def contains(self, x):
        x0, x1, x2 = (x >> 12) & 0xfffff, (x >> 5) & 0x7f, x & 0x1f
        C = self.findNodeWithPrefix(x0)
        if C == None:
            return False
        if C is not self.root:
            self.bubbleUp(C)
##             if self.bubbleCounter == 0:
##                 self.bubbleUp(C)
##                 self.bubbleCounter = 10
##             else:
##                 self.bubbleCounter -= 1
        # Set the bit in C's data
        z = C.data[x1]
        return (z & (1 << x2)) != 0

    def bubbleUp(self, C):
        B = C.previous
        D = C.next
        if B != None:
            A = B.previous
            if A != None:
                A.next = C
            B.next = D
            B.previous = C
        if D != None:
            D.previous = B
        C.next = B
        C.previous = A

    def performanceTest(self, f, n=100):
        t1 = time.time()
        for i in range(n):
            f()
        t2 = time.time()
        return (t2 - t1) / n

    def add_performance(self):
        n = 10**5
        def f():
            self.addRange(0, n)
        t = self.performanceTest(f, 1)
        return t / n

    def contains_performance(self):
        n = 10**5
        def f():
            for i in range(n):
                self.contains(i)
        t = self.performanceTest(f, 1)
        return t / n

    def asarray_performance(self):
        n = 10**5
        self.addRange(0, n)
        t = self.performanceTest(self.asArray, 1)
        return t / n

class Tests(unittest.TestCase):

    def intsetsize(self):
        len(self.x)

    def intsetcontains(self):
        self.x.contains_performance(self.n)

    def test_Set(self):
        x = Set()
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

    def test_SetContainsPerformance(self):
        x = Set()
        N = 10**4
        x.addRange(0, N)
        T = x.contains_performance()
        expectedTime = 7.0e-6
        if VERBOSE:
            stuff.append(("test_SetContainsPerformance", T, expectedTime))
        assert T <= expectedTime

    def test_SetMemoryUsage(self):
        x = Set()
        x.add(1)
        x.add(3)
        x.add(1800)
        if VERBOSE:
            stuff.append(("memusage", x.memUsage))
        assert x.memUsage < 530

    def test_SetAddPerformance(self):
        x = Set()
        T = x.add_performance()
        expectedTime = 10.0e-6
        if VERBOSE:
            stuff.append(("test_SetAddPerformance", T, expectedTime))
        assert T <= expectedTime

    def test_SetAsArrayPerformance(self):
        x = Set()
        T = x.asarray_performance()
        expectedTime = 2.0e-6
        if VERBOSE:
            stuff.append(("test_SetAsArrayPerformance", T, expectedTime))
        assert T <= expectedTime

    def test_SetAsArray(self):
        x = Set()
        N = 10**4
        a = Numeric.array(range(N), Numeric.UInt32)
        x.addRange(0, N)
        assert len(x) == len(a)
        assert len(x) == N
        xa = x.asArray()
        a = a - xa
        assert Numeric.vdot(a, a) == 0

def test():
    suite = unittest.makeSuite(Tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    test()
    if VERBOSE:
        for x in stuff:
            print x
