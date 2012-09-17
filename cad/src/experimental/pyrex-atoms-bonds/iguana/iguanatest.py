# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
# $Id$

import iguana
import unittest

baseline_code = """
+!:
    <atomic
        /* x p */
        dup fetch     /* x p (*p) */
        rot + swap    /* (*p)+x p */
        store
    atomic> exit

foo:
    rand exit

bar:
    2.718 exit

quux:
    ouch exit

/* this requires we set up some data memory */
tryloop:
    0 0 store
    600 0 do
        i 0 +!
    loop
    exit

tryloop2:
    0
    600 0 do
        i +
    loop
    exit

quickloop:
    600 0 do loop exit
"""

class IguanaTests(unittest.TestCase):

    def setUp(self):
        self.prog = prog = iguana.Program()
        prog.compile(baseline_code)

    def test_loop1(self):
        self.prog.compile("main: tryloop exit")
        mem = 3 * [ 0.0 ]
        self.prog.thread("main", mem)
        self.prog.run()
        assert mem[0] == (600.0 * 599) / 2
        assert mem[1] == 0.0
        assert mem[2] == 0.0

    # this is quite slow, because we're doing lots of "fetch" and "store" operations
    def test_loop1_many_threads(self):
        self.prog.compile("main: tryloop exit")
        mem = 3 * [ 0.0 ]
        for i in range(1000):
            self.prog.thread("main", mem)
        self.prog.run()
        assert mem[0] == 1000 * (600.0 * 599) / 2
        assert mem[1] == 0.0
        assert mem[2] == 0.0

    def test_loop2(self):
        self.prog.compile("main: tryloop2 exit")
        T = self.prog.thread("main")
        self.prog.run()
        assert T.pop() == (600.0 * 599) / 2

    def test_loop2_many_threads(self):
        self.prog.compile("main: tryloop2 exit")
        threads = [ ]
        for i in range(1000):
            threads.append(self.prog.thread("main"))
        self.prog.run()
        for i in range(1000):
            assert threads[i].pop() == (600.0 * 599) / 2

    def test_quickloop(self):
        self.prog.compile("main: quickloop exit")
        T = self.prog.thread("main")
        self.prog.run()

    def test_quux(self):
        T = self.prog.thread("quux")
        try:
            self.prog.run()
            assert False, "this should have failed"
        except iguana.IguanaError:
            pass

    def test_bar(self):
        T = self.prog.thread("bar")
        self.prog.run()
        assert T.pop() == 2.718

    def __test_foo(self):
        for i in range(20):
            T = self.prog.thread("foo")
            self.prog.run()
            print T.pop()

def test():
    suite = unittest.makeSuite(IguanaTests, 'test')
    #suite = unittest.makeSuite(Tests, 'test_atomset_atomInfo')
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    test()
