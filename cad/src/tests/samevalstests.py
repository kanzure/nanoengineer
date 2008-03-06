# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: EricM
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

import unittest
from samevals import same_vals, setArrayType
import Numeric

class SameValsTests(unittest.TestCase):

    def test_simple(self):
        assert same_vals(1, 1)
        assert not same_vals(1, 2)

    def test_dict1(self):
        a = {}
        b = {}
        assert same_vals(a, b)
        a["abc"] = 23 ;
        assert not same_vals(a, b)
        b["def"] = 45 ;
        assert not same_vals(a, b)
        a["def"] = 42 ;
        b["abc"] = 23 ;
        assert not same_vals(a, b)
        a["def"] = 45 ;
        assert same_vals(a, b)

    def test_list1(self):
        a = []
        b = []
        assert same_vals(a, b)
        a.append("ferd")
        assert not same_vals(a, b)
        b.append("asdf")
        assert not same_vals(a, b)
        a.append("poiu")
        b.append("poiu")
        assert not same_vals(a, b)
        a[0] = "asdf"
        assert same_vals(a, b)

    def test_tuple1(self):
        # anyone know how to generate a zero length tuple?
        assert same_vals((1,), (1,))
        assert not same_vals((1, 2), (1,))
        assert same_vals((1, 2), (1, 2))
        assert not same_vals((1, 2), (2, 1))

    def test_numeric_equals(self):
        a = Numeric.array((1, 2, 3))
        b = Numeric.array((1, 2, 3))
        print a == b
        print a != b
        assert a == b
        assert not a != b
        b = Numeric.array((1, 4, 5))
        print a == b
        print a != b
        assert a != b
        assert not a == b

def test():
    suite = unittest.makeSuite(SameValsTests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    setArrayType(type(Numeric.array((1,2,3))))
    test()
