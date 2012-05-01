#!/usr/bin/python
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
# Think about the set sizes for which this scheme is memory efficient.

import time
import unittest
import numpy

stuff = None
#stuff = [ ]
N = 10**4
#N = 1000

## Verifying Bruce's suspicion that the 9/9/9/5 scheme was a memory
## hog...
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

"""The present scheme uses a doubly linked list of node. Each node
holds a block of 128 words, or 4096 bits, and represents the set
membership states of 4096 consecutive integers. Each node has a 20-bit
prefix for the upper 20 bits of the integers in its block.

We search the blocks for some operations (add, remove, contains), and
we assume that we'll be doing those operations in consecutive ranges
most of the time. Therefore this scheme tries to be efficient when each
search is close to the previous search. We do this by bubbling nodes to
the top of the linked list when their blocks get searched, so that they
will be found faster on the next linked list traversal.

This will not be an efficient scheme for random searches, for two
reasons. One is that we'll have to search the linked list in a
non-optimal order. The other is that we'll waste time bubbling nodes
toward the top when it doesn't help. To avoid the latter, we save the
prefix for the previous search, and only bubble up if it matches the
present prefix.
"""

class NodeStruct:
    """
    /* (3 + 128) * 4 = 524 bytes */
    struct node {
        struct node *next;
        int prefix;
        unsigned int data[128];
    };
    """
    def __init__(self, prefix):
        self.prefix = prefix
        # next initialized to NULL
        self.next = None
        # all membership bits initially zero
        self.data = 128 * [ 0 ]

class Set:

    """
    /* 3 * 4 = 12 bytes */
    struct set {
        struct node *root;
        unsigned int population;
    };
    """
    def __init__(self):
        self.root = None
        self.population = 0

    def __len__(self):
        return self.population

    def findNodeWithPrefix(self, p):
        A = None
        B = self.root
        while True:
            if B == None:
                return None
            if B.prefix == p:
                # bubble B up toward the top
                if A != None:
                    A.next = B
                    B.next = self.root
                    self.root = B
                return B
            A = B
            B = B.next

    def bubbleUp(self, C):
        # bubble this node up toward the top of the list, but only
        # if we match the previous prefix
        B = C.previous
        # If C has no previous, then it's already at the top.
        if B != None:
            A = B.previous
            D = C.next
            if A != None:
                A.next = C
            else:
                self.root = C
            if D != None:
                D.previous = B
            B.next = D
            B.previous = C
            C.next = B
            C.previous = A

    def add(self, x):
        x0, x1, x2 = (x >> 12) & 0xfffff, (x >> 5) & 0x7f, x & 0x1f
        C = self.findNodeWithPrefix(x0)
        if C == None:
            # create a new node
            C = NodeStruct(x0)
            if self.root != None:
                self.root.previous = C
            C.next = self.root
            self.root = C
        # Set the bit in C's data
        z = C.data[x1]
        if (z & (1 << x2)) == 0:
            C.data[x1] = z | (1 << x2)
            self.population += 1

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
        # Set the bit in C's data
        z = C.data[x1]
        return (z & (1 << x2)) != 0

################################################

class SetWithTestMethods(Set):

    ADD_ELEMENT_TIME = 13.0e-6
    CONTAINS_ELEMENT_TIME = 12.0e-6
    ASARRAY_ELEMENT_TIME = 2.5e-6

    def __init__(self):
        Set.__init__(self)

    def __len__(self):
        return self.population

    def efficiency(self):
        # assume 1 bit per element, ideally
        idealMemUsage = (self.population + 7) / 8.0
        return idealMemUsage / self.memUsage()

    def memUsage(self):
        total = 2 * 4   # root, population, both ints
        r = self.root
        while r != None:
            total += (3 + 128) * 4
            r = r.next
        return total

    def addRange(self, m, n):
        while m != n:
            self.add(m)
            m += 1

    def performanceTest(self, f, n=100):
        t1 = time.time()
        for i in range(n):
            f()
        t2 = time.time()
        return (t2 - t1) / n

    def add_performance(self):
        def f():
            self.addRange(0, N)
        t = self.performanceTest(f, 1)
        return t / N

    def contains_performance(self):
        self.addRange(0, N)
        def f():
            for i in range(N):
                self.contains(i)
        t = self.performanceTest(f, 1)
        return t / N

    def asarray_performance(self):
        self.addRange(0, N)
        t = self.performanceTest(self.asArray, 1)
        return t / N

class Tests(unittest.TestCase):

    # FUNCTIONAL TESTS

    def test_Functionality(self):
        #
        # Test general set functionality, make sure it does
        # the right things.
        #
        x = SetWithTestMethods()
        for i in range(2 * N):
            if (i & 1) == 0:
                x.add(i)
        assert len(x) == N
        assert not x.contains(-2)
        assert not x.contains(-1)
        assert x.contains(0)
        assert not x.contains(1)
        assert x.contains(2)
        assert not x.contains(3)
        assert x.contains(4)
        if (N % 2) == 0:
            assert x.contains(N-4)
            assert not x.contains(N-3)
            assert x.contains(N-2)
            assert not x.contains(N-1)
            assert x.contains(N)
            assert not x.contains(N+1)
            assert x.contains(N+2)
        else:
            assert not x.contains(N-4)
            assert x.contains(N-3)
            assert not x.contains(N-2)
            assert x.contains(N-1)
            assert not x.contains(N)
            assert x.contains(N+1)
            assert not x.contains(N+2)
        assert x.contains(2*N-4)
        assert not x.contains(2*N-3)
        assert x.contains(2*N-2)
        assert not x.contains(2*N-1)
        assert not x.contains(2*N)
        assert not x.contains(2*N+1)

    def test_AsArray(self):
        x = SetWithTestMethods()
        a = Numeric.array(range(N), Numeric.UInt32)
        x.addRange(0, N)
        assert len(x) == len(a)
        assert len(x) == N
        xa = x.asArray()
        a = a - xa
        assert Numeric.vdot(a, a) == 0

    # MEMORY TEST

    def test_MemoryUsage(self):
        #
        # A very small set should occupy a small memory footprint.
        # It works out to 536 bytes for very small sets.
        #
        x = SetWithTestMethods()
        x.add(1)
        x.add(3)
        x.add(1800)
        if stuff != None:
            stuff.append(("memusage", x.memUsage()))
        assert x.memUsage() < 540

    # PERFORMANCE TESTS

    def test_AddPerformance(self):
        x = SetWithTestMethods()
        T = x.add_performance()
        if stuff != None:
            stuff.append(("test_AddPerformance", T))
        assert T <= x.ADD_ELEMENT_TIME

    def test_ContainsPerformance(self):
        x = SetWithTestMethods()
        T = x.contains_performance()
        if stuff != None:
            stuff.append(("test_ContainsPerformance", T))
        assert T <= x.CONTAINS_ELEMENT_TIME

    def test_AsArrayPerformance(self):
        x = SetWithTestMethods()
        T = x.asarray_performance()
        if stuff != None:
            stuff.append(("test_AsArrayPerformance", T))
        assert T <= x.ASARRAY_ELEMENT_TIME

def test():
    suite = unittest.makeSuite(Tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    test()
    if stuff != None:
        for x in stuff:
            print x
